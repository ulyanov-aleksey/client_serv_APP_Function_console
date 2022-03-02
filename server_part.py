import argparse
import sys
import json
import socket
import select

# from log.server_log_config import *
import time

from log.server_log_decorator import *
from utils import load_configs, send_message, get_message

CONFIGS = {}


# функция проверки "action - presence" сообщения от клиента
def handle_message(message, CONFIGS):
    # print(message[CONFIGS.get('USER')][CONFIGS.get('ACCOUNT_NAME')])
    if CONFIGS.get('ACTION') in message and message[CONFIGS.get('ACTION')] == CONFIGS.get('PRESENCE') \
            and CONFIGS.get('TIME') in message and CONFIGS.get('USER') in message:
        # == message[CONFIGS.get('USER')][CONFIGS.get('ACCOUNT_NAME')]:
        return {CONFIGS.get('RESPONSE'): 200,
                CONFIGS.get('USER'): message[CONFIGS.get('USER')][CONFIGS.get('ACCOUNT_NAME')]}
    return {
        CONFIGS.get('RESPONSE'): 400,
        CONFIGS.get('ERROR'): 'Bad Request'
    }


# функция для парсинга ком строки именными аргументами
def arg_parser(CONFIGS):
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=CONFIGS['DEFAULT_PORT'], type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        log('critical', f'Попытка запуска с некоректного порта: {listen_port}'
                        f'Порт должен быть в пределах от 1024 до 65535')
        sys.exit(1)

    return listen_address, listen_port


def read_request(r_list, clients):
    responses = {}

    for sock in r_list:
        try:
            data = get_message(sock, CONFIGS)
            responses[sock] = data
        except:
            clients.remove(sock)
    return responses


def write_responses(requests, w_list, clients):
    for sock in w_list:  # перебор всех клиентов в w_list
        for _, request in requests.items():  # тк requests это словарь {клиент: сообщение} вытягиваем все
            # смс от всех клиентов "_" это игнор
            # алиаса для "клиента" мы его не использ
            if request['action'] == 'presence':
                req_pres = handle_message(request, CONFIGS)
                send_message(sock, req_pres, CONFIGS)
                # print(req_pres)
            else:
                try:
                    send_message(sock, request, CONFIGS)
                    # print(f'отправлено смс {request}')
                except:
                    sock.close()
                    clients.remove(sock)


def main():
    global CONFIGS
    CONFIGS = load_configs()
    listen_address, listen_port = arg_parser(CONFIGS)
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.listen(CONFIGS.get('MAX_CONNECTIONS'))
    log('info', f'Сервер запущен по адресу: {listen_address}, на порту: {listen_port}.')
    transport.settimeout(0.5)
    clients = []
    # messages = []

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            log('info', f'Установлено соединение с ПК {client_address}')
            clients.append(client)
        finally:
            recv_data_list = []
            send_data_list = []
            error_list = []

            try:
                recv_data_list, send_data_list, error_list = select.select(clients, clients, [], 0)
                # print(f"send_data_list {send_data_list}")
            except OSError:
                pass

            requests = read_request(recv_data_list, clients)
            # print(f'Прочитаны смс {clients}')
            # print(f"send_data_list {recv_data_list}")
            if requests:
                write_responses(requests, send_data_list, clients)
                #print(f'Отправлены смс {clients}')


if __name__ == '__main__':
    main()
