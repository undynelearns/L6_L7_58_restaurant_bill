"""
Lab 6 - Branch coverage tests for restaurant_bill.py
Goal: every decision (if / elif) evaluates to both True and False,
including each part of the compound conditions (or / and).

Run:
    coverage run --branch -m pytest BranchCoverageTest_restaurant_bill.py
    coverage report -m
"""
import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# =====================================================================
# bill_total
# =====================================================================

# Decision 1: section not in SERVICE_CHARGE
def test_bill_unknown_section_true():
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


def test_bill_known_section_false():
    # dine_in, no happy hour, small party (original starter test)
    assert bill_total("dine_in", 1000, 2, False) == 1155


# Decision 2: food_total < 0 or guests < 1  (both sides of the "or")
def test_bill_negative_food_total():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_bill_zero_guests():
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", 1000, 0, False)


def test_bill_zero_food_is_valid():
    # boundary: food_total == 0 is allowed -> 0
    assert bill_total("dine_in", 0, 1, False) == 0


# Decision 3: is_happy_hour and section != "takeaway"
def test_bill_happy_hour_dine_in_discount():
    # True and True -> discount applied
    # 1000 -> 800, service 80, total 880, tax 44 -> 924
    assert bill_total("dine_in", 1000, 2, True) == 924


def test_bill_happy_hour_takeaway_no_discount():
    # True and False -> no discount for takeaway
    # 1000, service 0, total 1000, tax 50 -> 1050
    assert bill_total("takeaway", 1000, 2, True) == 1050


def test_bill_no_happy_hour_takeaway():
    # False (short-circuit) -> no discount
    assert bill_total("takeaway", 1000, 2, False) == 1050


# Decision 4: guests >= 8
def test_bill_large_party_surcharge():
    # rooftop, 8 guests: service 150 + 200 = 350, total 1350, tax 67 -> 1417
    assert bill_total("rooftop", 1000, 8, False) == 1417


def test_bill_seven_guests_no_surcharge():
    # boundary: 7 guests -> no surcharge
    # service 150, total 1150, tax 57 -> 1207
    assert bill_total("rooftop", 1000, 7, False) == 1207


def test_bill_happy_hour_large_party_rooftop():
    # discount + surcharge together
    # 800, service 120 + 200 = 320, total 1120, tax 56 -> 1176
    assert bill_total("rooftop", 1000, 8, True) == 1176


# =====================================================================
# split_bill
# =====================================================================

# Decision 1: people < 1
def test_split_zero_people():
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_split_one_person():
    # boundary: 1 person pays everything -> 1100
    assert split_bill(1000, 1, 10) == 1100


# Decision 2: tip_percent < 0
def test_split_negative_tip():
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 2, -5)


def test_split_zero_tip():
    # boundary: 0% tip is allowed -> 500
    assert split_bill(1000, 2, 0) == 500


# Decision 3: grand_total % people != 0
def test_split_even():
    # original starter test: 1100 / 4 = 275 exactly
    assert split_bill(1000, 4, 10) == 275


def test_split_uneven_rounds_up():
    # 1100 // 3 = 366 remainder 2 -> 367
    assert split_bill(1000, 3, 10) == 367


# =====================================================================
# table_wait
# =====================================================================

# Decision 1: party_size > 12
def test_wait_party_over_12():
    assert table_wait(13, 5, False) == "call ahead"


def test_wait_party_of_12():
    # boundary: 12 is not "call ahead"
    assert table_wait(12, 5, False) == "seat now"


# Decision 2: has_reservation
def test_wait_reservation_even_with_no_tables():
    assert table_wait(4, 0, True) == "seat now"


# Decision 3: free_tables == 0
def test_wait_no_free_tables():
    assert table_wait(4, 0, False) == "waitlist"


# Decision 4 (elif): party_size > 6 and free_tables < 2
def test_wait_big_party_one_table():
    # True and True -> waitlist
    assert table_wait(8, 1, False) == "waitlist"


def test_wait_big_party_two_tables():
    # True and False -> seat now
    assert table_wait(8, 2, False) == "seat now"


def test_wait_small_party_one_table():
    # False (short-circuit) -> seat now
    assert table_wait(6, 1, False) == "seat now"
