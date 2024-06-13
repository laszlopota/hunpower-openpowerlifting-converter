import os


PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEADERS = {
    "rnk":     "Place",
    "lifters": "Name",
    "name":    "Name",
    "team":    "Team",
    "d.o.b.":  "BirthYear",
    "bwt":     "BodyweightKg",
    "result":  "TotalKg",
    "total":   "TotalKg",
    "1 att.":  "Bench1Kg",
    "2 att.":  "Bench2Kg",
    "3 att.":  "Bench3Kg",
    "sq":      "Best3SquatKg",
    "bp":      "Best3BenchKg",
    "dl":      "Best3DeadliftKg",
}

SEX = ["F", "M", "Mx"]
DIVISION = ["Masters", "Open", "Juniors", "Sub-Juniors", "Team"]
EVENT =  ["SBD", "B", "D"]
EQUIPMENT = ["Raw", "Single-ply"]

WEIGHT_CLASSES = {
    "M":  ["59", "66", "74", "83", "93", "105", "120", "120+"],
    "F":  ["47", "52", "57", "63", "69", "76", "84", "84+"],
    "Mx": ["1"],
}

YOUNG_WEIGHT_CLASS = {
    "M":  "53",
    "F":  "43",
    "Mx": "0",
}

DQ_STRINGS = ["DQ", "DSQ", "-", "—", "OUT", "x", "X"]
DD_STRINGS = ["DD"]

TEXT_TO_REPLACE = {
    "û": "ű",
    "õ": "ő",
    "ifj.": "",
    "Dr.": "",
    "dr.": "",
    ".": "",
}
