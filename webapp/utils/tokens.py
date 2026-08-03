from datetime import UTC, datetime, timedelta

import jwt

from webapp.config import settings


class TokenUtils:
    """
    actions perfomred on tokens. has two methods:
        - create_access_token()
        - verify_access_token()
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
