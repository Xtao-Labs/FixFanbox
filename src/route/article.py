from persica.factory.component import AsyncInitializingComponent
from starlette.requests import Request
from starlette.responses import HTMLResponse

from .base import get_redirect_response

from src.core.web_app import WebApp
from src.error import ArticleError, ResponseException
from src.log import logger
from ..api.render import RenderArticle


class ArticlePlugin(AsyncInitializingComponent):
    def __init__(self, web_app: WebApp, render: RenderArticle):
        self.render = render
        web_app.app.add_api_route("/@{username}/posts/{post_id}", self.parse_article)
        web_app.app.add_api_route("/posts/{post_id}", self.parse_article)
        web_app.app.add_api_route(
            "/@{username}/posts/{post_id}/json", self.parse_article_json
        )
        web_app.app.add_api_route("/posts/{post_id}/json", self.parse_article_json)

    async def parse_article(self, post_id: str, request: Request):
        try:
            return HTMLResponse(await self.render.process_article(post_id))
        except ResponseException as e:
            logger.warning(e.message)
            return get_redirect_response(request)
        except ArticleError as e:
            logger.warning(e.msg)
            return get_redirect_response(request)
        except Exception as _:
            logger.exception("Failed to get article post_id[%s]", post_id)
            return get_redirect_response(request)

    async def parse_article_json(self, post_id: str, request: Request):
        try:
            return await self.render.get_post_info(post_id)
        except ArticleError as e:
            logger.warning(e.msg)
            return get_redirect_response(request)
        except Exception as _:
            logger.exception("Failed to get article post_id[%s]", post_id)
            return get_redirect_response(request)
