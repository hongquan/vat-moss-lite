import pytest

import vat_moss_lite.errors
import vat_moss_lite.id


# (name, raw_vat_id, expected_normalized, expected_country_code)
# NOTE: Albania ('al') is excluded — normalize raises UnrecognizedCountryError for it;
#       see test_normalize_unrecognized_country below.
_VALID_IDS: list[tuple[str, str, str, str]] = [
    ('at', 'ATU 38289400', 'ATU38289400', 'AT'),
    ('be', 'BE0844.044.609', 'BE0844044609', 'BE'),
    ('bg', 'BG160072254', 'BG160072254', 'BG'),
    ('cy', 'CY 10132211L', 'CY10132211L', 'CY'),
    ('cz', 'CZ15046575', 'CZ15046575', 'CZ'),
    ('de', 'DE 129273398', 'DE129273398', 'DE'),
    ('dk', 'DK 65 19 68 16', 'DK65196816', 'DK'),
    ('ee', 'EE 100 366 327', 'EE100366327', 'EE'),
    ('el', 'EL 094259216', 'EL094259216', 'GR'),
    ('gr', 'GR094259216', 'EL094259216', 'GR'),
    ('es', 'ES B58378431', 'ESB58378431', 'ES'),
    ('fi', 'FI- 2077474-0', 'FI20774740', 'FI'),
    ('fr', 'FR 35 552049447', 'FR35552049447', 'FR'),
    ('hr', 'HR76639357285', 'HR76639357285', 'HR'),
    ('hu', 'HU17780010', 'HU17780010', 'HU'),
    ('ie', 'IE6388047V', 'IE6388047V', 'IE'),
    ('it', 'IT05175700482', 'IT05175700482', 'IT'),
    ('lt', 'LT120212314', 'LT120212314', 'LT'),
    ('lu', 'LU26888617', 'LU26888617', 'LU'),
    ('lv', 'LV40003032949', 'LV40003032949', 'LV'),
    ('mt', 'MT20681625', 'MT20681625', 'MT'),
    ('nl', 'NL 004495445 B01', 'NL004495445B01', 'NL'),
    ('no', 'NO974760673MVA', 'NO974760673MVA', 'NO'),
    ('pl', 'PL 7740001454', 'PL7740001454', 'PL'),
    ('pt', 'pt 502332743', 'PT502332743', 'PT'),
    ('ro', 'RO 24063308', 'RO24063308', 'RO'),
    ('se', 'SE 556012579001', 'SE556012579001', 'SE'),
    ('si', 'si47992115', 'SI47992115', 'SI'),
    ('sk', 'sk2020270780', 'SK2020270780', 'SK'),
]

_INVALID_IDS: list[tuple[str]] = [('GBGD000',), ('IE000000',), ('AT1',)]


@pytest.mark.parametrize(
    'vat_id, expected_normalized, expected_country_code',
    [pytest.param(row[1], row[2], row[3], id=row[0]) for row in _VALID_IDS],
)
def test_normalize(vat_id: str, expected_normalized: str, expected_country_code: str) -> None:
    assert vat_moss_lite.id.normalize(vat_id) == expected_normalized


def test_normalize_unrecognized_country() -> None:
    """Albania is not in ID_PATTERNS — normalize must raise UnrecognizedCountryError."""
    with pytest.raises(vat_moss_lite.errors.UnrecognizedCountryError):
        vat_moss_lite.id.normalize('AL J 61929021 E')


# Integration test: hits the live VIES SOAP endpoint, so individual country
# parameters may be skipped (not failed) when the per-member-state backend
# returns MS_UNAVAILABLE / MS_MAX_CONCURRENT_REQ / SERVICE_UNAVAILABLE / TIMEOUT.
# These faults are transient (rate limiting or member-state outage), not a bug
# in the code under test — re-running later usually clears them. A retry-with-
# backoff wrapper would make the skip much rarer.
@pytest.mark.parametrize(
    'vat_id, expected_normalized, expected_country_code',
    [pytest.param(row[1], row[2], row[3], id=row[0]) for row in _VALID_IDS],
)
def test_validate_id(vat_id: str, expected_normalized: str, expected_country_code: str) -> None:
    try:
        result = vat_moss_lite.id.validate(vat_id)
        if result:
            country_code, normalized_vat_id, _name = result
            assert country_code == expected_country_code
            assert normalized_vat_id == expected_normalized
        else:
            assert expected_normalized == result
    except vat_moss_lite.errors.WebServiceUnavailableError:
        pytest.skip('VIES webservice unavailable')


@pytest.mark.parametrize('vat_id', [row[0] for row in _INVALID_IDS])
def test_validate_id_invalid(vat_id: str) -> None:
    with pytest.raises(vat_moss_lite.errors.InvalidError):
        vat_moss_lite.id.validate(vat_id)
