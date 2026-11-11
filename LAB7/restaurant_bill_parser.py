"""
Lab 7 - Fuzz Testing: restaurant_bill_parser.py (FIXED)

The original code assumed every input was well formed. Fuzzing with
Hypothesis showed it crashing (AttributeError, ValueError,
ZeroDivisionError) or returning wrong values (negative prices,
negative shares, names with stray spaces).

Rule after the fix: no function ever raises an exception. Each one
returns a clean result for valid input and None for invalid input,
so the caller can tell the user what went wrong.
"""

MARKERS = ['*', '#', '~']


def _to_whole_number(text):
    """Turn text like ' 250 ' into 250. Return None if it is not a
    whole number written with the digits 0-9.

    isascii() is needed because isdigit() is also True for characters
    like '²' that int() cannot convert.
    """
    text = text.strip()
    if not (text.isascii() and text.isdigit()):
        return None             # '', '-5', '+5', '1.5', '1_000', 'abc', '²'
    try:
        return int(text)
    except ValueError:          # more than 4300 digits (Python's int limit)
        return None


def clean_dish_name(name):
    """
    Removes the chef's-special markers (*, #, ~) and title-cases the name.
    Returns None if name is not a string or nothing is left after cleaning.
    """
    if not isinstance(name, str):           # FIX: None crashed with AttributeError
        return None
    for ch in MARKERS:
        name = name.replace(ch, '')
    name = name.strip()                     # FIX: strip AFTER removing markers,
                                            # so 'tikka *' gives 'Tikka' not 'Tikka '
    if not name:                            # FIX: '', '   ', '***' gave ''
        return None
    return name.title()


def parse_item_prices(text):
    """
    Parses comma-separated prices into a list of ints.
    Blank entries (e.g. '250,,180' or a trailing comma) are skipped.
    Returns None if text is not a string or any price is not a whole number.
    """
    if not isinstance(text, str):           # FIX: None crashed with AttributeError
        return None
    prices = []
    for part in text.split(','):
        if not part.strip():                # FIX: '' and '250,,180' crashed
            continue
        price = _to_whole_number(part)
        if price is None:                   # FIX: 'abc', '1.5' crashed;
            return None                     # '-5' was accepted as a price
        prices.append(price)
    return prices


def split_amount(text):
    """
    Splits 'TOTAL/PEOPLE' into the amount each person pays.
    Returns None if text is not in that form, either value is not a
    whole number, or people is zero.
    """
    if not isinstance(text, str):           # FIX: None crashed with AttributeError
        return None
    parts = text.split('/')
    if len(parts) != 2:                     # FIX: '1200' and '1/2/3' crashed
        return None
    total = _to_whole_number(parts[0])      # FIX: 'abc/4' crashed;
    people = _to_whole_number(parts[1])     # '-1200/4' gave a negative share
    if total is None or people is None:
        return None
    if people == 0:                         # FIX: '1200/0' crashed with
        return None                         # ZeroDivisionError
    return total // people


def main():
    print("==== Running clean_dish_name ====")
    value = input("Enter a dish name from the menu (e.g. *paneer tikka*): ")
    result = clean_dish_name(value)
    print("Dish name:", result if result is not None
          else "Invalid dish name - please enter a name")

    print("\n==== Running parse_item_prices ====")
    value = input("Enter item prices separated by commas (e.g. 250,180,320): ")
    result = parse_item_prices(value)
    print("Item prices:", result if result is not None
          else "Invalid prices - use whole numbers separated by commas")

    print("\n==== Running split_amount ====")
    value = input("Enter the bill and number of people as TOTAL/PEOPLE (e.g. 1200/4): ")
    result = split_amount(value)
    print("Each person pays:", result if result is not None
          else "Invalid input - use TOTAL/PEOPLE with whole numbers and PEOPLE > 0")


if __name__ == "__main__":
    main()