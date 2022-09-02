"""
Execute to run all tests
"""

import os
import unittest

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover(os.path.dirname(__file__))
    testRunner = unittest.runner.TextTestRunner()
    testRunner.run(tests)

