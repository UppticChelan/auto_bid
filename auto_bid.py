import sys, getopt
import pandas as pd
def main(argv):
    input_file = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print ('auto_bid.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('auto_bid.py -i <inputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
    df = pd.read_csv(input_file)
    baselines = df.groupby(['campaign_name']).sum().reset_index()
    df['unadjusted_bid'] = df.apply(lambda x: get_baselines(x['iap_revenue_7d'], x['installs'], 0.6), axis=1)
    baselines['base_bid'] = baselines.apply(lambda x: get_baselines(x['iap_revenue_7d'], x['installs'], 0.6), axis=1)
    df = df.join(baselines[['campaign_name', 'base_bid']].set_index('campaign_name'), on='campaign_name')
    df['final_bid_value'] = df.apply(lambda x: apply_bid_logic(x['unadjusted_bid'], x['installs'], x['base_bid']), axis=1)
    df = df.round(2)
    campaigns = df['campaign_id'].unique()
    for campaign in campaigns:
        subset = df[df['campaign_id'] == campaign][['campaign_id','campaign_name', 'application_id', 'application_name', 'final_bid_value']]
        subset['Country'] = 'US'
        subset_renamed = subset.rename(columns={'campaign_id':'Campaign ID',
                                           'campaign_name':'Campaign Name',
                                           'application_id':'Application ID',
                                           'application_name':'Application name',
                                            'final_bid_value':'Bid'
                                           })
        campaign_name = subset_renamed['Campaign Name'].iloc[0]
        subset_renamed.to_csv('{}_{}_bid.csv'.format(campaign, campaign_name))

def get_baselines(revenue, installs, target_percent):
    if installs != 0:
        d7_arpu = revenue/installs
        target_cpi = d7_arpu/target_percent
    else:
        target_cpi = 0.01
    if target_cpi < 0.01:
        target_cpi = 0.01
    return target_cpi

def apply_bid_logic(bid, installs, baseline):
    if bid > baseline * 2:
        bid = baseline * 2
        return bid
    elif installs < 50:
        bid = baseline
        return bid
    elif bid < 0.01:
        bid = 0.01
        return bid
    else:
        return bid

if __name__ == '__main__':
   main(sys.argv[1:])
