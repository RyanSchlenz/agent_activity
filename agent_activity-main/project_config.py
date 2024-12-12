config = {
    'scripts': [
        'calculate_complexity.py',
        'individual_categories.py',
        'aggregate_data.py',
        'calculate_time.py',
        'convert.py'
    ],
    'csv_files': [
        'complexity_data.csv',
        'individual_complexity_data.csv',
        'calculate_time.csv',
        'aggregated_data.csv',
        'aggregated_data.xlsx',
        'calculate_time.xlsx'
    ],
    'output_files': {
        'calculate_complexity.py': ['complexity_data.csv'],
        'individual_categories.py': ['individual_complexity_data.csv'],
        'aggregate_data.py': ['aggregated_data.csv'],
        'calculate_time.py': ['calculate_time.csv'],
        'convert.py': ['calculate_time.xlsx', 'aggregated_data.xlsx']  # Add output files if applicable
    }
}
