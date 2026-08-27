import pandas as pd
import argparse
import os
import sys
from datetime import datetime

# Import data_manager for standardization
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_management.data_manager import DATA_FILE, initialize_data_file, data_lock

def sync_submissions(import_csv_path):
    """
    Reads records from the provided CSV and appends any new, non-duplicate 
    submissions to data.csv.
    """
    print(f"Reading new submissions from: {import_csv_path}")
    try:
        new_df = pd.read_csv(import_csv_path)
    except Exception as e:
        print(f"Failed to read file: {e}")
        return

    # Ensure data.csv exists and is initialized
    if not os.path.exists(DATA_FILE):
        initialize_data_file()
        
    with data_lock:
        try:
            existing_df = pd.read_csv(DATA_FILE, dtype={"Roll Number": str})
        except Exception as e:
            print(f"Failed to read {DATA_FILE}: {e}")
            return
            
        # Standardize 'Roll Number' formatting (remove .0 from floats, trim whitespace)
        new_df['Roll Number'] = new_df['Roll Number'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        existing_df['Roll Number'] = existing_df['Roll Number'].fillna('').astype(str).str.strip()
        
        # Standardize other columns
        expected_cols = [
            'Coursera completion certificate link', 
            'LinkedIn Post Link', 
            'Email Address', 
            'Full Name', 
            'Timestamp'
        ]
        
        for col in expected_cols:
            if col in new_df.columns:
                new_df[col] = new_df[col].fillna('').astype(str).str.strip()
            else:
                new_df[col] = ''
        
        # Identify unique rows using Roll Number, Coursera link, and LinkedIn link
        merge_cols = ['Roll Number', 'Coursera completion certificate link', 'LinkedIn Post Link']
        
        # Create a set of existing keys to efficiently check for duplicates O(1)
        existing_keys = set(zip(
            existing_df[merge_cols[0]], 
            existing_df[merge_cols[1]], 
            existing_df[merge_cols[2]]
        ))
        
        records_to_add = []
        now = datetime.now()
        current_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        duplicates = 0
        for _, row in new_df.iterrows():
            roll = row['Roll Number']
            c_link = row['Coursera completion certificate link']
            l_link = row['LinkedIn Post Link']
            
            # Skip invalid or empty roll numbers
            if not roll or roll == 'nan':
                continue
                
            key = (roll, c_link, l_link)
            if key not in existing_keys:
                # Prepare a new record matching data.csv structure 
                records_to_add.append({
                    "Timestamp": current_timestamp,
                    "Email Address": row['Email Address'],
                    "Full Name": row['Full Name'],
                    "Roll Number": roll,
                    "Coursera completion certificate link": c_link,
                    "LinkedIn Post Link": l_link,
                    "Project": "-", # Default
                    "Submitted At": row['Timestamp'],
                    "Status": "", # Un-evaluated 
                    "Reason": ""
                })
                # Add to set so intra-file duplicates are also skipped
                existing_keys.add(key)
            else:
                duplicates += 1
                
        if records_to_add:
            print(f"Found {len(records_to_add)} new records. Appending to {DATA_FILE}...")
            added_df = pd.DataFrame(records_to_add)
            
            # Concat the old and new dataframes
            updated_df = pd.concat([existing_df, added_df], ignore_index=True)
            
            # Match the data_manager sort order
            updated_df = updated_df.sort_values("Roll Number")
            
            # Save updating file
            updated_df.to_csv(DATA_FILE, index=False)
            print(f"[OK] Successfully added {len(records_to_add)} records. {duplicates} records were skipped as duplicates.")
        else:
            print(f"[OK] No new records to add. All entries are already present. {duplicates} duplicate records skipped.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Synchronize Google Forms CSV mapped submissions with data.csv")
    parser.add_argument("csv_file", help="Path to the Google Forms submissions CSV file")
    args = parser.parse_args()
    
    if os.path.exists(args.csv_file):
        sync_submissions(args.csv_file)
    else:
        print(f"Error: Could not find file {args.csv_file}")
