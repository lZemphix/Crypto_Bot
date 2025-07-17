class NoCryptoCurrencyException(Exception):
    """Raised when a cryptocurrency is not found in your wallet."""
    pass


class IncorrectOrdersHistory(Exception):
    """Raised when the orders history is not in the expected format."""
    pass


class IncorrectOpenOrdersList(Exception):
    """Raised when the open orders list is not in the expected format."""
    pass


class OrderPlaceException(Exception):
    """Raised when an order cannot be placed."""
    pass
