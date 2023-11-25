import aiohttp
import asyncio
import re
from os import getenv
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

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

    def save_message(self, result: dict):
        user_message = UserMessage(result['message'])
        f_name = user_message.from_user.First_name.lower().strip()

        if self.save_messages_users.get(f_name) is None:
            self.save_messages_users[f_name] = []

        elif len(self.save_messages_users[f_name]) >= 15:
            self.save_messages_users[f_name].clear()

        self.save_messages_users[f_name].append(user_message)

    async def save_updates_messages(self) -> dict:
        async with aiohttp.ClientSession() as session:
            while True:
                if self.__cancel:
                    return

                async with session.get(f'{self.API_BOT_URL}/getUpdates?offset={self._offset + 1}') as response:
                    data = await response.json()
                    if data['result']:

                        for update_message in data['result']:
                            self._offset = update_message['update_id']
                            self.save_message(update_message)

    async def send_message_in_chat(self, msg: str, chat_id: str) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.API_BOT_URL}/sendMessage?chat_id={chat_id}&text={msg}') as response:
                data = await response.json()
                return data['ok']

    def print_all_messages_bot(self):
        print('<---------------->')
        it = 0
        for user, messages in self.save_messages_users.items():
            print(f'{user} -> {", ".join(map(lambda a: f"| {a.text} |", messages))}')
            it += 1
        if not it:
            print(" " + 'Пусто'.center(16, '-'))
        print('<---------------->')

    def print_help_command(self):
        print('bot-msgs -> Сообщения которые отправили для бота.')
        print('help -> Помощь по командам.')
        print('send | to=ник | text=<текст в <>> -> Отправить сообщение в чат к пользователю.')
        print('exit -> прекратить работу.')

    def give_user_messages(self, user: str):
        return self.save_messages_users.get(user.lower().strip())

    async def start(self, loop: asyncio.AbstractEventLoop) -> asyncio.Task:
        return loop.create_task(self.save_updates_messages())

    def stop(self):
        self.__cancel = True


def get_send_command_text(input_string):
    text = re.match(r'text=<(.*)>', input_string)
    if text:
        extracted_text = text.group(1)

        if extracted_text:

            extracted_text = extracted_text.replace("&lt;", "<").replace("&gt;", ">")
            return extracted_text.strip()

BOT_TOKEN = getenv('BOT_TOKEN')

async def main():
    loop = asyncio.get_running_loop()
    bot = TelegramBot(BOT_TOKEN)
    starting = True
    await bot.start(loop)

    while True:
        inp = await loop.run_in_executor(None, input, f'{"(напишите help)" if starting else ""}==> ')
        lst = list(map(lambda a: a.lower().strip(), inp.split('|')))

        try:
            command = lst[0]
        except IndexError:
            continue

        try:

            to = lst[1][3:]
            text = get_send_command_text(lst[2])
            if not text:
                raise Exception

        except Exception:

            to = None
            text = None

        match command:

            case 'exit':
                bot.stop()
                break

            case 'help':
                starting = False
                bot.print_help_command()

            case 'send':
                starting = False
                if None in (to, text):
                    print('Неверно написана команда. Напишите help')
                    continue

                user_msgs = bot.give_user_messages(to)
                if not user_msgs:
                    print('Такой пользователь не отправлял вам сообщений.')
                    continue

                await bot.send_message_in_chat(msg=text, chat_id=user_msgs[0].chat.Id)

            case 'bot-msgs':
                starting = False
                bot.print_all_messages_bot()

if __name__ == '__main__':
    asyncio.run(main())