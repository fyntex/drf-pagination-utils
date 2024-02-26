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

    def get_paginated_components_schemas(
        self, components: Mapping[str, Mapping[str, object]]
    ) -> Mapping[str, Mapping[str, object]]:
        """
        Return schema for pagination-related components.

        .. seealso::
          https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.2.md#components-object

        :param components: OpenAPI ``Components`` object.
        :return: Updated OpenAPI ``Components`` object.
        """
        if hasattr(super(), 'get_paginated_components_schemas'):
            components = super().get_paginated_components_schemas(components)

        component_name = 'headers'
        content = {
            'Link': {
                'description': 'Web Links (RFC 8288)',
                'schema': {'type': 'string'},
                'examples': {
                    'pagination': {
                        'summary': """Link Header Page Number Pagination.

A simple page number–based style that supports page numbers as query parameters
and includes pagination links in an RFC 8288–compliant `Link` header.""",
                        'value': ', '.join(
                            (
                                '<http://www.example.com/example-items/>; rel="first"',
                                '<http://www.example.com/example-items/?page=3>; rel="previous"',
                                '<http://www.example.com/example-items/?page=5>; rel="next"',
                                '<http://www.example.com/example-items/?page=42>; rel="last"',
                            )
                        ),
                    },
                },
            },
        }
        components = {
            component_name: {},
            **components,
        }
        components[component_name] = {
            **components[component_name],
            **content,
        }

        component_name = 'links'
        content = {
            'collection_first_page': {
                'description': """First page of the collection of items.

Use the URL returned in the relation type `first` of the response `Link` header.""",
            },
            'collection_previous_page': {
                'description': """Previous page of the collection of items.

Use the URL returned in the relation type `previous` of the response `Link` header.""",
            },
            'collection_next_page': {
                'description': """Next page of the collection of items.

Use the URL returned in the relation type `next` of the response `Link` header.""",
            },
            'collection_last_page': {
                'description': """Last page of the collection of items.

Use the URL returned in the relation type `last` of the response `Link` header.""",
            },
        }
        components = {
            component_name: {},
            **components,
        }
        components[component_name] = {
            **components[component_name],
            **content,
        }

        return components

    def get_paginated_response_headers_schema(
        self, response_headers: Mapping[str, Mapping[str, object]]
    ) -> Mapping[str, Mapping[str, object]]:
        """
        Return schema for headers of paginated responses.

        .. seealso::
          https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.2.md#response-object

        :param response_headers: Field ``headers`` of OpenAPI ``Response`` object.
        :return: Updated field ``headers`` of OpenAPI ``Response`` object.
        """
        if hasattr(super(), 'get_paginated_response_headers_schema'):
            response_headers = super().get_paginated_response_headers_schema(response_headers)

        response_headers = {
            **response_headers,
            'Link': {
                '$ref': '#/components/headers/Link',
            },
        }
        return response_headers

    def get_paginated_response_links_schema(
        self, response_links: Mapping[str, Mapping[str, object]]
    ) -> Mapping[str, Mapping[str, object]]:
        """
        Return schema for links of paginated responses.

        .. seealso::
          https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.2.md#response-object

        :param response_links: Field ``links`` of OpenAPI ``Response`` object.
        :return: Updated field ``links`` of OpenAPI ``Response`` object.
        """
        if hasattr(super(), 'get_paginated_response_links_schema'):
            response_links = super().get_paginated_response_links_schema(response_links)

        response_links = {
            **response_links,
            'first_page': {'$ref': '#/components/links/collection_first_page'},
            'previous_page': {'$ref': '#/components/links/collection_previous_page'},
            'next_page': {'$ref': '#/components/links/collection_next_page'},
            'last_page': {'$ref': '#/components/links/collection_last_page'},
        }
        return response_links


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

    def get_paginated_components_schemas(
        self, components: Mapping[str, Mapping[str, object]]
    ) -> Mapping[str, Mapping[str, object]]:
        """
        Return schema for pagination-related components.

        .. seealso::
          https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.2.md#components-object

        :param components: OpenAPI ``Components`` object.
        :return: Updated OpenAPI ``Components`` object.
        """
        if hasattr(super(), 'get_paginated_components_schemas'):
            components = super().get_paginated_components_schemas(components)

        if self.object_count_header:
            component_name = 'headers'
            content = {
                self.object_count_header: {
                    'description': """Total number of items in the collection.

Note: Header is optional for single-page responses.""",
                    'schema': {'type': 'integer'},
                },
            }
            components = {
                component_name: {},
                **components,
            }
            components[component_name] = {
                **components[component_name],
                **content,
            }

        return components

    def get_paginated_response_headers_schema(
        self, response_headers: Mapping[str, Mapping[str, object]]
    ) -> Mapping[str, Mapping[str, object]]:
        """
        Return schema for headers of paginated responses.

        .. seealso::
          https://github.com/OAI/OpenAPI-Specification/blob/3.0.2/versions/3.0.2.md#response-object

        :param response_headers: Field ``headers`` of OpenAPI ``Response`` object.
        :return: Updated field ``headers`` of OpenAPI ``Response`` object.
        """
        if hasattr(super(), 'get_paginated_response_headers_schema'):
            response_headers = super().get_paginated_response_headers_schema(response_headers)

        if self.object_count_header:
            response_headers = {
                **response_headers,
                self.object_count_header: {
                    '$ref': f'#/components/headers/{self.object_count_header}',
                },
            }
        return response_headers
