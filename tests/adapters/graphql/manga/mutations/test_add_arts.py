import uuid
from typing import Any
from unittest.mock import patch

import pytest
from result import Err

from app.core.domain.manga.art.command import AddArtsToMangaCommand
from app.core.errors import NotFoundError
from app.db.models import Manga
from lib.types import Language
from tests.adapters.graphql.client import GraphQLClient, GraphQLFile
from tests.adapters.graphql.utils import assert_not_authenticated
from tests.utils import TestFileStorage, create_dummy_image

QUERY = """mutation($input: MangaArtsAddInput!) {
  manga {
    addArts(input: $input) {
      manga {
        id
        arts {
          id
          volume
          language
          image {
            url
          }
          previewImage {
            url
          }
        }
      }
      error {
        __typename
      }
    }
  }
}"""


def _tpl(manga: object = None, error: object = None) -> object:
    return {
        "data": {
            "manga": {
                "addArts": {
                    "manga": manga,
                    "error": error,
                },
            },
        },
    }


@pytest.fixture
def input() -> dict[str, Any]:
    return {
        "mangaId": str(uuid.uuid4()),
        "arts": [],
    }


async def test_requires_authentication(
    graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    response = await graphql_client.query(QUERY, variables={"input": input})
    assert_not_authenticated(response)


async def test_validation_error(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    input["arts"].append(
        {"image": None, "volume": -1, "language": Language.eng.name.upper()},
    )
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
        files={
            "input.arts.0.image": GraphQLFile(
                name="some_file",
                buffer=create_dummy_image(),
                content_type="image/png",
            ),
        },
    )
    assert response == _tpl(error={"__typename": "ValidationErrors"})


async def test_err(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
) -> None:
    with patch.object(
        AddArtsToMangaCommand,
        AddArtsToMangaCommand.execute.__name__,
        return_value=Err(NotFoundError(entity_id="")),
    ):
        response = await authenticated_graphql_client.query(
            QUERY,
            variables={"input": input},
        )
    assert response == _tpl(error={"__typename": "NotFoundError"})


@pytest.mark.usefixtures("make_user_superuser")
async def test_ok(
    authenticated_graphql_client: GraphQLClient,
    input: dict[str, Any],
    manga: Manga,
    s3_mock: TestFileStorage,
) -> None:
    arts_count = 5
    input["mangaId"] = str(manga.id)
    input["arts"].extend(
        {"image": None, "volume": volume, "language": Language.eng.name.upper()}
        for volume in range(1, arts_count + 1)
    )
    response = await authenticated_graphql_client.query(
        QUERY,
        variables={"input": input},
        files={
            "input.arts.$.image": [
                GraphQLFile(
                    name=f"{i}.png",
                    buffer=create_dummy_image(),
                    content_type="image/png",
                )
                for i in range(arts_count)
            ],
        },
    )
    assert len(manga.arts) == arts_count
    expected = {
        "id": str(manga.id),
        "arts": [
            {
                "id": str(art.id),
                "image": {
                    "url": await s3_mock.url(art.image.path.as_posix()),
                },
                "previewImage": {
                    "url": await s3_mock.url(art.preview_image.path.as_posix()),
                },
                "language": art.language.name.upper(),
                "volume": art.volume,
            }
            for art in manga.arts
        ],
    }
    assert response == _tpl(manga=expected)
