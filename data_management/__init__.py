"""
Data Management Package

Handles all data operations for the submission system.
"""

from .data_manager import (
    initialize_data_file,
    add_submission,
    get_all_submissions,
    get_submissions_by_roll,
    get_submission_stats,
    export_to_csv,
    check_duplicate_submission,
    get_cached_evaluation_results,
    get_cached_result_for_submission,
    save_evaluation_result,
    DATA_FILE
)

__all__ = [
    'initialize_data_file',
    'add_submission',
    'get_all_submissions',
    'get_submissions_by_roll',
    'get_submission_stats',
    'export_to_csv',
    'check_duplicate_submission',
    'get_cached_evaluation_results',
    'get_cached_result_for_submission',
    'save_evaluation_result',
    'DATA_FILE'
]
