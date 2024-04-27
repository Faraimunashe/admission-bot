import re

def validate_subject_grade(string):
    pattern = r'^[A-Za-z\s]+,[a-z]$'
    return re.match(pattern, string) is not None


def is_integer(input_str):
    return input_str.isdigit()

def is_float(input_str):
    try:
        float(input_str)
        return True
    except ValueError:
        return False
    

def validate_zimbabwe_number(number):
    zimbabwe_pattern = re.compile(r'^0(?:7(?:[17]\d{7}|[8]\d{8}))$')
    if zimbabwe_pattern.match(number):
        return True
    else:
        return False
    

def compare_symbols(symbol1, symbol2):
    hierarchy = {'A': 7, 'B': 6, 'C': 5, 'D': 4, 'E': 3, 'F': 2, 'U': 1}
    return hierarchy.get(symbol1, 0) >= hierarchy.get(symbol2, 0)