
from dateutil.relativedelta import relativedelta

def calculate_next_payment(duration, started_on, billing_cycle):

    if billing_cycle == 'days':
        result = started_on + relativedelta(days=duration)
        return result

    elif billing_cycle == 'weekly':
        result = started_on + relativedelta(weeks=duration)
        return result

    elif billing_cycle == 'monthly':
        result = started_on + relativedelta(months=duration)
        return result

    elif billing_cycle == 'yearly':
        result = started_on + relativedelta(years=duration)
        return result

    return None



def total_price(all_subscriptions):
    totals = {
        'EUR': 0,
        'USD': 0,
        'GBP': 0
    }

    for sub in all_subscriptions:
        currency = sub['currency']
        price = sub['price']

        totals[currency] += price

    return totals


