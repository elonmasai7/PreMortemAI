import secrets


def generate_trace_id() -> str:
    return secrets.token_hex(16)


def generate_span_id() -> str:
    return secrets.token_hex(8)


def parse_traceparent(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    parts = value.split("-")
    if len(parts) != 4:
        return None, None
    _, trace_id, parent_span_id, _ = parts
    if len(trace_id) != 32 or len(parent_span_id) != 16:
        return None, None
    return trace_id, parent_span_id


def build_traceparent(trace_id: str, span_id: str) -> str:
    return f"00-{trace_id}-{span_id}-01"
