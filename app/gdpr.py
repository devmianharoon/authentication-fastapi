"""Authenticated GDPR routes; original OAuth and account routes are unchanged."""
import os
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import SQLModel, Field, Session
from .db import engine
from .model import Users
from integration import policy_adapter as policy
from pathlib import Path

class GdprConsent(SQLModel, table=True):
    __tablename__ = 'gdpr_consents'
    user_name: str = Field(primary_key=True, foreign_key='users.userName')
    value: str
    withdrawn: bool = False

router = APIRouter(prefix='/gdpr', tags=['PrivacyLib'])
bearer = OAuth2PasswordBearer(tokenUrl='/login')

def subject(token: str = Depends(bearer)):
    from . import main as host
    try:
        claims = jwt.decode(token, host.SECRET_KEY, algorithms=[host.ALGORITHM], options={'require_exp': True, 'require_sub': True})
        username = claims.get('sub')
        if not isinstance(username, str) or not username:
            raise JWTError('Invalid subject')
    except (JWTError, TypeError, ValueError):
        raise HTTPException(401, 'Invalid or expired token', headers={'WWW-Authenticate': 'Bearer'})
    with Session(engine) as session:
        user = session.get(Users, username)
        if not user:
            raise HTTPException(401, 'Account not found')
        return user

def profile(user):
    return {'userName': user.userName, 'name': user.name, 'email': user.email, 'created_at': user.created_at.isoformat()}

async def read(request, operation, write=False):
    if request.headers.get('content-type','').split(';')[0].strip().lower() != 'application/json':
        raise HTTPException(415, 'JSON content type required')
    raw = bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw) > 16384:
            raise HTTPException(413, 'Request too large')
    try:
        return policy.validate(operation, policy.decode(bytes(raw)), ('userName','name','email','created_at'), ('name','email'), write)
    except OverflowError as exc:
        raise HTTPException(413, str(exc))
    except policy.InvalidInput as exc:
        raise HTTPException(400, str(exc))

@router.get('', response_class=HTMLResponse)
def page():
    return HTMLResponse((Path(__file__).resolve().parent.parent/'integration/privacy-page.html').read_text(encoding='utf-8'), headers={'Cache-Control':'no-store'})

@router.get('/profile')
def identity(user=Depends(subject)):
    return JSONResponse(profile(user), headers={'Cache-Control':'no-store'})

@router.patch('/consent')
async def save_consent(request: Request, user=Depends(subject)):
    value = await read(request, 'consent', True)
    with Session(engine) as session:
        session.merge(GdprConsent(user_name=user.userName, **value))
        session.commit()
    return JSONResponse(value, headers={'Cache-Control':'no-store'})

@router.post('/{operation}')
async def decision(operation: str, request: Request, user=Depends(subject)):
    value = await read(request, operation)
    admins = [x.strip() for x in os.environ.get('GDPR_ADMIN_USER_IDS','').split(',') if x.strip()]
    if operation == 'breach' and user.userName not in admins:
        raise HTTPException(403, 'Administrator access required')
    with Session(engine) as session:
        saved = session.get(GdprConsent, user.userName)
        consent = {'value': saved.value, 'withdrawn': saved.withdrawn} if saved else None
    try:
        result = policy.evaluate(operation, profile(user), user.userName, consent, value)
    except Exception:
        raise HTTPException(502, 'OPA evaluation failed')
    return JSONResponse(result, headers={'Cache-Control':'no-store'})
