import logging
from fastiot_sample_services.producer.producer_module import ExampleProducerService

logging.basicConfig(level=logging.INFO)
ExampleProducerService.main()
