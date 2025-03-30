import re
from typing import List, Dict

from persica.factory.component import AsyncInitializingComponent

from src.api.httpxrequest import HTTPXRequest
from src.api.models import (
    KemonoPost,
    FanboxPost,
    FanboxPostBody,
    FanboxPostBodyBlock,
    FanboxPostBodyBlockType,
    FanboxPostBodyImage,
    KemonoPostPreview,
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
    def extract_img_src_and_clean_p(p_content: str):
        """
        使用正则表达式提取 p 标签中的 img src 并返回清理后的 p 标签

        参数:
            p_content (str): 包含 p 标签的 HTML 字符串

        返回:
            tuple: (img_src_list, cleaned_p_content)
                img_src_list: 所有 img 标签的 src 属性列表
                cleaned_p_content: 去除 img 标签后的 p 标签 HTML 字符串
        """
        # 正则表达式匹配 img 标签及其 src 属性
        img_pattern = re.compile(r'<img\s+[^>]*src=(["\'])(.*?)\1[^>]*>', re.IGNORECASE)

        # 查找所有匹配的 img 标签并提取 src
        img_matches = img_pattern.finditer(p_content)
        img_src_list = [match.group(2) for match in img_matches]

        # 移除所有 img 标签
        cleaned_p = img_pattern.sub("", p_content)

        return img_src_list, cleaned_p

    @staticmethod
    def parse_kemono_post_preview(
        preview: KemonoPostPreview,
        blocks: List["FanboxPostBodyBlock"],
        image_maps: Dict[str, "FanboxPostBodyImage"],
    ) -> None:
        blocks.append(
            FanboxPostBodyBlock(
                type=FanboxPostBodyBlockType.IMAGE, imageId=preview.name
            )
        )
        image_maps[preview.name] = FanboxPostBodyImage(
            id=preview.name, thumbnailUrl=preview.url
        )

    @staticmethod
    def parse_kemono_post(post: KemonoPost) -> FanboxPostBody:
        blocks = []
        image_maps = {}
        if post.post.content:
            for p in post.post.content.split("\n"):
                img_src_list, cleaned_p = KemonoApi.extract_img_src_and_clean_p(p)
                blocks.append(
                    FanboxPostBodyBlock(type=FanboxPostBodyBlockType.P, text=cleaned_p)
                )
                for img_src in img_src_list:
                    KemonoApi.parse_kemono_post_preview(
                        KemonoPostPreview.from_src(img_src), blocks, image_maps
                    )
        if post.previews:
            for preview in post.previews:
                KemonoApi.parse_kemono_post_preview(preview, blocks, image_maps)
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
