from __future__ import annotations

from typing import Iterable, Mapping, Optional

import rest_framework.pagination
from rest_framework.response import Response as DrfResponse
from rest_framework.utils.urls import remove_query_param, replace_query_param


class LinkHeaderPageNumberPagination(rest_framework.pagination.PageNumberPagination):
    """
    A simple page number–based style that supports page numbers as query parameters and includes
    pagination links in an RFC 8288–compliant `Link` header.

    Example URLs:
    - http://www.example.com/example-items/?page=4
    - http://www.example.com/example-items/?page=4&page_size=100

    Example header:
    Link: <http://www.example.com/example-items/>; rel="first",
     <http://www.example.com/example-items/?page=3>; rel="previous",
     <http://www.example.com/example-items/?page=5>; rel="next",
     <http://www.example.com/example-items/?page=42>; rel="last"

    See also:
    - https://tools.ietf.org/html/rfc8288
    - https://requests.readthedocs.io/en/latest/user/advanced/#link-headers
    - https://docs.github.com/en/rest/guides/traversing-with-pagination
    """

    _LINK_VALUE_TEMPLATE: str = '<{uri_reference}>; rel="{relation_type}"'
    """
    Link value template string.

    See also: [Link Serialisation in HTTP Headers](https://tools.ietf.org/html/rfc8288#section-3)
    """

    def get_paginated_response(self, data: object) -> DrfResponse:
        links: Mapping[str, Optional[str]] = {
            'first': self.get_first_link(),
            'previous': self.get_previous_link(),
            'next': self.get_next_link(),
            'last': self.get_last_link(),
        }
        link_values: Iterable[str] = (
            self._LINK_VALUE_TEMPLATE.format(uri_reference=uri_ref, relation_type=rel_type)
            for rel_type, uri_ref in links.items()
            if uri_ref is not None
        )

        headers: Optional[Mapping[str, str]] = None
        if link_values:
            headers = {
                'Link': ', '.join(link_values),
            }

        return DrfResponse(data, headers=headers)

    def get_last_link(self) -> Optional[str]:
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.paginator.num_pages
        result_url: str = replace_query_param(url, self.page_query_param, page_number)
        return result_url

    def get_first_link(self) -> Optional[str]:
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        result_url: str = remove_query_param(url, self.page_query_param)
        return result_url

    def get_paginated_response_schema(self, schema: Mapping[str, object]) -> Mapping[str, object]:
        """
        Return schema for paginated responses.

        .. note:: The paginated and non-paginated schemas are the same because pagination links are
          included in the response headers, not as part of the content of the response.

        .. seealso:: :meth:`rest_framework.pagination.BasePagination.get_paginated_response_schema`

        :param schema: Original, non-paginated response schema.
        :return: Paginated response schema.
        """
        return schema


class ObjectCountHeaderPageNumberPagination(rest_framework.pagination.PageNumberPagination):
    """
    A simple page number–based style that adds a header with the total number of objects to
    responses.
    """

    object_count_header: Optional[str] = None
    """
    Name of the response header that specifies the total number of objects.

    If ``None``, no header will be added.
    """

    def get_paginated_response(self, data: object) -> DrfResponse:
        response = super().get_paginated_response(data)

        if self.page.has_other_pages():
            self.add_object_count_header(response)

        return response

    def add_object_count_header(self, response: DrfResponse) -> None:
        if self.object_count_header:
            response[self.object_count_header] = self.page.paginator.count

    def get_paginated_response_schema(self, schema: Mapping[str, object]) -> Mapping[str, object]:
        """
        Return schema for paginated responses.

        .. note:: The paginated and non-paginated schemas are the same because pagination links are
          included in the response headers, not as part of the content of the response.

        .. seealso:: :meth:`rest_framework.pagination.BasePagination.get_paginated_response_schema`

        :param schema: Original, non-paginated response schema.
        :return: Paginated response schema.
        """
        return schema
