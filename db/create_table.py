from db.engine import engine
from db.engine import metadata
from db.tables import subscription_users, subscriptions


metadata.create_all(engine)