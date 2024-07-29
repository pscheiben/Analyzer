import pandas as pd

def add_data(data1, data2):
    return data1.add(data2, fill_value=0)

def subtract_data(data1, data2):
    return data1.subtract(data2, fill_value=0)
