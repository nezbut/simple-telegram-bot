import aiohttp
import asyncio
from dataclasses import dataclass
import exception


class BotCommand:

    def __init__(self, message, bot, command_name: str) -> None:
        self.message: UserMessage = message
        self.bot: TelegramBot = bot
        self.command_name = command_name.strip()

    async def send_message(self, message: str):
        try:
            return await self.bot.send_message_in_chat(
                msg=message.strip(),
                chat_id=self.message.chat.Id
                )

        except Exception:
            return False

    async def send_photo(self, link):
        try:

            return await self.bot.send_photo_in_chat(
                link_photo=link,
                chat_id=self.message.chat.Id
            )

        except Exception:
            return False

# Class Message
class UserMessage:

    @dataclass
    class From:
        Id: str
        Is_bot: str
        First_name: str
        Username: str
        Language_code: str

    @dataclass
    class Chat:
        Id: str
        Iirst_name: str
        Username: str
        Type_chat: str

    def __init__(self, message: dict) -> None:
        self.message_id: str = str(message['message_id'])
        txt = message.get('text')
        self.text: str = txt if txt else "Пользователь отправил фотографию."

        self.from_user = self.From(
            str(message['from']['id']),
            str(message['from']['is_bot']),
            str(message['from']['first_name']),
            str(message['from']['username']),
            str(message['from']['language_code'])
        )

        self.chat = self.Chat(
            str(message['chat']['id']),
            str(message['chat']['first_name']),
            str(message['chat']['username']),
            str(message['chat']['type']),
        )

    def __repr__(self) -> str:
        return f"{self.from_user.Username}Message({self.text})"

# Main Class Bot
class TelegramBot:

    def __init__(self, token: str) -> None:
        self.__token = token
        self.API_BOT_URL = f"https://api.telegram.org/bot{self.__token}"
        self._offset = -2
        self.__cancel = False
        self.save_messages_users: dict[str, list[UserMessage]] = {}
        self.commands_handler: dict[str, function] = {}
        self.commands_aliases: dict[str, tuple[str]] = {}

    def save_message(self, result: dict):
        if result.get('message'):
            user_message = UserMessage(result['message'])
            f_name = user_message.from_user.First_name.lower().strip()

            if self.save_messages_users.get(f_name) is None:
                self.save_messages_users[f_name] = []

            elif len(self.save_messages_users[f_name]) >= 20:
                self.save_messages_users[f_name].clear()

            self.save_messages_users[f_name].append(user_message)
            return user_message

    async def call_function_command(self, msg: UserMessage):
        command_name = msg.text[1:].lower().strip()
        func_command = self.commands_handler.get(command_name)

        if func_command is not None:
            command = BotCommand(
                message=msg,
                bot=self,
                command_name=command_name
            )

            await func_command(command)
            return

        for aliases_cmd in self.commands_aliases:
            if command_name in aliases_cmd:

                command = BotCommand(
                    message=msg,
                    bot=self,
                    command_name=command_name
                )

                func_command = self.commands_handler.get(self.commands_aliases[aliases_cmd])

                await func_command(command)
                return

    async def save_updates_messages_and_call_commands(self) -> dict:
        async with aiohttp.ClientSession() as session:
            while True:
                if self.__cancel:
                    return

                async with session.get(f'{self.API_BOT_URL}/getUpdates?offset={self._offset + 1}') as response:
                    data = await response.json()

                    if data.get('result'):

                        for update_message in data['result']:
                            self._offset = update_message['update_id']

                            if update_message.get('message'):
                                msg = self.save_message(update_message)
                                await self.call_function_command(msg=msg)

    async def send_message_in_chat(self, msg: str, chat_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.API_BOT_URL}/sendMessage?chat_id={chat_id}&text={msg}') as response:
                data = await response.json()
                return data['ok']

    async def send_photo_in_chat(self, link_photo: str, chat_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.API_BOT_URL}/sendPhoto?chat_id={chat_id}&photo={link_photo}') as response:
                data = await response.json()
                return data['ok']

    def command(self, name: str | None = None, aliases: tuple | None = None):

        def decorator(func):

            if not func.__code__.co_varnames:
                raise exception.MinimumOneArgument

            fname = name or func.__name__
            fname = fname.lower().strip()

            if self.commands_handler.get(fname) is not None:
                raise exception.CommandExists

            if not asyncio.iscoroutinefunction(func):
                raise exception.CommandIsNotCoroutine

            if isinstance(aliases, tuple):

                if aliases:
                    self.commands_aliases[tuple(set(filter(lambda a: a not in self.commands_handler, aliases)))[:10]] = fname

            self.commands_handler[fname] = func

        return decorator

    @property
    def give_all_messages(self):
        return self.save_messages_users

    def give_user_messages(self, user: str):
        return self.save_messages_users.get(user.lower().strip())

    async def start(self, loop: asyncio.AbstractEventLoop) -> asyncio.Task:
        return loop.create_task(self.save_updates_messages_and_call_commands())

    def stop(self):
        self.__cancel = True

__all__ = (
    'TelegramBot',
    'UserMessage'
)