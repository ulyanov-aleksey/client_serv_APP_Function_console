import os
import sys
import json


def load_configs(is_server=True):
    config_keys = [
        'DEFAULT_PORT',
        'MAX_CONNECTIONS',
        'MAX_PACKAGE_LENGTH',
        'ENCODING',
        'ACTION',
        'TIME',
        'USER',
        'ACCOUNT_NAME',
        'PRESENCE',
        'RESPONSE',
        'ERROR'
    ]
    if not is_server:
        config_keys.append('DEFAULT_IP_ADDRESS')
    if not os.path.exists('config.json'):      # Проверка на наличие файла
        print('Файл с конфигурациями не найден')
        sys.exit(1)            # Выход из кода(1 с ошибкой общепринятые соглашения, 0 - ОК)
    with open('config.json') as config_file:
        CONFIGS = json.load(config_file)
    loaded_configs_keys = list(CONFIGS.keys())   # Перебор всех полученных ключей из json
    for key in config_keys:
        if key not in loaded_configs_keys:
            print(f'В файле с конфигурациями не хватает ключа: {key}')
            sys.exit(1)
    return CONFIGS


def send_message(opened_socket, message, CONFIGS):
    json_message = json.dumps(message)      # Записываем сообщение
    response = json_message.encode(CONFIGS.get('ENCODING'))   # Декодим в байты
    opened_socket.send(response)  # Отправляем


def get_message(opened_socket, CONFIGS):
    response = opened_socket.recv(CONFIGS.get('MAX_PACKAGE_LENGTH'))      # Получение сообщения
    if isinstance(response, bytes):      # Если сообщ в байтах:
        json_response = response.decode(CONFIGS.get('ENCODING'))      # Декодим
        response_dict = json.loads(json_response)      # Парсим json-ом
        # print(response_dict)
        if isinstance(response_dict, dict):
            return response_dict
        raise ValueError
    raise ValueError
