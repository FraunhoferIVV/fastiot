import re

MSG_FORMAT_VERSION = 'v1'
HIERARCHY = '>'
WILDCARD_SAME_LEVEL = '*'


def sanitize_subject_name(subject_name: str) -> str:
    """
    This function will help you to check if the subject in right format and build it for you.
    In FastIoT Framework, the right format base for subject_name is: "v1.my_message**", this will only subscribe till my_message level.
    If you want to build a hierarchy for this topic, the subject_name must be "v1.my_topic.*" or "v1.my_topic.>"

    In summary, it will do the following for you:
     - "MyMessage" -> "v1.my_message";
     - "my_message" -> "v1.my_message";
     - "MyMessage.*" -> "v1.my_message.*"
     - "my_message.*" -> "v1.my_message.*"
     - "v1.MyMessage" -> "v1.my_message"
     - "v1.my_message" -> "v1.my_message"
     - "v1.MyMessage" -> "v1.my_message"
     - "v1.my_message.*" -> "v1.my_message.*"

    If the suffix is a ">" instead of a "*", it will also be kept.

    """
    subject_name_components = subject_name.split('.')

    if MSG_FORMAT_VERSION in subject_name_components:
        subject_name = f"{_convert_camelcase_to_snakecase(subject_name_components)}"
    else:
        subject_name = f"{MSG_FORMAT_VERSION}.{_convert_camelcase_to_snakecase(subject_name_components)}"

    return subject_name


def _convert_camelcase_to_snakecase(camel_list: list[str]) -> str:
    snake_list = [f"{re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()}" for camel in camel_list]
    return '.'.join(snake_list)
