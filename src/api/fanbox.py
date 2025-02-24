from persica.factory.component import AsyncInitializingComponent

from src.api.httpxrequest import HTTPXRequest
from src.api.models import FanboxUser, FanboxPost


class FanBoxApi(AsyncInitializingComponent):
    FANBOX_HEADERS = {
        "authority": "api.fanbox.cc",
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,zh-Hans;q=0.8,und;q=0.7,en;q=0.6,zh-Hant;q=0.5,ja;q=0.4",
        "dnt": "1",
        "origin": "https://www.fanbox.cc",
        "referer": "https://www.fanbox.cc/",
        "sec-ch-ua": '"Chromium";v="108", "Not?A_Brand";v="8"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
        "Safari/537.36",
    }
    FANBOX_USER_API = "https://api.fanbox.cc/creator.get"
    FANBOX_POST_API = "https://api.fanbox.cc/post.info"

    def __init__(self, httpx_request: HTTPXRequest):
        self.request = httpx_request

    async def get_fanbox_user(self, username: str) -> FanboxUser:
        params = {
            "creatorId": username,
        }
        req = await self.request.client.get(
            self.FANBOX_USER_API,
            params=params,
            headers=self.FANBOX_HEADERS,
        )
        assert req.status_code == 200
        return FanboxUser(**(req.json()["body"]))

    async def get_fanbox_post(self, post_id: str) -> FanboxPost:
        params = {
            "postId": post_id,
        }
        req = await self.request.client.get(
            self.FANBOX_POST_API,
            params=params,
            headers=self.FANBOX_HEADERS,
        )
        assert req.status_code == 200
        return FanboxPost(**(req.json()["body"]))
