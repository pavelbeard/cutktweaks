import asyncio
import os.path
import re
from typing import List

import aiofiles
import pandas as pd
from zipstream import AioZipStream


async def excel_files_handler(paths: List[str], current_period):
    result = await asyncio.gather(
        *(handle(path, current_period=current_period) for path in paths))

    for r in result:
        print(r)


async def handle(file: str, current_period: str):
    """
    Находит количество нарядов, которые соответствуют условиям:
        1. в наряде (список одинаковых чисел) следующий порядок групп пользователей:
            - в массиве групп пользователей (этапов) индекс АТС < ЦЭМТС.
            - присутствие АТС и ЦЭМТС в массиве.
        2. Дата в ЦЭМТС должна быть равна текущему периоду.
        3. текущий период - выбирается в форме
    :param file: файл xls
    :param current_period: текущий период
    :return: bytes
    """
    try:
        df = pd.read_excel(file, sheet_name="EXCELTABLESHEET1")

        result = []
        tmp = []

        # разбиваем DataFrame на группы:
        for i in range(len(df) - 1):
            if df['Номер наряда'].loc[i] == df['Номер наряда'].loc[i + 1]:
                tmp.append(i)
            else:
                try:
                    result.append(df.iloc[tmp[0]:tmp[-1] + 2])
                    tmp = []
                except IndexError:  # если наряд состоит из одной строки
                    pass

        # фильтруем:
        count = []
        for df1 in result:
            tmp_df = df1[['Конец этапа', 'Этап']] \
                [((df1['Этап'].str.contains('ЦЭМТС', regex=True)) & (
                        df1['Конец этапа'] > pd.to_datetime(current_period))) & \
                 (df1['Этап'].str.contains('АТС\s(ЦТС)|ЦЭМТС', regex=True))]
            if len(tmp_df) > 0:
                count.append((df1['Номер наряда'].unique()[0], df1[['Номер наряда', 'Конец этапа', 'Этап']]))

        # вставляем в таблицу:
        writer = pd.ExcelWriter(os.path.join("download", re.split(r"/|\\", file)[-1]), engine="xlsxwriter")

        df_sheet_empty = pd.DataFrame()
        df_sheet_empty.to_excel(writer, sheet_name="Результаты")

        worksheet = writer.sheets["Результаты"]

        # считаем наряды
        worksheet.write(0, 0, "Количество нарядов:")
        worksheet.write(1, 0, len(count))
        worksheet.write(2, 0, "Наряды:")

        for i, data in enumerate(count, 4):
            n, d = data
            worksheet.write(i, 0, n)

        df.to_excel(writer, sheet_name='Исходная таблица')

        writer.save()

        return True
    except (UnicodeEncodeError, ValueError) as e:
        return e


async def zipfiles(zipname, files):
    aiozip = AioZipStream(files, chunksize=32768)
    async with aiofiles.open(zipname, mode="wb") as z:
        async for chunk in aiozip.stream():
            await z.write(chunk)
