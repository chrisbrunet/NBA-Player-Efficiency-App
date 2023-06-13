# nba_player_efficiency.py
# Group 14
# Chris Brunet & Sean Buchanan
#
# A terminal based application that calculates player efficieny.
# Efficiency is defined by player scoring per unit power expended.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def import_data():
    """Import data from the data folder in this directory.

    Returns:
        pd.DataFrame: pandas dataframe of useful data. 
    """
    # import player bio's 
    bios_data = pd.read_csv("data/bios.csv", index_col=[2,1,0], usecols=[0,1,2,4,5,6,7,8,9,10])
    # import player tracking data
    speed_distance_data = pd.read_csv("data/speed_distance.csv", index_col=[2,1,0], usecols=[0,1,2,7,8,9,10,11,12,13])
    # import player scoring data
    scoring_data = pd.read_csv("data/scoring_data.csv", index_col=[2,1,0])

    full_merge = pd.merge(
        pd.merge(bios_data, speed_distance_data, on=['YEAR', 'TEAM', 'PLAYER']), 
        scoring_data, 
        on=['YEAR', 'TEAM', 'PLAYER']
        )

    # check if there is any duplicated data in the rows.
    # if so drop the duplicates
    if full_merge.duplicated().any():
        full_merge.drop_duplicates()

    # select and return only the data columns useful to this application
    useful_data = full_merge[['WEIGHT','AGE', 'MIN', 'AVG SPEED', 'DIST. FEET', 'GP', 'PTS', 'FGA', 'W']].copy()
    return useful_data.sort_index()

def energy_per_game(weight, dist):
    """Calculates energy required to move a player based on their weight and distance travelled.

    Parameters:
        weight (int): weight of player in lbs.
        dist (float): average distance travelled by player per game in feet.

    Returns:
        float: average energy output of player per game in Joules
    """
    # constant variables
    coef_of_frict = 0.6 # estimated coefficient of friction for running (https://commons.nmu.edu/cgi/viewcontent.cgi?article=1143&context=isbs)
    ag = 9.81
    lb_to_kg = 0.453592 
    ft_to_m = 0.3048
   
    # work calculation
    normal_force = weight * lb_to_kg * ag # Newtons
    dist_m = dist * ft_to_m # meters
    energy = normal_force * coef_of_frict * dist_m # Joules
    return energy

def power_per_game(energy, mins):
    """Calculates the power output of a player per game based on their energy output and play time.

    Parameters:
        energy (float): average energy output of player per game in Joules.
        mins (float): average playing time per game in minutes.

    Returns:
        power (float): average power output of player per game in Watts
    """
    # constant variables
    mins_to_sec = 60

    # power calculation
    power = energy / (mins * mins_to_sec)
    return power

def print_player_conv_stats(player, year, useful_data):
    """Prints the conventional stats of player.
    
    Parameters:
        player (str): player that is to be highlighted.
        year (str): year to output data for.
        useful_data (pd.DataFrame): DataFrame to be indexed for printing.
    """
    player_df = useful_data.loc[int(year), :, player]
    print(f"Games Played: \t\t\t{player_df['GP'].values[0]}")
    print(f"Points Per Game: \t\t{player_df['PTS'].values[0]}")
    print(f"Field Goal Attempts: \t\t{player_df['FGA'].values[0]}")
    print(f"Wins: \t\t\t\t{player_df['W'].values[0]}")

def print_player_power_stats(player, year, useful_data):
    """Prints the power and energy stats for player.
    
    Parameters:
        player (str): player that is to be highlighted.
        year (str): year to output data for.
        useful_data (pd.DataFrame): DataFrame to be indexed for printing.
    """
    player_df = useful_data.loc[int(year), :, player]
    print(f"Average Energy Per Game (J): \t{player_df['AVG ENERGY'].values[0].round(2)}")
    print(f"Average Power Per Game (W): \t{player_df['AVG POWER'].values[0].round(2)}")
    print(f"Average Power Per Point (W): \t{player_df['PWR PER PT'].values[0].round(2)}")

def print_player_power_rankings(player, year, useful_data):
    """Prints the ranking of the player in terms of the least
        power needed to score a point.
    
    Parameters:
        player (str): player that is to be highlighted.
        year (str): year to output data for.
        useful_data (pd.DataFrame): DataFrame to be indexed for printing.
    """
    # count number of players with less power per point in year using a mask
    useful_data_year = useful_data.loc[int(year), :, :]
    ranking = useful_data_year[useful_data_year["PWR PER PT"] < useful_data_year.loc(axis=0)[:, player]["PWR PER PT"][0]].count()[0]
    print(f"\n{player} ranked number {ranking+1} in the NBA in terms of least power needed per point scored.")

def print_power_output_per_team(year, useful_data):
    """Prints the total power output of each NBA team as well as all NBA teams over the course of a given season
    
    Parameters:
        year (str): year to output data for.
        useful_data (pd.DataFrame): DataFrame to be indexed for printing. 
    """
    # constant variables
    w_to_mw = 1/1000000 # convert Watts to Megawatts
    avg_home_pwr = 1.39 # megawatts to power average North-American home for a day (https://theogm.com/2023/03/09/understanding-megawatts-of-power-mws-role-in-renewable-energy-industry/#:~:text=One%20megawatt%2Dhour%20(MWh),33%2C333%20kWh%2F30%20days)

    print(f"Total Power Output (MW) Per NBA Team in {year} (Sorted highest to lowest):\n")

    # grouping player power output by team and multiplying to extend over entire NBA season
    team_power = (useful_data.loc[int(year), :].groupby('TEAM')['SZN POWER'].sum() * w_to_mw).round(2)
    total_NBA_energy = team_power.sum() # calculating total power output of all teams using a sum() aggregation computation

    # sorting and printing output
    print(team_power.sort_values(ascending=False).to_string(header=False),"\n")
    
    print("INSIGHTS:")
    print(f"\t- NBA players in {year} produced enough power to run an average North-American home for {(total_NBA_energy / avg_home_pwr).round(1)} days.")

def plot_weight_vs_ppp(useful_data, min_gp, weight_group):
    """Plots average power per point based on defined weight classes for all years.

    Parameters:
        useful_data (pd.DataFrame): DataFrame to be indexed for printing.
        min_gp (int): minmum number of games played to be included in data.
        weight_group (int): size of slice to group weights.
    """
    years = useful_data.index.get_level_values('YEAR').unique()
    weight_vs_ppp_tables = []

    # looping through each year of available data to create separate pivot tables for each season
    for year in years:
        useful_data_year = useful_data.loc[year, :]
        min_gp_data = useful_data_year[useful_data_year['GP'] >= min_gp] # using a mask to filter out data that does not meet min_GP
    
        # creating pivot table with weight groups as rows and mean of PWR PER POINT as values
        weight_vs_ppp = min_gp_data.pivot_table(
                                index=pd.cut(min_gp_data['WEIGHT'], bins=range(min_gp_data['WEIGHT'].min(), min_gp_data['WEIGHT'].max() + weight_group + 1, weight_group), right=False),
                                values='PWR PER PT',
                                aggfunc='mean')
        weight_vs_ppp_tables.append(weight_vs_ppp)

    
    # plotting and formatting plots for each year of data
    fig, (ax1, ax2) = plt.subplots(2)

    # creating plots
    weight_vs_ppp_tables[0].plot(ax=ax1)
    weight_vs_ppp_tables[1].plot(ax=ax2)

    # setting axis and chart titles
    ax1.set_xlabel('Weight Range (lbs)')
    ax1.set_ylabel('Avg Power per Point (W/pt)')
    ax1.set_title(f'{years[0]} Season')

    ax2.set_xlabel('Weight Range (lbs)')
    ax2.set_ylabel('Avg Power per Point (W/pt)')
    ax2.set_title(f'{years[1]} Season')

    # creating one more pivot table for all years to find overall optimal weight for efficient scoring
    min_gp_data = useful_data[useful_data['GP'] >= min_gp]
    weight_vs_ppp = min_gp_data.pivot_table(
                            index=pd.cut(min_gp_data['WEIGHT'], bins=range(min_gp_data['WEIGHT'].min(), min_gp_data['WEIGHT'].max() + weight_group + 1, weight_group), right=False),
                            values='PWR PER PT',
                            aggfunc='mean')

    # slicing output of most efficient weight range in order to print
    weight_range = weight_vs_ppp.idxmin().to_string(index=False)
    weight_range = weight_range.split(",")
    lower_weight = weight_range[0].removeprefix("[")
    upper_weight = weight_range[1].removesuffix(")").strip()
        
    print(f"\t- The optimal weight to score points in the NBA with the least amount of work is {lower_weight}-{upper_weight} lbs. \n")
    
    plt.tight_layout()
    plt.show()

def main():
    useful_data = import_data()

    # data manipulation (calculating player efficiency statistics and adding to DataFrame)
    useful_data['AVG ENERGY'] = energy_per_game(useful_data['DIST. FEET'].values, useful_data['WEIGHT'].values)
    useful_data['AVG POWER'] = power_per_game(useful_data['AVG ENERGY'].values, useful_data['MIN'].values)
    useful_data['SZN POWER'] = useful_data['AVG POWER'] * useful_data['GP']
    useful_data['PWR PER PT'] = useful_data['AVG POWER'] / useful_data['PTS']

    # replace inf values with nan
    useful_data.replace([np.inf, -np.inf], np.nan, inplace=True)
    # drop players with nan values because they don't have any points so they don't matter for this application
    useful_data.dropna(inplace=True)

    print("\n\n**************************************** NBA Player Efficiency App ****************************************\n")
    print("This program calculates NBA players energy efficiency using player size, tracking, and scoring data.")
    print("To use the program enter the year to be analyzed (only 2022 or 2023).")
    print("Then enter the full name of the player to analyze e.g. Kyrie Irving.")
    print("The program will then output player energy efficiency statistics for the selected year along with some other")
    print("general statistics.")
    print("\n\n*************************************************** INPUT **************************************************\n")

    while True:
        year = input("Enter a year: ")
        player = input("Enter a players name: ")

        try:
            # check if input is valid
            useful_data.loc[int(year), :, player]
            break
        except KeyError:
            print("Player name or year is invalid. Enter a valid player name and a year of 2022 or 2023.\n")
        except ValueError:
            print("Year is invalid. Enter a year of 2022 or 2023.\n")

    print("\n\n*************************************************** OUTPUT **************************************************")
    
    #### PLAYER STATS ####
    print(f"\n{year} PLAYER STATS - {player}:\n")

    # conventional player stats
    print_player_conv_stats(player, year, useful_data)

    # player energy/power stats
    print_player_power_stats(player, year, useful_data)

    # player rankings in NBA that year
    print_player_power_rankings(player, year, useful_data)

    #### LEAGUE STATS ####
    print(f"\n{year} LEAGUE STATS:\n")

    # overall stats from useful_data in selected year
    league_averages = useful_data.loc[int(year), ['WEIGHT', 'AVG SPEED', 'AVG POWER', 'PTS', 'PWR PER PT']].describe().round(2)
    print(league_averages, "\n")

    # Top 5 Players in Power Per Point
    print(f"Top 5 Most Efficient Players in {year} (Power Per Point):\n")
    top_5 = useful_data.loc[int(year), :].sort_values(by=['PWR PER PT'])['PWR PER PT'][:5]
    print(top_5.to_string(index=True, header=False), "\n")
   
    # Bottom 5 Players in Power Per Point
    print(f"Top 5 Least Efficient Players in {year} (Power Per Point):\n")
    bottom_5 = useful_data.loc[int(year), :].sort_values(by=['PWR PER PT'], ascending=False)['PWR PER PT'][:5]
    print(bottom_5.to_string(index=True, header=False), "\n")

    # total power output per team 
    print_power_output_per_team(year, useful_data)

    # save indexed data as excel file
    useful_data.to_excel('indexed_dataset.xlsx')

    # plotting power per point versus weight range of NBA players
    plot_weight_vs_ppp(useful_data, 20, 10)

if __name__ == '__main__':
    main()