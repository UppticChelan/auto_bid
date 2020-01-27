import sys, getopt
import pandas as pd
import ruleset
def main(argv):
    input_file = ''
    try:
        opts, args = getopt.getopt(argv,"hi:r:",["ifile=","rulesfile="])
    except getopt.GetoptError:
        print ('auto_bid.py -i <inputfile> -r <rulesfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('auto_bid.py -i <inputfile> -r <rulesfile>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            input_file = arg
        elif opt in ('-r', '--rulesfile'):
            rulesfile = arg
    df = pd.read_csv(input_file)
    df['original_bid'] = df['Bid']
    rules = ruleset.Ruleset()
    rules.makerules('ruless.csv')
    df = ruleset.format_cols_input(df, rules)
    df['d7_total_revenue'] = df['D7 IAP Revenue'] + df['D7 Ad Revenue']
    group_cols = rules.groupby.split('|')
    baselines = df.groupby(group_cols).sum().reset_index()
    df['unadjusted_bid'] = df.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    baselines['base_bid'] = baselines.apply(lambda x: ruleset.get_baselines(x['d7_total_revenue'], x['Installs'], rules), axis=1)
    df = df.join(baselines[['Campaign Name', 'Country','base_bid']].set_index(['Campaign Name', 'Country']), on=['Campaign Name', 'Country'])
    df['Bid'] = df.apply(lambda x: ruleset.apply_bid_logic(x['unadjusted_bid'], x['Installs'], x['base_bid'], rules), axis=1)
    df = df.round(2)
    df.to_csv('bids_0.csv')


def get_baselines(revenue, installs, target_percent):
    if installs != 0:
        d7_arpu = revenue/installs
        target_cpi = d7_arpu/target_percent
    else:
        target_cpi = 0.01
    if target_cpi < 0.01:
        target_cpi = 0.01
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

if __name__ == '__main__':
   main(sys.argv[1:])
