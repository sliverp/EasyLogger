import time
import unittest
from unittest import TestCase
import logger
logger = logger.get_logger()

class Test(TestCase):

    def test_ProgressBar(self):
        for i in logger.ProgressBar(range(100), check_points=[30, 70]):
            time.sleep(0.1)


if __name__ == '__main__':
    unittest.main()
