"""
Data Management Usage Examples

This script demonstrates how to use the data management system.
"""

from data_management import (
    add_submission,
    get_all_submissions,
    get_submissions_by_roll,
    get_submission_stats,
    export_to_csv
)


def example_1_view_all_submissions():
    """View all submissions in the database"""
    print("\n" + "="*60)
    print("Example 1: View All Submissions")
    print("="*60 + "\n")

    df = get_all_submissions()
    print(df.to_string(index=False))
    print(f"\nTotal submissions: {len(df)}")


def example_2_add_new_submission():
    """Add a new submission to the database"""
    print("\n" + "="*60)
    print("Example 2: Add New Submission")
    print("="*60 + "\n")

    success = add_submission(
        roll_number="2021010",
        name="Test Student",
        coursera_link="https://coursera.org/verify/test123",
        linkedin_link="https://www.linkedin.com/posts/test-student-123",
        status="PASS",
        reason="LinkedIn post mentions the Coursera project."
    )

    if success:
        print("\n✓ Submission added successfully!")
        print("\nUpdated database:")
        df = get_all_submissions()
        print(df.tail().to_string(index=False))


def example_3_get_statistics():
    """Get submission statistics"""
    print("\n" + "="*60)
    print("Example 3: View Statistics")
    print("="*60 + "\n")

    stats = get_submission_stats()

    print(f"Total Submissions: {stats['total']}")
    print(f"Unique Students: {stats['unique_students']}")
    print(f"\nStatus Breakdown:")
    print(f"  PASS: {stats['pass']}")
    print(f"  FAIL: {stats['fail']}")
    print(f"  INVALID: {stats['invalid']}")

    if stats['total'] > 0:
        pass_rate = (stats['pass'] / stats['total']) * 100
        print(f"\nPass Rate: {pass_rate:.1f}%")


def example_4_search_by_roll():
    """Search submissions by roll number"""
    print("\n" + "="*60)
    print("Example 4: Search by Roll Number")
    print("="*60 + "\n")

    roll_number = "2021001"
    df = get_submissions_by_roll(roll_number)

    if len(df) > 0:
        print(f"Found {len(df)} submission(s) for roll number {roll_number}:")
        print(df.to_string(index=False))
    else:
        print(f"No submissions found for roll number {roll_number}")


def example_5_export_data():
    """Export data to a custom CSV file"""
    print("\n" + "="*60)
    print("Example 5: Export Data")
    print("="*60 + "\n")

    output_file = "data_management/exported_data.csv"
    success = export_to_csv(output_file)

    if success:
        print(f"\n✓ Data exported to {output_file}")


def main():
    """Run all examples"""

    print("\n" + "="*60)
    print("  DATA MANAGEMENT SYSTEM - USAGE EXAMPLES")
    print("="*60)

    # Run examples
    example_1_view_all_submissions()
    example_2_add_new_submission()
    example_3_get_statistics()
    example_4_search_by_roll()
    example_5_export_data()

    print("\n" + "="*60)
    print("  All examples completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
