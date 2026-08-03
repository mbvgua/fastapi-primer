from pwdlib import PasswordHash

# create password hasher using argon2 with recommended settings
hashing_algo = PasswordHash.recommended()


class PasswordUtils:
    """
    actions performed on passwords. has two methods:
        * hash_password()
        * verify_hash()
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        staticmethod to hash passwords.

        takes in a "password" arguments and returns its value as a hash.
        hashes are preferred to encryption values since decryption is not
        possible even when data is leaked. also the "argon2" package generates
        random salts for each hash, which is nice

        Args:
            password:str - password to be hashed

        Returns:
            hashed value of the password passed in as a parameter

        Examples:
            >>> hashed_pass = PasswordUtils.hash_password("@1234")
            qtuvcegcegyw87398y
        """

        return hashing_algo.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        method to confirm if "password" passed in by user when calling the
        class, and "hashed_password" present in the database are a match.
        if true, it returns "True" else "False"

        Args:
            password:str - password input by user
            hashed_password:str - user data existing in database to verify
            against

        Returns:
            True if the password matches the hash, False otherwise.

        Raises:
            exceptions.UnknownHashError: If the hash is not recognized by any
            of the hashers.

        Examples:
            >>> hashed_pass = PasswordUtils.verify_password("@1234","hashed_password")
            True

            >>> hashed_pass = PasswordUtils.verify_password("INVALID_PASSWORD","hashed_password")
            False
        """
        return hashing_algo.verify(password, hashed_password)
