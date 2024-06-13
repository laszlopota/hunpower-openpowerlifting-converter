import os
import shutil
import glob
import pandas
import re
import json
import csv

from . import constants
from .HunpowerExcel import HunpowerExcel
from .ExcelConverter import ExcelConverter


class Competition:
    def __init__(self, meet_folder_name):
        self.path = f"{constants.PATH}/competitions/{meet_folder_name}".replace("\\", "/")
        
        self.initial_check()
        self.make_openpowerlifting_folder()
        
        self.urls = self.read_url_txt(f"{self.path}/__URL.txt")
        self.excel_config = self.read_excel_config()
        self.meet_config = self.read_meet_config()
        
        self.hunpowerexcels = [HunpowerExcel(path) for path in self.collect_result_excels()]
        
    def initial_check(self):
        def read_example_file(file):
            with open(f"{constants.PATH}/competitions/_example/{file}") as example_file:
                return example_file.read()
        
        files_to_check = ["__URL.txt", "__excel_config.json", "__meet_config.json"]
        for file in files_to_check:
            if not os.path.exists(f"{self.path}/{file}"):
                raise FileNotFoundError(f"""{file} does not exist!
                Please make the file manually in the {self.path} folder!
                
                Example file content:
                '''
                {read_example_file(file)}
                '''\
                """.replace(" "*16, ""))
    
    def make_openpowerlifting_folder(self):
        folder_path = f"{self.path}/openpowerlifting"
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
            except Exception as exception:
                print(f"Warning: {exception}")
                return
        os.mkdir(folder_path)
    
    def read_url_txt(self, path):
        with open(path) as txt_file:
            lines = txt_file.read().splitlines()
            return sorted(lines)
    
    def read_excel_config(self):
        with open(f"{self.path}/__excel_config.json", encoding="utf-8") as json_file:
            json_str = json_file.read()
            cleaned_json_str = re.compile(r',(\s*[\]}])').sub(r'\1', json_str)
            data = json.loads(cleaned_json_str)
            return {k.lower(): v for k, v in data.items()}
            
    def read_meet_config(self):
        with open(f"{self.path}/__meet_config.json", encoding="utf-8") as json_file:
            json_str = json_file.read()
            cleaned_json_str = re.compile(r',(\s*[\]}])').sub(r'\1', json_str)
            return json.loads(cleaned_json_str)
    
    def collect_result_excels(self):
        excels = glob.glob(f"{self.path}/*xls*")
        
        if not excels:
            raise FileNotFoundError("No excel files in this competition folder!")
        
        return [excel.lower() for excel in sorted(excels)]
    
    def save_url(self):
        with open(f"{self.path}/openpowerlifting/URL", "w") as file:
            file.write("\n".join(self.urls))
    
    def save_original_csvs(self):
        for i, hunpowerexcel in enumerate(self.hunpowerexcels, 1):
            hunpowerexcel.save_original_csv(f"{self.path}/openpowerlifting/original{i}.csv")
            
    def save_entries_csv(self, _print=False):
        dataframes = []
        for excel in self.hunpowerexcels:
            excel_name = excel.get_file_name()
            converter = ExcelConverter(excel, **self.excel_config[excel_name])
            converter.convert()
            dataframes.append(converter.get_data())
            
        merged_dataframe = pandas.concat(dataframes)
        merged_dataframe.to_csv(f"{self.path}/openpowerlifting/entries.csv", encoding="utf-8", index=False)
        
        if _print:
            print(merged_dataframe.to_string(index=False), end='\n\n')
        
    def save_meet_csv(self, _print=False):
        data = pandas.DataFrame({k: [v] for k, v in self.meet_config.items()})
        data.to_csv(f"{self.path}/openpowerlifting/meet.csv", encoding="utf-8", index=False)
        
        if _print:
            print(data.to_string(index=False), end='\n\n')

