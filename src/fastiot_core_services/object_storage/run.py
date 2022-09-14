from fastiot.helpers.read_yaml import read_log_config
from fastiot_core_services.object_storage.object_storage_service import ObjectStorageService
import logging.config

if __name__ == '__main__':

    try:
        logging.config.dictConfig(read_log_config())
    except ValueError as e:
        logging.warning('log config file not found')
    ObjectStorageService.main()

