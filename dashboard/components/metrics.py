"""Metric formatting."""
def compact_number(value: float) -> str:
    return f"{value/1_000_000:.1f}M" if abs(value) >= 1_000_000 else f"{value:,.0f}"
