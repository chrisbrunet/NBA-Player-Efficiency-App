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
import numpy as np
import matplotlib.pyplot as plt

def import_data():
    """Import data from the data folder in this directory.

    Returns:
        pd.DataFrame: pandas dataframe of useful data. 
    """
    # import player bio's 
    bios_data = pd.read_csv("data/bios.csv", index_col=[0,1,2], usecols=[0,1,2,4,5,6,7,8,9,10])
    # import player tracking data
    speed_distance_data = pd.read_csv("data/speed_distance.csv", index_col=[0,1,2], usecols=[0,1,2,7,8,9,10,11,12,13])
    # import player scoring data
    scoring_data = pd.read_csv("data/scoring_data.csv", index_col=[0,1,2])

    full_merge = pd.merge(
        pd.merge(bios_data, speed_distance_data, on=['YEAR', 'PLAYER', 'TEAM']), 
        scoring_data, 
        on=['YEAR', 'PLAYER', 'TEAM']
        )

    # check if there is any duplicated data in the rows.
    # if so drop the duplicates
    if full_merge.duplicated().any():
        full_merge.drop_duplicates()

    return full_merge[['WEIGHT','AGE', 'MIN', 'AVG SPEED', 'DIST. FEET', 'GP', 'PTS', 'FGA', 'W']].copy()

def energy_per_game(weight, dist):
    """Calculates energy required to move a player of based on their weight and distance travelled.

    Parameters:
        int: weight of player in lbs.
        float: average distance travelled by player per game in feet.

    Returns:
        float: average energy output of player per game in joules
    """
    # constant variables
    coef_of_frict = 0.8
    ag = 9.81
    lb_to_kg = 0.453592
    ft_to_m = 0.3048
   
    # work calculation
    normal_force = weight * lb_to_kg * ag
    dist_m = dist * ft_to_m
    energy = normal_force * coef_of_frict * dist_m
    return energy

def power_per_game(energy, mins):
    """Calculates the power output of a player per game based on their energy output and play time

    Parameters:
        float: average energy output of player per game in joules
        float: average playing time per game in minutes

    Returns:
        float: average power output of player per game in watts
    """
    # constant variables
    mins_to_sec = 60

    # power calculation
    power = energy / (mins * mins_to_sec)
    return power

def print_player_conv_stats(player, year, useful_data):
    """Prints the conventional stats of player.
    
    Parameters:
        str: player that is to be highlighted
        str: year to output data for
        pd.DataFrame: DataFrame to be indexed for printing
    """
    player_df = useful_data.loc[int(year), player, :]
    print(f"Games Played: {player_df['GP'].values[0]}, Points: {player_df['PTS'].values[0]},", end=" ")
    print(f"Field Goal Attempts: {player_df['FGA'].values[0]}, Wins: {player_df['W'].values[0]}")

def print_player_power_stats(player, year, useful_data):
    """Prints the power and energy stats for player.
    
    Parameters:
        str: player that is to be highlighted
        str: year to output data for
        pd.DataFrame: DataFrame to be indexed for printing
    """
    player_df = useful_data.loc[int(year), player, :]
    print(f"Average Energy (J): {player_df['AVG ENERGY'].values[0].round(2)},", end=" ")
    print(f"Average Power (W): {player_df['AVG POWER'].values[0].round(2)},", end=" ")
    print(f"Average Power Per Point (W/pt): {player_df['PWR PER PT'].values[0].round(2)}")

def print_player_power_rankings(player, year, useful_data):
    """Prints the ranking of the player in terms of the least
        power needed to score a point.
    
    Parameters:
        str: player that is to be highlighted
        str: year to output data for
        pd.DataFrame: DataFrame to be indexed for printing
    """
    # count number of players with less power per point using a mask
    ranking = useful_data[
        useful_data["PWR PER PT"] < useful_data.loc[int(year), player,:]["PWR PER PT"][0]
        ].count()[0]
    print(f"{player} ranks number {ranking} in the NBA in terms of least power needed per point scored.")

def main():
    # import and merge data
        # DONE - year, player names and teams as indices (index by team then player name)
        # DONE - min 10 columns & 200 rows
        # DONE - store as multi-indexted DataFrame
        # DONE - delete all duplicated columns/rows
        # DONE - data is sorted according to indices
    useful_data = import_data()

    # data manipulation (calculating player efficiency statistics)
        # DONE - program solution uses the describe method to print aggregate stats for the entire dataset
        # DONE - at least 2 columns are added to dataset
        # an aggregation computation is used for a subset of data (perhaps team efficiency?)
        # DONE - masking operation is used
        # groupby operation is used
        # pivot table is used
        # DONE - includes at least 2 user defined functions
    useful_data['AVG ENERGY'] = energy_per_game(useful_data['DIST. FEET'].values, useful_data['WEIGHT'].values)
    useful_data['AVG POWER'] = power_per_game(useful_data['AVG ENERGY'].values, useful_data['MIN'].values)
    useful_data['PWR PER PT'] = useful_data['AVG POWER']/useful_data['PTS']

    # replace inf values with nan
    useful_data.replace([np.inf, -np.inf], np.nan, inplace=True)
    # drop players with nan values because they don't have any points
    # so they don't matter!
    useful_data.dropna(inplace=True)

    # user interface and output
        # DONE - user is given clear guidance on how to enter the TWO given input values (year, player)
        # DONE - error handling on imvalid input
        # DONE - headers used to separate input and output
        # an exported Excel sheet shows the entire indexed dataset and a plot is shown that correctly depicts an aspect of the data
    print("\n\n********* NBA Player Efficiency App *********\n")
    print("This program calculates NBA players energy efficiency using player size, tracking, and scoring data.")
    print("To use the program enter a player name in any case when prompted then enter either 2022 or 2023 for the year.")
    print("The program will then output player energy efficiency statistics for the selected year.")
    
    while True:
        # change to year first and give option to list player names by selected team. - SEAN
        print("\n\n************ INPUT *******************\n")
        player = input("Enter a players name: ")
        year = input("Enter a year: ")

        try:
            # check if input is valid
            useful_data.loc[int(year), player, :]
            break
        except KeyError:
            print("Player name or year is invalid. Enter a valid player name and a year of 2022 or 2023")
        except ValueError:
            print("Year is invalid. Enter a year of 2022 or 2023.")

    print("\n\n************ OUTPUT *******************")

    # for testing...
    # player = "Luka Doncic"
    # year = 2022
    
    # PLAYER STATS
    # make nicer. - SEAN
    print(f"\n{year} PLAYER STATS - {player}\n")
    # conventional player stats
    print_player_conv_stats(player, year, useful_data)
    # player energy/power stats
    print_player_power_stats(player, year, useful_data)
    # player rankings in NBA that year
    print_player_power_rankings(player, year, useful_data)

    # LEAGUE STATS
    print(f"\n{year} LEAGUE STATS\n")

    # overall stats from useful_data in selected year
    league_averages = useful_data.loc[int(year), ['WEIGHT', 'AVG SPEED', 'AVG POWER', 'PTS', 'PWR PER PT']].describe().round(2)
    print(league_averages, "\n")

    # Top 5 Players in Power Per Point
    # try making this a pivot table
    print(f"Top 5 Most Efficient Players in {year} (Power Per Point):\n")
    top_5 = useful_data.loc[int(year), :].sort_values(by=['PWR PER PT'])['PWR PER PT'][:5]
    print(top_5.to_string(index=["PLAYER","TEAM","PWR PER PT"]), "\n")
   
    # Bottom 5 Players in Power Per Point
    print(f"Top 5 Least Efficient Players in {year} (Power Per Point):\n")
    bottom_5 = useful_data.loc[int(year), :].sort_values(by=['PWR PER PT'], ascending=False)['PWR PER PT'][:5]
    print(bottom_5.to_string(index=True, header=False), "\n")

    # total energy output per team 
    print(f"Total Energy Output (MJ) Per NBA Team in {year}:\n")
    team_energy = (useful_data.loc[int(year), :].groupby('TEAM')['AVG ENERGY'].sum()*82/1000000).round(1)
    print(team_energy.sort_values(ascending=False).to_string(header=False))

    # # WIP... needs to implement aggregation or groupby. just an idea to get us started
    # for team in useful_data.index.get_level_values(level=2).unique():
    #     team_totals = useful_data.loc[:, :, team]
    #     megajoules = (team_totals['AVG ENERGY'].sum() * 82 / 1000000).round(1)
    #     print(f"{team} generated {megajoules} MJ this season, which could power a home for {(megajoules/3240).round(1)} months")

    # PLOTS
    # most efficient teams
    # player weight vs PPP 

    # after exiting loop do plot and export to excel sheet

    # save data as excel file
    # useful_data.to_excel('indexed_dataset.xlsx')

if __name__ == '__main__':
    main()