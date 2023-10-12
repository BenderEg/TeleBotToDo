from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from functions import get_tasks, create_tasks_list_for_mark, \
    create_tasks_builder, update_mark_task, filter_active_task
from models import FSMmodel

router: Router = Router()


@router.message(Command(commands=["mark_done"]),
                StateFilter(default_state))
async def process_mark_task_command(message: Message,
                                    state: FSMContext):
    id = message.from_user.id
    all_tasks = await get_tasks(id, 'current', 'ASC')
    tasks = await filter_active_task(all_tasks)
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
    await message.answer('Вы вышли из режима отметки выполненных задач.')
    await update_mark_task(message.from_user.id, state)
    # await state.set_state(state=None)


@router.callback_query(StateFilter(FSMmodel.mark_done))
async def process_buttons_press(callback: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    if not data:
        await callback.message.edit_text(
                text='Выберите режим из меню.')
        await state.clear()
    else:
        tasks_dict: dict = data['tasks_dict']
        marked_tasks: set = set(data['marked_tasks'])
        removed_value = tasks_dict.pop(callback.data)
        try:
            builder = await create_tasks_builder(tasks_dict)
            marked_tasks.add(callback.data)
            marked_tasks = list(marked_tasks)
            await state.update_data(tasks_dict=tasks_dict,
                                    marked_tasks=marked_tasks)
            if tasks_dict:
                await callback.message.edit_text(
                        text=f'Выбранная задача: <strike>{removed_value[1]}</strike>.\n\
Для выхода из режима и сохранения данных нажмите /cancel:',
                        reply_markup=builder.as_markup(),
                        parse_mode='html')
            else:
                await callback.message.edit_text(
                        text=f'Выбранная задача: <strike>{removed_value[1]}</strike>.\n\
Перечень невыполненных задач пуст. Вы вышли из режима отметки выполненных задач.\n\
Для продолжения работы выберите команду из меню.',
                        parse_mode='html')
                await update_mark_task(callback.from_user.id, state)
        except:
            pass