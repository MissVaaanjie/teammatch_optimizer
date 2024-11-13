from ortools.linear_solver import pywraplp
from settings import CONFIG
import numpy as np


class IP_model():

    def init_variables(self):
        x = dict()
        y = dict()
        p = dict()
        n = dict()
        q = dict()
        obj_cont = dict()

        # Create assignment variables (x)
        for (heat_no, style), heat in self.heats.items():
            for l_name in heat.leads:
                for f_name in heat.follows:
                    lead = self.dancers[l_name]
                    follow = self.dancers[f_name]
                    pref_lead = lead.lead_prefs[style]
                    pref_follow = follow.follow_prefs[style]
                    v_name = f'x_({l_name},{f_name},({heat_no},{style}))'

                    x[lead, follow, heat] = self.solver.BoolVar(name=v_name)
                    obj_cont[lead, follow, heat] = pref_lead + pref_follow

        # Create slack variable for assigning a pair multiple times (y)
        for lead in self.dancers.values():
            for follow in self.dancers.values():
                if lead.name != follow.name:
                    v_name = f'y_({lead.name},{follow.name})'
                    y[lead, follow] = self.solver.BoolVar(name=v_name)

        # Create slack variable for preferred pairing
        # Create slack variable for number of heats per dancer
        for dancer in self.dancers.values():
            n[dancer] = self.solver.BoolVar(name=f'n_({dancer.name})')

            if dancer.pref_pair[0] != "":
                part = self.dancers[dancer.pref_pair[0]]
                style = dancer.pref_pair[1]
                if style != "":
                    v_name = f'p_({dancer.name},{part.name},({style}))'
                    p[dancer, part, style] = self.solver.BoolVar(name=v_name)
                else:
                    v_name = f'p_({dancer.name},{part.name},(Any))'
                    p[dancer, part, "Any"] = self.solver.BoolVar(name=v_name)

            if CONFIG.constraint6_included:
                for heat_no in self.cons_heats.keys():
                    v_name = f'q_({dancer.name},{heat_no})'
                    q[dancer, heat_no] = self.solver.BoolVar(name=v_name)

        return x, y, p, n, q, obj_cont

    def init_constraints(self):

        # (1) each heat is assigned exactly one pairing
        for heat in self.heats.values():
            possible_pairings = [self.x[l, f, h]
                                 for (l, f, h) in self.x.keys()
                                 if h == heat]
            self.solver.Add(self.solver.Sum(possible_pairings) == 1,
                            name=f'(1)_({heat.style})')

        # (2) each dancer dances between self.min_dances and max_dances
        for dancer in self.dancers.values():
            heats_per_dancer = [self.x[l, f, h] for (l, f, h)
                                in self.x.keys()
                                if (l == dancer or f == dancer)]
            self.solver.Add(self.solver.Sum(heats_per_dancer) <=
                            self.max_heat,
                            name=f'(2)_({dancer.name},max)')
            self.solver.Add(self.solver.Sum(heats_per_dancer) >=
                            self.min_heat - self.n[dancer],
                            name=f'(2)_({dancer.name},min)')

        # (3) each pairing is assigned at most once
        for lead in self.dancers.values():
            for follow in self.dancers.values():
                if lead.name != follow.name:
                    assignments = [self.x[l, f, h] for (l, f, h)
                                   in self.x.keys()
                                   if (l == lead and f == follow)]
                    self.solver.Add(self.solver.Sum(assignments) <=
                                    1 + self.y[lead, follow],
                                    name=f'(3)_({lead.name},{follow.name})')

        # (4) people can't dance with themselves
        possible_pairings = [self.x[l, f, h]
                             for (l, f, h)
                             in self.x.keys() if l == f]
        self.solver.Add(self.solver.Sum(possible_pairings) <= 0,
                        name='(4)_no_solos')

        # (5) honoring preferred pairings
        for (dancer, pref, style) in self.p.keys():
            if style == "Any":
                possible_pairings = [self.x[l, f, h]
                                     for (l, f, h) in self.x.keys()
                                     if ((l == dancer and f == pref)
                                         or (l == pref and f == dancer))]
            else:
                possible_pairings = [self.x[l, f, h]
                                     for (l, f, h) in self.x.keys()
                                     if (((l == dancer and f == pref)
                                         or (l == pref and f == dancer))
                                         and h.style == style)]
            self.solver.Add(self.solver.Sum(possible_pairings) >=
                            1 - self.p[dancer, pref, style],
                            name=f'(5)_({dancer.name},{pref.name},{style})')

        # (6) preferably not two dances in a row
        if CONFIG.constraint6_included:
            for dancer in self.dancers.values():
                for heat_no, heat_pair in self.cons_heats.items():
                    curr_heat = [self.x[l, f, h] for (l, f, h) in self.x.keys()
                                 if (l == dancer or f == dancer)
                                 and h == heat_pair[0]]
                    next_heat = [self.x[l, f, h] for (l, f, h) in self.x.keys()
                                 if (l == dancer or f == dancer)
                                 and h == heat_pair[1]]
                    self.solver.Add(self.solver.Sum(curr_heat + next_heat) <=
                                    1 + self.q[dancer, heat_no],
                                    name=f'(6)_({dancer.name},{heat_no})')

    def init_objective(self):
        pref_contributions = [self.obj_cont[l, f, h]*self.x[l, f, h]
                              for (l, f, h) in self.x.keys()]
        double_pair_contribution = [CONFIG.double_pairing_penalty*self.y[l, f]
                                    for (l, f) in self.y.keys()]
        pref_pair_penalty = [CONFIG.pref_pairing_penalty*self.p[l, f, h]
                             for (l, f, h) in self.p.keys()]
        min_dance_penalty = [CONFIG.min_dance_penalty*self.n[d]
                             for d in self.n.keys()]
        if CONFIG.constraint6_included:
            cons_dance_penalty = [CONFIG.cons_dance_penalty*self.q[d, i]
                                  for (d, i) in self.q.keys()]
        else:
            cons_dance_penalty = []

        objective_terms = self.solver.Sum(pref_contributions +
                                          double_pair_contribution +
                                          pref_pair_penalty +
                                          min_dance_penalty +
                                          cons_dance_penalty)
        self.solver.Maximize(objective_terms)

    def __init__(self, heat_dict: dict, dancer_dict: dict, cons_heats: dict):
        self.heats = heat_dict
        self.dancers = dancer_dict
        self.cons_heats = cons_heats
        self.solver = pywraplp.Solver.CreateSolver("SCIP")
        print("bounds:")
        print(len(heat_dict)*2/len(dancer_dict))
        print(np.floor(len(heat_dict)*2/len(dancer_dict)))
        print(np.ceil(len(heat_dict)*2/len(dancer_dict)))
        self.min_heat = np.floor(len(heat_dict)*2/len(dancer_dict)+0.0000001)
        self.max_heat = np.ceil(len(heat_dict)*2/len(dancer_dict)+0.0000001)

        (self.x, self.y, self.p, self.n,
         self.q, self.obj_cont) = self.init_variables()
        self.init_constraints()
        self.init_objective()

        filepath = CONFIG.output_mps_name
        with open(filepath, "w") as out_f:
            mps_text = self.solver.ExportModelAsMpsFormat(fixed_format=False,
                                                          obfuscated=False)
            out_f.write(mps_text)

        filepath = CONFIG.output_lp_name
        with open(filepath, "w") as out_f:
            mps_text = self.solver.ExportModelAsLpFormat(False)
            out_f.write(mps_text)
