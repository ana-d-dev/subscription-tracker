from flask import session, redirect, url_for
from functools import wraps
from services.demo import prepare_demo_session


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


def demo_session_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        prepare_demo_session()

        return view(*args, **kwargs)

    return wrapped_view