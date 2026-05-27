from urllib.error import URLError


class UndefinitiveError(ValueError):
    """
    An error representing an undefinitive answer to determining what VAT rate
    a user is subject to
    """

    pass


class InvalidError(ValueError):
    """
    An error representing an invalid VAT ID
    """

    pass


class UnrecognizedCountryError(ValueError):
    pass


class WebServiceError(URLError):
    """
    If there was an unexpected result from a call to one of the VAT validation
    APIs
    """

    pass


class WebServiceUnavailableError(WebServiceError):
    """
    If the VIES service VAT ID check was unavailable at the time of the request
    """

    pass
