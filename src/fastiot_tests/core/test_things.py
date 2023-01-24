from datetime import datetime
import unittest

from fastiot.msg.thing import Thing


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


if __name__ == '__main__':
    unittest.main()
