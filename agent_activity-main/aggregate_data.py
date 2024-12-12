import pandas as pd

def load_data(data_path):
    """Load the data from the CSV file."""
    return pd.read_csv(data_path)

def aggregate_data(df):
    """Aggregate the data to calculate required metrics per Assignee."""

    # Calculate total tickets solved per Assignee (sum the tickets)
    total_tickets_df = df.groupby('Assignee name', as_index=False).agg({
        'Tickets solved': 'sum'
    })

    # Count unique days where more than 5 tickets were solved
    def count_valid_days(group):
        # For each Assignee, count days where more than 5 tickets were solved
        daily_ticket_count = group.groupby('Ticket solved - Date')['Tickets solved'].sum()
        valid_days = daily_ticket_count[daily_ticket_count > 5].count()  # Count only days with more than 3 tickets
        return valid_days

    # Apply the count_valid_days function to each Assignee
    total_days_df = df.groupby('Assignee name').apply(count_valid_days).reset_index(name='Total Days Worked')

    # Adjust 'Total Days Worked' for "Ryan Schlenz" by subtracting 2 hours a day from total days worked (30 days, 60 hours total, divide 60/8) subtract 7.5 days worked
    total_days_df.loc[total_days_df['Assignee name'] == 'Ryan Schlenz', 'Total Days Worked'] -= 7.5

    # Merge total tickets solved and total valid days worked
    merged_df = pd.merge(total_tickets_df, total_days_df, on='Assignee name')

    # Calculate daily solved ticket average:
    # Tickets solved / Total days worked (where more than 3 tickets were solved)
    # Avoid division by zero in case someone has no valid workdays
    merged_df['Daily Solved Ticket Average'] = (merged_df['Tickets solved'] / merged_df['Total Days Worked'].replace(0, 1)).round(1)

    # Calculate mean complexity score per Assignee
    complexity_df = df.groupby('Assignee name', as_index=False).agg({
        'Complexity': 'mean'
    })
    complexity_df['Complexity'] = complexity_df['Complexity'].round(1)

    # Merge the complexity score into the result
    merged_df = pd.merge(merged_df, complexity_df, on='Assignee name')

    # Assign complexity categories
    merged_df['Mean Complexity Category'] = merged_df['Complexity'].apply(classify_complexity)

    # Rename columns for clarity
    merged_df.rename(columns={
        'Assignee name': 'Assignee Name',
        'Tickets solved': 'Total Tickets Solved',
        'Complexity': 'Mean Complexity Score'
    }, inplace=True)

    return merged_df

def classify_complexity(complexity_score):
    """Classify the complexity score into a category based on the new rules."""
    if complexity_score < 15.0:
        return 'Low'
    elif complexity_score <= 25.0:
        return 'Medium'
    else:
        return 'High'

def save_results(df, output_file_path):
    """Save the aggregated data to a CSV file."""
    df.to_csv(output_file_path, index=False)
    print(f"Aggregated data saved to {output_file_path}")

def main():
    # Define file paths
    data_path = 'complexity_data.csv'  # Input file with raw data
    output_file_path = 'aggregated_data.csv'  # Output file with aggregated results

    # Load data
    df = load_data(data_path)

    # Display initial structure of the DataFrame
    print("Initial DataFrame Info:")
    print(df.info())
    print(df.head())

    # Process and aggregate data
    aggregated_df = aggregate_data(df)

    # Display final structure of the DataFrame
    print("\nAggregated DataFrame Info:")
    print(aggregated_df.info())
    print(aggregated_df.head())

    # Save final results
    save_results(aggregated_df, output_file_path)

if __name__ == "__main__":
    main()
