import pandas as pd
import ruleset


def get_ecpm_bid(ipm, Ruleset):
    target_cpi = ipm/Ruleset.target_ecpm
    if target_cpi < Ruleset.min:
        target_cpi = Ruleset.min
    return target_cpi

def adjust_bid(data, baselines):
    baselines['d7_arpu'] = baselines['d7_total_revenue']/baselines['Installs']
    baselines.fillna(0, inplace=True)
    us_data = baselines[baselines['Country']=='US'].sample()
    baselines['scaling_factor'] = baselines['d7_arpu']/us_data['d7_arpu'].iloc[0]
    data = data.join(baselines[['Campaign Name', 'Country','scaling_factor', 'base_bid']].set_index(['Campaign Name', 'Country']), on=['Campaign Name', 'Country'], how='inner')
    data['ecpm_bid'] = data['scaling_factor']*data['ecpm_bid']
    return data

def ecpm_weighted_avg(bid, installs, baseline, Ruleset):
    baseline_adj = (installs*0.01)+1
    if Ruleset.max == 'default':
        if bid > baseline * baseline_adj:
            bid = baseline * baseline_adj
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

def ecpm_bid_logic(bid,installs, baseline, Ruleset):
    baseline_adj = (installs*0.01)+1
    if Ruleset.max == 'default':
        if installs < Ruleset.install_threshold:
            bid = baseline
            return bid
        elif bid > baseline * baseline_adj:
            bid = baseline * baseline_adj
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
