class Errors(Exception):
    """The base class for all library errors."""

    def __init__(self, code=None, message: str | None = None):
        self.code = code
        self.message = message or ""
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message or super().__str__()


class Forbidden(Errors):
    """Raised If you API key is invalid"""

    def __init__(self, code, url, message):
        self.url = url
        super().__init__(code, message)


class TagNotFoundError(Errors):
    """Raised when a invalid player or club tag is passed"""

    def __init__(self, code, **kwargs):
        message = "An Invalid Tag has been passed!"
        self.reason = kwargs.pop("reason", None)
        self.invalid_characters = kwargs.pop("invalid_characters", [])
        if self.reason:
            message += "".join(f"\n Reason : {self.reason}")
        elif self.invalid_characters:
            message += "".join(f"\n Invalid characters : {self.invalid_characters}")
        super().__init__(code, message)


class RateLimitError(Errors):
    """Raised when the rate limit is reached."""

    def __init__(self, code, url):
        self.url = url
        super().__init__(code, "The rate limit has been reached.")


class UnexpectedError(Errors):
    """Raised if an unknown error has occured."""

    def __init__(self, url, code, text):
        self.url = url
        super().__init__(code, f"An unexpected error has occured.\n{text}")


class ServerError(Errors):
    """Raised if the API is down."""

    def __init__(self, code, url):
        self.url = url
        super().__init__(
            code, "The API is down. Please be patient and try again later."
        )


class BrawlerNotFound(Errors):
    """Raised when Invalid brawlerID has been passed"""

    def __init__(self, code, id=None):
        self.brawler_id = id
        message = "Invalid ID passed!" if id is None else f"Invalid ID passed! {id}"
        super().__init__(code, message)


class CountryNotFound(Errors):
    """Raised when Invalid countryCode has been passed"""

    def __init__(self, code, countryCode=None):
        self.country_code = countryCode
        message = (
            "Invalid countryCode passed!"
            if countryCode is None
            else f"Invalid countryCode passed! {countryCode}"
        )
        super().__init__(code, message)
