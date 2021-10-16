DJANGO_ADMIN ?= ./manage.py
COVERAGE ?= coverage

.PHONY: django-test
django-test:
	$(DJANGO_ADMIN) test
	$(DJANGO_ADMIN) makemigrations --dry-run --check -v3

.PHONY: django-test-report
django-test-report: UNITTEST_JUNIT_REPORT_DIR = $(TEST_REPORT_DIR)/junit/unittest
django-test-report:
	mkdir -p "$(UNITTEST_JUNIT_REPORT_DIR)"
	-export \
		DJANGO_TEST_OUTPUT_DIR="$(UNITTEST_JUNIT_REPORT_DIR)" \
		DJANGO_TEST_RUNNER=xmlrunner.extra.djangotestrunner.XMLTestRunner \
		&& $(MAKE) --no-print-directory django-test

.PHONY: django-test-coverage
django-test-coverage:
	-$(COVERAGE) run $(DJANGO_ADMIN) test
