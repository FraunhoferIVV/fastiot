import unittest
from datetime import datetime
from typing import List

from fastiot.core import FastIoTData
from fastiot.helpers.object_helper import parse_object, parse_object_list
from fastiot.msg.thing import Thing
from fastiot.testlib.testlib import populate_test_env


class TestValue(FastIoTData):
    real: float
    img: float


class TestCustomMsg(FastIoTData):
    x: TestValue
    y: TestValue


class TestCustomMsgList(FastIoTData):
    values: List[TestCustomMsg]


class TestObjectHelper(unittest.TestCase):

    def setUp(self):
        populate_test_env()

    def tearDown(self):
        pass

    def test_return_thing(self):
        thing_msg = Thing(machine='test_machine', name='sensor_0', measurement_id='123456',
                          value=1, timestamp=datetime(year=2022, month=10, day=10, second=10))

        thing_dict = thing_msg.dict()
        converted_msg = parse_object(thing_dict, Thing)
        self.assertEqual(thing_msg, converted_msg)

    def test_return_thing_list(self):
        thing_list = [Thing(machine='test_machine', name=f'sensor_{i}', measurement_id='123456',
                            value=1, timestamp=datetime(year=2022, month=10, day=10, second=i)) for i in range(2)]
        thing_dict_list = [thing.dict() for thing in thing_list]

        converted_msg_list = parse_object_list(thing_dict_list, Thing)
        self.assertEqual(thing_list, converted_msg_list)

    def test_return_custom_object(self):
        test_custom_msg = TestCustomMsgList(
            values=[TestCustomMsg(x=TestValue(real=1, img=2),
                                  y=TestValue(real=1, img=2))])
        test_custom_msg_dict = test_custom_msg.dict()
        converted_msg = parse_object(test_custom_msg_dict, TestCustomMsgList)
        self.assertEqual(test_custom_msg, converted_msg)

    def test_return_custom_object_list(self):
        test_custom_msg_list = [TestCustomMsgList(
            values=[TestCustomMsg(x=TestValue(real=1, img=2),
                                  y=TestValue(real=1, img=2))]) for _ in range(2)]
        test_custom_msg_dict_list = [test_custom_msg.dict() for test_custom_msg in test_custom_msg_list]
        converted_msg_list = parse_object_list(test_custom_msg_dict_list, TestCustomMsgList)
        self.assertEqual(test_custom_msg_list, converted_msg_list)

    def test_return_wrong_type(self):
        class TestClass:
            def __init__(self, a):
                self.a = a

        converted_msg = parse_object({'a': 1}, TestClass)
        self.assertIsNone(converted_msg)


if __name__ == '__main__':
    unittest.main()
