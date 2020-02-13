import csv

class Ruleset():
    def __init__(self):
        self.rulesdict = {}
    def makerules(self, rules_csv):
        with open(rules_csv, mode='r') as infile:
            reader = csv.reader(infile)
            rules_dict = {rows[0]:rows[1] for rows in reader}
        self.rulesdict = rules_dict
    def rules_update(self):
        self.input = self.rulesdict['input']
        self.output = self.rulesdict['output']
        self.method = self.rulesdict['method']
        self.target = float(self.rulesdict['target'])
        self.groupby = self.rulesdict['group_cols']
        self.max = self.rulesdict['max_bid_cap']
        self.min = float(self.rulesdict['min_bid_cap'])
        self.install_threshold = float(self.rulesdict['install_threshold'])
        self.use_ecpm = eval(self.rulesdict['use_ecpm'])
        self.target_ecpm = eval(self.rulesdict['target_ecpm'])
        self.baseline = float(self.rulesdict['baseline'])


def get_baselines(revenue, installs, Ruleset):
    if installs != 0:
        d7_arpu = revenue/installs
        target_cpi = d7_arpu/Ruleset.target
    else:
        target_cpi = Ruleset.min
    if target_cpi < Ruleset.min:
        target_cpi = Ruleset.min
    return target_cpi

def weighted_avg_bid(bid, installs, baseline, Ruleset):
    if Ruleset.max == 'default':
        if bid > baseline * 2.2:
            bid = baseline * 2.2
            return bid
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            new_bid_numer = (Ruleset.install_threshold*baseline)+(installs*bid)
            new_bid = new_bid_numer/(Ruleset.install_threshold+installs)
            return new_bid
    elif float(Ruleset.max) > 0:
        max_bid = float(Ruleset.max)
        if bid > max_bid:
            bid = max_bid
            return bid
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            new_bid_numer = (Ruleset.install_threshold*baseline)+(installs*bid)
            new_bid = new_bid_numer/(Ruleset.install_threshold+installs)
            return new_bid
    else:
        return "Invalid max bid value."

def apply_bid_logic(bid,installs, baseline, Ruleset):
    if Ruleset.max == 'default':
        if installs < Ruleset.install_threshold:
            bid = baseline
            return bid
        elif bid > baseline * 2.2:
            bid = baseline * 2.2
            return bid
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            return bid
    elif float(Ruleset.max) > 0:
        max_bid = float(Ruleset.max)
        if installs < Ruleset.install_threshold:
            bid = baseline
            return bid
        elif bid > max_bid:
            bid = max_bid
            return bid
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            return bid
    else:
        return "Invalid max bid value."

def format_cols_input(df, ruleset):
    if ruleset.input == 'acquired':
        df = df.rename(columns={"Campaign": "Campaign Name"})
    return df

def format_cols_output(df, ruleset):
    if ruleset.output == 'unity':
        df = df[['Country', 'Site ID', 'Bid']]
        df = df.rename(columns={"Country": "Country code", "Site ID": "Source ID"})
        return df

    elif ruleset.output == 'vungle':
        df = df[['Subpublisher Name', 'Site ID', 'Country', 'Bid']]
        df = df.rename(columns={"Subpublisher Name": "name", "Site ID": "pub_app_id", "Country":"geo", "Bid":"rate"})
        return df

    else:
        return df
