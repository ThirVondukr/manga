from tests.adapters.graphql.client import GraphQLResponseData


def assert_not_authenticated(response: GraphQLResponseData) -> None:
    assert "errors" in response
    assert any(
        err["extensions"]["code"] == "UNAUTHORIZED"
        for err in response["errors"]
    )
