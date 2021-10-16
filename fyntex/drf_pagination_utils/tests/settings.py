"""
Django settings for testing purposes.

For more information on this file, see https://docs.djangoproject.com/en/3.1/topics/settings/.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/

For a deployment checklist, see https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/.
"""

from __future__ import annotations

import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent

# -----BEGIN Testing-----

# Documentation: https://docs.djangoproject.com/en/3.1/ref/settings/#test-runner
# Default: 'django.test.runner.DiscoverRunner'
TEST_RUNNER: str
TEST_RUNNER = os.getenv('DJANGO_TEST_RUNNER', default='django.test.runner.DiscoverRunner')

# unittest-xml-reporting
#
# Documentation:
#   https://github.com/xmlrunner/unittest-xml-reporting/blob/3.0.4/README.md#django-support
TEST_OUTPUT_DIR: str
TEST_OUTPUT_DIR = str(Path(os.getenv('DJANGO_TEST_OUTPUT_DIR', default=BASE_DIR)).resolve())

# -----END Testing-----
