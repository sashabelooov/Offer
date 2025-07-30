from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    language = State()
    phone = State()
    fio = State()
    conf = State()
    issue = State()