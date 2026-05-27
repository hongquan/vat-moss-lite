from decimal import Decimal

import pytest

import vat_moss_lite.exchange_rates


_CURRENCY_FORMATS: list[tuple[str, str, str]] = [
    ('BGN', '4101.79', '4,101.79 Lev'),
    ('CZK', '4101.79', '4.101,79 Kč'),
    ('DKK', '4101.79', '4.101,79 Dkr'),
    ('EUR', '4101.79', '€4.101,79'),
    ('GBP', '4101.79', '£4,101.79'),
    ('HRK', '4101.79', '4.101,79 Kn'),
    ('HUF', '4101.79', '4.101,79 Ft'),
    ('NOK', '4101.79', '4.101,79 Nkr'),
    ('PLN', '4101.79', '4 101,79 Zł'),
    ('RON', '4101.79', '4.101,79 Lei'),
    ('SEK', '4101.79', '4 101,79 Skr'),
    ('USD', '4101.79', '$4,101.79'),
]


def test_fetch() -> None:
    valid_currency_codes: list[str] = [
        'CZK',
        'DKK',
        'EUR',
        'GBP',
        'HUF',
        'NOK',
        'PLN',
        'RON',
        'SEK',
        'USD',
    ]
    date, rates = vat_moss_lite.exchange_rates.fetch()
    assert isinstance(date, str)
    for code in valid_currency_codes:
        assert code in rates


@pytest.mark.parametrize('code, amount, expected_result', _CURRENCY_FORMATS)
def test_format(code: str, amount: str, expected_result: str) -> None:
    assert vat_moss_lite.exchange_rates.format(Decimal(amount), code) == expected_result
