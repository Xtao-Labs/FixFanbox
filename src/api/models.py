import datetime
import enum
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, model_validator


class FanboxLiteUser(BaseModel):
    name: str
    userId: str
    iconUrl: Optional[str]


class FanboxUser(BaseModel):
    coverImageUrl: Optional[str]
    creatorId: str
    description: str
    hasAdultContent: bool
    user: FanboxLiteUser

    @property
    def url(self) -> str:
        return f"https://{self.creatorId}.fanbox.cc"

    @property
    def kemono_url(self) -> str:
        return f"https://kemono.su/fanbox/user/{self.user.userId}"

    @property
    def name(self) -> str:
        return f"🔞 {self.user.name}" if self.hasAdultContent else self.user.name

    @property
    def text(self) -> str:
        return (
            f"<b>Fanbox User Info</b>\n\n"
            f"Name: <code>{self.user.name}</code>\n"
            f'Username: <a href="{self.url}">{self.creatorId}</a>\n'
            f"Bio: <code>{self.description.strip()}</code>"
        )


class FanboxLitePost(BaseModel):
    id: str
    publishedDatetime: str
    title: str

    @property
    def create_time(self) -> datetime.datetime:
        # 2022-10-05T20:21:19+09:00
        jp_time = datetime.datetime.strptime(
            self.publishedDatetime, "%Y-%m-%dT%H:%M:%S%z"
        )
        cn_time = jp_time.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
        return cn_time


class FanboxPostBodyBlockType(str, enum.Enum):
    P = "p"
    IMAGE = "image"
    UNKNOWN = "unknown"


class FanboxPostBodyBlock(BaseModel):
    type: FanboxPostBodyBlockType
    raw_type: str
    text: Optional[str] = None
    imageId: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def before(cls, values: Any) -> Any:
        values["raw_type"] = values.pop("type")
        try:
            values["type"] = FanboxPostBodyBlockType(values["raw_type"])
        except ValueError:
            values["type"] = FanboxPostBodyBlockType.UNKNOWN
        return values


class FanboxPostBodyImage(BaseModel):
    id: str
    extension: str
    width: int
    height: int
    originalUrl: str
    thumbnailUrl: str


class FanboxPostBody(BaseModel):
    blocks: List[FanboxPostBodyBlock]
    imageMap: Dict[str, FanboxPostBodyImage]


class FanboxPost(FanboxLitePost):
    body: Optional[FanboxPostBody] = None
    coverImageUrl: Optional[str]
    creatorId: str
    excerpt: str
    feeRequired: int
    likeCount: int
    user: FanboxLiteUser
    nextPost: Optional[FanboxLitePost] = None
    prevPost: Optional[FanboxLitePost] = None

    @property
    def user_url(self) -> str:
        return f"https://{self.creatorId}.fanbox.cc/"

    @property
    def url(self) -> str:
        return f"{self.user_url}posts/{self.id}"

    @property
    def kemono_url(self) -> str:
        return f"https://kemono.su/fanbox/user/{self.user.userId}/post/{self.id}"

    @property
    def stat(self) -> str:
        return f"❤️ {self.likeCount}・{self.feeRequired} 日元"

    @property
    def text(self) -> str:
        return (
            f"<b>Fanbox Post Info</b>\n\n"
            f"<code>{self.excerpt.strip()}</code>\n\n"
            f'<a href="{self.user_url}">{self.user.name}</a> 发表于 {self.create_time}\n'
            f"❤️ {self.likeCount}・{self.feeRequired} 日元"
        )
