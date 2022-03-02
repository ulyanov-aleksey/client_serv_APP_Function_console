import unittest
from serv_7_less_рассылка import handle_message
from utils import load_configs


class TestServer(unittest.TestCase):
    CONFIGS = load_configs(True)
    error_message = {
        CONFIGS['RESPONSE']: 400,
        CONFIGS['ERROR']: 'Bad Request'
    }
    success_message = {CONFIGS['RESPONSE']: 200}

    def test_without_action(self):
        self.assertEqual(
            handle_message({
                self.CONFIGS['TIME']: '1.1',
                self.CONFIGS['USER']: {
                    self.CONFIGS['ACCOUNT_NAME']: 'Dikson'
                }
            }, self.CONFIGS),
            self.error_message
        )

    def test_wrong_action(self):
        self.assertEqual(
            handle_message({
                self.CONFIGS['ACTION']: 'Wrong',
                self.CONFIGS['TIME']: 1.1,
                self.CONFIGS['USER']: {
                    self.CONFIGS['ACCOUNT_NAME']: 'Dikson'
                }
            }, self.CONFIGS),
            self.error_message
        )

    def test_without_time(self):
        self.assertEqual(
            handle_message({
                self.CONFIGS['ACTION']: self.CONFIGS['PRESENCE'],
                self.CONFIGS['USER']: {
                    self.CONFIGS['ACCOUNT_NAME']: 'Dikson'
                }
            }, self.CONFIGS),
            self.error_message
        )

    def test_wrong_user(self):
        self.assertEqual(
            handle_message({
                self.CONFIGS['ACTION']: self.CONFIGS['PRESENCE'],
                self.CONFIGS['TIME']: 1.1,
                self.CONFIGS['USER']: {
                    self.CONFIGS['ACCOUNT_NAME']: 'Dikson'
                }
            }, self.CONFIGS),
            self.success_message
        )

    def test_without_user(self):
        self.assertEqual(
            handle_message({
                self.CONFIGS['ACTION']: self.CONFIGS['PRESENCE'],
                self.CONFIGS['TIME']: 1.1
            }, self.CONFIGS),
            self.error_message
        )

    def test_success_check(self):
        self.assertEqual(
            handle_message({
                self.CONFIGS['ACTION']: self.CONFIGS['PRESENCE'],
                self.CONFIGS['TIME']: 1.1,
                self.CONFIGS['USER']: {
                    self.CONFIGS['ACCOUNT_NAME']: 'Dikson'
                }
            }, self.CONFIGS),
            self.success_message
        )


if __name__ == '__main__':
    unittest.main()
