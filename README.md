# FastAPI OAuth2 Authentication Application

This is a FastAPI-based application implementing OAuth2 authentication with Google and GitHub, along with basic user registration and login functionalities. It also provides routes to get all registered users.

## Features

- OAuth2 authentication with Google and GitHub.
- User registration.
- User login with JWT token generation.
- Fetch all registered users.

## Prerequisites
- Python 3.11+
- FastAPI
- SQLModel
- HTTPX
- Uvicorn
- python-dotenv

## Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/devmianharoon/authentication-fastapi.git
   cd fastapi-oauth2-authentication

   ```

2. **Install the dependencies:**
   `poetry install `

3. **Create and activate a virtual environment:**
   `poetry shell`

4. **Create a .env file in the root directory and add the following variables:**

    ```ALGORITHM=HS256
    SECRET_KEY=your_secret_key
    GITHUB_CLIENT_ID=your_github_client_id
    GITHUB_CLIENT_SECRET=your_github_client_secret
    GITHUB_REDIRECT_URI=your_github_redirect_uri
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_PROJECT_ID=your_google_project_id
    GOOGLE_REDIRECT_URI=your_google_redirect_uri
    GOOGLE_TOKEN_URL=https://oauth2.googleapis.com/token
    ```
5. **Run the application:**
    ```poetry run dev```

6. **Usage**
    ## Endpoints:

    # Google Login:
       - GET /google-login - Redirects to Google OAuth2 login page.
       - GET /auth/google - Callback URL for Google authentication.

    # GitHub Login:
       - GET /github-login - Redirects to GitHub OAuth2 login page.
       - GET /auth/callback - Callback URL for GitHub authentication.

    # User Registration:
       - POST /resister - Register a new user.

    # User Login:
       - POST /login - Login with username and password.

    # Get All Users:

       - GET /users - Retrieve all registered users.

**Contributing**

    Contributions are welcome! Please open an issue or submit a pull request.


## PrivacyLib GDPR integration

Original framework: **[PrivacyLib-REGO](https://github.com/CS-UCY-SEIT-lab/PrivacyLib-REGO)**. The unchanged Python router and eleven Rego modules are bundled under `integration/privacy_lib/`. Host authentication, validation and consent storage are separate adapters.

### Setup and run

Use Python 3.12 and the original `poetry.lock` dependencies, plus [OPA 1.x](https://www.openpolicyagent.org/docs). On Windows the lock's Linux-only uvloop package is not used. No new Python runtime package is required by this integration. Keep virtual environments, `.env`, database files and private keys out of Git.

Export the original application's `SQLALCHEMY_DATABASE_URL`, `SECRET_KEY` and `ALGORITHM=HS256` before importing it: the original database module loads before `.env` is read. For a local demo, a SQLite URL such as `sqlite:///./privacy-demo.sqlite3` works; the original PostgreSQL engine option is retained. Use a private generated secret. Google/GitHub credentials are not needed for the existing username/password login.

On an existing database, add only the separate consent table:

```sh
python -m integration.migrate
```

For a new database, the original table initializer must run first (`from app.db import create_tables; create_tables()`). The original `poetry run dev` startup initializes registered tables. GDPR request handlers never create tables or alter existing account rows.

Start OPA from this directory:

```sh
opa run --server --addr 127.0.0.1:8181 integration/privacy_lib/gdpr
```

`OPA_QUERY_URL` defaults to `http://localhost:8181/v1/query`. Configure synthetic controller, purposes, retention and services in `integration/privacy-config.json` for the intended application.

Start the app without the original development reloader:

```sh
python -m uvicorn app.main:app --host 127.0.0.1 --port 8040
```

Open `/docs` for the original API. Its registration route is spelled `/resister`; provide dummy userName/name/email/password and omit created_at to use the model's default. Open `/gdpr` for privacy checks and sign in with the same username/password. The page calls the original `/login` and handles its original `access token` response field. The bearer token stays in page memory and is cleared on refresh; no auth cookie or browser token storage is introduced. The public page contains no embedded account data.

### Scope and authorization

Routes: `GET /gdpr` (public shell), `GET /gdpr/profile` (authenticated identity), `PATCH /gdpr/consent`, and eleven `POST /gdpr/{operation}` calls: consent, lawful, information, access, rectification, erasure, restriction, portability, objection, complaint, breach. Count:14 HTTP method/operation pairs. Private calls require `Authorization: Bearer <token>`; mutations require JSON. These routes verify JWT signature, allowed algorithm, required expiry/subject and expiration, then resolve the existing database account. They do not trust a client subject or role. Cookie-based authentication is not accepted, so no ambient session/CSRF token is used for these bearer-only routes.

Mapped fields are userName, name, email and creation date. The subject is the current stored userName primary key. Passwords, JWTs and other users are excluded. Rectification accepts name/email only. Consent is stored separately. Other responses are decisions and proposed plans: account edits, deletion, transfers, complaint delivery, notifications and audit writes are not executed. Access returns metadata; portability returns selected real values. Synthetic metadata and passing checks do not establish legal compliance.

The original app has no administrator role. Breach is disabled by default; an operator may explicitly set `GDPR_ADMIN_USER_IDS` to trusted usernames (comma-separated) in the server environment. This setting cannot be supplied by clients.

Existing registration/OAuth/login/user-list routes are unchanged. Their original password representation and user-list authorization behavior are outside the new GDPR routes; the original `/users` result is not a GDPR export. This integration does not claim to repair unrelated host authentication or external OAuth flows. Use dummy data for the demonstration.

### Verify

```sh
python integration/test.py
```

Set `OPA_BINARY` if OPA is not on PATH. The native runner uses the current Python environment, an independent temporary SQLite database, private random signing key and local app/OPA ports. It exercises actual registration/login, malformed/tampered/expired/no-expiry JWT rejection, all policies, two-user isolation, consent/withdrawal, strict input limits and OPA outage behavior. Temporary processes/database/files are cleaned before reporting success. No external test framework or repository evaluation report is added.
