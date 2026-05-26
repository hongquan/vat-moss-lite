Changelog following https://common-changelog.org/ convention

## Unreleased

### Changed

- `exchange_rates.py`: Removed BGN (Bulgaria) and HRK (Croatia) from the applicable-currency filter — both countries adopted the Euro (Croatia Jan 2023, Bulgaria Jan 2025) and ECB no longer publishes those rates.
- `id.py`: Migrated Norwegian VAT validation from the retired `data.brreg.no/enhetsregisteret/enhet/{id}.json` endpoint to the new REST API (`/enhetsregisteret/api/enheter/{id}`). Response field `organisasjonsnummer` is now a string; company name now read from `navn`.
- `id.py`: VIES endpoint switched from HTTP to HTTPS; `Content-Type` corrected from `application/x-www-form-urlencoded` to `text/xml` (resolves HTTP 400 errors).
- `id.py`, `exchange_rates.py`: Replaced deprecated `cgi.parse_header` with `email.message.Message.get_param` for charset extraction.

### Fixed

- `id.py`: SOAP faults from VIES (`INVALID_INPUT`, `MS_UNAVAILABLE`, `MS_MAX_CONCURRENT_REQ`, etc.) are now mapped to `InvalidError` or `WebServiceUnavailableError` instead of falling through to a misleading `WebServiceError`.
- Test data: Updated VAT rates for Luxembourg (15% → 17%), Portugal Azores (0% → 18%), and Portugal Madeira (0% → 22%) across all test modules to match current rates already in `rates.py`.
- Test data: Replaced deregistered VIES company VAT IDs for DE, EE, HU, LU, LV, NL, PL, SE with currently valid ones. Removed GB (no longer in VIES post-Brexit). FR updated to SNCF (skips gracefully on rate-limit).
- Test data: Removed BGN and HRK from `test_exchange_rates` expected-currency list.

## 0.11.0

### Added

- `id.py`: `normalize()` function.

### Fixed

- `exchange_rates.py`: `fetch()` now returns the date correctly.
- `exchange_rates.py`: `fetch()` returns the date as `unicode` under Python 2.

## 0.10.0

### Added

- `declared_residence.py`: `exceptions_by_country()` function.

## 0.9.0

Initial release.
