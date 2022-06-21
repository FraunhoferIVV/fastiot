from fastiot.cli.model import ModulePackageConfig

extensions = ['fastiot_ivv_tools.extension']

project_namespace = 'fastiot'

library_package = 'fastiot'
module_packages = [ModulePackageConfig(package_name='fastiot_sample_services',
                                       cache_name='fastiot:latest',
                                       extra_caches=['fastiot-dev:latest'])]

test_package = 'fastiot_test'
test_config = 'fastiot_test_env'
