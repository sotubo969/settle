# Firebase Authentication Module
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException
import os
import json
import logging

logger = logging.getLogger(__name__)

# Firebase Admin SDK initialization
_firebase_app = None

def get_firebase_app():
    """Get or initialize Firebase Admin SDK"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    
    try:
        # Try to load service account from environment variable (JSON string)
        service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
        
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                cred = credentials.Certificate("./firebase-adminsdk.json")
                _firebase_app = firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized from environment variable")
                return _firebase_app
            except json.JSONDecodeError:
                logger.warning("Failed to parse FIREBASE_SERVICE_ACCOUNT as JSON")
        
        # Try to load from file path
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-admin.json')
        
        if os.path.exists(service_account_path):
            cred = credentials.Certificate("./firebase-adminsdk.json")
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin SDK initialized from file: {service_account_path}")
            return _firebase_app
        
        # Initialize without credentials (for testing/development)
        # This will only work for basic operations
        _firebase_app = firebase_admin.initialize_app()
        logger.warning("Firebase Admin SDK initialized without credentials (limited functionality)")
        return _firebase_app
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return None


async def verify_firebase_token(id_token: str) -> dict:
    """
    Verify Firebase ID token and return user info.
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        dict with user info: uid, email, email_verified, name, picture, auth_provider
    """
    app = get_firebase_app()
    
    if not app:
        raise HTTPException(
            status_code=500, 
            detail="Firebase not configured. Please set up Firebase credentials."
        )
    
    try:
        # Verify the ID token
        decoded_token = firebase_auth.verify_id_token(id_token)
        
        # Extract user information
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        email_verified = decoded_token.get('email_verified', False)
        name = decoded_token.get('name')
        picture = decoded_token.get('picture')
        
        # Determine auth provider
        sign_in_provider = decoded_token.get('firebase', {}).get('sign_in_provider', 'password')
        
        # Google users are always considered verified
        if sign_in_provider == 'google.com':
            email_verified = True
            auth_provider = 'google'
        else:
            auth_provider = 'email'
        
        return {
            'uid': uid,
            'email': email,
            'email_verified': email_verified,
            'name': name,
            'picture': picture,
            'auth_provider': auth_provider,
            'sign_in_provider': sign_in_provider
        }
        
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Firebase token expired")
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Firebase token revoked")
    except firebase_auth.CertificateFetchError:
        raise HTTPException(status_code=500, detail="Failed to fetch Firebase certificates")
    except Exception as e:
        logger.error(f"Firebase token verification error: {e}")
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")


async def get_firebase_user(uid: str) -> dict:
    """Get Firebase user by UID"""
    app = get_firebase_app()
    
    if not app:
        raise HTTPException(status_code=500, detail="Firebase not configured")
    
    try:
        user = firebase_auth.get_user(uid)
        return {
            'uid': user.uid,
            'email': user.email,
            'email_verified': user.email_verified,
            'display_name': user.display_name,
            'photo_url': user.photo_url,
            'disabled': user.disabled
        }
    except firebase_auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Firebase user not found")
    except Exception as e:
        logger.error(f"Error fetching Firebase user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def is_firebase_configured() -> bool:
    """Check if Firebase is properly configured"""
    app = get_firebase_app()
    return app is not None
