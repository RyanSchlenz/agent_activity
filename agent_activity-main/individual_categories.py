import pandas as pd

def add_complexity_column(input_file_path, output_file_path):
    # Load your cleaned ticket data
    df = pd.read_csv(input_file_path)

    # Print the column names to debug
    print("Columns in the input file:", df.columns.tolist())

    # Check if the required columns exist
    required_columns = [
        'Ticket group', 
        'Ticket subject', 
        'Product - Service Desk Tool', 
        'Assignee name', 
        'Tickets solved', 
        'Action Taken to Resolve',
        'Ticket solved - Date'  # Added to ensure this column exists
    ]
    if not all(col in df.columns for col in required_columns):
        raise ValueError("The required columns are not found in the data.")

    # Print the structure of the DataFrame
    print(df.info())
    print(df.head())

    # Ensure 'Ticket solved - Date' is a datetime type
    df['Ticket solved - Date'] = pd.to_datetime(df['Ticket solved - Date'], errors='coerce')

    # Filter out rows where the 'Ticket solved - Date' is NaT (invalid dates)
    df = df[df['Ticket solved - Date'].notna()]

    # List of keywords to check in the Ticket subject
    keywords = [
        'Voicemail',
        'voicemail',
        'voice mail',
        'vm', 
        'Call with caller', 
        'Call With Caller', 
        'Call With', 
        'Call with Caller',
        'Abandoned Call', 
        'Abandoned call',
        'Missed Call',
        'call back',
        'CallBack',
        'callback',
        'Call Back',
        'Call back',
        'Missed call',  
        'Conversation with',
        'Unknown caller'
    ]

    # Count unique days where more than 5 tickets were solved
    def count_valid_days(group):
        # For each Assignee, count days where more than 5 tickets were solved
        daily_ticket_count = group.groupby('Ticket solved - Date')['Tickets solved'].sum()
        valid_days = daily_ticket_count[daily_ticket_count > 5].count()  # Count only days with more than 5 tickets
        return valid_days

    # Filter the DataFrame to include only dates where total tickets solved are greater than 5
    df_filtered = df.groupby(['Ticket solved - Date', 'Assignee name']).filter(
        lambda x: x['Tickets solved'].sum() > 5
    )

    # List of products that should multiply the complexity by 10 (high complexity)
    high_complexity_products = [
        'ADUC', 'Exchange', 'Fuze', 'HCHB', 'MOBI',
        'Printer/Scanner/Copier', 'Teams', 'Zendesk',
        'Windows', 'Citrix', 'Intune', 'Network'
    ]

    # Assign complexity levels and their sources
    def assign_complexity(ticket_group, ticket_subject, product, action_taken):
        if pd.isna(ticket_group) or pd.isna(ticket_subject):
            return None, None  # Return None if any required value is NaN

        ticket_groups = [group.strip() for group in ticket_group.split(',')]
        complexity = None  # To track the complexity score
        actual_value = None  # To track the actual value used for categorization

        # Check for specific ticket groups
        if 'UAP' in ticket_groups:
            complexity = 2.0
            actual_value = ticket_group  # Use the ticket group directly
        if 'Mobile Reconciliation' in ticket_groups:
            complexity = 5.0
            actual_value = ticket_group  # Use the ticket group directly
        elif any(keyword.lower() in ticket_subject.lower() for keyword in keywords):
            complexity = 0.0
            actual_value = ticket_subject  # Use the ticket subject directly
        elif pd.notna(action_taken) and any(action in action_taken for action in ['Password Reset', 'Errant Fax', 'Unlocked Account', 'Create']):
            complexity = 15.0
            actual_value = action_taken  # Use the action taken directly
        elif pd.notna(action_taken) and any(action in action_taken for action in ['No Action Taken', 'Automation', 'Meter Reading']):
            complexity = 1.0
            actual_value = action_taken  # Use the action taken directly
        elif pd.notna(action_taken) and any(action in action_taken for action in ['Terminated Employee Process', 'Account Created', 'Access Change', 'Add/Remove from Distribution List', 'Account Change', 'Updated DL Group', 'Added License', 'Add to Allowlist', 'Account Locked', 'HCHB', 'Contractor/Volunteer Set-Up', 'Day 1 Concierge']):
            complexity = 20.0
            actual_value = action_taken  # Use the action taken directly
        elif product in high_complexity_products:
            complexity = 75.0
            actual_value = product  # Use the product directly
        else:
            complexity = 25.0
            actual_value = ticket_subject  # Use the ticket subject as a fallback

        return complexity, actual_value

    # Apply the complexity function
    df_filtered[['Complexity', 'Category']] = df_filtered.apply(
        lambda row: assign_complexity(
            row['Ticket group'], 
            row['Ticket subject'], 
            row['Product - Service Desk Tool'], 
            row.get('Action Taken to Resolve')
        ), axis=1, result_type='expand'
    )

    # Categorize complexity levels into Low, Medium, and High
    def categorize_complexity(points):
        if points < 15:
            return 'Low'
        elif points <= 25:
            return 'Medium'
        else:
            return 'High'

    df_filtered['Complexity Category'] = df_filtered['Complexity'].apply(categorize_complexity)

    # Print required details: Ticket ID, Assignee name, Category, Points
    print("\nTicket details with complexity levels:\n")
    for index, row in df_filtered.iterrows():
        print(f"Ticket ID: {row['Ticket ID']}, Assignee: {row['Assignee name']}, Category: {row['Category']}, Points: {row['Complexity']}")

    # Sort by Assignee name
    df_sorted = df_filtered.sort_values(by='Assignee name')

    # Prepare for totals and blank rows
    output_data = []
    for assignee, group in df_sorted.groupby('Assignee name'):
        output_data.append(group)
        total_points = group['Complexity'].sum()
        total_row = pd.DataFrame({
            'Ticket ID': ['Total'],
            'Assignee name': [assignee],
            'Category': [''],
            'Complexity': [total_points]
        })
        output_data.append(total_row)
        output_data.append(pd.DataFrame({'Ticket ID': [''], 'Assignee name': [''], 'Category': [''], 'Complexity': ['']}))  # Blank row

        # Print total points for each assignee
        print(f"Total points for {assignee}: {total_points}")

    # Concatenate the output
    final_output = pd.concat(output_data, ignore_index=True)

    # Select relevant columns for the output
    final_output = final_output[['Ticket solved - Date','Ticket ID', 'Assignee name', 'Category', 'Complexity']].copy()
    final_output.columns = ['Date','Ticket #', 'Agent', 'Category', 'Points']

    # Save the updated DataFrame to a new CSV file
    final_output.to_csv(output_file_path, index=False)
    print(f"Updated ticket data with complexity levels saved to {output_file_path}")

if __name__ == "__main__":
    input_file = 'ticket_data.csv'  # Replace with your actual input file path
    output_file = 'individual_complexity_data.csv'  # Specify the output file path
    add_complexity_column(input_file, output_file)
