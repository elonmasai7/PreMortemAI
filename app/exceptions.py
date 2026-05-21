class ConfigurationError(Exception):
    pass


class SplunkConnectionError(Exception):
    pass


class SplunkAuthenticationError(Exception):
    pass


class SplunkSearchError(Exception):
    pass


class AIProviderError(Exception):
    pass


class InvestigationNotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass
