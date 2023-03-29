import gc
import unittest

from pydantic import ValidationError

from fastiot import InfrastructureService
from fastiot_tests.cli.service_test import SomeTestService


class TestInfrastructureService(unittest.TestCase):
    def test_infrastructure_service_available(self):
        _ = SomeTestService  # Make sure test service is imported first
        all_services = InfrastructureService.all.values()
        self.assertTrue('test_service' in [service.name for service in all_services])

    # @unittest.skip("Disturbing other tests")
    def test_infrastructure_service_name_validation(self):
        invalid_service = None

        class InvalidService(InfrastructureService):
            name: str = "invalid-service"

        with self.assertRaises(ValidationError):
            invalid_service = InvalidService()

        class InvalidService(InfrastructureService):
            name: str = "now_valid"

        # Overwriting class and forcing garbage collection seems to be the only way not to have an invalid service
        # left over in memory
        invalid_service = InvalidService()
        self.assertTrue(invalid_service.name == "now_valid")

        gc.collect()
