import re

MSG_FORMAT_VERSION = 'v1'
HIERARCHY = '>'
THING = 'thing'
WILDCARD_SAME_LEVEL = '*'


def sanitize_subject(subject_name: str) -> str:
    subject_name_components = subject_name.split('.')
    if MSG_FORMAT_VERSION in subject_name_components and HIERARCHY in subject_name_components:
        return subject_name
    elif HIERARCHY in subject_name_components and MSG_FORMAT_VERSION not in subject_name_components:
        return f'{MSG_FORMAT_VERSION}.{subject_name}'

    if MSG_FORMAT_VERSION in subject_name_components:
        if THING in subject_name_components and WILDCARD_SAME_LEVEL in subject_name_components:
            subject_name = subject_name
        elif THING in subject_name_components and WILDCARD_SAME_LEVEL not in subject_name_components:
            subject_name = \
                f"{MSG_FORMAT_VERSION}.{re.sub(r'(?<!^)(?=[A-Z])', '_', subject_name_components[1]).lower()}.{WILDCARD_SAME_LEVEL}"
        else:
            subject_name = f"{MSG_FORMAT_VERSION}.{re.sub(r'(?<!^)(?=[A-Z])', '_', subject_name_components[1]).lower()}"
    else:
        if THING in subject_name_components and WILDCARD_SAME_LEVEL not in subject_name_components:
            subject_name = f"{MSG_FORMAT_VERSION}.{re.sub(r'(?<!^)(?=[A-Z])', '_', subject_name).lower()}.{WILDCARD_SAME_LEVEL}"
        else:
            subject_name = f"{MSG_FORMAT_VERSION}.{re.sub(r'(?<!^)(?=[A-Z])', '_', subject_name).lower()}"
    return subject_name
