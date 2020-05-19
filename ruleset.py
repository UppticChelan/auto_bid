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
        self.install_bias_method = self.rulesdict['install_bias_method']
        self.target = float(self.rulesdict['target'])
        self.groupby = self.rulesdict['group_cols']
        self.max = self.rulesdict['max_bid_cap']
        self.min = float(self.rulesdict['min_bid_cap'])
        self.install_threshold = float(self.rulesdict['install_threshold'])
        self.bid_calculation_method = self.rulesdict['bid_calculation_method']
        self.baseline = float(self.rulesdict['baseline'])

def format_cols_input(df, ruleset):
    if ruleset.input == 'acquired':
        df = df.rename(columns={"Campaign": "Campaign Name"})
    if ruleset.input == 'big_query':
        df = df.rename(columns={"tracker_campaign_id": "Campaign Name", "country_field":"Country", "clean_subpub":"Application ID", "d7":"d7_total_revenue", "installs":"Installs"})
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
