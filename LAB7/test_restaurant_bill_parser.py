"""
Lab 7 - Fuzz Testing: test_restaurant_bill_parser.py

Run:  pytest test_restaurant_bill_parser.py
 or:  python -m pytest test_restaurant_bill_parser.py

Three kinds of Hypothesis tests for each function:
  1. no_crash    - random Unicode text or None must never raise an
                   exception (the three starter To-Do tests).
  2. bad_values  - text built from the characters these inputs really
                   use (digits, commas, '/', '-', spaces, markers), so
                   Hypothesis quickly reaches cases like '1200/0',
                   '250,,180' and '-5'. The result must be None or a
                   valid value - never a negative price or share.
  3. valid_input - well-formed input built from real numbers must
                   still give the right answer after the fix.
"""
from hypothesis import given, settings, strategies as st

from restaurant_bill_parser import clean_dish_name, parse_item_prices, split_amount

settings.register_profile("lab7", max_examples=300, deadline=None)
settings.load_profile("lab7")

MARKERS = "*#~"
names_text = st.text(alphabet=" abcXYZ" + MARKERS + "\t")
prices_text = st.text(alphabet="0123456789,- .a")
split_text = st.text(alphabet="0123456789/- .a")


def crash_message(func, s, e):
    return f"{func.__name__}({s!r}) crashed with {type(e).__name__}: {e}"


# ------------------------------------------------------------ clean_dish_name
@given(st.text() | st.none())
def test_clean_dish_name_no_crash(s):
    try:
        clean_dish_name(s)
    except Exception as e:
        assert False, crash_message(clean_dish_name, s, e)


@given(names_text)
def test_clean_dish_name_bad_values(s):
    result = clean_dish_name(s)
    if result is not None:
        assert result != "", "empty name should be rejected (None)"
        assert result == result.strip(), f"stray spaces left in {result!r}"
        assert not any(m in result for m in MARKERS), f"marker left in {result!r}"


@given(st.text(alphabet="abcdefg ", min_size=1).filter(str.strip),
       st.sampled_from(["*", "#", "~", "**", "~#"]))
def test_clean_dish_name_valid_input(name, marker):
    expected = name.strip().title()
    assert clean_dish_name(marker + name + marker) == expected
    assert clean_dish_name(name) == expected


# ---------------------------------------------------------- parse_item_prices
@given(st.text() | st.none())
def test_parse_item_prices_no_crash(s):
    try:
        parse_item_prices(s)
    except Exception as e:
        assert False, crash_message(parse_item_prices, s, e)


@given(prices_text)
def test_parse_item_prices_bad_values(s):
    result = parse_item_prices(s)
    if result is not None:
        assert isinstance(result, list)
        assert all(isinstance(p, int) and p >= 0 for p in result), \
            f"invalid price in {result!r} from {s!r}"


@given(st.lists(st.integers(min_value=0, max_value=100000)),
       st.sampled_from([",", ", ", " , "]))
def test_parse_item_prices_valid_input(prices, sep):
    assert parse_item_prices(sep.join(str(p) for p in prices)) == prices


# --------------------------------------------------------------- split_amount
@given(st.text() | st.none())
def test_split_amount_no_crash(s):
    try:
        split_amount(s)
    except Exception as e:
        assert False, crash_message(split_amount, s, e)


@given(split_text)
def test_split_amount_bad_values(s):
    try:
        result = split_amount(s)
    except Exception as e:
        assert False, crash_message(split_amount, s, e)
    if result is not None:
        assert isinstance(result, int) and result >= 0, \
            f"split_amount({s!r}) gave {result!r}"


@given(st.integers(min_value=0, max_value=10**7),
       st.integers(min_value=1, max_value=100))
def test_split_amount_valid_input(total, people):
    assert split_amount(f"{total}/{people}") == total // people
    assert split_amount(f" {total} / {people} ") == total // people