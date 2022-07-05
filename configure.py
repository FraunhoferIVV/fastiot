from fastiot.cli import find_services

extensions = ['fastiot_ivv_tools.extension']

project_namespace = 'fastiot'

library_package = 'fastiot'
services = find_services(package='fastiot_sample_services')

test_package = 'fastiot_tests'
integration_test_deployment = 'integration_test'

compile_lib = 'only_source'
