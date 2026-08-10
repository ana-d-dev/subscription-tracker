from sqlalchemy import String, Column, Table, Integer, Date, DateTime, Numeric, Boolean, ForeignKey, func
from db.engine import metadata



subscription_users = Table(
    'subscription_users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50), unique=True, nullable=False),
    Column('hashed_password', String(255), nullable=False),
    Column('created_at', DateTime, server_default=func.now())
)

subscriptions = Table(
    'subscriptions',
    metadata,
Column('id', Integer, primary_key=True),
    Column('user_id', Integer,ForeignKey('subscription_users.id'), nullable=False),
    Column('service', String(50), nullable=False),
    Column('price', Numeric(10, 2), nullable=False),
    Column('currency', String(3), nullable=False),
    Column('category', String(30), nullable=False),
    Column('plan', String(30), nullable=False),
    Column('billing_cycle', String(20), nullable=False),
    Column('started_on', Date),
    Column('next_payment', Date),
    Column('duration', Integer),
    Column('auto_renew', String),
    Column('notes', String(100)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('updated_at', DateTime, server_default=func.now(), onupdate=func.now())
)