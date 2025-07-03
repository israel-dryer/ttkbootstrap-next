class InvalidThemeError(Exception):
    """Exception raised when a user-provided theme is invalid.

    Attributes:
        message: Explanation of the error.
        theme_name: Optional name of the theme, if known.
    """

    def __init__(self, message: str, theme_name: str = None):
        self.message = message
        self.theme_name = theme_name
        if theme_name:
            full_message = f"Invalid theme '{theme_name}': {message}"
        else:
            full_message = f"Invalid theme: {message}"
        super().__init__(full_message)


class InvalidTokenError(Exception):
    """Exception raised when an invalid style token is provided

    Attributes:
        message: Explanation of the error.
        token: The name of the color token provided
    """

    def __init__(self, message: str, token: str = None):
        self.message = message
        self.token = token
        if token:
            full_message = f"Invalid style token '{token}': {message}"
        else:
            full_message = f"Invalid style token: {message}"
        super().__init__(full_message)
