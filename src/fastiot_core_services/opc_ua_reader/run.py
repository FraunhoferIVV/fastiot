import logging

from fastiot_core_services.opc_ua_reader.machine_monitoring_module import OPCUAReader

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    OPCUAReader.main()
