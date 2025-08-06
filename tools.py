from agents import Agent, Runner, trace, function_tool
from utilities import import_2023_results, import_2024_results, import_2025_results

@function_tool
def get_2025_number_of_children():
    """
    Get the number of children on the programme in 2024
    """
    initial_df, midline_df = import_2025_results()
    number_of_children = len(midline_df)
    return number_of_children