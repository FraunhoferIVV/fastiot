import csv
from typing import List, Dict, Callable, Optional

from fastiot.exceptions import CSVError

csv.register_dialect('strict', delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, strict=True, skipinitialspace=False)


class CSVReader:
    """
    A class for csv file reading. It uses python-lib's csv package and does more strict checks on how the csv file
    must be formatted. Raises a CSVError if the file is incorrectly formatted.

    Example usage:

    with CSVReader('my_file.csv',
                   required_fields=['my_field1', 'my_field2'],
                   optional_fields=['my_optional_field2']) as reader:
        for data_row in reader:
            print(data_row['my_field1'])
            print(data_row['my_field2'])
            print(data_row.get('my_optional_field2', 'unset'))
    """

    def __init__(self,
                 filename: str,
                 required_fields: Optional[List[str]] = None,
                 optional_fields: Optional[List[str]] = None,
                 checks: Optional[Dict[str, Callable[[str], bool]]] = None,
                 do_allow_arbitrary_fields: bool = False):
        """
        Constructor for csv reader.

        :param filename: The filename of the csv file. Must be relative to workdir.
        :param required_fields: Specify required field names which must be in the csv header line. If not, it will raise
                                a CSVError during parsing.
        :param optional_fields: Specify optional field names. If the csv file contains field names, which are not
                                specified, it will raise a CSVError during parsing.
        :param checks: Specify checks for fields as a mapping of field names to callables. The callables should return
                       true if a given value is valid, false otherwise.
        :param do_allow_arbitrary_fields: If true, it will consider all possible field names as optional. Use this
                                          option with caution because it will prevent possible errors from being
                                          detected.
        """
        if required_fields is None:
            required_fields = []
        if optional_fields is None:
            optional_fields = []
        if checks is None:
            checks = {}
        self.filename = filename
        self._required_fields = required_fields
        self._optional_fields = optional_fields
        self._checks = checks
        self._do_allow_arbitrary_fields = do_allow_arbitrary_fields

    def __enter__(self):
        # Upon entering we want to read through the hole csv file and check if its correctly formatted.
        # We do so, to be able to detect multiple errors at once and output them properly.
        self.file = open(self.filename, encoding='utf-8-sig')
        reader = csv.reader(self.file, dialect='strict')
        invalid_lines_log_msgs: List[str] = []
        for row in reader:
            if reader.line_num == 1:
                self._parse_header_line(row)
            else:
                if len(row) != len(self._header_fields):
                    invalid_lines_log_msgs.append(
                        f"Line {reader.line_num}, Actual number of columns: {len(row)}, "
                        f"expected {len(self._header_fields)} columns"
                    )
                else:
                    invalid_fields_for_current_row = self._get_invalid_fields(row)
                    for header_field, cell in invalid_fields_for_current_row.items():
                        invalid_lines_log_msgs.append(
                            f"Line {reader.line_num}, Checks failed for header field '{header_field}'. "
                            f"Incorrect value '{cell}'."
                        )
        if len(invalid_lines_log_msgs) > 0:
            invalid_lines_log_msg = "\n".join(invalid_lines_log_msgs)
            raise CSVError(f"Following error(s) occurred during parsing of file '{self.filename}': \n"
                           f"{invalid_lines_log_msg}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def __iter__(self):
        self.file.close()
        self.file = open(self.filename, encoding='utf-8-sig')
        self._csv_reader = csv.reader(self.file, dialect='strict')
        self._csv_reader_iter = self._csv_reader.__iter__()
        return self

    def __next__(self) -> Dict[str, str]:
        row = self._csv_reader_iter.__next__()
        if self._csv_reader.line_num == 1:  # skip header line
            row = self._csv_reader_iter.__next__()
        result = {  # we assume that no error checks are needed here because we checked csv file before
            header: row for header, row in zip(self._header_fields, row)
        }
        return result

    def _parse_header_line(self, row: List[str]):
        headers_temp = [field for field in row]
        for required_field in self._required_fields:
            if required_field not in headers_temp:
                raise CSVError(f"Error parsing file '{self.filename}' Line 1: Required field '{required_field}' "
                               f"not found in csv header-line")
            headers_temp.remove(required_field)
        for optional_field in self._optional_fields:
            if optional_field in headers_temp:
                headers_temp.remove(optional_field)

        if len(headers_temp) > 0 and self._do_allow_arbitrary_fields is False:
            unrecognized_fields = ', '.join([f"'{field}'" for field in headers_temp])
            raise CSVError(f"Error parsing file '{self.filename}' Line 1: Unrecognized header fields "
                           f"{unrecognized_fields}.")
        self._header_fields = row

    def _get_invalid_fields(self, row: List[str]) -> Dict[str, str]:
        invalid_fields = {}
        for header_field, cell in zip(self._header_fields, row):
            if header_field in self._checks.keys():
                if self._checks[header_field](cell) is False:
                    invalid_fields[header_field] = cell
        return invalid_fields
