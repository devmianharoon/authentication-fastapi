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
    Endpoints:

    Google Login:

    GET /google-login - Redirects to Google OAuth2 login page.
    GET /auth/google - Callback URL for Google authentication.
    GitHub Login:

    GET /github-login - Redirects to GitHub OAuth2 login page.
    GET /auth/callback - Callback URL for GitHub authentication.
    User Registration:

    POST /resister - Register a new user.
    User Login:

    POST /login - Login with username and password.
    Get All Users:

    GET /users - Retrieve all registered users.

**Contributing**
    Contributions are welcome! Please open an issue or submit a pull request.