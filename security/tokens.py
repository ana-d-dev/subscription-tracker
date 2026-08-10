import secrets


def generate_token():
    new_token = secrets.token_hex()
    return new_token