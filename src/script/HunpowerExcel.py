import os
import pandas

from pandas.io.excel._openpyxl import OpenpyxlReader
from openpyxl.cell import Cell as OpenpyxlCell
from pandas.io.excel._xlrd import XlrdReader
from xlrd import open_workbook


class XlsxReader(OpenpyxlReader):
    def get_sheet_data(self, sheet, convert_float):
        data = []
        for row in sheet.rows:
            new_cells = []
            for cell in row:
                if cell.value is not None:
                    cell_value = cell.value
                    if cell.font.strike:
                        cell_value = f"-{cell.value}"        
                new_cells.append(cell_value)
            data.append(new_cells)
        return data


class XlsReader(XlrdReader):
    def load_workbook(self, filepath_or_buffer):
        if hasattr(filepath_or_buffer, "read"):
            data = filepath_or_buffer.read()
            self.workbook = open_workbook(file_contents=data, formatting_info=True)
            return self.workbook
        else:
            self.workbook = open_workbook(filepath_or_buffer, formatting_info=True)
            return self.workbook
            
    def get_sheet_data(self, sheet, convert_float):
        data = []
        for i_row in range(sheet.nrows):
            new_cells = []
            for i_col in range(len(sheet.row_values(i_row))):
                xf = self.workbook.xf_list[sheet.cell_xf_index(i_row, i_col)]
                font = self.workbook.font_list[xf.font_index]
                cell = sheet.cell(i_row, i_col)
                if cell.value is not None:
                    cell_value = cell.value
                    if font.struck_out:
                        cell_value = f"-{cell.value}"
                new_cells.append(cell_value if cell_value or not len(new_cells) else new_cells[-1])
            data.append(new_cells)
        return data


class ExcelFile(pandas.ExcelFile):
    _engines = {
        "xlrd": XlsReader,
        "openpyxl": XlsxReader
    }


class HunpowerExcel(pandas.ExcelFile):
    def __init__(self, path):
        full_path, ext = os.path.splitext(path)
        engine = "xlrd" if ext == ".xls" else "openpyxl"
        file = ExcelFile(path, engine=engine)
        
        self.path = path
        self.file_name = os.path.basename(full_path).split('/')[-1].lower()
        self.data = file.parse(header=None)
        
    def get_data(self):
        return self.data
        
    def get_file_name(self):
        return self.file_name
    
    def save_original_csv(self, file_name="original.csv"):
        self.data.to_csv(file_name, encoding="utf-8", index=False, header=False)

