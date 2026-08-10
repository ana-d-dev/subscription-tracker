from db.tables import subscription_users, subscriptions
from sqlalchemy import insert, select, update, delete
from db.engine import engine



def user_exists(username):
    with engine.connect() as conn:
        statement = select(subscription_users).where(subscription_users.c.username == username)
        result = conn.execute(statement)
        if result.first():
            return True
        return False


def save_user(data):
    with engine.begin() as conn:
        statement = insert(subscription_users).values(data)
        conn.execute(statement)


def get_user_by_username(username):
    with engine.connect() as conn:
        statement = select(subscription_users).where(subscription_users.c.username == username)
        result = conn.execute(statement)
        user = result.mappings().first()
        return user


def get_user_by_id(user_id):
    with engine.connect() as conn:
        statement = select(subscription_users).where(subscription_users.c.id == user_id)
        result = conn.execute(statement)
        user = result.mappings().first()
        return user


def save_subscription(data):
    with engine.begin() as conn:
        statement = insert(subscriptions).values(data)
        conn.execute(statement)


def get_subscriptions(user_id):
    with engine.connect() as conn:
        statement = select(subscriptions).where(subscriptions.c.user_id == user_id)
        result = conn.execute(statement)
        all_subscriptions = result.mappings().all()
        return all_subscriptions


def get_subscription_by_id(subscription_id, user_id):
    with engine.connect() as conn:
        statement = select(subscriptions).where(
            subscriptions.c.id == subscription_id,
            subscriptions.c.user_id == user_id
        )
        result = conn.execute(statement)
        subscription_detail = result.mappings().one_or_none()
        return subscription_detail


def update_subscription(subscription_id, user_id, data):
    with engine.connect() as conn:
        statement = update(subscriptions).where(
            subscriptions.c.user_id == user_id,
            subscriptions.c.id == subscription_id
        ).values(data)
        conn.execute(statement)
        conn.commit()


def delete_subscription(subscription_id, user_id):
    with engine.connect() as conn:
        statement = delete(subscriptions).where(
            subscriptions.c.user_id == user_id,
            subscriptions.c.id == subscription_id
        )
        conn.execute(statement)
        conn.commit()