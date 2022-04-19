import pandas as pd
import csv
import os
import shutil
from openpyxl import load_workbook

"""
    author : 유준상
    data : 2022-04-19
    특정 엑셀 파일을 복사 후 새로운 directory에 만든 뒤 특정 sheet에 csv의 값을 붙여넣기.
"""

CSV_DIR = 'D:\\csv_dir'
XLSX_DIR = 'D:\\result_dir'
FORM_PATH = 'D:\\original_form.xlsx'

def open_csv(csv_path):
    f = open(csv_path)
    reader = csv.reader(f)
    csv_list = []
    for i in reader:
        csv_list.append(i)
    f.close()
    df = pd.DataFrame(csv_list)
    return df

# 소수점 자리수 조정
def isfloat(df_col, rounding_digits):
    for index in range(len(df_col)):
        try:
            df_col[index] = round(float(df_col[index]), rounding_digits)
        except:
            continue

if __name__ == '__main__':
    
    csv_directory = os.listdir(CSV_DIR)

    for csv_index in range(len(csv_directory)):
        csv_path = os.path.join(CSV_DIR, csv_directory[csv_index])
        print(f"{csv_path} ({csv_index + 1}/{len(csv_directory)}) 변환 중.......")
        df = open_csv(csv_path)
    
        # 자리수 조정
        isfloat(df[0], 2)
        
        # 서식 파일 복사 후 저장
        xlsx_name, _ = csv_directory[csv_index].split(".")
        after_path = os.path.join(XLSX_DIR, xlsx_name + ".xlsx")
        shutil.copy(FORM_PATH, after_path)
        
        # 특정 sheet에 csv data 덮어쓰기
        book = load_workbook(after_path)
        writer = pd.ExcelWriter(after_path, engine = 'openpyxl')
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        df.to_excel(writer, sheet_name = sheet_name, index = False, header = False)
        writer.close()