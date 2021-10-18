from __future__ import annotations

import unittest

import rest_framework.pagination

from ..styles import LinkHeaderPageNumberPagination, ObjectCountHeaderPageNumberPagination


class LinkHeaderPageNumberPaginationTest(unittest.TestCase):
    """
    Tests for :class:`LinkHeaderPageNumberPagination`.
    """

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


class ObjectCountHeaderPageNumberPaginationTest(unittest.TestCase):
    """
    Tests for :class:`ObjectCountHeaderPageNumberPagination`.
    """

    def test_inherits_from_page_number_pagination_class(self) -> None:
        self.assertTrue(
            issubclass(
                ObjectCountHeaderPageNumberPagination,
                rest_framework.pagination.PageNumberPagination,
            ),
        )
