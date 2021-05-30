import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from smartcontract_interaction import *
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_KEY")

bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    first_name = State()
    second_name = State()
    third_name = State()
    benefits = State()
    documents = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.first_name.set()
    await message.answer("Привіт 👋 \n\n "
                         "🏠 Цей бот допоможе Вам зареєструватися в чергу до гуртожитку! \n\n"
                         "✔️Для заповнення заявки Ви маєте надати такі персональні дані: \n"
                         "<b>1.</b> Ім`я\n"
                         "<b>2.</b> Прізвище\n"
                         "<b>3.</b> По батькові\n"
                         "<b>4.</b> У яку чергу Вас записувати? (<b>пільгову</b> чи звичайну)\n"
                         "<b>5.</b> Документи для поселення в гуртожиток (бажано додати в архів дані заявки) 🧾 \n"
                         "\t\t<b>5.1</b> (Направлення на поселення (видане комісією з поселення)\n"
                         "\t\t<b>5.2</b> Заява на поселення\n"
                         "\t\t<b>5.3</b> Копія паспорта\n"
                         "\t\t<b>5.4</b> Копія ідентифікаційного коду\n"
                         "\t\t<b>5.5</b> Фотокартка 3 x 4 \n"
                         "\n"
                         "\n"
                         "Для перевірки прозорості всіх транзакцій використовується мережа "
                         "<code>Rinkeby Ethereum</code>\n"
                         "https://rinkeby.etherscan.io/address/0xcec0faa3dfbcdc5c6e3de6e5c5955a65245483fb",
                         parse_mode="HTML")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    await message.reply('Відмінено! ❌', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.second_name)
async def process_second_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text

    await Form.next()
    await message.reply("Введіть Ваше Прізвище: ")


@dp.message_handler(state=Form.third_name)
async def process_third_name(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(second_name=message.text)
    await message.reply("Введіть Ваше По Батькові: ")


@dp.message_handler(state=Form.benefits)
async def process_benefits(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(third_name=message.text)
    await message.reply("Введіть +, якщо Ви є іноземцем або студентом з пільгами: ")


@dp.message_handler(lambda message: "+" in message.text or "-" in message.text, state=Form.documents)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text == '-':
        await state.update_data(benefits=False)
    else:
        await state.update_data(benefits=True)

    async with state.proxy() as data:
        data['documents'] = message.document
        User().create_record(message.document, Form.first_name, Form.second_name, Form.third_name, Form.benefits)

    # Finish conversation
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
