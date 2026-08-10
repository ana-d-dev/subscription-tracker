from werkzeug.security import generate_password_hash, check_password_hash
from db.queries import get_user_by_username



def hash_password(password):
    hashed_password = generate_password_hash(password)
    return hashed_password


def check_password(username, password):
    user = get_user_by_username(username)

    if not user:
        return False

    hashed_password = user['hashed_password']
    return check_password_hash(hashed_password, password)




