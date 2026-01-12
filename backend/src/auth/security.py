import bcrypt

def hash_password(password: str):
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password=bytes, salt=salt)
    return hashed_pw

def verify_pw(password: str, hashed_password: str) -> bool:
    result = bcrypt.checkpw(
        password=password.encode('utf-8'), 
        hashed_password=hashed_password.encode('utf-8')
    )
    return result