from datetime import UTC, datetime, timedelta
import hashlib
import secrets

import jwt

from app.config import settings


class TokenUtils:
    """
    actions perfomred on tokens. has two methods:
        - create_access_token
        - verify_access_token
        - generate_reset_token
        - hash_reset_token
    """

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        staticmethod to create  a JWToken(Json Web Token)

        Args:
            data:dict

        Returns:
            access_token:str - the access token created
        """
        # create copy of the data, which usually consists of username, email
        # and password
        to_encode = data.copy()

        # add expiration time on it
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expiration_minutes,
        )
        to_encode.update({"exp": expire})

        # encode token and data to be passed in JSON
        # ".get_secret_value()" ensures we get actual string and not asteriks
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key.get_secret_value(),
            algorithm=settings.algorithm,
        )

        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str) -> str | None:
        """
        staticmethod to decode and verify a JWToken(Json Web Token). it returns the
        "sub"(subject) which conatins the "user_id" if it's valid.

        Args:
            token:str

        Returns:
            sub: which is the "user_id" as a string

        Raises:
            jwt.InvalidTokenError: if the token is not valid
        """

        try:
            payload = jwt.decode(
                token,
                settings.secret_key.get_secret_value(),
                algorithms=[settings.algorithm],
                options={"require": ["exp", "sub"]},
            )
        except jwt.InvalidTokenError:
            return None
        else:
            return payload.get("sub")

    @staticmethod
    def generate_reset_token() -> str:
        """
        return urlsafe token link of base64 characters thats perfect for email links

        NOTE:
        - its length must be 64 since thisis the max size we defined in our
          database
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_reset_token(token: str) -> str:
        """
        takes a token and returns its sha256. we used this here

        NOTE:
        - we used hashlib and not not argon2  like we did with our passwords
        since inthe latter case, passwords are weak and predictable hence a string
        has was needed tomake brute force impossible. in this case, tokens are
        already randomized, hence a weak hash is acceptable.
        """
        return hashlib.sha256(token.encode()).hexdigest()
