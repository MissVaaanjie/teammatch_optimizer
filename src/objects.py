class dancer_obj():
    def __init__(self,
                 dancer_name: str,
                 preferred_pairing: tuple,  # (dancer.name, style.name)
                 lead_preferences: dict,
                 follow_preferences: dict):
        self.name = dancer_name
        self.pref_pair = preferred_pairing
        self.lead_prefs = lead_preferences
        self.follow_prefs = follow_preferences


class heat_obj():
    def __init__(self,
                 heat_number: int,
                 style_name: str,
                 round_no: int,
                 leads_list: list,
                 follows_list: list):
        self.heat_no = heat_number
        self.style = style_name
        self.round = round_no
        self.leads = leads_list
        self.follows = follows_list
