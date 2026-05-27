from decimal import Decimal

import pytest

import vat_moss_lite.declared_residence


_RESIDENCES = [
    # User input                           # Expected result
    ('AT', 'Jungholz', Decimal('0.19'), 'AT', 'Jungholz'),
    ('AT', 'Mittelberg', Decimal('0.19'), 'AT', 'Mittelberg'),
    ('AT', None, Decimal('0.20'), 'AT', None),
    ('BE', None, Decimal('0.21'), 'BE', None),
    ('BG', None, Decimal('0.20'), 'BG', None),
    ('CY', None, Decimal('0.19'), 'CY', None),
    ('CZ', None, Decimal('0.21'), 'CZ', None),
    ('DE', 'Heligoland', Decimal('0.0'), 'DE', 'Heligoland'),
    ('DE', 'Büsingen am Hochrhein', Decimal('0.0'), 'DE', 'Büsingen am Hochrhein'),
    ('DE', None, Decimal('0.19'), 'DE', None),
    ('DK', None, Decimal('0.25'), 'DK', None),
    ('EE', None, Decimal('0.20'), 'EE', None),
    ('ES', 'Canary Islands', Decimal('0.0'), 'ES', 'Canary Islands'),
    ('ES', 'Melilla', Decimal('0.0'), 'ES', 'Melilla'),
    ('ES', 'Ceuta', Decimal('0.0'), 'ES', 'Ceuta'),
    ('ES', None, Decimal('0.21'), 'ES', None),
    ('FI', None, Decimal('0.24'), 'FI', None),
    ('FR', None, Decimal('0.20'), 'FR', None),
    ('GB', 'Akrotiri', Decimal('0.19'), 'CY', None),
    ('GB', 'Dhekelia', Decimal('0.19'), 'CY', None),
    ('GB', None, Decimal('0.20'), 'GB', None),
    ('GR', 'Mount Athos', Decimal('0.0'), 'GR', 'Mount Athos'),
    ('GR', None, Decimal('0.23'), 'GR', None),
    ('HR', None, Decimal('0.25'), 'HR', None),
    ('HU', None, Decimal('0.27'), 'HU', None),
    ('IE', None, Decimal('0.23'), 'IE', None),
    ('IT', "Campione d'Italia", Decimal('0.0'), 'IT', "Campione d'Italia"),
    ('IT', 'Livigno', Decimal('0.0'), 'IT', 'Livigno'),
    ('IT', None, Decimal('0.22'), 'IT', None),
    ('LT', None, Decimal('0.21'), 'LT', None),
    ('LU', None, Decimal('0.17'), 'LU', None),
    ('LV', None, Decimal('0.21'), 'LV', None),
    ('MT', None, Decimal('0.18'), 'MT', None),
    ('NL', None, Decimal('0.21'), 'NL', None),
    ('PL', None, Decimal('0.23'), 'PL', None),
    ('PT', 'Azores', Decimal('0.18'), 'PT', 'Azores'),
    ('PT', 'Madeira', Decimal('0.22'), 'PT', 'Madeira'),
    ('PT', None, Decimal('0.23'), 'PT', None),
    ('RO', None, Decimal('0.24'), 'RO', None),
    ('SE', None, Decimal('0.25'), 'SE', None),
    ('SI', None, Decimal('0.22'), 'SI', None),
    ('SK', None, Decimal('0.20'), 'SK', None),
    ('MC', None, Decimal('0.20'), 'MC', None),
    ('IM', None, Decimal('0.20'), 'IM', None),
    ('NO', None, Decimal('0.25'), 'NO', None),
    ('US', None, Decimal('0.0'), 'US', None),
    ('CA', None, Decimal('0.0'), 'CA', None),
]

_EXCEPTIONS: list[tuple[str, list[str]]] = [
    ('AT', ['Jungholz', 'Mittelberg']),
    ('DE', ['Büsingen am Hochrhein', 'Heligoland']),
    ('ES', ['Canary Islands', 'Ceuta', 'Melilla']),
    ('GB', ['Akrotiri', 'Dhekelia']),
    ('GR', ['Mount Athos']),
    ('IT', ["Campione d'Italia", 'Livigno']),
    ('PT', ['Azores', 'Madeira']),
    ('US', []),
    ('IM', []),
]


@pytest.mark.parametrize(
    'country_code, exception_name, expected_rate, expected_country_code, expected_exception_name',
    _RESIDENCES,
)
def test_calculate_rate(
    country_code, exception_name, expected_rate, expected_country_code, expected_exception_name
):
    result = vat_moss_lite.declared_residence.calculate_rate(country_code, exception_name)
    result_rate, result_country_code, result_exception_name = result
    assert result_rate == expected_rate
    assert result_country_code == expected_country_code
    assert result_exception_name == expected_exception_name


@pytest.mark.parametrize('country, expected_exceptions', _EXCEPTIONS)
def test_exceptions_by_country(country, expected_exceptions):
    assert vat_moss_lite.declared_residence.exceptions_by_country(country) == expected_exceptions
