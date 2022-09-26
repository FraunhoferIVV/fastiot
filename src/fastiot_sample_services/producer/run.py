import logging
from fastiot_sample_services.producer.producer_module import ExampleProducerService

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    ExampleProducerService.main()
