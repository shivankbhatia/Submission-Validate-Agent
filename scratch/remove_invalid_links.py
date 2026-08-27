import pandas as pd
import os

def clean_data():
    file_path = r'c:\Users\bhati\OneDrive\Documents\6th Sem\6th Sem\DS1\agentic_evaluator\data_management\data.csv'
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path)
    
    initial_count = len(df)
    
    # Target column name from observation
    target_column = 'Project'
    
    if target_column not in df.columns:
        print(f"Error: Column '{target_column}' not found in CSV.")
        print(f"Available columns: {list(df.columns)}")
        return

    # Remove records where the link is '-'
    # Also handling potential leading/trailing whitespace just in case
    df_cleaned = df[df[target_column].astype(str).str.strip() != '-']
    
    removed_count = initial_count - len(df_cleaned)
    
    print(f"Initial records: {initial_count}")
    print(f"Records removed: {removed_count}")
    print(f"Final records: {len(df_cleaned)}")
    
    # Save the cleaned data back to the same file
    df_cleaned.to_csv(file_path, index=False)
    print(f"Cleaned data saved to {file_path}")

if __name__ == "__main__":
    clean_data()
