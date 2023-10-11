RU = {
    'start': 'Этот бот помогает создавать to_do лист.\n'
    'Чтобы узнать больше о функционале,\n'
    'отправьте команду /help',
    'help': 'Перечень доступных команд:\n\
/start - краткое описание работы;\n\
/help - выводит это сообщение;\n\
/list_all - выводит все объекты из базы данных;\n\
/add - переводит в режим добавления объектов в формате ключ = значение;\n\
(поддерживается добавление объектов из файла в формате .csv с разделителем "=")\n\
/learn - переводит в режим изучения новых/проблемных объектов;\n\
/delete - переводит в режим удаления объектов \
(для удаления достаточно указать часть ключа);\n\
/cancel - выход из режима и сохранение данных.',
    '/cancel': 'Вы в режиме ожидания. Выберите команду из \
перечня команд (для вывода команд нажмите /help)',
    '/no_training': 'На сегодня нет объектов для тренировки, \
вы можете попробовать повторить \
новые объекты или объекты, которые пока плохо запомнились:)',
    '/stop_training': 'Тренировка остановлена. Данные обновлены.\n\
Вы можете продолжить позже повторно выбрав команду /training \n\
или перейти в режим изучения новых/проблемных объектов выбрав команду /learn',
    '/end_training': 'Тренировка остановлена. Данные обновлены.\n\
Вы можете продолжить позже повторно выбрав команду /training \n\
или перейти в режим изучения новых/проблемных объектов выбрав команду /learn',
    'default_state': 'Выберите команду из списка.\n\
Текстовые сообщения воспринимаются только в режиме /add и /delete.'
}

commands = ('add', 'training', 'learn', 'delete')