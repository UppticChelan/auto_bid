import pandas as pd
import ruleset


def get_ecpm_bid(ipm, Ruleset, baseline):
    if ipm > 0:
        target_cpi = ipm/Ruleset.target_ecpm
    else:
        target_cpi = baseline
    if target_cpi < Ruleset.min:
        target_cpi = Ruleset.min
    return target_cpi

def adjust_baselines_by_geo(baselines):
    baselines['d7_arpu'] = baselines['d7_total_revenue']/baselines['Installs']
    baselines.fillna(0, inplace=True)
    us_data = baselines[baselines['Country']=='US'].sample()
    baselines['scaling_factor'] = baselines['d7_arpu']/us_data['d7_arpu'].iloc[0]
    baselines['baseline_ecpm'] = baselines['baseline_ecpm']*baselines['scaling_factor']
    return baselines

def ecpm_weighted_avg(ecpm_bid, installs, roas_bid, Ruleset):
    bid_num = (Ruleset.install_threshold*ecpm_bid)+(installs*roas_bid)
    new_bid = bid_num/(Ruleset.install_threshold+installs)
    if Ruleset.max == 'default':
        if new_bid > roas_bid*2.2:
            bid = roas_bid*2.2
            return new_bid
        elif new_bid < Ruleset.min:
            new_bid = Ruleset.min
            return new_bid
        else:
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
