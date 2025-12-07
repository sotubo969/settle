import jwt
import time
import os
from fastapi import HTTPException

class AppleOAuth:
    SERVICE_ID = os.environ.get('APPLE_SERVICE_ID')
    TEAM_ID = os.environ.get('APPLE_TEAM_ID')
    KEY_ID = os.environ.get('APPLE_KEY_ID')
    PRIVATE_KEY_PATH = os.environ.get('APPLE_PRIVATE_KEY_PATH')
    
    @staticmethod
    def generate_client_secret():
        """Generate Apple client secret JWT"""
        try:
            # Read private key
            if os.path.exists(AppleOAuth.PRIVATE_KEY_PATH):
                with open(AppleOAuth.PRIVATE_KEY_PATH, 'r') as f:
                    private_key = f.read()
            else:
                # Placeholder for when key file doesn't exist
                raise FileNotFoundError("Apple private key not found. Please add your .p8 file.")
            
            headers = {
                'kid': AppleOAuth.KEY_ID
            }
            
            payload = {
                'iss': AppleOAuth.TEAM_ID,
                'iat': int(time.time()),
                'exp': int(time.time()) + 3600,
                'aud': 'https://appleid.apple.com',
                'sub': AppleOAuth.SERVICE_ID
            }
            
            client_secret = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
            return client_secret
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Apple OAuth error: {str(e)}")
    
    @staticmethod
    async def verify_token(id_token: str):
        """Verify Apple ID token"""
        try:
            # Decode without verification for now (in production, verify with Apple's public keys)
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            
            return {
                'apple_id': decoded.get('sub'),
                'email': decoded.get('email', ''),
                'name': decoded.get('name', 'Apple User')
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid Apple token: {str(e)}")
    
    @staticmethod
    def get_authorization_url():
        """Get Apple Sign In authorization URL"""
        redirect_uri = os.environ.get('FRONTEND_URL') + '/api/auth/apple/callback'
        return (
            f"https://appleid.apple.com/auth/authorize?"
            f"client_id={AppleOAuth.SERVICE_ID}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code id_token&"
            f"scope=name email&"
            f"response_mode=form_post"
        )