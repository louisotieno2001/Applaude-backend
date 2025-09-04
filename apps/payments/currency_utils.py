import os
import requests
from django.core.cache import cache
from decimal import Decimal

def get_exchange_rates():
    """
    Fetches the latest exchange rates from ExchangeRate-API and caches them.
    The free tier of this API allows for 1,500 requests per month.
    Caching for 24 hours (86400 seconds) ensures we only use ~30 requests per month.
    """
    rates = cache.get('exchange_rates')
    if rates:
        return rates

    api_key = os.getenv('EXCHANGERATE_API_KEY')
    if not api_key:
        # Fallback to a mock response if the API key is not set
        return {'USD': 1.0, 'EUR': 0.92, 'JPY': 155.0}

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get('result') == 'success':
            rates = data.get('conversion_rates', {})
            # Convert rates to Decimal for precision
            rates_decimal = {k: Decimal(str(v)) for k, v in rates.items()}
            cache.set('exchange_rates', rates_decimal, 86400) # Cache for 24 hours
            return rates_decimal
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch exchange rates: {e}")

    # Return a default/fallback if the API call fails
    return {'USD': Decimal('1.0')}
