"""Screener service delegates bounded filtering to the repository."""
from database.repository import StockRepository


def screen(repository: StockRepository, **filters):
    return repository.screener(**filters)
