# OAuth Configuration Guide

## Environment Variables

Add the following variables to your `.env` file:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Facebook OAuth
FACEBOOK_CLIENT_ID=your_facebook_app_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret_here
```

## Setup Instructions

### 1. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure the OAuth consent screen
6. Set application type to "Web application"
7. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://your-production-domain.com/accounts/google/login/callback/`
8. Copy the Client ID and Client Secret to your `.env` file

### 2. Django Admin Configuration

After running migrations, you need to configure the OAuth app in Django admin:

1. Run migrations:
   ```bash
   python manage.py migrate
   ```

2. Access Django admin at `http://localhost:8000/admin/`

3. Go to **Sites** and verify/update the domain:
   - For development: `localhost:8000`
   - For production: `your-production-domain.com`

4. Go to **Social applications** → **Add social application**

5. For Google:
   - Provider: Google
   - Name: Google OAuth
   - Client id: (from .env)
   - Secret key: (from .env)
   - Sites: Select your site

## Testing

1. Navigate to `/login/` or `/signup/`
2. Click "Continue with Google"
3. Complete the OAuth flow
4. Verify you're redirected back and logged in
5. Check that a Profile was created automatically in the database
