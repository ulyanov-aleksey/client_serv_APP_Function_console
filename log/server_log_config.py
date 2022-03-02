import logging
import sys
from logging import handlers

format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s")
# log_handler = handlers.TimedRotatingFileHandler('log_files/serv_log.log', when='D', interval=1, encoding='utf-8')
log_handler = logging.FileHandler('log_files/serv_log.log', encoding='utf-8')
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(format_str)


log = logging.getLogger('server_log')
log.addHandler(log_handler)
log.setLevel(logging.INFO)


def main():
    log.info('info msg')
    log.error('error msg')
    log.critical('critical msg')
    log.warning('warning msg')


if __name__ == '__main__':
    main()
