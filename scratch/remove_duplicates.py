import pandas as pd
import os

def remove_duplicates():
    data_file = os.path.join("../data_management", "data.csv")
    backup_file = os.path.join("../data_management", "data_backup.csv")
    
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found.")
        return

    try:
        # 1. Load the database
        df = pd.read_csv(data_file, dtype={"Roll Number": str})
        original_count = len(df)
        
        # Create a backup just in case
        df.to_csv(backup_file, index=False)
        print(f"Backup created at {backup_file}")

        # 2. Normalize identifying columns for comparison
        # We'll create temporary columns for matching so we don't change the original formatting
        df["_match_roll"] = df["Roll Number"].fillna("").astype(str).str.strip()
        df["_match_project"] = df["Project"].fillna("").astype(str).str.strip().str.lower()
        df["_match_status"] = df["Status"].fillna("").astype(str).str.strip().str.upper()

        # 3. Handle PASS duplicates specifically
        # We only want to enforce uniqueness for (Roll Number, Project) if Status is PASS
        
        is_pass = df["_match_status"] == "PASS"
        is_val_project = df["_match_project"] != "-"
        
        pass_df = df[is_pass & is_val_project].copy()
        other_df = df[~(is_pass & is_val_project)].copy()
        
        # Drop duplicates in PASS records, keeping the first one found (usually the oldest)
        cleaned_pass_df = pass_df.drop_duplicates(subset=["_match_roll", "_match_project"], keep="first")
        
        # 4. Recombine
        final_df = pd.concat([cleaned_pass_df, other_df], ignore_index=True)
        
        # 5. Clean up temporary columns
        final_df = final_df.drop(columns=["_match_roll", "_match_project", "_match_status"])
        
        # 6. Sort by Roll Number for consistency
        final_df["Roll Number"] = final_df["Roll Number"].astype(str)
        final_df = final_df.sort_values("Roll Number")

        # 7. Save back
        final_df.to_csv(data_file, index=False)
        
        removed_count = original_count - len(final_df)
        print(f"\nSuccess!")
        print(f"Original records: {original_count}")
        print(f"Cleaned records:  {len(final_df)}")
        print(f"Removed duplicates: {removed_count}")
        print(f"Updated database saved to {data_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    remove_duplicates()
