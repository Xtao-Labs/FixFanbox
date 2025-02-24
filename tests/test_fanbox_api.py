import pytest

from src.api.httpxrequest import HTTPXRequest
from src.api.fanbox import FanBoxApi


@pytest.mark.asyncio
class TestFanboxApi:
    @staticmethod
    async def test_fanbox_api():
        api = FanBoxApi(HTTPXRequest())
        user = await api.get_fanbox_user("miyuuu")
        print(user)
        post = await api.get_fanbox_post("9431597")
        print(post)
        post = await api.get_fanbox_post("9431591111")
        print(post)
