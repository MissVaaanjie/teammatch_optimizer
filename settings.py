import os


class CONFIG:

    team_name = "team5"

    # General model settings
    optimizer_name = "highspy"  # Options: "highspy", "SCIP"
    constraint6_included = True  # Enable constraint for consecutive heats
    output_enabled = True  # Enable output printed by solver
    presolve_enabled = True

    # File paths
    data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'data')
    input_data = os.path.join(data_folder, '0_input')
    processed_data = os.path.join(data_folder, '1_processed')
    output_data = os.path.join(data_folder, '2_output')

    # File names
    preferences_file_name = os.path.join(input_data, "team5_preferences_v2.xlsx")
    heats_file_name = os.path.join(input_data, "heats_data.xlsx")
    heats_sheet_name = "heats"
    dancer_sheet_name = "Dancers"
    solution_file_name = os.path.join(processed_data,
                                      f'{team_name}_raw_schedule.csv')
    output_mps_name = os.path.join(processed_data, f'{team_name}_ip.mps')
    output_lp_name = os.path.join(processed_data, f'{team_name}_ip.lp')
    output_schedule_name = os.path.join(output_data,
                                        f'{team_name}_schedule.csv')

    # Objective contributions
    pref_to_score = {"favorite": 150,
                     "preference": 100,
                     "slight preference": 50,
                     "rather not": -50,
                     "highly dislike": -350,
                     "custom1": 500}
    pref_pairing_penalty = -600
    min_dance_penalty = -1000
    double_pairing_penalty = -2000
    cons_dance_penalty = -60

# Column names in input file
#     preference_col_names = ["Style", "Dance",
#                             "Lead_preference", "Follow_preference"]
#     dancers_col_names = ["Name", "Preferred partner",
#                          "Preferred dance together"]
