import random
import uuid
from collections.abc import MutableMapping, Sequence
from io import BytesIO
from pathlib import PurePath
from typing import Any
from unittest.mock import patch

import pytest
from result import Err
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.domain.chapters.commands import ChapterCreateCommand
from app.core.domain.const import NAME_LENGTH
from app.core.errors import (
    EntityAlreadyExistsError,
    PermissionDeniedError,
    RelationshipNotFoundError,
)
from app.db.models import MangaBranch, MangaChapter
from tests.adapters.graphql.client import GraphQLClient, GraphQLFile
from tests.utils import TestFileStorage

QUERY = """mutation($input: ChapterCreateInput!, $pages: [Upload!]!) {
  chapters {
    create(input: $input, pages: $pages) {
      chapter {
        __typename
        id
        title
        number
        volume
        pages {
          __typename
          id
          image
          number
        }
      }
      error {
        __typename
      }
    }
  }
}"""


def _tpl(chapter: object = None, error: object = None) -> object:
    return {
        "data": {
            "chapters": {
                "create": {
                    "chapter": chapter,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def upload_pages() -> Sequence[GraphQLFile]:
    files = []
    for i in range(10):
        io = BytesIO()
        io.write(str(i).encode())
        io.seek(0)
        extension = random.choice(["png", "jpg", "jpeg"])
        files.append(GraphQLFile(buffer=io, name=f"{i}.{extension}"))
    return files


@pytest.fixture
def input(manga_branch: MangaBranch) -> MutableMapping[str, Any]:
    return {
        "title": "Chapter Title",
        "volume": 1,
        "number": [69, 420],
        "branchId": str(manga_branch.id),
    }


async def test_file_upload_error(
    authenticated_graphql_client: GraphQLClient,
    input: MutableMapping[str, Any],
) -> None:
    file = GraphQLFile(name="some_file", buffer=BytesIO(), content_type=None)
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={
            "input": input,
        },
        files={"pages": [file]},
    )
    assert response == _tpl(error={"__typename": "FileUploadError"})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", "a" * (NAME_LENGTH + 1)),
        ("number", []),
        ("number", [-1]),
        ("number", [0, -1]),
    ],
)
async def test_validation_error(
    authenticated_graphql_client: GraphQLClient,
    input: MutableMapping[str, Any],
    upload_pages: Sequence[GraphQLFile],
    field: str,
    value: object,
) -> None:
    input[field] = value
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={
            "input": input,
        },
        files={"pages": upload_pages},
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


@pytest.mark.parametrize(
    ("error", "typename"),
    [
        (
            RelationshipNotFoundError(entity_id=str(uuid.uuid4())),
            "RelationshipNotFoundError",
        ),
        (PermissionDeniedError(), "PermissionDeniedError"),
        (EntityAlreadyExistsError(), "EntityAlreadyExistsError"),
    ],
)
async def test_err(
    authenticated_graphql_client: GraphQLClient,
    input: MutableMapping[str, Any],
    upload_pages: Sequence[GraphQLFile],
    error: object,
    typename: str,
) -> None:
    input["branchId"] = str(uuid.uuid4())
    with patch.object(
        ChapterCreateCommand,
        ChapterCreateCommand.execute.__name__,
        return_value=Err(error),
    ):
        response = await authenticated_graphql_client.query(
            query=QUERY,
            variables={
                "input": input,
            },
            files={"pages": upload_pages},
        )
    assert response == _tpl(error={"__typename": typename})


async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    input: MutableMapping[str, Any],
    session: AsyncSession,
    s3_mock: TestFileStorage,
    upload_pages: Sequence[GraphQLFile],
) -> None:
    response = await authenticated_graphql_client.query(
        query=QUERY,
        variables={
            "input": input,
        },
        files={"pages": upload_pages},
    )
    new_chapter = (
        await session.scalars(
            select(MangaChapter).options(selectinload(MangaChapter.pages)),
        )
    ).one()
    for file, page in zip(upload_pages, new_chapter.pages, strict=True):
        assert PurePath(file.name).suffix == PurePath(page.image_path).suffix

    expected = {
        "__typename": "MangaChapter",
        "id": str(new_chapter.id),
        "title": input["title"],
        "volume": input["volume"],
        "number": ".".join(str(n) for n in input["number"]),
        "pages": [
            {
                "__typename": "MangaPage",
                "id": str(page.id),
                "number": page.number,
                "image": await s3_mock.url(page.image_path),
            }
            for page in new_chapter.pages
        ],
    }
    assert response == _tpl(chapter=expected)
