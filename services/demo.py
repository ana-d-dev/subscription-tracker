from datetime import datetime, timedelta
from flask import session


DEMO_TIMEOUT = timedelta(minutes=30)

def prepare_demo_session():
    now = datetime.now()

    if 'demo_last_activity' not in session:
        session['demo_last_activity'] = now.isoformat()
    else:
        last_activity = datetime.fromisoformat(
            session['demo_last_activity']
        )

        if now - last_activity > DEMO_TIMEOUT:
            session.pop('demo_all_subscriptions', None)
            session.pop('demo_total', None)

        session['demo_last_activity'] = now.isoformat()

    if 'demo_all_subscriptions' not in session:
        session['demo_all_subscriptions'] = []

    if 'demo_total' not in session:
        session['demo_total'] = {
            'EUR': 0,
            'USD': 0,
            'GBP': 0
        }