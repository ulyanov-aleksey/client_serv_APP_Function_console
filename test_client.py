import os
import sys
import unittest
from clnt_7_less_рассылка import create_presence_message, handle_response
from utils import load_configs

sys.path.append(os.path.join(os.getcwd(), '..'))


class TestClient(unittest.TestCase):
    CONFIGS = load_configs(True)

    def test_presence(self):
        test = create_presence_message('Dikson', CONFIGS=self.CONFIGS)
        test[self.CONFIGS['TIME']] = 1.1
        self.assertEqual(
            test,
            {
                self.CONFIGS['ACTION']: self.CONFIGS['PRESENCE'],
                self.CONFIGS['TIME']: 1.1,
                self.CONFIGS['USER']: {
                    self.CONFIGS['ACCOUNT_NAME']: 'Dikson'
                }
            }
        )

    def test_correct_answer(self):
        self.assertEqual(
            handle_response({self.CONFIGS['RESPONSE']: 200}, self.CONFIGS),
            '200: OK'
        )

    def test_band_request(self):
        self.assertEqual(
            handle_response({
                self.CONFIGS['RESPONSE']: 400,
                self.CONFIGS['ERROR']: 'Bad Request'
            }, self.CONFIGS),
            '400: Bad Request'
        )

    def test_no_response(self):
        self.assertRaises(
            ValueError,
            handle_response,
            {self.CONFIGS['ERROR']: 'Bad Request'},
            self.CONFIGS
        )


if __name__ == '__main__':
    unittest.main()
