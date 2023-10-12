from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from functions import get_tasks, create_tasks_list_for_mark, \
    create_tasks_builder
from models import FSMmodel, CategoryResponse

router: Router = Router()


@router.message(Command(commands=["mark_done"]),
                StateFilter(default_state))
async def process_mark_task_command(message: Message,
                                    state: FSMContext):
    id = message.from_user.id
    tasks = await get_tasks(id, 'ASC')
    if not tasks:
        await message.answer('На данный момент список актуальных задач пуст.')
    else:
        builder = await create_tasks_list_for_mark(tasks, state)
        await message.answer(text='Выберите задачу из списка.\n\
Для выхода из режима и сохранения данных нажмите /cancel:',
                             reply_markup=builder.as_markup())
        await state.set_state(FSMmodel.mark_done)


@router.message(StateFilter(FSMmodel.mark_done),
                Command(commands='cancel'))
async def process_exit_add_mode_command(message: Message,
                                        state: FSMContext):
    await message.answer('Вы вышли из режима отметки выполенных задач.')
    await state.set_state(state=None)


@router.callback_query(StateFilter(FSMmodel.mark_done),
                       CategoryResponse())
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    if not data or not data['tasks_list']:
        await callback.message.edit_text(
                text='Выберите режим из меню.')
        await state.clear()
    else:
        tasks_list = data['tasks_list']
        marked_tasks = data['marked_tasks']
        value = int(callback.data)
        try:
            builder = await create_tasks_builder(tasks_list)
            await callback.message.edit_text(
                text=f'Выбранная задача: <strike>{tasks_list[value][1]}</strike>.\n\
Для выхода из режима и сохранения данных нажмите /cancel:',
                reply_markup=builder.as_markup(),
                parse_mode='html')
            marked_tasks.append(tasks_list[value])
            await state.update_data(marked_tasks=marked_tasks)
        except:
            pass