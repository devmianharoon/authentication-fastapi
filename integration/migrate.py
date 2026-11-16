from app.gdpr import GdprConsent
from app.db import engine
if __name__ == '__main__':
    GdprConsent.__table__.create(engine, checkfirst=True)
    print('PrivacyLib consent table ready.')
