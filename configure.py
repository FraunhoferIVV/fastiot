from fastiot.cli import find_services

extensions = ['fastiot_ivv_tools.extension']

project_namespace = 'fastiot'

library_package = 'fastiot'
modules = find_services(package='fastiot_sample_services')

test_package = 'fastiot_tests'
test_config = 'integration_test'

compile_lib = 'only_source'
