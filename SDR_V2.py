import pandas as pd
from openpyxl import load_workbook
import numpy as np
from openpyxl.utils import column_index_from_string #(row,column) to column index formula = ((r - 1) * 12 + c) + 1 maybe use df.iat for finding the values

#helper functions | start:
def find_first_blank(df, col_index, start_row):
    # Select the part of the series starting from the given row
    series_part = df.iloc[start_row:, col_index]
    
    # Find the index of the first NaN (blank) value
    blank_index = series_part.index[series_part.isnull()].min()

    return blank_index

def extract_num(s):
    """
    Extracts the number from the end of a string.

    Args:
    - s (str): The input string.

    Returns:
    - int: The extracted number if present, None otherwise.
    """
    i = len(s) - 1
    while i >= 0 and s[i].isdigit():
        i -= 1

    if i < len(s) - 1:
        return int(s[i+1:])
    else:
        return None
#helper functions | end

#constants that can be changed with config
time_col_name = "Time [s]"
time_col_index = 1 #zero-indexed
data_cols = "B:CU"

#user input | star:
XDC_file = input("Enter the XDC sheet filename: ").strip()

    #ask for number of assays
number_of_assays = int(input("Enter the number of assays you would like to load: ").strip())

    #ask for assay 1 -- n file paths
assay_file_list = []
for i in range(number_of_assays):
    assay_file_list.append(input(f"Enter the filename for assay{i + 1}: ").strip())
#user inout | end:

#read sample information | start:
sample_info = pd.read_excel(
    XDC_file,
    header = None,
    sheet_name = "Sample",
    skiprows = 1,
    usecols = "A:D"
)
#read sample information | end

#generate dataframes | start:
dataframe_list = []

for i in range(number_of_assays):
    raw = pd.read_excel(assay_file_list[i])
    locations = (raw.where(raw == time_col_name).stack().index.tolist()) #used to locate where the data starts
    blank = pd.DataFrame()
    for j in range(len(locations)): #this loop is for sheets with multiple data sets
        num_skiprows = locations[j][0] + 2 
        num_read_rows = (find_first_blank(raw, time_col_index, locations[j][0]) - locations[j][0] - 1)
        read_cols = data_cols
        temp = pd.read_excel(
            assay_file_list[i],
            header = None, 
            skiprows = num_skiprows,
            nrows = num_read_rows,
            usecols = read_cols
        )
        blank = pd.concat([blank,temp])
    dataframe_list.append(blank)
#generate dataframes | end

#build final dataframe | start:
output = pd.DataFrame()
current_measurement = -1
for i in range(len(sample_info)):
    #extracting the information from the df
    sample_id = sample_info.iat[i,0]
    row = int(sample_info.iat[i,1])
    column = int(sample_info.iat[i,2])
    assay_id = sample_info.iat[i,3]
    
    #processing info
    assay_read_col = (row - 1) * 12 + column + 1
    assay_num = extract_num(assay_id) - 1
    working_df = dataframe_list[assay_num].iloc[:, [0,assay_read_col]].copy() #time and value cols
    
    
    
    #signal label
    signals = []
    num_rows_per_signal = int(len(working_df) / len(locations))
    for j in range(len(locations)):
        for k in range(num_rows_per_signal):
            signals.append(f"Signal{j + 1}")
    working_df.insert(0, "Signal ID", signals)
    
    #sample label
    sample_ids = [sample_id] * len(working_df)
    working_df.insert(0, "Sample ID", sample_ids)

    #measurement label
    measurement_ids = []
    for j in range(len(working_df)):
        current_measurement += 1
        measurement_ids.append(f"Measurement{current_measurement}")
    working_df.insert(0, "Measurement ID", measurement_ids)
    standard_cols = ['Measurement ID', 'Sample ID', 'Signal ID', 'Time', 'Value']
    working_df.columns = standard_cols
    #adding working df to output
    output = pd.concat([output, working_df], ignore_index=True)
#build final dataframe | end

#write to xdc sheet
book = load_workbook(XDC_file)
with pd.ExcelWriter(XDC_file, engine = 'openpyxl') as writer:
    writer.book = book

    # Write the cleaned data to the output Excel sheet without overwriting
    output.to_excel(writer, sheet_name = "Measurement", index = False, header = False, startrow = 1 , startcol = 0 )


