import os


def parse_bool_flag(env_var: str, default: bool) -> bool:
    """
    Helper function for parsing flag env variables (returns true or false).

    Please use this function for parsing boolean flags for unified behavior across fastiot. Please also note, that this
    function exists because a bool cast doesn't cut it because bool('false') is true why this function exists.

    :param env_var: The name of the env var
    :param default: The default flag if the env var doesn't exist in os environment.
    :return The flag, true or false
    """
    if env_var in os.environ:
        return os.environ[env_var].lower() == 'true'

    return default
