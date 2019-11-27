import csv

class Ruleset():
    def __init__(self):
        self.rulesdict = {}
    def makerules(self, rules_csv):
        with open(rules_csv, mode='r') as infile:
            reader = csv.reader(infile)
            rules_dict = {rows[0]:rows[1] for rows in reader}
        self.rulesdict = rules_dict
        self.output_format = rules_dict['channel']
        self.bid_calc_function = rules_dict['bid_calc_method']
        self.target = float(rules_dict['target'])
        self.groupby = rules_dict['group_cols']
        self.max = rules_dict['max_bid_cap']
        self.min = float(rules_dict['min_bid_cap'])
        self.install_threshold = float(rules_dict['install_threshold'])

def get_baselines(revenue, installs, Ruleset):
    if installs != 0:
        if Ruleset.bid_calc_function == 'default':
            d7_arpu = revenue/installs
            target_cpi = d7_arpu/Ruleset.target
        else:
            return "Bid Calculation method not recognized."
    else:
        target_cpi = Ruleset.min
    if target_cpi < Ruleset.min:
        target_cpi = Ruleset.min
    return target_cpi

def apply_bid_logic(bid,installs, baseline, Ruleset):
    if Ruleset.max == 'default':
        if bid > baseline * 2:
            bid = baseline * 2
            return bid
        elif installs < Ruleset.install_threshold:
            bid = baseline
            return bid
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            return bid
    elif float(Ruleset.max) > 0:
        max_bid = float(Ruleset.max)
        if bid > max_bid:
            bid = max_bid
            return bid
        elif installs < Ruleset.install_threshold:
            bid = baseline
            return bid
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            return bid
    else:
        return "Invalid max bid value."

def format_csv(df, Ruleset, path, output_name):
    if Ruleset.output_format == 'ironsource':
        df.to_csv(path + '{}'.format(output_name))
    else:
        return "Invalid output format."
