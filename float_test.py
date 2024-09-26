# Generated (mostly) by ChatGPT
# Tests if are there any defects with non-integer coordinates or dimensions

import os
import pandas as pd

# Function to check if a column contains non-integer values
def check_for_non_integer(df, column):
    return df[column].apply(lambda x: x != int(x)).any()

# Path to the main datasets folder
base_path = 'datasets'

# Loop through all subdirectories and files
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('defects.csv'):  # Check only defect.csv files
            file_path = os.path.join(root, file)
            
            # Read the CSV file
            df = pd.read_csv(file_path, sep=';')
            
            # Columns to check
            columns_to_check = ['X', 'Y', 'WIDTH', 'HEIGHT']
            
            # Check each column and print the result
            for column in columns_to_check:
                if check_for_non_integer(df, column):
                    print(f"File {file_path}: Column {column} contains non-integer values.")
                else:
                    pass
                    # print(f"File {file_path}: Column {column} contains only integer values.")
