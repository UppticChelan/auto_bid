import sys, getopt
import pandas as pd
import ruleset

def generate_roas_bids(revenue, installs, target_percent):
    if installs != 0:
        d7_arpu = revenue/installs
        target_cpi = d7_arpu/target_percent
    else:
        target_cpi = 0.01
    if target_cpi < 0.01:
        target_cpi = 0.01
    return target_cpi

def generate_cpa_mod(target_cpa, purchasers, installs):
    bid_modifier = target_cpa*(purchasers/installs)
    return bid_modifier

def weighted_avg_bid(bid, installs, baseline, Ruleset):
        new_bid_numer = (Ruleset.install_threshold*baseline)+(installs*bid)
        new_bid = new_bid_numer/(Ruleset.install_threshold+installs)
        return new_bid

def modify_bids(bid,installs, baseline, Ruleset):
    if Ruleset.max == 'default':
        if installs < Ruleset.install_threshold:
            bid = baseline
            return bid
        elif bid > baseline:
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
        elif bid < Ruleset.min:
            bid = Ruleset.min
            return bid
        else:
            return bid
    else:
        return "Invalid max bid value."

def generate_target_cpi(ipm, Ruleset):
    if ipm > 0:
        target_cpi = Ruleset.target/ipm
    else:
        target_cpi = 2
    if target_cpi < Ruleset.min:
        target_cpi = Ruleset.min
    return target_cpi

def adjust_baselines_by_geo(baselines):
    baselines['d7_arpu'] = baselines['d7_total_revenue']/baselines['Installs']
    baselines.fillna(0, inplace=True)
    us_data = baselines[baselines['Country']=='US'].sample()
    baselines['scaling_factor'] = baselines['d7_arpu']/us_data['d7_arpu'].iloc[0]
    baselines['base_bid'] = baselines['base_bid']*baselines['scaling_factor']
    return baselines
