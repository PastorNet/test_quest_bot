import logging
import requests
import os
from aiogram import Bot, Dispatcher, executor, types
from config import Configuration
from dbcontroller import DbController, datetime
import matplotlib.pyplot as plt
import asyncio

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Configuration.TOKEN)
dp = Dispatcher(bot)
dbcontroller_ = DbController(Configuration.DB_NAME)


async def load_rate_from_api() -> dict:
    return dict(dict(requests.get(Configuration.API + 'latest', params={'base': 'USD'}).json()).get('rates'))


async def load_history_from_api(key: str) -> dict:
    return dict(dict(requests.get(Configuration.API + 'history',
                                  params={'base': 'USD',
                                          'start_at': datetime.datetime.now().date() - datetime.timedelta(days=7),
                                          'end_at': datetime.datetime.now().date(),
                                          'symbols': key}).json()).get('rates'))


@dp.message_handler(commands=['lst', 'list'])
async def get_last_rates(msg: types.Message):
    currentTime = datetime.datetime.now()
    answer = 'Rates:\n\n'
    if currentTime - dbcontroller_.last_update_date > datetime.timedelta(seconds=10):
        response = await load_rate_from_api()
        if not dbcontroller_.inited:
            dbcontroller_.insert(response)
        else:
            dbcontroller_.update(response)

    else:

        dbcontroller_.select()
        response = dbcontroller_.response_state

    if response:
        for key in response.keys():
            answer += f'{key}: {round(response.get(key), 2)}\n'
        await msg.answer(answer)

    elif dbcontroller_.errlog:
        await msg.answer(f'Error with database. Trying manual request...')
        print(dbcontroller_.errlog)

    else:
        await msg.answer('Try later..')


@dp.message_handler(commands=['exchange'])
async def exchange(msg: types.Message):
    currentTime = datetime.datetime.now()
    splitted = msg.text.upper().split(' ')
    count, key = float(splitted[1]), splitted[4]

    if currentTime - dbcontroller_.last_update_date > datetime.timedelta(seconds=10):
        response = await load_rate_from_api()
        if not dbcontroller_.inited:
            dbcontroller_.insert(response)
        else:
            dbcontroller_.update(response)

    dbcontroller_.select(key=key)

    response = dbcontroller_.response_state

    await msg.answer(f'{round(response.get(key) * count,2)} {key}')


@dp.message_handler(commands=['history'])
async def history(msg: types.Message):
    name = msg.text.split(' ')[1].upper()
    response = {}
    try:
        response = await load_history_from_api(name)
    except Exception as e:
        await msg.answer('No exchange rate data is available for the selected currency.')
    if response:
        fig, ax = plt.subplots()
        ax.plot(list(response.keys()), [round(x.get(name),2) for x in response.values()])
        plt.title('Rates')
        ax.set_xlabel('Date', fontsize=15, color='red')

        ax.set_ylabel(f'{name} Rate', fontsize=15, color='red')

        plt.savefig('temp.png')
        while not os.path.exists('temp.png'):

            await asyncio.sleep(1)
        else:
            with open('temp.png', 'rb') as file:
                await msg.answer_photo(file)
            os.remove('temp.png')


@dp.message_handler(commands=['start', 'help'])
async def help(msg: types.Message):
    await msg.answer(Configuration.HELP_MESSAGE)


executor.start_polling(dp, skip_updates=True)
