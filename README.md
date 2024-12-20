# Chat

## Описание

Программный продукт состоит из серверной и клиентской частей.

Сервер: 
 - Принимает TCP запросы на подключение
 - Управляет отправкой сообщений
 - Выполняет набор команд пользователя

Клиент:
 - При запуске подключается к серверу
 - Запрашивает ник у пользователя для регистрации
 - В случае успешной регистрации позволяет пользователю отправлять сообщения другим пользователям
 - Позволяет отправить на сервер команды, такие как: смена ника, запрос списка доступных пользователей и др.
 - Информирует пользователя об успехе отправки сообщения или выполнения команды

## Установка

Требования:
 - ОС Ubuntu 20.04
 - Python 3.10+

Для установки сервера и клиента необходимо скопировать, соответственно, папки Server и Client из репозитория 

## Запуск и работа с сервером
Запуск сервера осуществляется при помощи bash-скрипта _run_server.sh_ находящегося в папке Server. 
Необходимо предоставить текущему пользователя права на исполнение файла в ОС.

При запуске скрипта после _run_server.sh_ необходимо указать адрес файла конфигурации,
требующийся для корректной работы сервера. По умолчанию файл конфигурации _config_ находится в
папке Server.
```commandline
bash run_server.sh config
```

Альтернативным способом является запуск файла _server.py_ при помощи команды:
```commandline
python3 server.py path_to_config
```

Логирование производится в файл _syslog.log_.

## Запуск и работа с клиентом
Запуск приложения клиента осуществляется при помощи bash-скрипта _client_start.sh_ находящегося в папке Client. 
Необходимо предоставить текущему пользователя права на исполнение файла в ОС.

```commandline
bash client_start.sh
```

Альтернативным способом является запуск файла _client.py_  находящегося в папке Client при помощи команды:
```commandline
python3 client.py
```

Настройка клиента осуществляется изменением значений аттрибутов класса _ClientInfo_ находящимся в файле 
_client.py_ в папке Client.

После запуска клиент, в случае успешного подключения к серверу, сообщает пользователю ограничение 
по длине сообщений и список поддерживаемых команд. Далее, пользователю выводиться список доступных 
пользователй и предлагается ввести свой ник.

После успешного прохождения регистрации, пользователь получает возможность отправления сообщений 
другим пользователям. Для этого следует поддерживать следующий формат сообщений:

_Имя_адресата_: _Текст_сообщения_

Поскольку комбинация "*/" зарезервирована для отправки команд на сервер, недопустимо использование этой
комбинации в начале ника или текста сообщения. Аналогично, имя пользователя не должно содержать символа ":".

После отправки сообщения, пользователь получает уведомление об успешности отправки этого
сообщения указанному пользователю.
