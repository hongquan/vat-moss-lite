import builtins
from decimal import Decimal
from email.message import Message
from typing import Any, TypedDict
from urllib.request import urlopen
from xml.etree import ElementTree


try:
    from money import xrates  # type: ignore[import-not-found]
except ImportError:
    xrates = None

from .errors import WebServiceError


class _FormattingRule(TypedDict):
    symbol: str
    symbol_first: bool
    decimal_mark: str
    thousands_separator: str
    decimal_places: int


def fetch() -> tuple[str, dict[str, Decimal]]:
    """Fetch the latest exchange rates from the European Central Bank.

    These rates are used for invoice display since some countries require
    the local currency. Returns rates updated on ECB business days between
    2:15 and 3:00pm CET — cache locally rather than fetching per request.

    :return:
        A tuple of (date string in YYYY-MM-DD format, rates dict). The
        rates dict has currency-code keys and Decimal values relative to
        EUR base (1.0000). Included currencies: CZK, DKK, EUR, GBP, HUF,
        NOK, PLN, RON, SEK, USD.

    :raises:
        WebServiceError - If the ECB XML structure is unexpected.
        urllib.error.URLError - If the ECB endpoint is unreachable.
    """

    response = urlopen('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    msg = Message()
    msg['content-type'] = response.headers['Content-Type']
    encoding = msg.get_param('charset') or 'utf-8'

    return_xml = response.read().decode(encoding)

    # Example return data
    #
    # <gesmes:Envelope xmlns:gesmes="http://www.gesmes.org/xml/2002-08-01" xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref">
    #     <gesmes:subject>Reference rates</gesmes:subject>
    #     <gesmes:Sender>
    #         <gesmes:name>European Central Bank</gesmes:name>
    #     </gesmes:Sender>
    #     <Cube>
    #         <Cube time="2015-01-09">
    #             <Cube currency="USD" rate="1.1813"/>
    #             <Cube currency="JPY" rate="140.81"/>
    #             <Cube currency="BGN" rate="1.9558"/>
    #             <Cube currency="CZK" rate="28.062"/>
    #             <Cube currency="DKK" rate="7.4393"/>
    #             <Cube currency="GBP" rate="0.77990"/>
    #             <Cube currency="HUF" rate="317.39"/>
    #             <Cube currency="PLN" rate="4.2699"/>
    #             <Cube currency="RON" rate="4.4892"/>
    #             <Cube currency="SEK" rate="9.4883"/>
    #             <Cube currency="CHF" rate="1.2010"/>
    #             <Cube currency="NOK" rate="9.0605"/>
    #             <Cube currency="HRK" rate="7.6780"/>
    #             <Cube currency="RUB" rate="72.8910"/>
    #             <Cube currency="TRY" rate="2.7154"/>
    #             <Cube currency="AUD" rate="1.4506"/>
    #             <Cube currency="BRL" rate="3.1389"/>
    #             <Cube currency="CAD" rate="1.3963"/>
    #             <Cube currency="CNY" rate="7.3321"/>
    #             <Cube currency="HKD" rate="9.1593"/>
    #             <Cube currency="IDR" rate="14925.34"/>
    #             <Cube currency="ILS" rate="4.6614"/>
    #             <Cube currency="INR" rate="73.6233"/>
    #             <Cube currency="KRW" rate="1290.29"/>
    #             <Cube currency="MXN" rate="17.3190"/>
    #             <Cube currency="MYR" rate="4.2054"/>
    #             <Cube currency="NZD" rate="1.5115"/>
    #             <Cube currency="PHP" rate="53.090"/>
    #             <Cube currency="SGD" rate="1.5789"/>
    #             <Cube currency="THB" rate="38.846"/>
    #             <Cube currency="ZAR" rate="13.6655"/>
    #         </Cube>
    #     </Cube>
    # </gesmes:Envelope>

    envelope = ElementTree.fromstring(return_xml.encode('utf-8'))

    namespaces = {
        'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
        'eurofxref': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref',
    }

    date_elements = envelope.findall('./eurofxref:Cube/eurofxref:Cube[@time]', namespaces)
    if not date_elements:
        raise WebServiceError('Unable to find <Cube time=""> tag in ECB XML')

    # XPath filtered for [@time], so the attribute is always present
    date: str = date_elements[0].attrib['time']

    currency_elements = envelope.findall(
        './eurofxref:Cube/eurofxref:Cube/eurofxref:Cube[@currency][@rate]', namespaces
    )
    if not currency_elements:
        raise WebServiceError('Unable to find <Cube currency="" rate=""> tags in ECB XML')

    rates: dict[str, Decimal] = {'EUR': Decimal('1.0000')}

    applicable_currenties = {
        'CZK': True,
        'DKK': True,
        'EUR': True,
        'GBP': True,
        'HUF': True,
        'NOK': True,
        'PLN': True,
        'RON': True,
        'SEK': True,
        'USD': True,
    }

    for currency_element in currency_elements:
        code = currency_element.attrib.get('currency')

        if code not in applicable_currenties:
            continue

        rate = currency_element.attrib.get('rate')
        rates[code] = Decimal(rate)  # type: ignore[arg-type]

    return (date, rates)


def setup_xrates(base: str, rates: dict[str, Decimal]) -> None:
    """Configure the `money` package exchange rates from ECB data.

    :param base:
        Currency code to use as the base (use ``'EUR'`` with ECB data).

    :param rates:
        Dict of currency-code → Decimal exchange rate.
    """

    xrates.install('money.exchange.SimpleBackend')
    xrates.base = base
    for code, value in rates.items():
        xrates.setrate(code, value)


def format(amount: Decimal | Any, currency: str | None = None) -> str:
    """Format a currency amount for invoice display.

    Accepts either a ``Decimal`` plus an explicit currency code, or a
    ``money.Money`` object (which carries its own currency).

    :param amount:
        A ``Decimal`` amount, or a ``Money`` object with ``.amount``
        and ``.currency`` attributes.

    :param currency:
        Three-character currency code; required when ``amount`` is a
        ``Decimal``, ignored when ``amount`` is a ``Money`` object.

    :return:
        Locale-formatted string, e.g. ``'€4.101,79'`` or ``'$4,101.79'``.

    :raises:
        ValueError - If ``currency`` is not a string, is unsupported, or
            ``amount`` is not a ``Decimal``.
    """

    if currency is None and hasattr(amount, 'currency'):
        currency = amount.currency

    # Allow Money objects
    if not isinstance(amount, Decimal) and hasattr(amount, 'amount'):
        amount = amount.amount

    if not isinstance(currency, str):
        raise ValueError('The currency specified is not a string')

    if currency not in FORMATTING_RULES:
        valid_currencies = sorted(FORMATTING_RULES.keys())
        formatted_currencies = ', '.join(valid_currencies)
        raise ValueError(
            f'The currency specified, "{currency}", is not a supported currency: {formatted_currencies}'
        )

    if not isinstance(amount, Decimal):
        raise ValueError('The amount specified is not a Decimal')

    rules = FORMATTING_RULES[currency]

    format_string = ',.{}f'.format(rules['decimal_places'])

    result = builtins.format(amount, format_string)

    result = result.replace(',', '_')
    result = result.replace('.', '|')

    result = result.replace('_', rules['thousands_separator'])
    result = result.replace('|', rules['decimal_mark'])

    if rules['symbol_first']:
        result = rules['symbol'] + result
    else:
        result = result + rules['symbol']

    return result


FORMATTING_RULES: dict[str, _FormattingRule] = {
    'BGN': {
        'symbol': ' Lev',
        'symbol_first': False,
        'decimal_mark': '.',
        'thousands_separator': ',',
        'decimal_places': 2,
    },
    'CZK': {
        'symbol': ' Kč',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'DKK': {
        'symbol': ' Dkr',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'EUR': {
        'symbol': '€',
        'symbol_first': True,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'GBP': {
        'symbol': '£',
        'symbol_first': True,
        'decimal_mark': '.',
        'thousands_separator': ',',
        'decimal_places': 2,
    },
    'HRK': {
        'symbol': ' Kn',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'HUF': {
        'symbol': ' Ft',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'NOK': {
        'symbol': ' Nkr',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'PLN': {
        'symbol': ' Zł',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': ' ',
        'decimal_places': 2,
    },
    'RON': {
        'symbol': ' Lei',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': '.',
        'decimal_places': 2,
    },
    'SEK': {
        'symbol': ' Skr',
        'symbol_first': False,
        'decimal_mark': ',',
        'thousands_separator': ' ',
        'decimal_places': 2,
    },
    'USD': {
        'symbol': '$',
        'symbol_first': True,
        'decimal_mark': '.',
        'thousands_separator': ',',
        'decimal_places': 2,
    },
}
