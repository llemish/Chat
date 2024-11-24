class Message:
    """

    Класс для обработки и анализа сообщений от пользователей
    is_correct - логический флаг, показывающий корректность формата сообщения
    is_command - флаг показывающий, является ли сообщение командой
    message - сообщение пользователю или команда
    target_user - имя пользователя получателя сообщения (в случае если это сообщение)
    или параметр передаваемый команде

    """

    def __init__(self, raw_data):

        self._is_correct = False
        self._is_command = False
        self._message = ''
        self._target_user = None

        self._handle(raw_data)

    @property
    def is_correct(self):
        return self._is_correct

    @property
    def is_command(self):
        return self._is_command

    @property
    def message(self):
        return self._message

    @property
    def target_user(self):
        return self._target_user

    def _handle(self, raw_data):
        data = raw_data.strip().decode()

        # Проверка корректности формата сообщения
        if len(data) > 3 and (':' in data or data[:2] == '*/'):
            self._is_correct = True
        else:
            return False

        # Определение является сообщение командой
        if data[:2] == '*/':
            self._is_command = True
            if ':' in data:
                self._target_user = data.split(':')[0].strip()[2:]
                self._message = data.split(':')[1].strip()
            else:
                self._target_user = data[2:].strip()
        else:
            self._target_user = data.split(':')[0].strip()
            self._message = data.split(':')[1].strip()

