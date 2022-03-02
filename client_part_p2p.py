import argparse
import json
import socket
import sys
import threading
import time

from log.client_log_decorator import *

from utils import load_configs, send_message, get_message

CONFIGS = {}
semafore = threading.Semaphore(0)


def help_text():
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


def create_exit_message(account_name):
    return {
        CONFIGS['ACTION']: CONFIGS['EXIT'],
        CONFIGS['TIME']: time.time(),
        CONFIGS['ACCOUNT_NAME']: account_name
    }


# функция создания presense сообщения
def create_presence_message(account_name, CONFIGS):
    msg_dict = {
        CONFIGS.get('ACTION'): CONFIGS.get('PRESENCE'),
        CONFIGS.get('TIME'): time.time(),
        CONFIGS.get('USER'): {
            CONFIGS.get('ACCOUNT_NAME'): account_name  # Здесь нужно сделать привязку к конкреному аккаунту
        }
    }
    return msg_dict


# функция создания сообщения для клиента (модель/dict)
def create_message_to_client(sock, CONFIGS, account_name):  # функция создания сообщения
    to_client = input("Введите имя получателя или \'q\' для завершения работы: ")
    message = input("Введите текст сообщения или \'q\' для завершения работы: ")
    if message == "q" or to_client == "q":
        sock.close()
        sys.exit(0)
    message_dict = {
        CONFIGS['ACTION']: CONFIGS['MESSAGE'],
        CONFIGS['SENDER']: account_name,
        CONFIGS['TIME']: time.time(),
        CONFIGS['ACCOUNT_NAME']: account_name,
        CONFIGS['TO_CLIENT']: to_client,
        CONFIGS['MESSAGE_TEXT']: message
    }
    # print(message_dict)
    try:
        send_message(sock, message_dict, CONFIGS)
        # semafore.acquire()
        log('info', f'Отправлено сообщение для пользователя {to_client}')

    except:
        log('critical', 'Потеряно соединение с сервером.')
        sys.exit(1)


# функция получения сообщений (action - message) от сервера и проверки конфигурации смс
def handle_server_message_from_client(sock, account_name):
    while True:
        try:
            message = get_message(sock, CONFIGS)
            if CONFIGS['ACTION'] in message and message[CONFIGS['ACTION']] == CONFIGS['MESSAGE'] \
                    and message[CONFIGS['TO_CLIENT']] == account_name and CONFIGS['MESSAGE_TEXT'] in message:

                print(
                    f"{account_name} Для Вас получено сообщение от пользователя {message[CONFIGS['SENDER']]}: \n {message[CONFIGS['MESSAGE_TEXT']]}")
                # semafore.release()
            else:
                log('error', f"Получено некоректное сообщение от сервера для {account_name}: {message}")

        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            log('critical', 'Потеряно соединение с сервером.')
            break


# функция отправки сообщения пользователю (action - message)
def send_to_user(sock, account_name):
    print(help_text())
    while True:

        command = input('Введите команду: ')

        if command == 'message':
            create_message_to_client(sock, CONFIGS, account_name)

        elif command == 'help':
            print(help_text())
        elif command == 'exit':
            send_message(sock, create_exit_message(account_name), CONFIGS)
            print('Завершение соединения.')
            log('info', 'Завершение работы по команде пользователя.')

            time.sleep(0.5)
            break

        else:
            print('Команда не распознана, попробуйте снова. help - вывести поддерживаемые команды.')
        # semafore.acquire()


# функция проверки response сообщения от сервера (ответ на presense)
def handle_response(message, CONFIGS):
    if CONFIGS.get('RESPONSE') in message:
        if message[CONFIGS.get('RESPONSE')] == 200:
            # print('OK')
            return '200: OK'
        # print('False')
        return f'400: {message[CONFIGS.get("ERROR")]}'
    raise ValueError


# функция для парсинга ком строки именными аргументами
def arg_parser(CONFIGS):
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=CONFIGS['DEFAULT_IP_ADDRESS'], nargs='?')
    parser.add_argument('port', default=CONFIGS['DEFAULT_PORT'], type=int, nargs='?')
    # parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    if not 1023 < server_port < 65536:
        log('critical', 'Порт должен быть в пределах от 1024 до 65535')
        sys.exit(1)

    return server_address, server_port


def main():
    account_name = input("Your name: ")

    global CONFIGS
    CONFIGS = load_configs(is_server=False)
    server_address, server_port = arg_parser(CONFIGS)

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        presence_message = create_presence_message(account_name, CONFIGS)
        # print(presence_message)
        send_message(transport, presence_message, CONFIGS)
        # print(server_port, server_address)
        answer = handle_response(get_message(transport, CONFIGS), CONFIGS)
        log('info', f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print("Соединение установлено")
    except json.JSONDecodeError:
        log('error', 'Не удалось декодировать JSON-строку')
        sys.exit(1)
    except ConnectionRefusedError:
        log('critical', f'Не удалось подключиться к серверу {server_address}:{server_port},'
                        f'конечный компьютер отверг запрос на подключение')
        sys.exit(1)

    else:
        # запуск ПЕРВОГО потока (демона) на прием сообщений от клиентов
        receiver = threading.Thread(target=handle_server_message_from_client, args=(transport, account_name))
        receiver.daemon = True
        receiver.start()
        #print('1')
        # запуск ВТОРОГО потока (демона) на отправку сообщений от клиентов
        user_interface = threading.Thread(target=send_to_user, args=(transport, account_name))
        # print('1')
        user_interface.daemon = True
        # print('2')
        user_interface.start()
        #print('2')
        receiver.join()
        user_interface.join()

        log('info', 'Запущены процессы')
        # print('4')


if __name__ == '__main__':
    main()
