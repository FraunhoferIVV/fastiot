import logging
import os
import subprocess
import unittest
from tempfile import TemporaryDirectory

from fastiot.cli.version import get_version, create_version_file


class TestGitVersioning(unittest.TestCase):

    def setUp(self) -> None:
        self.test_dir = TemporaryDirectory()
        self.git_path = self.test_dir.name
        self._old_cwd = os.getcwd()
        os.chdir(self.git_path)

    def tearDown(self) -> None:
        self.test_dir.cleanup()
        os.chdir(self._old_cwd)

    @staticmethod
    def _init_git_repo():
        subprocess.check_output('git init', shell=True)

        # Just reading the config file seems to be not enough, add config to avoid git errors
        subprocess.check_output('git config --local user.email "test.user@ivv-dd.fraunhofer.de"', shell=True)
        subprocess.check_output('git config --local user.name "Test User"', shell=True)

    def test_git_unavailable(self):
        """ We should get an output, not an error """
        self.assertEqual("git-unspecified", get_version())

    def test_without_tags(self):
        """ Should start count at version 0.0 """
        logging.disable(logging.WARNING)  # Disable the warning about no tags being set
        self._init_git_repo()

        for i in range(1, 3):
            with open(os.path.join(self.git_path, f'{i}.txt'), 'w'):
                pass
            subprocess.check_output(f'git add {i}.txt', shell=True)
            subprocess.check_output('git commit -m "1"', shell=True)

            self.assertEqual(f'0.0.{i}', get_version())

        logging.disable(logging.NOTSET)

    def test_with_tags(self):
        """ Does tagging and counting the patch level work? """
        self._init_git_repo()

        with open(os.path.join(self.git_path, '0.txt'), 'w'):
            pass
        subprocess.check_output('git add 0.txt', shell=True)
        subprocess.check_output('git commit -m "0"', shell=True)

        subprocess.check_output('git tag 1.0', shell=True)
        self.assertEqual('1.0', get_version())

        for i in range(1, 3):
            with open(os.path.join(self.git_path, f'{i}.txt'), 'w'):
                pass
            subprocess.check_output(f'git add {i}.txt', shell=True)
            subprocess.check_output('git commit -m "1"', shell=True)

            self.assertEqual(f'1.0.{i}', get_version())
            self.assertEqual('1', get_version(only_major=True))
            self.assertEqual('1.0', get_version(minor=True))

    def test_non_master_branch(self):
        """ Should add the branch to the version and replace - and _ """
        self._init_git_repo()

        with open(os.path.join(self.git_path, '0.txt'), 'w'):
            pass
        subprocess.check_output('git add 0.txt', shell=True)
        subprocess.check_output('git commit -m "0"', shell=True)

        subprocess.check_output('git tag 1.0', shell=True)

        subprocess.check_output('git branch dev-feature_b', shell=True)
        subprocess.check_output('git checkout dev-feature_b', shell=True)

        for i in range(1, 3):
            with open(os.path.join(self.git_path, f'{i}.txt'), 'w'):
                pass
            subprocess.check_output(f'git add {i}.txt', shell=True)
            subprocess.check_output('git commit -m "1"', shell=True)

            self.assertEqual(f'1.0.dev{i}+dev.feature.b', get_version())  # - and _ should be replaced with . (PEP 440)

    def test_create_version_file(self):

        self._init_git_repo()

        with open(os.path.join(self.git_path, '0.txt'), 'w'):
            pass
        subprocess.check_output('git add 0.txt', shell=True)
        subprocess.check_output('git commit -m "0"', shell=True)

        version_file_path = os.path.join(self.git_path, 'vers.py')
        create_version_file(destination=version_file_path)

        with open(version_file_path, 'r') as f:
            lines = f.readlines()

        result = lines[0].strip()
        self.assertEqual("__version__ = '0.0.1'", result)


if __name__ == '__main__':
    unittest.main()
