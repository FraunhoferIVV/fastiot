class ServiceError(Exception):
    """
    Raised when something goes wrong during connection to a service.
    """


class SQLSchemaCheckError(Exception):
    """
    Raised when the database schema is invalid. This can happen if a table for an enum does not have the expected
    values.
    """


