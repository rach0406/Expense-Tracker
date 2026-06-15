import requests

API_KEY = "806806bfd211f01cd6dd21a9"  
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

# All currencies we support in our app
SUPPORTED_CURRENCIES = ["INR", "USD", "EUR", "GBP", "JPY", "AED", "SGD", "AUD"]


def get_exchange_rates(base_currency="INR"):
    """
    Fetch live exchange rates for a given base currency.
    Returns a dict like: {"USD": 0.012, "EUR": 0.011, ...}
    """
    try:
        url = f"{BASE_URL}/latest/{base_currency}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data["result"] == "success":
            return data["conversion_rates"]
        else:
            print(f"API Error: {data['error-type']}")
            return None

    except requests.exceptions.ConnectionError:
        print("❌ No internet connection.")
        return None
    except requests.exceptions.Timeout:
        print("❌ Request timed out.")
        return None


def convert_to_inr(amount, from_currency):
    """
    Convert any amount from a given currency to INR.
    Returns the converted amount rounded to 2 decimal places.
    """
    if from_currency == "INR":
        return round(amount, 2)  # no conversion needed

    rates = get_exchange_rates(base_currency=from_currency)

    if rates and "INR" in rates:
        converted = amount * rates["INR"]
        return round(converted, 2)
    else:
        print(f"⚠️ Could not convert {from_currency} to INR. Using original amount.")
        return round(amount, 2)  # fallback: return as-is


def get_conversion_info(amount, from_currency, to_currency="INR"):
    """
    Returns a friendly summary string of the conversion.
    Example: "$ 10.00 USD  →  ₹ 836.50 INR"
    """
    rates = get_exchange_rates(base_currency=from_currency)

    SYMBOLS = {
        "INR": "₹", "USD": "$", "EUR": "€",
        "GBP": "£", "JPY": "¥", "AED": "د.إ",
        "SGD": "S$", "AUD": "A$"
    }

    if rates and to_currency in rates:
        converted = round(amount * rates[to_currency], 2)
        from_sym = SYMBOLS.get(from_currency, "")
        to_sym = SYMBOLS.get(to_currency, "")
        return f"{from_sym} {amount:.2f} {from_currency}  →  {to_sym} {converted:.2f} {to_currency}"
    else:
        return f"{amount:.2f} {from_currency} (conversion unavailable)"


# ─── Quick test ───────────────────────────────────────────────

if __name__ == "__main__":
    print("🌐 Testing Currency API...\n")

    # Test 1: Get rates
    rates = get_exchange_rates("USD")
    if rates:
        print(f"✅ Live rates fetched!")
        print(f"   1 USD = ₹ {rates['INR']:.2f} INR")
        print(f"   1 USD = € {rates['EUR']:.4f} EUR\n")

    # Test 2: Convert to INR
    amount_inr = convert_to_inr(100, "USD")
    print(f"✅ 100 USD = ₹ {amount_inr} INR\n")

    # Test 3: Conversion info string
    info = get_conversion_info(50, "EUR", "INR")
    print(f"✅ Conversion info: {info}")