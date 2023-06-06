# nba_player_efficiency.py
# Group 14
# Chris Brunet & Sean Buchanan
#
# A terminal based application that calculates player efficieny.
# Efficiency is defined by player scoring per unit energy expended.

# General 
    # no global variables
    # comments throughout
    # docstring on functions
    # names and group numbers included on all submitted files
    # proper spacing and naming conventions throughout
import pandas as pd

# import and merge data
    # DONE - year, player names and teams as indices (index by team then player name)
    # DONE - min 10 columns & 200 rows
    # DONE - store as multi-indexted DataFrame
    # DONE - delete all duplicated columns/rows
    # data is sorted according to indices

bios_data = pd.read_csv("data/bios.csv", index_col=[0,1,2], usecols=[0,1,2,4,5,6,7,8,9,10])
speed_distance_data = pd.read_csv("data/speed_distance.csv", index_col=[0,1,2], usecols=[0,1,2,7,8,9,10,11,12,13])
scoring_data = pd.read_csv("data/scoring_data.csv", index_col=[0,1,2])

full_merge = pd.merge(pd.merge(bios_data, speed_distance_data, on=['YEAR', 'PLAYER', 'TEAM']), scoring_data, on=['YEAR', 'PLAYER', 'TEAM'])

useful_data = full_merge[['WEIGHT','AGE', 'MIN', 'AVG SPEED', 'DIST. FEET', 'GP', 'PTS', 'FGA', 'W']].copy()

# data manipulation (calculating player efficiency statistics)
    # program solution uses the describe method to print aggregate stats for the entire dataset
    # at least 2 columns are added to dataset
    # an aggregation computation is used for a subset of data (perhaps team efficiency?)
    # masking operation is used
    # groupby operation is used
    # pivot table is used
    # includes at least 2 user defined functions

# user interface and output
    # user is given clear guidance on how to enter the TWO given input values (year, player)
    # error handling on imvalid input
    # headers used to separate input and output
    # an exported Excel sheet shows the entire indexed dataset and a plot is shown that correctly depicts an aspect of the data