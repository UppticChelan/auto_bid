import sys, getopt
import pandas as pd
def main(argv):
    input_file = ''
    try:
        opts, args = getopt.getopt(argv,"hi:p:",["ifile=","percent="])
    except getopt.GetoptError:
        print ('auto_bid.py -i <inputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('auto_bid.py -i <inputfile> -p <target_percent_roas>')
            sys.exit()
        elif opt in ('-i', '--ifile'):
            input_file = arg
        elif opt in ('-p', '--percent'):
            target_roas = float(arg)
    df = pd.read_csv(input_file)
    baselines = df.groupby(['Campaign Name', 'Country']).sum().reset_index()
    df['unadjusted_bid'] = df.apply(lambda x: get_baselines(x['D7 IAP Revenue'], x['Installs'], 0.6), axis=1)
    baselines['base_bid'] = baselines.apply(lambda x: get_baselines(x['D7 IAP Revenue'], x['Installs'], 0.6), axis=1)
    df = df.join(baselines[['Campaign Name', 'Country','base_bid']].set_index(['Campaign Name', 'Country']), on=['Campaign Name', 'Country'])
    df['final_bid_value'] = df.apply(lambda x: apply_bid_logic(x['unadjusted_bid'], x['Installs'], x['base_bid']), axis=1)
    df = df.round(2)
    list_of_dfs = [df.loc[i:i+100000-1,:] for i in range(0, len(df),100000)]
    for i in range(len(list_of_dfs)):
        list_of_dfs[i]['Bid'] = list_of_dfs[i]['final_bid_value']
        list_of_dfs[i].iloc[:, :-3].to_csv('bids_{}.csv'.format(i))


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
