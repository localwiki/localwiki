"""
A custom test runner that doesn't do anything except run syncdb to create our
test-only models.
"""

OUR_TESTS = 'versionutils.versioning.tests'

from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings
from utils import TestSettingsManager

class CreateModelsTestRunner(DjangoTestSuiteRunner):
    def setup_test_environment(self):
        super(CreateModelsTestRunner, self).setup_test_environment()

        mgr = TestSettingsManager()
        INSTALLED_APPS=list(settings.INSTALLED_APPS)
        INSTALLED_APPS.append(OUR_TESTS)
        mgr.set(INSTALLED_APPS=INSTALLED_APPS) 

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # we run setup_databases *first* here
        old_config = self.setup_databases()
        self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        result = self.run_suite(suite)
        self.teardown_databases(old_config)
        self.teardown_test_environment()
        return self.suite_result(suite, result)
