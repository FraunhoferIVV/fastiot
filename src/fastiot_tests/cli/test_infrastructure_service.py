import unittest

from fastiot import InfrastructureService
from fastiot_tests.cli.service_test import SomeTestService


class TestInfrastructureService(unittest.TestCase):
    def test_infrastructure_service_available(self):
        _ = SomeTestService  # Make sure test service is imported first
        all_services = InfrastructureService.all.values()
        self.assertTrue('test_service' in [service.name for service in all_services])
