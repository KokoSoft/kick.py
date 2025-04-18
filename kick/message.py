from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from .object import HTTPDataclass
from .users import PartialUser, User
from .utils import cached_property

if TYPE_CHECKING:
    from .chatroom import Chatroom, PartialChatroom
    from .types.message import PartialAuthorPayload, AuthorPayload, MessagePayload, MessageDeletedPayload, MessagePinPayload, ReplyMetaData, UserBannedPayload, UserUnbannedPayload

__all__ = ("PartialAuthor", "Author", "Message", "PartialMessage", "MessageDeletedEventData", "PinnedMessage", "UserBannedEventData", "UserUnbannedEventData")


class PartialAuthor(HTTPDataclass["PartialAuthorPayload"]):
    """
    Represents the partial author of a message on kick

    Attributes
    -----------
    id: int
        The author's id
    slug: str
        The author's slug
    username: str
        The author's username
    """

    @property
    def id(self) -> int:
        """
        The author's id
        """

        return self._data["id"]

    @property
    def slug(self) -> str:
        """
        The author's slug
        """

        return self._data["slug"]
    
    @property
    def username(self) -> str:
        """
        The author's username
        """

        return self._data["username"]

    async def to_user(self) -> User:
        """
        |coro|

        Fetches a user object for the author

        Raises
        -----------
        `HTTPException`
            Fetching the user failed
        `NotFound`
            User Not Found

        Returns
        -----------
        `User`
            The user
        """

        return await self.http.client.fetch_user(self.slug)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __str__(self) -> str:
        return self.slug

    def __repr__(self) -> str:
        return f"<PartialAuthor id={self.id!r} slug={self.slug!r}>"

class Author(PartialAuthor, HTTPDataclass["AuthorPayload"]):
    """
    Represents the author of a message on kick

    Attributes
    -----------
    id: int
        The author's id
    slug: str
        The author's slug
    username: str
        The author's username
    color: str
        The authors... color?
    badges: list
        Unknown
    """

    @property
    def color(self) -> str:
        """
        The authors... color?
        """

        return self._data["identity"]["color"]

    @property
    def badges(self) -> list:
        """THIS IS RAW DATA"""
        return self._data["identity"]["badges"]

    def __repr__(self) -> str:
        return f"<Author id={self.id!r} slug={self.slug!r}>"


class PartialMessage(HTTPDataclass["ReplyMetaData"]):
    """
    This represents a partial message. Mainly used as the message someone is replying too.

    Attributes
    -----------
    id: str
        The message's id
    content: str
        The message's content
    author: `PartialUser`
        The message's author
    """

    @property
    def id(self) -> str:
        """
        The message's id
        """

        return self._data["original_message"]["id"]

    @property
    def content(self) -> str:
        """
        The message's content
        """

        return self._data["original_message"]["content"]

    @cached_property
    def author(self) -> PartialUser:
        """
        The message's author
        """

        return PartialUser(
            id=int(self._data["original_sender"]["id"]),
            username=self._data["original_sender"]["username"],
            http=self.http,
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return f"<Message id={self.id!r} author={self.author!r}>"


class Message(HTTPDataclass["MessagePayload"]):
    """
    Represents a message sent on kick

    Attributes
    -----------
    id: str
        the message's id
    is_reply: bool
        If the message is replying to any message
    references: `PartialMessage` | None
        If the message is replying to a message, a `PartialMessage` object is returned. Otherwise None
    chatroom_id: int
        The id of the chatroom the message was sent in
    chatroom: `Chatroom` | None
        The chatroom the message was sent in.
    content: str
        The message's content
    created_at: datetime.datetime
        When the message was sent
    author: `Author`
        The message's author
    """

    @property
    def id(self) -> str:
        """
        the message's id
        """

        return self._data["id"]

    @cached_property
    def is_reply(self) -> bool:
        """
        If the message is replying to any message
        """

        return bool(self._data.get("metadata"))

    @cached_property
    def references(self) -> PartialMessage | None:
        """
        If the message is replying to a message, a `PartialMessage` object is returned. Otherwise None
        """

        data = self._data.get("metadata")
        if not data:
            return
        return PartialMessage(data=data, http=self.http)

    @property
    def chatroom_id(self) -> int:
        """
        The id of the chatroom the message was sent in
        """

        return self._data["chatroom_id"]

    @property
    def chatroom(self) -> Chatroom | PartialChatroom | None:
        """
        The chatroom the message was sent in.
        """

        return self.http.client.get_chatroom(self.chatroom_id)

    @property
    def content(self) -> str:
        """
        The message's content
        """

        return self._data["content"]

    @cached_property
    def created_at(self) -> datetime:
        """
        When the message was sent
        """

        return datetime.fromisoformat(self._data["created_at"])

    @cached_property
    def author(self) -> Author:
        """
        The message's author
        """

        return Author(data=self._data["sender"], http=self.http)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return f"<Message id={self.id!r} chatroom={self.chatroom_id!r} author={self.author!r}>"

class MessageDeletedEventData(HTTPDataclass["MessageDeletedPayload"]):
    """
    Represents a delete message event

    Attributes
    -----------
    id: str
        the event id
    message_id: str
        the message's id
    ai_moderated: bool
        If the message was moderated by ai
    violated_rules: [?]
        the list of violated rules
    chatroom: `Chatroom` | None
        The chatroom the message was sent in.
    """
    @property
    def id(self) -> str:
        """
        the event id
        """

        return self._data["id"]

    @property
    def message_id(self) -> str:
        """
        the message's id
        """

        return self._data["message"]["id"]

    @cached_property
    def ai_moderated(self) -> bool:
        """
        If the message was moderated by ai
        """

        return bool(self._data.get("aiModerated"))

    @property
    def violated_rules(self) -> list:
        """
        the list of violated rules
        """

        return self._data.get("violatedRules")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return f"<MessageDeletedEventData id={self.id!r} message_id={self.message_id!r}>"

class PinnedMessage(HTTPDataclass["MessagePinPayload"]):
    """
    Represents a pin message event

    Attributes
    -----------
    message: Message
        Pinned message
    duration: int
        Duration of message pin
    pinned_by: `Author`
        Who pin the message
    """

    @cached_property
    def message(self) -> Message:
        """
        Pinned message
        """
        return Message(data=self._data["message"], http=self.http)

    @cached_property
    def duration(self) -> int:
        """
        Duration of message pin
        """

        return int(self._data["duration"])

    @cached_property
    def pinned_by(self) -> Author:
        """
        Who pin the message
        """
        return Author(data=self._data["pinnedBy"], http=self.http)

    def __repr__(self) -> str:
        return f"<PinnedMessage message={self.message!r} duration={self.duration!r} pinned_by={self.pinned_by!r}>"


class UserBannedEventData(HTTPDataclass["UserBannedPayload"]):
    """
    Represents a user banned event data

    Attributes
    -----------
    id: str
        the event's id
    user: `PartialAuthor`
        The banned user
    banned_by: `PartialAuthor`
        Member who banned the user
    is_permanent: bool
        If ban is permanent
    """

    @property
    def id(self) -> str:
        """
        the message's id
        """

        return self._data["id"]

    @cached_property
    def is_permanent(self) -> bool:
        """
        If ban is permanent
        """

        return bool(self._data.get("permanent"))

    @cached_property
    def user(self) -> Author:
        """
        The banned user
        """

        return PartialAuthor(data=self._data["user"], http=self.http)

    @cached_property
    def banned_by(self) -> Author:
        """
        Member who banned the user
        """

        return PartialAuthor(data=self._data["banned_by"], http=self.http)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return f"<UserBannedEventData banned={self.user!r} by={self.banned_by!r}>"


class UserUnbannedEventData(HTTPDataclass["UserUnbannedPayload"]):
    """
    Represents a user unbanned event data

    Attributes
    -----------
    id: str
        the event's id
    user: `PartialAuthor`
        The unbanned user
    unbanned_by: `PartialAuthor`
        Member who banned the user / Member who unbanned the user ??
    is_permanent: bool
        If ban was permanent / If unban is permanent ??
    """

    @property
    def id(self) -> str:
        """
        the message's id
        """

        return self._data["id"]

    @cached_property
    def is_permanent(self) -> bool:
        """
        If ban was permanent / If unban is permanent ??
        """

        return bool(self._data.get("permanent"))

    @cached_property
    def user(self) -> Author:
        """
        The banned user
        """

        return PartialAuthor(data=self._data["user"], http=self.http)

    @cached_property
    def unbanned_by(self) -> Author:
        """
        Member who banned the user / Member who unbanned the user ??
        """

        return PartialAuthor(data=self._data["unbanned_by"], http=self.http)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and other.id == self.id

    def __repr__(self) -> str:
        return f"<UserUnbannedEventData unbanned={self.user!r} by={self.unbanned_by!r}>"
