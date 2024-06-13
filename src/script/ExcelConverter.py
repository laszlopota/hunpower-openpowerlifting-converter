import src.script.constants as constants


class ExcelConverter:
    def __init__(self, hunpower_excel, event, equipment, division, sex):
        if event not in constants.EVENT:
            raise ValueError(f"Invalid event! Valid values are: {constants.EVENT}")
            
        if equipment not in constants.EQUIPMENT:
            raise ValueError(f"Invalid equipment! Valid values are: {constants.EQUIPMENT}")
            
        if division not in constants.DIVISION:
            raise ValueError(f"Invalid division! Valid values are: {constants.DIVISION}")
            
        if sex not in constants.SEX:
            raise ValueError(f"Invalid sex! Valid values are: {constants.SEX}")
            
        self.sex = sex
        self.division = division
        self.event = event
        self.equipment = equipment
        
        self.file_name = hunpower_excel.get_file_name()
        self.data = hunpower_excel.get_data()
        
        self.unused_rows = {}
        
        self.data = self.data.dropna()
        
    def remove_unused_rows(self):
        if self.division in ["Team", "Masters"]:
            if self.division == "Team":
                data = self.data[self.data.iloc[:, 1].str.contains(" - ", na=False)]

            if self.division == "Masters":
                data = self.data[self.data.iloc[:, 1].str.startswith("Masters", na=False)]
            
            for i_data in range(len(data)-1):
                self.unused_rows[data.iloc[i_data+1].name] = data.iloc[i_data][0].strip()
            self.unused_rows[99999] = data.iloc[-1][0].strip()
        
        self.data = self.data[~(self.data.iloc[:, -3:-1].iloc[:, 0] == self.data.iloc[:, -3:-1].iloc[:, 1])]
        
    def remove_unused_cols(self):
        cols_to_drop = [col for col in self.data.columns if "unused_" in col]
        self.data.drop(columns=cols_to_drop, inplace=True)
    
    def add_weightclass_col(self):
        weight_classes = constants.WEIGHT_CLASSES[self.sex]
        if self.division in ["Juniors", "Sub-Juniors"]:
            weight_classes = [constants.YOUNG_WEIGHT_CLASS[self.sex]] + weight_classes
        
        def add(data):
            curr_weightclass = weight_classes[-1]
            for weight_class in weight_classes[:-1]:
                if float(data) <= int(weight_class):
                    return weight_class
            return curr_weightclass
        
        self.data["WeightClassKg"] = self.data["BodyweightKg"].apply(lambda n: add(n))
    
    def add_best_attempt_col(self):
        if self.event == "B":
            self.data["Best3BenchKg"] = self.data["TotalKg"]
            
        if self.event == "D":
            self.data["Best3DeadliftKg"] = self.data["TotalKg"]
    
    def add_team_col(self):
        if self.division == "Team":
            self.data["Team"] = ["" for _ in range(len(self.data))]
    
    def add_constant_cols(self):
        self.data["Event"]     = [self.event for _ in range(len(self.data))]
        self.data["Equipment"] = [self.equipment for _ in range(len(self.data))]
        self.data["Division"]  = [self.division for _ in range(len(self.data))]
        self.data["Sex"]       = [self.sex for _ in range(len(self.data))]
        self.data["BirthDate"] = ["" for _ in range(len(self.data))]
    
    def add_essential_cols(self):
        self.add_best_attempt_col()
        self.add_team_col()
        self.add_weightclass_col()
        self.add_constant_cols()
        
    def fix_headers(self):
        for i_col in range(len(self.data.iloc[0])):
            old_header = self.data.iloc[0, i_col].strip().lower()
            if old_header in list(constants.HEADERS.keys()):
                new_header = constants.HEADERS[old_header]
                if new_header not in list(self.data.columns):
                    self.data.rename(columns={self.data.columns[i_col]: new_header}, inplace=True)
                    continue
            self.data.rename(columns={self.data.columns[i_col]: f"unused_{i_col}"}, inplace=True)
            
        if self.event == "D":
            self.data.rename(columns={
                "Bench1Kg": "Deadlift1Kg",
                "Bench2Kg": "Deadlift2Kg",
                "Bench3Kg": "Deadlift3Kg",
            }, inplace=True)
        
        self.data = self.data.iloc[1:, :]
    
    def fix_lifter_names(self):
        def fix(data):
            new_data = data
            for k, v in constants.TEXT_TO_REPLACE.items():
                new_data = new_data.replace(k, v)
            
            data_parts = new_data.strip().split(" ")
            return " ".join(data_parts[1:] + [data_parts[0]])
            
        self.data["Name"] = self.data["Name"].apply(lambda n: fix(n))
    
    def fix_birthyear(self):
        def fix(data):
            new_data = data
            if str(new_data).startswith("01.01."):
                yeardigits = data[-2:]
                new_data = f"20{yeardigits}" if int(yeardigits) < 35 else f"19{yeardigits}"
            return new_data
            
        self.data["BirthYear"] = self.data["BirthYear"].apply(lambda n: fix(n))
    
    def fix_numbers(self):
        def fix(data):
            new_data = str(data)
            
            if "," in new_data:
                new_data = new_data.replace(",", ".")
                
            new_data = new_data if new_data.strip() not in constants.DQ_STRINGS else ""
            
            if new_data.strip().endswith(".0"):
                new_data = new_data[:-2]
                
            return new_data
        
        cols_to_fix = [
            "BodyweightKg", "BirthYear", "Best3SquatKg", "Best3BenchKg", "Best3DeadliftKg", "TotalKg",
            "Bench1Kg", "Bench2Kg", "Bench3Kg"
        ]
        for col in cols_to_fix:
            if col in list(self.data.columns):
                self.data[col] = self.data[col].apply(lambda n: fix(n))
    
    def fix_places(self):
        if self.division == "Team":
            for i_row in range(len(self.data)):
                row_data = self.data.iloc[i_row]
                row_name = row_data.name
                
                for index in list(self.unused_rows.keys()):
                    if int(row_name) < index:
                        new_place, new_team = self.unused_rows[index].split(" - ")
                        if self.data["Place"].iloc[i_row] not in constants.DQ_STRINGS + constants.DD_STRINGS:
                            self.data["Place"].iloc[i_row] = new_place
                        self.data["Team"].iloc[i_row] = new_team
                        break
        
        for i_row in range(len(self.data)):
            place = str(self.data["Place"].iloc[i_row])
            total = self.data["TotalKg"].iloc[i_row]
            new_place = place if place.strip() not in constants.DQ_STRINGS else ("DQ" if total not in constants.DD_STRINGS else "DD")
            if new_place.strip().endswith(".0"): new_place = new_place[:-2]
            self.data.iloc[i_row, 0] = new_place
    
    def fix_divisions(self):
        if self.division == "Masters":
            for i_row in range(len(self.data)):
                row_data = self.data.iloc[i_row]
                row_name = row_data.name
                
                for index in list(self.unused_rows.keys()):
                    if int(row_name) < index:
                        self.data["Division"].iloc[i_row] = self.unused_rows[index]
                        break
    
    def convert(self):
        self.remove_unused_rows()
        
        self.fix_headers()
        self.remove_unused_cols()
        
        self.fix_numbers()
        self.fix_lifter_names()
        self.fix_birthyear()
        
        self.add_essential_cols()
        
        self.fix_places()
        self.fix_divisions()
        
    def get_data(self):
        return self.data
    
    def print_data(self):
        print(self.data.to_string(index=False))

