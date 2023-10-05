#!venv/bin/python
import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from config import bot, dp, client_manager_password, god_password
import json
import os
import asyncio
import helpers
from helpers import *



class HandleClient(StatesGroup):
    waiting_for_name = State()
    waiting_for_number = State()
    waiting_for_email = State()


async def start(message: types.Message):
    god = await read_god_by_id(str(message.chat.id))
    print(god)
    if god.id == -1:
        await message.answer(
            'Привет! Я бот Алгоритмики, и я помогу вам оставить заявку в нашу школу. Давайте знакомиться. \nКак вас зовут?')
        await HandleClient.waiting_for_name.set()


async def name(message: types.Message, state: FSMContext):
    name = (message.text[0].upper() + message.text[1:].lower()).strip()
    await state.update_data(name=name)
    await message.answer('Очень приятно! Осталось пару шагов  Напишите номер телефона для связи.')
    await HandleClient.next()


async def number(message: types.Message, state: FSMContext):
    number = message.text.lower().strip()
    if not is_valid_number(number):
        await message.answer('Пожалуйста, введите корректный номер телефона.')
        return

    await state.update_data(number=number)
    await message.answer(
        'И имейл.Он понадобится нам, чтобы отправить информацию по обучению. Обещаем не спамить без разрешения)')
    await HandleClient.next()


async def email(message: types.Message, state: FSMContext):
    email = message.text.lower().strip()
    if not is_valid_email(email):
        await message.answer('Пожалуйста, введите корректный адрес электронной почты.')
        return
    await state.update_data(email=email)
    await message.answer(
        'Готово! Спасибо, что оставили заявку в Алгоритмику. Мы свяжемся с вами в рабочее время, чтобы рассказать '
        'подробности участия и ответить на ваши вопросы. ☎️ Звонок поступит с номера +7 953 997 92 76.')
    result_managers = await read_all_managers()
    user_data = await state.get_data()
    await state.finish()
    user_name = user_data.get('name')
    user_number = user_data.get('number')
    user_email = user_data.get('email')
    user_tg_login = message.from_user.username
    await save_request(user_name, user_number, user_email, user_tg_login)
    for result in result_managers:
        await bot.send_message(int(result.manager_chat_id),
                               f"Новая заявка:\nИмя: {user_name}\nНомер: {user_number}\nПочта: {user_email}\nТг: {user_tg_login}")


async def cancel(message: types.Message, state: FSMContext):
    managers = await read_all_managers()
    user_data = await state.get_data()
    user_name = user_data.get('name')
    user_number = user_data.get('number')
    user_email = user_data.get('email')
    user_tg_login = message.from_user.username
    await save_request(user_name, user_number, user_email, user_tg_login)
    for manager in managers:
        await bot.send_message(int(manager.manager_chat_id),
                               f"Новая неполная заявка:\nИмя: {user_name}\nНомер: {user_number}\nПочта: {user_email}\nТг: {user_tg_login}")
    await message.answer("Будем рады видеть вас снова!")
    await state.finish()


async def logout(message: types.Message, state: FSMContext):
    manager = await read_manager_by_id(str(message.chat.id))
    if manager == -1:
        god = await read_god_by_id(str(message.chat.id))
        if god != -1:
            await remove_god(str(message.chat.id))
            await message.answer('Вы больше не администратор.')
    else:
        await remove_manager(str(message.chat.id))
        await message.answer('Вы больше не клиентский менеджер.')


async def god(message: types.Message, state: FSMContext):
    password = message.text.split(' ')[1]
    if god_password == password.strip():
        god = await read_god_by_id(str(message.chat.id))
        if god.id == -1:
            await save_god(str(message.chat.id), str(message.from_user.username))
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["Список менеджеров", "Список заявок", "Удалить менеджера", "Файл"]
            keyboard.add(*buttons)
            await message.answer('Теперь вы администратор. Выберите нужное действие на клавиатуре.',
                                 reply_markup=keyboard)
        else:
            await message.answer('Вы уже администратор. Выберите нужное действие на клавиатуре')
    else:
        await message.answer('Неправильный пароль. Попробуйте снова')
    await bot.delete_message(message.chat.id, message.message_id)
    await state.finish()


@dp.message_handler(Text(equals=["Список менеджеров", "Список заявок", "Удалить менеджера", "Файл"]))
async def god_action(message: types.Message, state: FSMContext):
    god = await read_god_by_id(str(message.chat.id))
    if god.id != -1:
        await state.finish()
        text = message.text
        if text == "Список менеджеров":
            result_managers = await read_all_managers()
            result1 = ''
            for result in result_managers:
                result1 += f'{result.manager_chat_id} - {result.manager_tg_login}\n'
            await message.answer(result1)
        elif text == "Список заявок":
            result_requests = await read_all_requests()
            result1 = 'Все заявки:\n'
            for result in result_requests:
                result1 += f'Заявка #{str(result.id)}: {str(result.name)} -- {str(result.number)} -- {str(result.email)} -- {str(result.user_tg_login)}\n'
            await message.answer(result1)
        elif text == "Удалить менеджера":
            await message.answer('Для удаления менеджера отправьте в чат команду /remove id, где id - id менеджера.')
        elif text == 'Файл':
            result_requests = await read_all_requests()
            result_dict = dict()
            for result in result_requests:
                result_dict[result.id] = {'name': result.name, 'number': result.number, 'email': result.email, 'user_tg_login': result.user_tg_login}
            fp = open('result.json', 'w')
            json.dump(result_dict, fp)
            fp.close()
            fp = open('result.json', 'rb')
            await message.reply_document(fp)


async def remove_manager(message: types.Message):
    god = await read_god_by_id(str(message.chat.id))
    if god is not None:
        manager_chat_id = message.text.split(' ')[1].strip()
        manager = await read_manager_by_id(manager_chat_id)
        if manager is not None:
            await remove_manager(manager_chat_id)
            await message.answer('Менеджер удалён.')
        else:
            await message.answer('Попробуйте снова.')


async def client_manager(message: types.Message, state: FSMContext):
    password = message.text.split(' ')[1]
    if client_manager_password == password.strip():
        manager = await read_manager_by_id(str(message.chat.id))
        if manager is None:
            await save_manager(str(message.chat.id), str(message.from_user.username))
            await message.answer('Добро пожаловать! В этот чат будут приходить уведомления о новых заявках.')
        else:
            await message.answer('Вы уже зарегистрированы как клиентский менеджер')
    else:
        await message.answer('Неправильный пароль. Попробуйте снова.')
    await bot.delete_message(message.chat.id, message.message_id)
    await state.finish()


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")
    return True


@dp.errors_handler(exception=ChatNotFound)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Чат не найден!\nСообщение: {update}\nОшибка: {exception}")
    return True


def register_handlers_algo(dp: Dispatcher):
    dp.register_message_handler(start, commands="start", state="*")
    dp.register_message_handler(client_manager, commands="manager", state="*")
    dp.register_message_handler(remove_manager, commands="remove", state="*")
    dp.register_message_handler(cancel, commands="cancel", state="*")
    dp.register_message_handler(logout, commands="logout", state="*")
    dp.register_message_handler(god, commands="admin", state="*")
    dp.register_message_handler(name, state=HandleClient.waiting_for_name)
    dp.register_message_handler(number, state=HandleClient.waiting_for_number)
    dp.register_message_handler(email, state=HandleClient.waiting_for_email)


register_handlers_algo(dp)

async def main():
    await create_tables()
    print(await read_all_managers())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
