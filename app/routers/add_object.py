from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram_dialog import DialogManager, setup_dialogs, StartMode

from functions import add_task
from models import FSMmodel, TextFilter, redis
from my_calendar import add_dialog

router: Router = Router()
router.include_router(add_dialog)
setup_dialogs(router)


@router.message(Command(commands=["add"]),
                StateFilter(default_state, FSMmodel.add))
async def process_add_object_command(message: Message,
                                     dialog_manager: DialogManager,
                                     state: FSMContext):
    date = await redis.get(f'date:{message.from_user.id}')
    await state.set_state(FSMmodel.add)
    if not date:
        await dialog_manager.start(FSMmodel.calendar,
                                   mode=StartMode.RESET_STACK)
    else:
        await message.answer(text=f'Вы в режиме ввода задачи.\n\
Выбранная дата: <b>{date}</b>, введите задачу. \
Для выхода из режима нажмите /cancel.\n\
Для смены даты нажмите /calendar.', parse_mode='html')


@router.message(StateFilter(FSMmodel.add),
                Command(commands='cancel'))
async def process_exit_add_mode_command(message: Message,
                                        state: FSMContext):
    await message.answer('Вы вышли из режима ввода задачи.\n\
Для отметки выполненных задач нажмите /mark_done.\n\
Для просмотра актуальных задач нажмите /get_current.')
    await state.set_state(state=None)


@router.message(StateFilter(FSMmodel.add),
                Command(commands='add'))
async def process_add_in_process_command(message: Message):
    await message.answer('Вы уже в режиме создания задачи.\n\
Для выхода из режима выберите команду /cancel')


@router.message(StateFilter(FSMmodel.add),
                Command(commands=['mark_done',
                                  'get_current',
                                  'get_outdated']))
async def process_mark_done_command(message: Message):
    await message.answer('Вы в режиме создания задачи.\n\
Для выхода из режима выберите команду /cancel.')


@router.message(StateFilter(FSMmodel.add), TextFilter())
async def process_text(message: Message, state: FSMContext,
                       dialog_manager: DialogManager,
                       text: str):
    id = message.from_user.id
    date = await redis.get(f'date:{id}')
    if not date:
        await process_add_object_command(message, dialog_manager, state)
    else:
        await add_task(id, text, date)
        await message.answer(
            text=('Задача добавлена. \n\
Для выхода из режима выберите команду /cancel или \
продолжайте вводить задачи.\nДля смены даты нажмите /calendar.')
        )
