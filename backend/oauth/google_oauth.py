from google.oauth2 import id_token
from google.auth.transport import requests
import os
from fastapi import HTTPException

class GoogleOAuth:
    CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    @staticmethod
    async def verify_token(token: str):
        """Verify Google OAuth token and get user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                GoogleOAuth.CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'avatar': idinfo.get('picture', '')
            }
        except ValueError as e:
            raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
    
    @staticmethod
    def get_authorization_url():
        """Get Google OAuth authorization URL"""
        redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
        return (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GoogleOAuth.CLIENT_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=openid email profile&"
            f"access_type=offline&"
            f"prompt=consent"
        )