"""A shared password for the site."""

import hmac

from flask import Flask, Response, current_app, request

REALM = "CDPP"


def init_app(app: Flask) -> None:
    app.before_request(require_password)


def require_password() -> Response | None:
    """Refuse a request that does not give the password in PASSWORD.

    If PASSWORD is not set, all requests continue. The browser asks for a user
    name and a password. The user name can be any text.
    """
    password = current_app.config.get("PASSWORD")
    if not password:
        return None
    credentials = request.authorization
    if (
        credentials is not None
        and credentials.type == "basic"
        and credentials.password is not None
        and hmac.compare_digest(credentials.password.encode(), password.encode())
    ):
        return None
    return Response(
        "Enter the password for this site.",
        401,
        {"WWW-Authenticate": f'Basic realm="{REALM}", charset="UTF-8"'},
        mimetype="text/plain",
    )
