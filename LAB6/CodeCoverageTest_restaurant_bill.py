"""
Lab 6 - Code (line) coverage tests for restaurant_bill.py
Goal: execute every line of restaurant_bill.py at least once.

Run:
    coverage run -m pytest CodeCoverageTest_restaurant_bill.py
    coverage report -m
"""
import pytest
from restaurant_bill import bill_total, split_bill, table_wait


# ---------- Starter tests (given) ----------
def test_dine_in_bill():
    assert bill_total("dine_in", 1000, 2, False) == 1155


def test_even_split():
    assert split_bill(1000, 4, 10) == 275


# ---------- bill_total ----------
def test_unknown_section_raises():
    # line 6: raise ValueError("unknown section")
    with pytest.raises(ValueError, match="unknown section"):
        bill_total("patio", 1000, 2, False)


def test_invalid_order_raises():
    # line 8: raise ValueError("invalid order")
    with pytest.raises(ValueError, match="invalid order"):
        bill_total("dine_in", -1, 2, False)


def test_happy_hour_large_party_rooftop():
    # line 10 (happy hour discount) and line 13 (large party surcharge)
    # food 1000 -> 800, service 800*15//100 = 120, +200 = 320
    # total 1120, tax 1120*5//100 = 56 -> 1176
    assert bill_total("rooftop", 1000, 8, True) == 1176


# ---------- split_bill ----------
def test_invalid_people_raises():
    # line 20
    with pytest.raises(ValueError, match="invalid people count"):
        split_bill(1000, 0, 10)


def test_invalid_tip_raises():
    # line 22
    with pytest.raises(ValueError, match="invalid tip"):
        split_bill(1000, 2, -5)


def test_uneven_split_rounds_up():
    # line 26: share += 1
    # grand total 1100, 1100 // 3 = 366, remainder 2 -> 367
    assert split_bill(1000, 3, 10) == 367


# ---------- table_wait ----------
def test_party_too_large_call_ahead():
    # line 32
    assert table_wait(13, 5, False) == "call ahead"


def test_reservation_seat_now():
    # line 34
    assert table_wait(4, 0, True) == "seat now"


def test_no_free_tables_waitlist():
    # line 36
    assert table_wait(4, 0, False) == "waitlist"


def test_big_party_one_table_waitlist():
    # line 38
    assert table_wait(8, 1, False) == "waitlist"


def test_walk_in_seat_now():
    # line 39
    assert table_wait(4, 3, False) == "seat now"
