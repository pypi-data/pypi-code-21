import os
import json
from pact_test.utils.logger import *
from pact_test.config.config_builder import Config
from pact_test.utils.logger import log_consumers_test_results
from pact_test.utils.logger import log_providers_test_results
from pact_test.runners.service_consumers.test_suite import ServiceConsumerTestSuiteRunner
from pact_test.runners.service_providers.test_suite import ServiceProviderTestSuiteRunner


def verify(verify_consumers=False, verify_providers=False):
    config = Config()

    if verify_consumers:
        run_consumer_tests(config)
    if verify_providers:
        run_provider_tests(config)


def run_consumer_tests(config):
    test_results = ServiceConsumerTestSuiteRunner(config).verify()
    log_consumers_test_results(test_results)


def run_provider_tests(config):
    test_results = ServiceProviderTestSuiteRunner(config).verify()
    log_providers_test_results(test_results)
    for pact in test_results.value:
        filename = pact['consumer']['name'] + '_' + pact['provider']['name'] + '.json'
        filename = filename.replace(' ', '_').lower()
        info('Writing pact to: ' + filename)
        with open(os.path.join(os.getcwd(), 'pacts', filename), 'w+') as file:
            file.write(json.dumps(pact))
