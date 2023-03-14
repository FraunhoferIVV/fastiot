from datetime import datetime
import unittest

from fastiot.core import FastIoTPublish
from fastiot.core.subject_helper import MSG_FORMAT_VERSION
from fastiot.msg.thing import Thing


class NonHierarchicalObject(FastIoTPublish):
    _handles_hierarchical_subjects = False
    some_data: int = 0


class HierarchicalObject(FastIoTPublish):
    _handles_hierarchical_subjects = True
    some_data: int = 0


class UnclearIfHierarchicalObject(FastIoTPublish):
    some_data: int = 0


class TestSubjectHelper(unittest.TestCase):
    def test_default_thing_subject_with_space_in_machine_name(self):
        thing = Thing(
            machine="a machine",
            name="a name",
            value="1",
            timestamp=datetime(year=2023, month=1, day=1)
        )
        self.assertTrue(len(thing.default_subject.name) > 0)
        # Nats subject name must not include spaces
        self.assertTrue(thing.default_subject.name.find(" ") == -1)

    def test_subject_hierarchy_checks(self):

        hierarchical_subject_name = 'stuff.*'

        with self.assertRaises(RuntimeError):
            NonHierarchicalObject.get_subject(hierarchical_subject_name)

        subject = HierarchicalObject.get_subject(hierarchical_subject_name)
        self.assertEqual(f"{MSG_FORMAT_VERSION}.hierarchical_object.{hierarchical_subject_name}", subject.name)
        subject = UnclearIfHierarchicalObject.get_subject(hierarchical_subject_name)
        self.assertEqual(f"{MSG_FORMAT_VERSION}.unclear_if_hierarchical_object.{hierarchical_subject_name}",
                         subject.name)

    def test_subject_no_hierarchy_checks(self):

        with self.assertRaises(RuntimeError):
            HierarchicalObject.get_subject()

        subject = NonHierarchicalObject.get_subject()
        self.assertEqual(f"{MSG_FORMAT_VERSION}.non_hierarchical_object", subject.name)

        subject = UnclearIfHierarchicalObject.get_subject()
        self.assertEqual(f"{MSG_FORMAT_VERSION}.unclear_if_hierarchical_object",                         subject.name)

if __name__ == '__main__':
    unittest.main()
