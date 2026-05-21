from app.config import Settings
from app.exceptions import ValidationError


def validate_spl_query(query: str, settings: Settings) -> None:
    if len(query) > settings.max_spl_query_length:
        raise ValidationError(f"SPL query too long. Max length is {settings.max_spl_query_length} characters.")
    dangerous_patterns = ["| script", "| map ", "| rest "]
    lowered = query.lower()
    for pattern in dangerous_patterns:
        if pattern in lowered:
            raise ValidationError(f"Query contains disallowed operator: {pattern.strip()}")
