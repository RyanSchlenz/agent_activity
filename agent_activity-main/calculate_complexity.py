import pandas as pd

def add_complexity_column(input_file_path, output_file_path):
    # Load your cleaned ticket data
    df = pd.read_csv(input_file_path)

    # Print the column names to debug
    print("Columns in the input file:", df.columns.tolist())

    # Check if the required columns exist
    required_columns = ['Ticket group', 'Ticket subject', 'Product - Service Desk Tool', 'Assignee name', 'Tickets solved', 'Action Taken to Resolve']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("The required columns are not found in the data.")

    # Print the structure of the DataFrame
    print(df.info())
    print(df.head())

    # List of keywords to check in the Ticket subject
    keywords = [
        'Voicemail',
        'voicemail',
        'voice mail',
        'vm', 
        'Call with caller', 
        'Call With Caller', 
        'Call With', 
        'Call with Caller'
        'Abandoned Call', 
        'Abandoned call',
        'Missed Call'
        'call back',
        'CallBack',
        'callback',
        'Call Back',
        'Call back',
        'Missed Call',
        'Missed call',
        'Conversation with',
        'Unknown caller'
    ]

    # List of products that should multiply the complexity by 10 (high complexity)
    high_complexity_products = [
        'ADUC',
        'Exchange',
        'Fuze',
        'HCHB',
        'MOBI',
        'Printer/Scanner/Copier',
        'Teams',
        'Zendesk',
        'Windows',
        'Citrix',
        'Intune', 
        'Network'
    ]

    # Assign complexity levels based on the 'Ticket group', 'Ticket subject', 'Product - Service Desk Tool', and 'Action Taken to Resolve'
    def assign_complexity(ticket_group, ticket_subject, product, action_taken):
        if pd.isna(ticket_group) or pd.isna(ticket_subject):
            return None  # Return None if any required value is NaN
        ticket_groups = [group.strip() for group in ticket_group.split(',')]

        # Check for specific ticket groups
        if 'UAP' in ticket_groups:
            return 2.0
        if 'Mobile Reconciliation' in ticket_groups:
            return 5.0
        elif any(keyword.lower() in ticket_subject.lower() for keyword in keywords):
            return 0.0  # Complexity level for ticket subjects with specified keywords
        elif pd.notna(action_taken) and any(action in action_taken for action in ['Password Reset', 'Errant Fax', 'Unlocked Account', 'Create']):
            return 15.0  # Complexity level for password reset action and Errant Fax
        elif pd.notna(action_taken) and any(action in action_taken for action in ['No Action Taken', 'Automation', 'Meter Reading']):
            return 1.0  # Complexity for these actions
        elif pd.notna(action_taken) and any(action in action_taken for action in ['Access Change', 'Add/Remove from Distribution List', 'Account Change', 'Updated DL Group', 'Added License', 'Add to Allowlist', 'Account Locked', 'HCHB', 'Contractor/Volunteer Set-Up', 'Day 1 Concierge']):
            return 20.0  # Complexity for these actions
        elif product in high_complexity_products:
            return 75.0  # Complexity level for high complexity products
        else:
            return 25.0  # Default complexity level for other groups

    # Apply the complexity function
    df['Complexity'] = df.apply(lambda row: assign_complexity(
        row['Ticket group'], 
        row['Ticket subject'], 
        row['Product - Service Desk Tool'], 
        row.get('Action Taken to Resolve')), axis=1)

    # Categorize complexity levels into Low, Medium, and High
    def categorize_complexity(points):
        if points < 15:
            return 'Low'
        elif points <= 25:
            return 'Medium'
        else:
            return 'High'

    df['Complexity Category'] = df['Complexity'].apply(categorize_complexity)

    # Print required details: Ticket ID, Assignee name, Category, Points
    print("\nTicket details with complexity levels:\n")
    for index, row in df.iterrows():
        print(f"Ticket ID: {row['Ticket ID']}, Assignee: {row['Assignee name']}, Category: {row['Complexity Category']}, Points: {row['Complexity']}")

    # Save the updated DataFrame to a new CSV file
    df.to_csv(output_file_path, index=False)
    print(f"Updated ticket data with complexity levels saved to {output_file_path}")

if __name__ == "__main__":
    input_file = 'ticket_data.csv'  # Replace with your actual input file path
    output_file = 'complexity_data.csv'  # Specify the output file path
    add_complexity_column(input_file, output_file)