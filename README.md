Fyntex’s Pagination Utilities for Django REST Framework
==========================================================

This is a library that provides custom pagination styles and pagination-related utilities for Django
REST Framework.


## Dashboard

### Development

| VCS Branch | Deployment Environment | VCS Repository | CI/CD Status |
| ---------- | ---------------------- | -------------- | ------------ |
| `develop` | Staging | [GitHub](https://github.com/fyntex/drf-pagination-utils/tree/develop) | [![GitHub Actions](https://github.com/fyntex/drf-pagination-utils/actions/workflows/ci-cd.yaml/badge.svg?branch=develop)](https://github.com/fyntex/drf-pagination-utils/actions/workflows/ci-cd.yaml?query=branch:develop) |
| `master` | Production | [GitHub](https://github.com/fyntex/drf-pagination-utils/tree/master)  | [![GitHub Actions](https://github.com/fyntex/drf-pagination-utils/actions/workflows/ci-cd.yaml/badge.svg?branch=master)](https://github.com/fyntex/drf-pagination-utils/actions/workflows/ci-cd.yaml?query=branch:master) |


| Code Coverage |
| ------------- |
| [![Codecov](https://codecov.io/gh/cordada/drf-pagination-utils/graph/badge.svg?token=66RN4HVW2C)](https://codecov.io/gh/cordada/drf-pagination-utils) |


### Hosting

| Deployment Environment | Python Package Registry |
| ---------------------- | ----------------------- |
| Production | [PyPI](https://pypi.org/project/fyntex-drf-pagination-utils/)  |


## Installation

Install Python package:

```sh
pip install fyntex-drf-pagination-utils
```


## Usage

```python
from typing import Optional

import fyntex.drf_pagination_utils.styles
from rest_framework.settings import api_settings as drf_settings


class StandardResultSetPagination(
    fyntex.drf_pagination_utils.styles.ObjectCountHeaderPageNumberPagination,
    fyntex.drf_pagination_utils.styles.LinkHeaderPageNumberPagination,
):
    """
    Custom pagination class used to override pagination settings from
    :class:`rest_framework.pagination.PageNumberPagination`.

    See also:
    - https://www.django-rest-framework.org/api-guide/pagination/#configuration
    - https://www.django-rest-framework.org/api-guide/pagination/#modifying-the-pagination-style
    """

    page_size_query_param: Optional[str] = 'page_size'
    """
    Name of the query parameter that allows the client to set the page size on a per-request basis.
    """

    max_page_size: Optional[int] = drf_settings.PAGE_SIZE * 2 if drf_settings.PAGE_SIZE else None
    """
    Maximum page size the client may request.
    """

    object_count_header: Optional[str] = 'X-Pagination-Total-Item-Count'
```

Django settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'example.StandardResultSetPagination',
}
```


## Additional Information

- https://www.django-rest-framework.org/api-guide/pagination/#custom-pagination-styles
