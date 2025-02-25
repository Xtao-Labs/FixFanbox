from persica.factory.component import AsyncInitializingComponent

from src.api.httpxrequest import HTTPXRequest
from src.api.models import (
    KemonoPost,
    FanboxPost,
    FanboxPostBody,
    FanboxPostBodyBlock,
    FanboxPostBodyBlockType,
    FanboxPostBodyImage,
)
from src.log import logger


class KemonoApi(AsyncInitializingComponent):
    def __init__(self, httpx_request: HTTPXRequest):
        self.request = httpx_request

    async def get_kemono_user_post(self, user: str, post: str) -> KemonoPost:
        route = f"https://kemono.su/api/v1/fanbox/user/{user}/post/{post}"
        req = await self.request.client.get(route)
        assert req.status_code == 200
        return KemonoPost(**req.json())

    @staticmethod
    def parse_kemono_post(post: KemonoPost) -> FanboxPostBody:
        blocks = []
        image_maps = {}
        if post.post.content:
            for p in post.post.content.split("\n"):
                blocks.append(
                    FanboxPostBodyBlock(type=FanboxPostBodyBlockType.P, text=p)
                )
        if post.previews:
            for preview in post.previews:
                blocks.append(
                    FanboxPostBodyBlock(
                        type=FanboxPostBodyBlockType.IMAGE, imageId=preview.name
                    )
                )
                image_maps[preview.name] = FanboxPostBodyImage(
                    id=preview.name, thumbnailUrl=preview.url
                )
        return FanboxPostBody(blocks=blocks, imageMap=image_maps)

    async def patch_post_info(self, post: FanboxPost) -> FanboxPost:
        if not post.feeRequired:
            return post
        user = post.user.userId
        try:
            kemono_post = await self.get_kemono_user_post(user, post.id)
        except AssertionError:
            logger.warning(f"Kemono post not found for {user}/{post.id}")
            return post
        post.body = self.parse_kemono_post(kemono_post)
        logger.info(f"Patched post info for {user}/{post.id}")
        return post
