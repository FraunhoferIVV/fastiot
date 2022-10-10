import logging

from fastiot_core_services.machine_monitoring.machine_monitoring_module import MachineMonitoring

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    MachineMonitoring.main()
