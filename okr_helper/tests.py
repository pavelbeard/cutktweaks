import asyncio
import os.path
import unittest
from .logic import excel_files_handler


class Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = os.path.join(os.getcwd(), "files")

    def test_excel_file_handler(self):
        async def t_excel_file_handler():
            await excel_files_handler(self.path, "01.01.23")

        asyncio.run(t_excel_file_handler())

