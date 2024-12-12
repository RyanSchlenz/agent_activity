import pandas as pd
import os

# List of CSV files to convert
csv_files = ['aggregated_data.csv', 'calculate_time.csv']  # Replace with your CSV file paths

# Loop through each CSV file and convert it to a separate Excel file
for csv_file in csv_files:
    # Extract the base name (without extension) for naming the output file
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    xlsx_file = f'{base_name}.xlsx'  # Define the output Excel file path in the current directory

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Write the DataFrame to a separate Excel file
    df.to_excel(xlsx_file, index=False, engine='openpyxl')

    # Confirmation message for each conversion
    print(f"CSV file '{csv_file}' has been successfully converted to '{xlsx_file}'")