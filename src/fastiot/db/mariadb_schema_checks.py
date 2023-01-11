from enum import Enum

from fastiot.exceptions import SQLSchemaCheckError


def check_is_enum_represented(connection, sql_query: str, enum: type[Enum]):
    """
    Checks if enum values are in database table. The query must select a single column table with the enum values.

    :raises SQLSchemaCheckError: raised if an enum is missing.
    """

    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        result = cursor.fetchall()
        enum_value_list = [i.value for i in list(enum)]
        for row in result:
            if row[0] not in enum_value_list:
                raise SQLSchemaCheckError(sql_query)
            enum_value_list.remove(row[0])
        if len(enum_value_list) > 0:
            raise SQLSchemaCheckError(sql_query)
