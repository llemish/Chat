class ConfigReader:
    """

    Объект класса читает данные файла конфигурации и хранит из в аттрибутах

    """
    def __init__(self, path_to_file):
        self._port = 50001
        self._logging_level = 'DEBUG'
        self._max_user = 11
        self._max_message_length = 139
        self._read_file(path_to_file)

    def _read_file(self, path_to_file):
        with open(path_to_file) as f:
            for raw_line in f:
                if raw_line[0] != '#':
                    (key, value) = raw_line.split(':')
                    if key == 'LOGGING_LEVEL':
                        self._logging_level = value.strip()
                    elif key == 'PORT':
                        self._port = int(value)
                    elif key == 'MAX_MESSAGE_LENGTH':
                        # В силу ограниченного времени на написание приложения, со стороны клиента
                        # не была реализована возможность получения сообщения состоящего из нескольких
                        # пакетов, поэтому для избежания потери данных и некорректной работы,
                        # максимальная длина сообщений искусственно ограничена значением 1024
                        if int(value) > 1024:
                            value = 1024
                        self._max_message_length = int(value)
                    elif key == 'MAX_USERS':
                        self._max_user = int(value)

    @property
    def port(self):
        return self._port

    @property
    def logging_level(self):
        return self._logging_level

    @property
    def max_user(self):
        return self._max_user

    @property
    def max_message_length(self):
        return self._max_message_length
