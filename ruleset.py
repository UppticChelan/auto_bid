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
        self.baseline = self.rulesdict['baseline']

def format_cols_input(df, ruleset):
    if ruleset.input == 'tableau':
        df = df.rename(columns={"campaign_name": "Campaign Name", "campaign_id": "Campaign ID", "country":"Country", "publisher_id(_)":"Application ID", "revenue":"d7_total_revenue"})
        df = df.groupby(['Campaign Name', 'Campaign ID', 'Country', 'Application ID']).sum().reset_index()
        df['Country'] = df['Country'].str[:2]
    if ruleset.input == 'big_query':
        df = df.rename(columns={"tracker_campaign_name": "Campaign Name", "tracker_campaign_id": "Campaign ID", "country_field":"Country", "publisher_id":"Application ID", "Revenue":"d7_total_revenue", "installs":"Installs"})
        df['Country'] = df['Country'].str[:2]
    else:
        df = df.rename(columns={ "revenue":"d7_total_revenue"})
    return df

def format_cols_output(df, ruleset):
    if ruleset.output == 'unity':
        df = df[['Country', 'Application ID', 'Bid']]
        df = df.rename(columns={"Country": "Country code", "Application ID": "Source ID"})
        return df

    elif ruleset.output == 'vungle':
        df = df[['publisher_name','Application ID', 'Country', 'Bid']]
        df = df.rename(columns={"publisher_name": "name", "Application ID": "pub_app_id", "Country":"geo", "Bid":"rate"})
        return df

    elif ruleset.output == 'ad_colony':
        df['campaign_name'] = ''
        df['app_nundle_id'] = ''
        df['zone_name'] = ''
        df['zone_uuid'] = ''
        df = df[['Application ID', 'Country', 'Bid']]
        df = df.rename(columns={"Application ID": "hashed_app_id", "Country":"country", "Bid":"cpi_bid"})
        return df

    else:
        return df
