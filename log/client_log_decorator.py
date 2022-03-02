import logging


def client_log_decorator(fn):
    def wrapper(*args, **kwargs):
        format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s")
        log_handler = logging.FileHandler('log_files/client_log.log', encoding='utf-8')
        # log_handler.setLevel(logging.INFO)
        level_dict = {'critical': 50,
                      'error': 40,
                      'warning': 30,
                      'info': 20,
                      'debug': 10,
                      'notset': 0}
        level = fn(args[0])
        level_log = level_dict[level[0]]
        res = fn(*args)
        msg = f'Запись вызвына {fn}, содержание:  {res[1]}'
        log_handler.setFormatter(format_str)
        log = logging.getLogger('client_log')
        log.addHandler(log_handler)
        log.setLevel(logging.INFO)

        log.log(level_log, msg)
        return log

    return wrapper


@client_log_decorator
def log(*args):
    return args


# log('critical', 'crit ошибка!!!!')
