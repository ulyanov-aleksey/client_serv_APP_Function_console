import logging
import sys

format_str = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s")
log_handler = logging.FileHandler('log_files/client_log.log', encoding='utf-8')
# log_handler.setLevel(logging.INFO)
log_handler.setFormatter(format_str)

log = logging.getLogger('client_log')
log.addHandler(log_handler)
log.setLevel(logging.INFO)


def main():
    log.info('info msg')
    log.error('error msg')
    log.critical('critical msg')
    log.warning('warning msg')


if __name__ == '__main__':
    main()

