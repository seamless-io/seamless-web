# I made the logic based on this tutorial
# https://auth0.com/docs/quickstart/core/python/01-authorization#validate-access-tokens
import json
import urllib.request
from functools import wraps

import jwt
from flask import request, _request_ctx_stack  # type: ignore
from jwt.algorithms import RSAAlgorithm

import config

ALGORITHMS = ["RS256"]


class CoreAuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header(req):
    """Obtains the Access Token from the Authorization Header
    """
    auth = req.headers.get("Authorization", None)
    if not auth:
        raise CoreAuthError({"code": "authorization_header_missing",
                             "description":
                                 "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise CoreAuthError({"code": "invalid_header",
                             "description":
                                 "Authorization header must start with"
                                 " Bearer"}, 401)
    elif len(parts) == 1:
        raise CoreAuthError({"code": "invalid_header",
                             "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise CoreAuthError({"code": "invalid_header",
                             "description":
                                 "Authorization header must be"
                                 " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header(request)
        with urllib.request.urlopen(config.AUTH0_BASE_URL + "/.well-known/jwks.json") as url:
            jwks = json.loads(url.read().decode())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = RSAAlgorithm.from_jwk(json.dumps(key))
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=config.AUTH0_WEB_API_AUDIENCE,
                    issuer=config.AUTH0_BASE_URL + "/"
                )
            except jwt.ExpiredSignatureError:
                raise CoreAuthError({"code": "token_expired",
                                     "description": "token is expired"}, 401)
            except jwt.MissingRequiredClaimError:
                raise CoreAuthError({"code": "invalid_claims",
                                     "description":
                                         "incorrect claims,"
                                         "please check the audience and issuer"}, 401)
            except Exception as e:
                raise CoreAuthError({"code": "invalid_header",
                                     "description": str(e)}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise CoreAuthError({"code": "invalid_header",
                             "description": "Unable to find appropriate key"}, 401)

    return decorated
