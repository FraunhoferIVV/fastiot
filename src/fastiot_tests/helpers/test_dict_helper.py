import unittest

from fastiot.helpers.dict_helper import dict_subtract
from fastiot.testlib.testlib import populate_test_env


class TestDictHelper(unittest.TestCase):

    def setUp(self):
        populate_test_env()

    def tearDown(self):
        pass

    def test_dict_sub(self):
        a = {'_id': '123', '_subject': 'test_thing', '_timestamp': '1234', 'machine': 'test_machine',
             'sensor': 'test_sensor'}
        b = {'_id': '123', '_subject': 'test_thing', '_timestamp': '1234'}
        expected_dict = {'machine': 'test_machine', 'sensor': 'test_sensor'}
        dict_ = dict_subtract(a, b)
        self.assertDictEqual(expected_dict, dict_)

        a = {'_id': '123', '_subject': 'test_thing', '_timestamp': '1234'}
        b = {'_id': '123', '_subject': 'test_thing', '_timestamp': '1234', 'machine': 'test_machine',
             'sensor': 'test_sensor'}
        dict_ = dict_subtract(a, b)
        self.assertDictEqual(expected_dict, dict_)

        a = {'_id': '123', '_subject': 'test_thing', '_timestamp': '1234'}
        b = {'machine': 'test_machine', 'sensor': 'test_sensor'}
        dict_ = dict_subtract(a, b)
        self.assertEqual(None, dict_)

        a = {'_id': '1234', '_subject': 'test_things', '_timestamp': '1234', 'machine': 'test_machine',
             'sensor': 'test_sensor'}
        b = {'_id': 123, '_subject': 'test_thing', '_timestamp': '1234'}
        expected_dict = {'machine': 'test_machine', 'sensor': 'test_sensor'}
        dict_ = dict_subtract(a, b)
        self.assertDictEqual(expected_dict, dict_)


if __name__ == '__main__':
    unittest.main()
