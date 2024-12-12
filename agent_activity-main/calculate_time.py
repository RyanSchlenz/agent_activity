import pandas as pd

# Load the CSV file
file_path = 'individual_complexity_data.csv'  # Change this to your input file path
df = pd.read_csv(file_path)

# Group by 'Date' and 'Agent', then sum the 'Points'
grouped_df = df.groupby(['Date', 'Agent'])['Points'].sum().reset_index()

# Convert Points to hours and round to the nearest tenth
grouped_df['Hours'] = (grouped_df['Points'] / 60).clip(upper=9).round(1)

# Sort by Agent and Date
grouped_df.sort_values(by=['Agent', 'Date'], inplace=True)

# Create a new DataFrame for the output
output_df = pd.DataFrame()

# Iterate through the grouped DataFrame and add blank rows as needed
current_agent = None
for _, row in grouped_df.iterrows():
    if row['Agent'] != current_agent:
        if current_agent is not None:  # If not the first agent, add total row
            # Calculate total hours and unique date count for the previous agent
            total_hours = grouped_df[grouped_df['Agent'] == current_agent]['Hours'].sum()
            unique_dates_count = grouped_df[grouped_df['Agent'] == current_agent]['Date'].nunique()
            
            # Calculate average hours per day
            average_hours = (total_hours / unique_dates_count).round(1) if unique_dates_count > 0 else 0
            
            # Create total row with average hours
            total_row = pd.DataFrame({'Date': ['Average'], 'Agent': [current_agent], 'Hours': [average_hours]})
            output_df = pd.concat([output_df, total_row], ignore_index=True)

            # Add a blank row after the total row
            output_df = pd.concat([output_df, pd.DataFrame({'Date': [''], 'Agent': [''], 'Hours': ['']})], ignore_index=True)

        current_agent = row['Agent']  # Update current agent
    
    # Append the current row to the output DataFrame
    output_df = pd.concat([output_df, row.to_frame().T], ignore_index=True)

# Calculate total hours and average for the last agent
if current_agent is not None:
    total_hours = grouped_df[grouped_df['Agent'] == current_agent]['Hours'].sum()
    unique_dates_count = grouped_df[grouped_df['Agent'] == current_agent]['Date'].nunique()
    average_hours = (total_hours / unique_dates_count).round(1) if unique_dates_count > 0 else 0
    total_row = pd.DataFrame({'Date': ['Average'], 'Agent': [current_agent], 'Hours': [average_hours]})
    output_df = pd.concat([output_df, total_row], ignore_index=True)

    # Add a blank row after the total row for the last agent
    output_df = pd.concat([output_df, pd.DataFrame({'Date': [''], 'Agent': [''], 'Hours': ['']})], ignore_index=True)

# Save the result to a new CSV file
output_file_path = 'calculate_time.csv'  # Change this to your output file path
output_df.to_csv(output_file_path, index=False)

print("Total hours per day for each agent have been calculated and saved to", output_file_path)
