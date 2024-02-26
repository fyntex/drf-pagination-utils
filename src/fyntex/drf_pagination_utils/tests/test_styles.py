from __future__ import annotations

import http
import unittest
from collections import OrderedDict
from unittest import mock

import rest_framework.pagination
import rest_framework.request
from django.core.paginator import Page, Paginator
from rest_framework.response import Response as DrfResponse

from ..styles import LinkHeaderPageNumberPagination, ObjectCountHeaderPageNumberPagination


class LinkHeaderPageNumberPaginationTest(unittest.TestCase):
    """
    Tests for :class:`LinkHeaderPageNumberPagination`.
    """

    def setUp(self) -> None:
        # Set up the pagination and page objects.

        # Pagination with 2 pages.
        self.data_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.paginator_1 = Paginator(self.data_list, 2)
        self.pagination_obj_1 = LinkHeaderPageNumberPagination()
        self.pagination_obj_1.request = mock.create_autospec(
            rest_framework.request.Request,
            instance=True,
            build_absolute_uri=mock.Mock(
                return_value='https://example.com/api/v1/endpoint/',
            ),
        )
        self.pagination_obj_1.page = Page(self.paginator_1.get_page(1), 1, self.paginator_1)

        # Empty Pagination with 1 page.
        self.paginator_2 = Paginator([], 2)
        self.pagination_obj_2 = LinkHeaderPageNumberPagination()
        self.pagination_obj_2.request = mock.create_autospec(
            rest_framework.request.Request,
            instance=True,
            build_absolute_uri=mock.Mock(
                return_value='https://example.com/api/v1/endpoint/',
            ),
        )
        self.pagination_obj_2.page = Page(self.paginator_2.get_page(1), 1, self.paginator_2)

    def test_inherits_from_base_pagination_class(self) -> None:
        self.assertTrue(
            issubclass(LinkHeaderPageNumberPagination, rest_framework.pagination.BasePagination),
        )

    def test_inherits_from_page_number_pagination_class(self) -> None:
        self.assertTrue(
            issubclass(
                LinkHeaderPageNumberPagination,
                rest_framework.pagination.PageNumberPagination,
            ),
        )

    def test_get_paginated_response_with_items(self) -> None:
        """
        Test that the pagination response is correct.
        """
        response = self.pagination_obj_1.get_paginated_response(self.data_list)
        expected_headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Link': (
                '<https://example.com/api/v1/endpoint/?page=2>; rel="next", '
                '<https://example.com/api/v1/endpoint/?page=4>; rel="last"'
            ),
        }
        self.assertEqual(response.data, self.data_list)
        self.assertEqual(response.headers, expected_headers)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

        # Check on page 2
        self.pagination_obj_1.page = Page(self.paginator_1.get_page(2), 2, self.paginator_1)
        response = self.pagination_obj_1.get_paginated_response(self.data_list)

        self.assertEqual(response.data, self.data_list)
        expected_headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Link': (
                '<https://example.com/api/v1/endpoint/>; rel="first", '
                '<https://example.com/api/v1/endpoint/>; rel="previous", '
                '<https://example.com/api/v1/endpoint/?page=3>; rel="next", '
                '<https://example.com/api/v1/endpoint/?page=4>; rel="last"'
            ),
        }
        self.assertEqual(response.headers, expected_headers)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_get_paginated_response_with_empty_page(self) -> None:
        """
        Test that returns a paginated response when page has no items.
        """
        response = self.pagination_obj_2.get_paginated_response([])

        expected_headers = {
            'Content-Type': 'text/html; charset=utf-8',
            'Link': '',
        }
        self.assertEqual(response.data, [])
        self.assertEqual(response.headers, expected_headers)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_get_paginated_response_schema(self) -> None:
        """
        Test that the schema of the response is correct.
        """
        test_schema = {
            "type": "array",
            "items": {
                "type": "object",
            },
        }
        response = self.pagination_obj_1.get_paginated_response_schema(test_schema)

        # Check the given schema has not changed.
        self.assertEqual(response, test_schema)

    def test_get_paginated_components_schemas(self) -> None:
        """
        Test that the schema of the response is correct.
        """
        response = self.pagination_obj_1.get_paginated_components_schemas({})

        expected_schema = {
            'links': {
                'collection_first_page': {
                    'description': (
                        'First page of the collection of items.\n\n'
                        'Use the URL returned in the relation type `first` of the response `Link` '
                        'header.'
                    )
                },
                'collection_previous_page': {
                    'description': (
                        'Previous page of the collection of items.\n\n'
                        'Use the URL returned in the relation type `previous` of the response '
                        '`Link` header.'
                    )
                },
                'collection_next_page': {
                    'description': (
                        'Next page of the collection of items.\n\n'
                        'Use the URL returned in the relation type `next` of the response `Link` '
                        'header.'
                    )
                },
                'collection_last_page': {
                    'description': (
                        'Last page of the collection of items.\n\n'
                        'Use the URL returned in the relation type `last` of the response `Link` '
                        'header.'
                    )
                },
            },
            'headers': {
                'Link': {
                    'description': 'Web Links (RFC 8288)',
                    'schema': {'type': 'string'},
                    'examples': {
                        'pagination': {
                            'summary': (
                                'Link Header Page Number Pagination.\n\n'
                                'A simple page number–based style that supports page numbers as '
                                'query parameters\nand includes pagination links in an RFC '
                                '8288–compliant `Link` header.'
                            ),
                            'value': (
                                '<http://www.example.com/example-items/>; rel="first", '
                                '<http://www.example.com/example-items/?page=3>; rel="previous", '
                                '<http://www.example.com/example-items/?page=5>; rel="next", '
                                '<http://www.example.com/example-items/?page=42>; rel="last"'
                            ),
                        }
                    },
                }
            },
        }
        self.assertEqual(response, expected_schema)

    def test_get_paginated_response_headers_schema(self) -> None:
        """
        Test that the schema of the response headers is correct.
        """
        response = self.pagination_obj_1.get_paginated_response_headers_schema(
            {
                'Content-Type': {
                    "text/html": {
                        "schema": {"$ref": "#/components/schemas/Example"},
                    },
                },
                'Link': {
                    "$ref": "#/test",
                },
            }
        )
        expected_schema = {
            'Content-Type': {
                "text/html": {
                    "schema": {"$ref": "#/components/schemas/Example"},
                },
            },
            'Link': {'$ref': '#/components/headers/Link'},
        }
        self.assertEqual(response, expected_schema)

    def test_get_paginated_response_links_schema(self) -> None:
        """
        Test that the schema of the response links is correct.
        """

        response = self.pagination_obj_1.get_paginated_response_links_schema({})

        expected_links_schema = {
            'first_page': {'$ref': '#/components/links/collection_first_page'},
            'previous_page': {'$ref': '#/components/links/collection_previous_page'},
            'next_page': {'$ref': '#/components/links/collection_next_page'},
            'last_page': {'$ref': '#/components/links/collection_last_page'},
        }
        self.assertEqual(response, expected_links_schema)


class ObjectCountHeaderPageNumberPaginationTest(unittest.TestCase):
    """
    Tests for :class:`ObjectCountHeaderPageNumberPagination`.
    """

    def setUp(self) -> None:
        # Set up the pagination and page objects.

        self.data_list = ['a', 'b', 'c', 'd']

        # Pagination with 2 pages.
        self.paginator_1 = Paginator(self.data_list, 2)
        self.pagination_obj_1 = ObjectCountHeaderPageNumberPagination()
        self.pagination_obj_1.request = mock.create_autospec(
            rest_framework.request.Request,
            instance=True,
            build_absolute_uri=mock.Mock(
                return_value='https://example.com/api/v1/endpoint/',
            ),
        )
        self.pagination_obj_1.page = Page(self.paginator_1.get_page(1), 1, self.paginator_1)

        # Empty Pagination with 1 page.
        self.paginator_2 = Paginator([], 1)
        self.pagination_obj_2 = ObjectCountHeaderPageNumberPagination()
        self.pagination_obj_2.request = mock.create_autospec(
            rest_framework.request.Request,
            instance=True,
            build_absolute_uri=mock.Mock(
                return_value='https://example.com/api/v1/endpoint/',
            ),
        )
        self.pagination_obj_2.page = Page(self.paginator_2.get_page(1), 1, self.paginator_2)

        # Pagination with 2 pages and object count header set.
        self.paginator_3 = Paginator(self.data_list, 2)
        self.pagination_obj_3 = ObjectCountHeaderPageNumberPagination()
        self.pagination_obj_3.object_count_header = 'Count-Header'
        self.pagination_obj_3.request = mock.create_autospec(
            rest_framework.request.Request,
            instance=True,
            build_absolute_uri=mock.Mock(
                return_value='https://example.com/api/v1/endpoint/',
            ),
        )
        self.pagination_obj_3.page = Page(self.paginator_3.get_page(1), 1, self.paginator_3)

    def test_inherits_from_page_number_pagination_class(self) -> None:
        self.assertTrue(
            issubclass(
                ObjectCountHeaderPageNumberPagination,
                rest_framework.pagination.PageNumberPagination,
            ),
        )

    def test_get_paginated_response_with_items(self) -> None:
        """
        Test that returns a paginated response when page has items.
        """
        # Test with object count header not set.
        self.assertTrue(self.pagination_obj_1.page.has_other_pages())
        response = self.pagination_obj_1.get_paginated_response(self.data_list)

        expected_response = DrfResponse(
            OrderedDict(
                [
                    ('count', 4),
                    ('next', 'https://example.com/api/v1/endpoint/?page=2'),
                    ('previous', None),
                    ('results', self.data_list),
                ]
            )
        )
        self.assertEqual(response.data, expected_response.data)
        self.assertNotIn('Count-Header', response)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

        # Test with object count header set.
        self.assertTrue(self.pagination_obj_3.page.has_other_pages())
        response = self.pagination_obj_3.get_paginated_response(self.data_list)
        expected_response = DrfResponse(
            OrderedDict(
                [
                    ('count', 4),
                    ('next', 'https://example.com/api/v1/endpoint/?page=2'),
                    ('previous', None),
                    ('results', self.data_list),
                ]
            )
        )
        self.assertEqual(response.data, expected_response.data)
        self.assertIn('Count-Header', response)
        self.assertEqual(response['Count-Header'], '4')
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_get_paginated_response_with_empty_page(self) -> None:
        """
        Test that returns a paginated response when page has no items.
        """
        self.assertFalse(self.pagination_obj_2.page.has_other_pages())
        response = self.pagination_obj_2.get_paginated_response([])

        expected_response = DrfResponse(
            OrderedDict(
                [
                    ('count', 0),
                    ('next', None),
                    ('previous', None),
                    ('results', []),
                ]
            )
        )
        self.assertEqual(response.data, expected_response.data)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_get_paginated_response_schema(self) -> None:
        """
        Test that the schema of the response is correct.
        """
        test_schema = {
            'type': 'object',
            'properties': {
                'count': {'type': 'integer'},
                'next': {'type': ['string', 'null']},
                'previous': {'type': ['string', 'null']},
                'results': {'type': 'array'},
            },
            'required': ['count', 'next', 'previous', 'results'],
        }

        response = self.pagination_obj_1.get_paginated_response_schema(test_schema)

        # Check the given schema has not changed.
        self.assertEqual(response, test_schema)

    def test_get_paginated_components_schemas_without_count_header(self) -> None:
        """
        Test that the schema of the components is correct when the count header is None.
        """
        response = self.pagination_obj_1.get_paginated_components_schemas({})
        self.assertEqual(response, {})

    def test_get_paginated_components_schemas_with_count_header(self) -> None:
        """
        Test that the schema of the components is correct when the count header is set.
        """
        response = self.pagination_obj_3.get_paginated_components_schemas({})

        expected_schema = {
            'headers': {
                'Count-Header': {
                    'description': 'Total number of items in the collection.\n\n'
                    'Note: Header is optional for single-page responses.',
                    'schema': {'type': 'integer'},
                }
            }
        }
        self.assertEqual(response, expected_schema)

    def test_get_paginated_response_headers_schema_without_count_header(self) -> None:
        """
        Test that the schema of the response headers is correct when the count header is None.
        """
        response = self.pagination_obj_1.get_paginated_response_headers_schema(
            {
                'Content-Type': {
                    "text/html": {
                        "schema": {"$ref": "#/components/schemas/Example"},
                    },
                },
                'Link': {
                    "$ref": "#/test",
                },
            }
        )
        expected_schema = {
            'Content-Type': {
                "text/html": {
                    "schema": {"$ref": "#/components/schemas/Example"},
                },
            },
            'Link': {'$ref': '#/test'},
        }
        self.assertEqual(response, expected_schema)

    def test_get_paginated_response_headers_schema_with_count_header(self) -> None:
        """
        Test that the schema of the response headers is correct when the count header is set.
        """
        response = self.pagination_obj_3.get_paginated_response_headers_schema(
            {
                'Content-Type': {
                    "text/html": {
                        "schema": {"$ref": "#/components/schemas/Example"},
                    },
                },
                'Link': {
                    "$ref": "#/test",
                },
            }
        )
        expected_schema = {
            'Content-Type': {
                "text/html": {
                    "schema": {"$ref": "#/components/schemas/Example"},
                },
            },
            'Link': {'$ref': '#/test'},
            'Count-Header': {'$ref': '#/components/headers/Count-Header'},
        }
        self.assertEqual(response, expected_schema)
