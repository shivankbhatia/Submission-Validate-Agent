import pandas as pd
import os

def check_for_duplicates():
    data_file = os.path.join("../data_management", "data.csv")
    
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found.")
        return

    try:
        # Read the database
        df = pd.read_csv(data_file, dtype={"Roll Number": str})
        
        # Clean data
        df["Roll Number"] = df["Roll Number"].fillna("").astype(str).str.strip()
        df["Project"] = df["Project"].fillna("").astype(str).str.strip().str.lower()
        df["Status"] = df["Status"].fillna("").astype(str).str.strip().str.upper()

        # We care about multiple PASS records for the same student and same project
        pass_records = df[df["Status"] == "PASS"]
        
        if pass_records.empty:
            print("No PASS records found in the database.")
            return

        # Find duplicates based on Roll Number and Project title
        # (excluding cases where project is '-')
        valid_pass_records = pass_records[pass_records["Project"] != "-"]
        
        duplicates = valid_pass_records[valid_pass_records.duplicated(subset=["Roll Number", "Project"], keep=False)]
        
        if duplicates.empty:
            print("No duplicate PASS solutions (same student, same project) found.")
        else:
            # Count unique pairs that have duplicates
            unique_duplicate_pairs = duplicates.groupby(["Roll Number", "Project"]).size()
            total_cases = len(unique_duplicate_pairs)
            total_extra_records = len(duplicates) - total_cases
            
            print(f"Found {total_cases} students who have multiple PASS records for the same project.")
            print(f"Total extra duplicate records: {total_extra_records}")
            
            print("\nDetailed list of duplicates:")
            print("-" * 60)
            for (roll, project), count in unique_duplicate_pairs.items():
                print(f"Roll: {roll} | Project: {project} | Records: {count}")
            print("-" * 60)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    check_for_duplicates()
