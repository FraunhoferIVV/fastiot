from uuid import uuid1


def get_uuid() -> str:
    """
    This method returns a UUID in project canonical format.
    """
    return str(uuid1())
