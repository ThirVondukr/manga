from starlette.responses import Response

from app.core.domain.auth.dto import TokenWrapper


def set_cookie(
    response: Response,
    token: TokenWrapper,
    cookie_name: str,
) -> None:
    response.set_cookie(
        key=cookie_name,
        value=token.token,
        httponly=True,
        expires=token.claims.exp,
        secure=True,
        samesite="strict",
    )
