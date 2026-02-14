import requests
from jose import jwt
from jose.exceptions import JWTError
from app.core.config import settings

ALGORITHMS = ["ES256"]


def get_jwks():
    """
    Fetch JWKS (public keys) from Supabase.
    This is used to verify JWT signatures.
    """
    response = requests.get(settings.SUPABASE_JWKS_URL)
    response.raise_for_status()
    return response.json()


def verify_jwt(token: str):
    """
    Verify Supabase JWT and return payload if valid.
    Returns None if token is invalid or expired.
    """
    try:
        jwks = get_jwks()
        header = jwt.get_unverified_header(token)

        key = next(
            k for k in jwks["keys"]
            if k["kid"] == header["kid"]
        )

        payload = jwt.decode(
            token,
            key,
            algorithms=ALGORITHMS,
            audience="authenticated"
        )
        return payload

    except (JWTError, StopIteration):
        return None
