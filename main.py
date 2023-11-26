from telegram_bot import TelegramBot, BotCommand
from api_numbers import request_to_numbers_api
from animals_photos import RandomPhotoAnimal
from random import randint
from os import getenv
from dotenv import load_dotenv
import asyncio

load_dotenv()

bot = TelegramBot(getenv('BOT_TOKEN'))
random_photos_animals = RandomPhotoAnimal()

@bot.command(name='hi', aliases=('hello',))
async def command(cmd: BotCommand):
    await cmd.send_message(f'Привет {cmd.message.from_user.First_name}')

@bot.command(name='cats', aliases=('dogs', 'foxs'))
async def command_random_photo_cats(cmd: BotCommand):
    await cmd.send_photo(await random_photos_animals.request(cmd.command_name))

@bot.command(name='randomnum', aliases=('rnum',))
async def command_random_description_number(cmd: BotCommand):
    num = str(randint(1, 1_000_000))
    await cmd.send_message(await request_to_numbers_api(num))

async def main():
    loop = asyncio.get_running_loop()
    await bot.start(loop=loop)

    await loop.run_in_executor(None, input, 'Нажмите пробел чтобы завершить работу\n')

    bot.stop()

if __name__ == "__main__":
    asyncio.run(main())