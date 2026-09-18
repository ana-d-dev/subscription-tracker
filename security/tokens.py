import secrets


def generate_subscription_id():
    new_token = secrets.token_hex()
    return new_token