import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.helper_fn import parse_env_file


class TestEnvFileParser(unittest.TestCase):

    def test_comments(self):
        with NamedTemporaryFile(mode="w") as f:
            f.write("var=test #Comment\n")
            f.seek(0)
            cfg = parse_env_file(f.name)
            self.assertEqual(cfg['var'], 'test')

    def test_no_comment(self):
        with NamedTemporaryFile(mode="w") as f:
            f.write("var=test#pass\n")
            f.seek(0)
            cfg = parse_env_file(f.name)
            self.assertEqual(cfg['var'], 'test#pass')

    def test_line_comment(self):
        with NamedTemporaryFile(mode="w") as f:
            f.write("#var=test\n")
            f.write("var=new_test\n")
            f.seek(0)
            cfg = parse_env_file(f.name)
            self.assertEqual(cfg['var'], 'new_test')

    def test_empty_line(self):
        with NamedTemporaryFile(mode="w") as f:
            f.write("\n")
            f.seek(0)
            cfg = parse_env_file(f.name)
            self.assertEqual(cfg, {})


if __name__ == '__main__':
    unittest.main()
