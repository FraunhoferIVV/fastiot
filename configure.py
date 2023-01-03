extensions = ['fastiot_ivv_tools.extension']

project_namespace = 'fastiot'

library_package = 'fastiot'

test_package = 'fastiot_tests'
integration_test_deployment = 'integration_test'

lib_compilation_mode = 'only_source'

# There are some internal tools at Fraunhofer IVV CI runner with some additional configuration:
ivv_tools = {'pypi_upload': 'only_tagged'}
