"""Файл с текстами для сообщений бота"""

start_message = ('<strong><em>Приветствую!👋 Я бот-напоминалка для задач этого чата.</em></strong>'
                 '\n\n<em>🔹Моя работа</em> - получать от вас описание задачи и высылать вам уведомления:'
                 '\n- за час до дедлайна'
                 '\n- в момент дедлайна'
                 '\n- за час после дедлайна.'
                 '\n- в 9:00 каждого дня списком всех задач'
                 '\n\n🔹Я принимаю задачи вида:'
                 '\n<code>#задача подготовить годовой отчёт о работе компании @tg_executor '
                 '#дедлайн 12:00 15.08.2024</code>\n'
                 '\nДля получения более <strong>подробной инструкции</strong> '
                 'по оформлению запросов и о возможных командах напишите /help'
                 '\n\n‼️Чтобы <strong>запустить бота</strong> для '
                 'отслеживания сообщений в этом чате напишите команду /bot_on')

help_message = ('<strong><em>Инструкция к использованию бота.</em></strong>'
                '\nЧтобы бот смог отслеживать сообщения этого чата первым делом необходимо вызвать '
                'команду /start, затем /bot_on'
                '\n\n🔸<u>Команды:</u>'
                '\n/start - получение стартового сообщения для запуска бота а данном чате'
                '\n/help - получение информационного сообщения с инструкцией по использованию бота'
                '\n/bot_on - включение бота для обработки данного чата'
                '\n/bot_off - отключение бота от обработки данного чата'
                '\n/get_tasks - получение всех задач для данного чата'
                '\n/done_all - отметить все задачи чата выполненными и удалить'
                '\n/done [id задачи] - отметить задачу выполненной и удалить'
                '\n/change_time [id задачи] [новое время] - изменение дедлайна для ранее добавленной задачи '
                '(параметры - id задачи и новое время)'
                '\n/nothing_is_working - если бот перестал присылать актуальные уведомления'
                '\n\n🔸<u>Форматы описания задачи:</u>'
                '\n- #задача [описание] @ответственный #дедлайн [время]'
                '\n- #задача @ответственный [описание] #дедлайн [время]'
                '\n- #дедлайн [время] #задача @ответственный [описание]'
                '\nкомпоненты [@ответственный] и [#дедлайн [время]] - не обязательно, '
                'однако без указания времени уведомление не высылается'
                '\n\n🔸<u>Формат указания времени:</u>'
                '\n- DD.MM.YYYY HH:MM'
                '\n- HH:MM DD.MM.YYYY'
                '\n- DD.MM HH:MM'
                '\n- HH:MM DD.MM'
                '\n- DD.MM.YYYY <i>[авто время: 10:00 указанного дня]</i>'
                '\n- DD.MM <i>[авто время: 10:00 указанного дня]</i>'
                '\n- HH:MM <i>[авто дата: сегодня]</i>'
                '\n\n🔸<u>Примеры:</u>'
                '\n<code>#задача подготовить годовой отчёт о работе компании @tg_executor '
                '#дедлайн 12:00 15.08.2024</code>\n'
                '\n<code>#задача  @tg_executor оформить договор о неразглашении #дедлайн 18:00</code>\n'
                '\n<code>#дедлайн 17.07 #задача связаться с заказчиков, контакт: +7-(900)-000-00-00, '
                'ответственный: @камердинер</code>\n'
                '\n<code>#задача поставить + в чат, что вы на рабочем месте</code>\n')

bot_on = '🔔Бот успешно добавил данный чат в таблицу отслеживания и теперь готов помогать!'
bot_off = '🔕Бот успешно отключил отслеживание этого чата! Уведомления больше не высылаются.'

change_message = 'Дедлайн задачи успешно изменён!'
change_time_err = ('⚠️Пропишите после команды id той задачи, время которой хотите изменить, и её новый дедлайн. '
                   '\n[например: /change_time 1 14:00 21.08]')

done_message = f'<strong><em>Поздравляю с выполнением!✅</em></strong>\nЗадача удалена. ID: '
done_err = ('⚠️Пропишите после команды цифрой id той задачи, которую хотите отметить выполненной. '
            '\n[например: /done 1]')

done_all_message = 'Все задачи этого чата <strong>удалены</strong>✅'
done_all_err = '⛔️<em>что-то пошло не так при удалении всех задач...</em>'

remind_hour = '🔔<strong><u>Напоминание</u></strong>: до дедлайна час!'
remind_less_hour = '🔔<strong><u>Напоминание</u></strong>: до дедлайна меньше часа!'
remind_deadline = '🔔<strong><u>Напоминание</u></strong>: вот и дедлайн!'
remind_more_hour = '🔔<strong><u>Напоминание</u></strong>: задача просрочена на час!'

daily_plane_message = '<strong><em>Доброе утро!</em></strong>🔔Напоминаю все задачи этого чата:'

baseException = ('⛔️<em>Что-то пошло не так, но уведомление об ошибке уже отправлено администратору.'
                 '\nПопробуйте вызвать бота позже.</em>')
executorException = ('❌<strong>Ошибка</strong>: в назначении ответственного.'
                     '\nПроверьте формат написания ответственного.')
deadlineException = ('❌<strong>Ошибка</strong>: в указании даты.'
                     '\nПроверьте формат и актуальность даты. Попробуйте изменить формат записи.')
descriptionException = ('❌<strong>Ошибка</strong>: в описании задачи - минимальное описание должно быть обязательно.\n'
                        'Проверьте формат описания.'
                        '\n(#задача [описание] @ответственный #дедлайн [время])')
noneChatException = ('❌<strong>Oшибка</strong>: данного чата нет в списке отслеживания.'
                     '\nВыполните команду /start, а затем включите бота командой /bot_on')
noneTaskException = ('❌<strong>Ошибка</strong>: задачи с таким id нет в списке вашего чата.'
                     '\nЧтобы узнать id, получите список всех команд через команду /get_tasks')

nothing_is_working = ('<strong>Не беспокойтесь!</strong>\n'
                      'Все задачи данного чата сохранены в защищённой базе данных.'
                      'Если бот по каким-то причинам упал и не присылает уведомления - вероятно, '
                      'слетело время напоминания.\n'
                      'Разработчику очень жаль, что так получилось.'
                      'Что можно сделать для восстановления:\n'
                      '0. Проверить, что вы вызвали команды /start и /bot_on в этом чате.'
                      '1. Вызвать задачи командой /get_tasks;\n'
                      '2. Убедиться, что уведомления действительно не приходят, несмотря на верное время;\n'
                      '3. Вновь отправить боту задачи, скопировав информацию о задачах из полученного списка. '
                      'Тогда напоминания восстановятся;\n'
                      '4. Изменить время задач (можно и на такое же) - тогда напоминания тоже перезагрузятся.\n\n'
                      '<i>Благодарим за понимание!</i>')
