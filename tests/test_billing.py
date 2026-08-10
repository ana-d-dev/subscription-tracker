from services.billing import calculate_next_payment, total_price
from datetime import date


def test_calculate_next_payment():
    started_on = date(2027, 1, 1)
    assert calculate_next_payment(3, started_on, 'monthly') == date(2027, 4, 1)


def test_total_price():
    all_subscriptions = [
        {'service': 'Netflix', 'price': 9.99, 'currency': 'EUR'},
        {'service': 'Youtube', 'price': 4.54, 'currency': 'USD'},
        {'service': 'Amazon prime', 'price': 7.89, 'currency': 'GBP'}
    ]

    totals = {'EUR': 9.99, 'USD': 4.54, 'GBP': 7.89}

    assert total_price(all_subscriptions) == totals