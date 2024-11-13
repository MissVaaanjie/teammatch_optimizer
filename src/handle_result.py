import pandas as pd
import re
from settings import CONFIG


def parse_data(sol_df, heat_dict):
    # Initialize lists to hold the parsed data for the DataFrame
    round_list = []
    heat_list = []
    dance_list = []
    lead_list = []
    follow_list = []

    # Initialize the dictionary for x_sol
    x_sol = {}

    # Iterate over each row in the DataFrame
    for _, row in sol_df.iterrows():
        # Check if the row starts with "x_"
        if row[0].startswith('x_'):
            # Use regular expression to extract the relevant data
            match_exp = r'x_\(([^,]+),\s*([^,]+),\s*\(([^,]+),\s*([^\)]+)\)\)'
            match = re.match(match_exp, row[0])
            if match:
                lead = match.group(1).strip().replace("_", " ")
                follow = match.group(2).strip().replace("_", " ")
                heat = match.group(3).strip()
                dance = match.group(4).strip()

                # Replace all the underscores in the dance name with spaces
                dance = dance.replace("_", " ")

                # Find the corresponding dance round
                round = [heat_iter.round for heat_iter in heat_dict.values()
                         if heat_iter.heat_no == int(heat)]

                # Append to lists for DataFrame
                round_list.append(round[0])
                heat_list.append(heat)
                dance_list.append(dance)
                lead_list.append(lead)
                follow_list.append(follow)

                # Populate the dictionary
                x_sol[(heat, dance)] = (lead, follow)

    # Create a pandas DataFrame from the lists
    df_result = pd.DataFrame({
        'Round': round_list,
        'Heat': heat_list,
        'Dance': dance_list,
        'Lead': lead_list,
        'Follow': follow_list
    })

    return x_sol, df_result


def write_solution(heat_dict, delimiter=";"):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(CONFIG.solution_file_name,
                     header=None,
                     sep=";")

    # Convert data to a format you can work with
    # The dictionary can be used to calculate statistics
    _, schedule = parse_data(df, heat_dict)

    schedule.to_csv(CONFIG.output_schedule_name,
                    index=False,
                    sep=delimiter)
