from src.objects import dancer_obj, heat_obj
import pandas as pd
from settings import CONFIG


# Read excel files
def excel_to_df(file_name: str, sheet_name: str):
    return pd.read_excel(file_name, sheet_name=sheet_name)


# Convert all characters in each string in a column to lowercase
def convert_to_lowercase(column):
    return column.apply(lambda x: x.casefold()
                        if isinstance(x, str) else x)


def create_preference_dict(df, role: str, f_name: str):
    # Determine lead or follow
    if role == "Lead":
        col_names = ["Dance", "Lead_preference"]
    elif role == "Follow":
        col_names = ["Dance", "Follow_preference"]
    else:
        print("Error: invalid input for role in create_preference_dict")

    # Remove all styles the dancer doesn't want to dance
    pref_df = df[col_names].dropna()

    # Convert all preferences to lowercase to prepare for mapping
    pref_df[col_names[1]] = convert_to_lowercase(pref_df[col_names[1]])

    # Map all preferences to scores
    pref_df[col_names[1]] = pref_df[col_names[1]].map(
        pd.Series(CONFIG.pref_to_score))

    nan_detected = False
    nan_positions = pref_df.loc[pref_df[col_names[1]].isna(),
                                col_names[0]].tolist()
    if nan_positions:
        print(f"Error for {f_name}, {role}: nan at {nan_positions}")
        nan_detected = True

    # Create the preference dictionary
    pref_dict = dict(zip(pref_df["Dance"], pref_df[col_names[1]]))
    return pref_dict, nan_detected


def create_dancer(f_dancer_name: str,
                  f_pref_pair: tuple):
    # Load preference data from Excel
    dancer_pref_df = excel_to_df(CONFIG.preferences_file_name, f_dancer_name)

    nan_detected = 0
    # Create dictionary for lead preferences
    lead_pref_dict, nan_detected = create_preference_dict(dancer_pref_df,
                                                          "Lead",
                                                          f_dancer_name)

    # Create dictionary for follow preferences
    follow_pref_dict, nan_detected = create_preference_dict(dancer_pref_df,
                                                            "Follow",
                                                            f_dancer_name)

    # Create dancer object
    dancer = dancer_obj(f_dancer_name, f_pref_pair,
                        lead_pref_dict, follow_pref_dict)

    return dancer, nan_detected


def load_dancers():
    # Load the partner preference data
    dancer_df = excel_to_df(CONFIG.preferences_file_name,
                            CONFIG.dancer_sheet_name)

    # Replace all nan values by "" and rename to more concise column names
    dancer_df = dancer_df.set_index("Name", inplace=False).fillna("")
    dancer_df.rename(columns={"Preferred partner": "Partner",
                              "Preferred dance together": "Style"},
                     inplace=True)

    # Create dict of form: {dancer_name: {'Partner': dancer_name2,
    #                        'Style': style_name}}
    pref_pairings = dancer_df.to_dict('index')

    # Create a dictionary containing all dancer objects with key = dancer name
    dancer_dict = dict()
    nan_error = False
    for dancer_name in pref_pairings.keys():
        pref_pair = (pref_pairings[dancer_name]["Partner"],
                     pref_pairings[dancer_name]["Style"])
        dancer_dict[dancer_name], nan_detected = create_dancer(dancer_name,
                                                               pref_pair)
        if nan_detected:
            nan_error = True

    if nan_error:
        raise ValueError('NaNs detected. Aborting')
    return dancer_dict


def create_consecutive_heats(heats_df, heats_dict: dict):
    # Initialize empty list
    cons_dict = dict()

    # Sort dataframe in ascending order (should already be the case, but doing
    # it just to be sure)
    heats_df = heats_df.sort_values(by='heat_no', ascending=True)

    # Iterative over all rows eicluding the last row
    for i in range(len(heats_df)-1):
        if heats_df.loc[i, 'round'] == heats_df.loc[i + 1, 'round']:
            heat_no = int(heats_df.loc[i, 'heat_no'])
            heat_current = heats_dict[heats_df.loc[i, 'heat_no'],
                                      heats_df.loc[i, 'style']]
            heat_next = heats_dict[heats_df.loc[i+1, 'heat_no'],
                                   heats_df.loc[i+1, 'style']]
            cons_dict[heat_no] = (heat_current, heat_next)
    return cons_dict


def load_heats(dancer_dict):
    # Load the heats data
    heats_df = excel_to_df(CONFIG.heats_file_name, CONFIG.heats_sheet_name)

    # Create a dictionary containing all the heats data with key =
    # (heat number, style name), by looping over all rows of the heats data
    heats_dict = dict()
    for row in range(len(heats_df)):

        # Load as separate variables to keep reading concise
        style = heats_df.iloc[row]["style"]
        round = heats_df.iloc[row]["round"]
        heat_no = heats_df.iloc[row]["heat_no"]

        # Find all dancer names that can lead this style
        style_leads = [dancer.name for dancer in dancer_dict.values() if
                       style in dancer.lead_prefs.keys()]

        # Find all dancer names that can follow this style
        style_follows = [dancer.name for dancer in dancer_dict.values() if
                         style in dancer.follow_prefs.keys()]

        # Create heat object and add entry to heats dictionary
        heats_dict[heat_no, style] = heat_obj(heat_no, style, round,
                                              style_leads, style_follows)

    consecutive_heats_dict = create_consecutive_heats(heats_df, heats_dict)
    return heats_dict, consecutive_heats_dict


def create_scenario():
    dancers = load_dancers()
    heats, cons_heats = load_heats(dancers)
    return dancers, heats, cons_heats
