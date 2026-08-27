import pandas as pd
from datetime import datetime, timedelta
import os

def reset_entries():
    file_path = r'c:\Users\bhati\OneDrive\Documents\6th Sem\6th Sem\DS1\agentic_evaluator\data_management\data.csv'
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path)
    
    # Target timestamp
    target_time_str = "2026-04-19 00:36:11"
    target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
    
    # 2 minute range
    start_range = target_time - timedelta(minutes=2)
    end_range = target_time + timedelta(minutes=2)
    
    print(f"Targeting records between {start_range} and {end_range}")
    
    # Convert Timestamp column to datetime
    # We use errors='coerce' to handle any malformed dates
    df['dt_temp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    
    # Mask for records in range
    mask = (df['dt_temp'] >= start_range) & (df['dt_temp'] <= end_range)
    
    affected_count = mask.sum()
    print(f"Found {affected_count} records in range.")
    
    if affected_count > 0:
        # Reset Status, Reason, and Project
        # Based on backend logic, Status == "" or Project == "-" makes them "new"
        df.loc[mask, 'Status'] = ""
        df.loc[mask, 'Reason'] = ""
        df.loc[mask, 'Project'] = "-"
        
        # Remove temp column
        df = df.drop(columns=['dt_temp'])
        
        # Save back to CSV
        df.to_csv(file_path, index=False)
        print(f"Successfully reset {affected_count} records.")
    else:
        print("No records found in the specified range. No changes made.")

if __name__ == "__main__":
    reset_entries()
