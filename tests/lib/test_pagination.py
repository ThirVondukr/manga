import pytest

from lib.pagination.pagination import PagePaginationParamsDTO, PaginationError


def test_pagination_params_dto() -> None:
    for i in (-1, 0):
        with pytest.raises(PaginationError):
            PagePaginationParamsDTO(page=i, page_size=10)

        with pytest.raises(PaginationError):
            PagePaginationParamsDTO(page=10, page_size=i)
