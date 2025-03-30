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
    HEADER = "header"
    UNKNOWN = "unknown"


class FanboxPostBodyBlock(BaseModel):
    type: FanboxPostBodyBlockType = FanboxPostBodyBlockType.UNKNOWN
    raw_type: str = ""
    text: Optional[str] = None
    imageId: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def before(cls, values: Any) -> Any:
        old_type = values.get("type")
        if isinstance(old_type, FanboxPostBodyBlockType):
            values["raw_type"] = old_type.value
        else:
            values["raw_type"] = old_type
            try:
                values["type"] = FanboxPostBodyBlockType(values["raw_type"])
            except ValueError:
                values["type"] = FanboxPostBodyBlockType.UNKNOWN
        return values


class FanboxPostBodyImage(BaseModel):
    id: str
    extension: str = ""
    width: int = 0
    height: int = 0
    originalUrl: str = ""
    thumbnailUrl: str


class FanboxPostBody(BaseModel):
    blocks: Optional[List[FanboxPostBodyBlock]] = None
    imageMap: Optional[Dict[str, FanboxPostBodyImage]] = None
    text: Optional[str] = None


class FanboxPost(FanboxLitePost):
    body: Optional[FanboxPostBody] = None
    imageForShare: str
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


class KemonoPostInfo(BaseModel):
    id: str
    user: str
    title: str
    content: str


class KemonoPostPreview(BaseModel):
    type: Optional[str] = None
    server: Optional[str] = None
    name: str
    path: str
    content: bool = False

    @property
    def url(self) -> str:
        if self.content:
            return self.path
        return f"https://img.kemono.su/thumbnail/data" + self.path

    @classmethod
    def from_src(cls, src: url) -> "KemonoPostPreview":
        name = src.split("/")[-1]
        return cls(name=name, path=src, content=True)


class KemonoPost(BaseModel):
    post: KemonoPostInfo
    previews: List[KemonoPostPreview]
