import unittest

from fastiot.core.subject_helper import sanitize_pub_subject_name


class TestSubjectHelper(unittest.TestCase):
    def test_subject_name(self):

        my_message = 'v1.my_message'
        my_message_wildcard = 'v1.my_message.*'
        my_message_hierarchy = 'v1.my_message.>'

        test_subject_name = 'MyMessage'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message, subject_name)

        test_subject_name = 'MyMessage.MyData'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual('v1.my_message.my_data', subject_name)

        test_subject_name = 'MyMessage.*.*'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual('v1.my_message.*.*', subject_name)

        test_subject_name = 'MyMessage.*.>'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual('v1.my_message.*.>', subject_name)

        test_subject_name = 'my_message'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message, subject_name)

        test_subject_name = 'MyMessage.*'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message_wildcard, subject_name)

        test_subject_name = 'my_message.*'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message_wildcard, subject_name)

        test_subject_name = 'v1.MyMessage'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message, subject_name)

        test_subject_name = 'v1.my_message'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message, subject_name)

        test_subject_name = 'v1.MyMessage.*'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message_wildcard, subject_name)

        test_subject_name = 'v1.MyMessage.MyData.*'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual('v1.my_message.my_data.*', subject_name)

        test_subject_name = 'v1.my_message.*'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message_wildcard, subject_name)

        test_subject_name = 'v1.my_message.>'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual(my_message_hierarchy, subject_name)

        test_subject_name = 'v1.my_message.*.my_data'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual('v1.my_message.*.my_data', subject_name)

        test_subject_name = '>'
        subject_name = sanitize_pub_subject_name(test_subject_name)
        self.assertEqual('v1.>', subject_name)


if __name__ == '__main__':
    unittest.main()
