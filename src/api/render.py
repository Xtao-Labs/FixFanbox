from persica.factory.component import AsyncInitializingComponent

from src import template_env
from src.api.fanbox import FanBoxApi
from src.api.models import FanboxPost, FanboxPostBodyBlockType
from src.error import ArticleNotFoundError


class RenderArticle(AsyncInitializingComponent):
    def __init__(self, fanbox_api: FanBoxApi):
        self.fanbox_api = fanbox_api
        self.template = template_env.get_template("article.jinja2")

    async def get_post_info(self, post_id: str):
        try:
            return await self.fanbox_api.get_fanbox_post(post_id)
        except AssertionError:
            raise ArticleNotFoundError(post_id)

    @staticmethod
    def parse_content(post_info: "FanboxPost") -> str:
        text = ""
        data = post_info.body
        if not data:
            return text
        if data.blocks:
            for item in data.blocks:
                if item.type is FanboxPostBodyBlockType.P:
                    text += f"<p>{item.text}</p><br/>\n"
                elif item.type is FanboxPostBodyBlockType.IMAGE:
                    text += f'<img src="{data.imageMap[item.imageId].thumbnailUrl}"/><br/>\n'
                elif item.type is FanboxPostBodyBlockType.HEADER:
                    text += f"<h2>{item.text}</h2><br/>\n"
        elif data.text:
            text += f"<p>{data.text}</p><br/>\n"
        return text

    async def process_article_text(self, post_info: "FanboxPost") -> str:
        data = {
            "published_time": post_info.create_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "channel": "shota_audio",
            "post": post_info,
            "author": post_info.user,
        }
        content = self.parse_content(post_info)
        return self.template.render(
            description=post_info.excerpt.strip(),
            article=content,
            **data,
        )

    async def process_article(self, post_id: str) -> str:
        post_info = await self.get_post_info(post_id)
        return await self.process_article_text(post_info)
