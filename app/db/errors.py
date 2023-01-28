class EntityDoesNotExist(Exception):
    """Raised when entity was not found in database."""


class UnchangeableAttribute(Exception):
    """Raised when attribute is not changeable."""
