"""PIN Code Lookup - enter an Indian PIN code and get details about the area.

Data source: https://api.postalpincode.in (free public India Post data).

Run:
    pip install requests
    python pincode_lookup.py            # asks for a PIN
    python pincode_lookup.py 110001     # or pass it directly
"""

import re
import sys

import requests

API_URL = "https://api.postalpincode.in/pincode/{pin}"
PIN_PATTERN = re.compile(r"^[1-9][0-9]{5}$")  # 6 digits, cannot start with 0


def is_valid_pin(pin):
    return bool(PIN_PATTERN.match(pin))


def get_pin_details(pin):
    """Return a list of post offices for the PIN, or raise ValueError with a message."""
    try:
        response = requests.get(API_URL.format(pin=pin), timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.Timeout:
        raise ValueError("The service took too long to respond. Try again.")
    except (requests.RequestException, ValueError):
        raise ValueError("Could not reach the postal data service.")

    entry = data[0] if isinstance(data, list) and data else {}
    offices = entry.get("PostOffice") or []
    if entry.get("Status") != "Success" or not offices:
        raise ValueError(f"No post offices found for PIN code {pin}.")
    return offices


def print_details(pin, offices):
    first = offices[0]
    delivery = sum(1 for o in offices if o.get("DeliveryStatus") == "Delivery")

    print(f"\nPIN code : {pin}")
    print(f"State    : {first.get('State')}")
    print(f"District : {first.get('District')}")
    print(f"Division : {first.get('Division')}")
    print(f"Region   : {first.get('Region')}")
    print(f"Circle   : {first.get('Circle')}")
    print(f"Country  : {first.get('Country')}")
    print(f"\n{len(offices)} post office(s), {delivery} with delivery:\n")

    print(f"{'Post office':<30} {'Type':<22} {'Delivery':<13} Block")
    print("-" * 80)
    for o in offices:
        print(
            f"{str(o.get('Name')):<30} "
            f"{str(o.get('BranchType')):<22} "
            f"{str(o.get('DeliveryStatus')):<13} "
            f"{o.get('Block') or '-'}"
        )


def main():
    pin = sys.argv[1] if len(sys.argv) > 1 else input("Enter 6-digit PIN code: ")
    pin = pin.strip()

    if not is_valid_pin(pin):
        print("Invalid PIN. Enter 6 digits, not starting with 0.")
        sys.exit(1)

    try:
        offices = get_pin_details(pin)
    except ValueError as error:
        print(error)
        sys.exit(1)

    print_details(pin, offices)


if __name__ == "__main__":
    main()