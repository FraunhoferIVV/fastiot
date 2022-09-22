import unittest

from fastiot.core.subject_helper import sanitize_subject
from fastiot_tests.generated import set_test_environment


class TestSubjectHelper(unittest.TestCase):
    def setUp(self):
        set_test_environment()

    def test_subject_name(self):
        test_subject_name = 'ContaminationList'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.contamination_list', subject_name)

        test_subject_name = 'contamination_list'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.contamination_list', subject_name)

        test_subject_name = 'v1.ContaminationList'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.contamination_list', subject_name)

        test_subject_name = 'v1.contamination_list'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.contamination_list', subject_name)

        test_subject_name = 'thing.*'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.thing.*', subject_name)

        test_subject_name = 'v1.thing.*'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.thing.*', subject_name)

        test_subject_name = 'thing'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.thing.*', subject_name)

        test_subject_name = 'v1.thing'
        subject_name = sanitize_subject(test_subject_name)
        self.assertEqual('v1.thing.*', subject_name)


if __name__ == '__main__':
    unittest.main()
