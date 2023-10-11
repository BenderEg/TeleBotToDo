from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram_dialog import DialogManager, setup_dialogs, StartMode

from functions import add_task
from models import FSMmodel, TextFilter, redis
from my_calendar import dialog


router: Router = Router()
router.include_router(dialog)
setup_dialogs(router)


@router.message(Command(commands=["add"]),
                StateFilter(default_state, FSMmodel.add))
async def process_add_object_command(message: Message,
                                     dialog_manager: DialogManager,
                                     state: FSMContext):
    await state.set_state(FSMmodel.add)
    await dialog_manager.start(FSMmodel.calendar, mode=StartMode.RESET_STACK)


@router.message(StateFilter(FSMmodel.add),
                Command(commands='cancel'))
async def process_exit_add_mode_command(message: Message,
                                        state: FSMContext):
    await message.answer('Вы вышли из режима ввода задачи.')
    await state.set_state(state=None)


@router.message(StateFilter(FSMmodel.add),
                Command(commands='add'))
async def process_add_in_process_command(message: Message):
    await message.answer('Вы уже в режиме создания задачи.\n\
Для выхода из режима выберите команду /cancel')


@router.message(StateFilter(FSMmodel.add), TextFilter())
async def process_text(message: Message, state: FSMContext,
                       dialog_manager: DialogManager):
    id, task = message.from_user.id, message.text
    date = await redis.get(f'date:{id}')
    if not date:
        await process_add_object_command(message, dialog_manager, state)
    else:
        await add_task(id, task, date)
        await message.answer(
            text=('Задача добавлена. \n\
Для выхода из режима выберите команду /cancel.')
        )
