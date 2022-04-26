"""
Author Name:    Victoria Scavetta
Date:           4/19/2022
Course:         Concepts in AI

This program predicts the results of NBA games based on each team's stats and past matchups between the teams.

This file (data_processing.py) contains all of the functions responsible for creating the dataset that will be used to
train the model.
"""

from nba_api.stats.endpoints import teamdashboardbygeneralsplits, leaguegamelog, scoreboard, leaguegamefinder
from nba_api.stats.static import teams
import pandas as pd
from datetime import timedelta, datetime
import time

stats = {
    'W_PCT': 'Base',
    'FG_PCT': 'Base',
    'FG3_PCT': 'Base',
    'FT_PCT': 'Base',
    'REB': 'Base',
    'AST': 'Base',
    'TOV': 'Base',
    'STL': 'Base',
    'BLK': 'Base',
    'PLUS_MINUS': 'Base',
    'OFF_RATING': 'Advanced',
    'DEF_RATING': 'Advanced',
    'TS_PCT': 'Advanced'
}


def get_teams():
    """
    Pulls all of the current teams from the NBA api and returns a dictionary containing the team names and their IDs

    :return:    A dictionary containing the team names and their team ID
    """
    nba_teams = teams.get_teams()

    teams_dict = {}
    # We only need the team's name and their ID, so we make a dict containing only those values
    for team in nba_teams:
        teams_dict.update({team['full_name']: team['id']})

    teams_dict.update({'LA Clippers': 1610612746})  # This team is already in the dict, but for some reason the API
    # refers to them as either LA or Los Angeles Clippers

    return teams_dict


def get_team_stats(team, start_date, end_date, season, nba_teams):
    """
    Gets the stats for a team between the specified start date and end date

    :param nba_teams:   Dictionary containing all of the NBA teams and their IDs
    :param team:        The team to return stats for
    :param start_date:  The start date for the stats in format 'mm/dd/yyyy'
    :param end_date:    The end date for the stats in format 'mm/dd/yyyy'
    :param season:      The NBA season to get the stats from. ex: '2021-22'
    :return:            A dictionary containing team stats
    """

    # There are many different exceptions that could occur from this, but it will work after a few attempts at most
    success = False
    while not success:
        try:
            team_stats = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=nba_teams[team],
                                                                                   per_mode_detailed='Per100Possessions',
                                                                                   season=season,
                                                                                   date_from_nullable=start_date,
                                                                                   date_to_nullable=end_date)
            success = True
        except:
            print("An exception occurred. Trying again...")
            time.sleep(0.1)

    team_stats_dict = team_stats.get_normalized_dict()  # Puts the stats into a dictionary for easier use
    team_dashboard = team_stats_dict['OverallTeamDashboard'][0]

    # There are many different exceptions that could occur from this, but it will work after a few attempts at most
    # Advanced stats are NBA stats that are more complex
    success = False
    while not success:
        try:
            advanced_team_stats = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=nba_teams[team],
                                                                                            measure_type_detailed_defense='Advanced',
                                                                                            season=season,
                                                                                            date_from_nullable=start_date,
                                                                                            date_to_nullable=end_date)
            success = True
        except:
            print("An exception occurred. Trying again...")
            time.sleep(0.1)

    advanced_team_stats_dict = advanced_team_stats.get_normalized_dict()  # Puts the advanced stats into a dictionary
    advanced_team_dashboard = advanced_team_stats_dict['OverallTeamDashboard'][0]

    # Creating a dictionary containing all of the important team stats
    final_team_stats = {
        'W_PCT': team_dashboard['W_PCT'],
        'FG_PCT': team_dashboard['FG_PCT'],
        'FG3_PCT': team_dashboard['FG3_PCT'],
        'FT_PCT': team_dashboard['FT_PCT'],
        'REB': team_dashboard['REB'],
        'AST': team_dashboard['AST'],
        'TOV': team_dashboard['TOV'],
        'STL': team_dashboard['STL'],
        'BLK': team_dashboard['BLK'],
        'PLUS_MINUS': team_dashboard['PLUS_MINUS'],
        'OFF_RATING': advanced_team_dashboard['OFF_RATING'],
        'DEF_RATING': advanced_team_dashboard['DEF_RATING'],
        'TS_PCT': advanced_team_dashboard['TS_PCT']
    }

    return final_team_stats


def get_matchups(date, nba_teams):
    """
    Gets all game matchups happening on a specified date

    :param nba_teams:   Dictionary containing all of the NBA teams and their IDs
    :param date:        The date to get all matchups from
    :return:            The matchups from a specified date in a dictionary where the home team is the key
    """
    # Get all of the matchups from the API and put them into a dictionary
    matchups = scoreboard.Scoreboard(league_id='00', game_date=date)
    matchups_dict = matchups.get_normalized_dict()
    games = matchups_dict['GameHeader']

    # Create a new dictionary in the format {home team: away team}
    daily_matchups = {}
    for game in games:
        home_team = ''
        away_team = ''

        home_team_id = game['HOME_TEAM_ID']
        for team_name, team_id in nba_teams.items():
            # Matching the home team ID to an ID in the nba_teams dict to get the team's name
            if team_id == home_team_id:
                home_team = team_name

        away_team_id = game['VISITOR_TEAM_ID']
        for team_name, team_id in nba_teams.items():
            # Matching the away team ID to an ID in the nba_teams dict to get the team's name
            if team_id == away_team_id:
                away_team = team_name

        daily_matchups.update({home_team: away_team})

    return daily_matchups


def get_past_matchups(date, season):
    """
    Gets all matchups and results from a specified date in the past

    :param date:    Date to get past matchup results from
    :param season:  NBA season in which the matchups were played
    :return:        A list containing a dictionary of all matchups and a list of the results
    """

    # There are many different exceptions that could occur from this, but it will work after a few attempts at most
    success = False
    while not success:
        try:
            games = leaguegamelog.LeagueGameLog(season=season, league_id='00', date_from_nullable=date,
                                                date_to_nullable=date,
                                                season_type_all_star='Regular Season')
            success = True
        except:
            print("An exception occurred. Trying again...")
            time.sleep(0.1)
    games_dict = games.get_normalized_dict()['LeagueGameLog']  # Puts the games into a dict

    matchups = {}  # Home teams are the keys, away teams are the values
    results = []  # List containing results of home teams, either W or L

    # Iterate through pairs of rows since there are 2 rows for each game. One row is associated with the home team and
    # the other row is associated with the away team.
    for i in range(0, len(games_dict), 2):

        # If the value associated with the MATCHUP key for the current row includes 'vs.', the team associated with the
        # row is the home team and the team associated with the next row is the away team
        # Otherwise, the away team is the current row and the home team is the next row
        if 'vs.' in games_dict[i]['MATCHUP']:
            home_team = games_dict[i]['TEAM_NAME']
            away_team = games_dict[i + 1]['TEAM_NAME']
            game_result = games_dict[i]['WL']
        else:
            home_team = games_dict[i + 1]['TEAM_NAME']
            away_team = games_dict[i]['TEAM_NAME']
            game_result = games_dict[i + 1]['WL']

        matchups.update({home_team: away_team})
        results.append(game_result)

    return [matchups, results]


def get_season_games_df(start_date, end_date, season, nba_teams):
    """
    Puts all of the games that happened in a specified season and each team's stats per game into a Pandas DataFrame

    :param start_date:      The start date of the season as a datetime object
    :param end_date:        The end date of the season as a datetime object
    :param season:          The NBA season to collect games and stats from
    :param nba_teams:       Dictionary containing all of the NBA teams and their IDs
    :return:                A Pandas DataFrame containing all games played in the season and both team's stats from each
                            day
    """
    season_games = []

    curr_date = start_date
    end = end_date + timedelta(days=1)  # Make end a day after the end date so the loop ends at the correct date
    season_start_str = start_date.strftime('%m/%d/%Y')  # Turns the start date into a string

    # Get all the games and team stats for each day from start_date to end_date
    while curr_date != end:
        curr_date_str = curr_date.strftime('%m/%d/%Y')  # Turn the current date into a string
        print(curr_date_str)
        time.sleep(0.01)
        curr_games = get_past_matchups(curr_date_str, season)

        # If there are games occurring on that day, get the stats for each team and add them to the list of games
        if curr_games:
            # Combine the stats with the games
            curr_games_stats = combine_games_stats(curr_games, season_start_str, curr_date_str, season, nba_teams)

            # Add the games with stats into the list of season games
            for game in curr_games_stats:
                game.append(curr_date_str)
                season_games.append(game)

        curr_date = curr_date + timedelta(days=1)  # Increment the day by 1

    # Create a pandas Data Frame containing all of the games with each team's stats, the date, and the result
    season_games_df = pd.DataFrame(season_games, columns=['HOME_TEAM', 'AWAY_TEAM', 'H_W_PCT', 'H_FG_PCT', 'H_FG3_PCT',
                                                          'H_FT_PCT', 'H_REB', 'H_AST', 'H_TOV', 'H_STL', 'H_BLK',
                                                          'H_PLUS_MINUS', 'H_OFF_RATING', 'H_DEF_RATING', 'H_TS_PCT',
                                                          'A_W_PCT', 'A_FG_PCT', 'A_FG3_PCT', 'A_FT_PCT', 'A_REB',
                                                          'A_AST', 'A_TOV', 'A_STL', 'A_BLK', 'A_PLUS_MINUS',
                                                          'A_OFF_RATING', 'A_DEF_RATING', 'A_TS_PCT', 'RESULT', 'DATE'])
    return season_games_df


def combine_games_stats(games, start_date, end_date, season, nba_teams):
    """
    Gets the home team's and away team's stats for all of the games happening in a specified day

    :param games:       A list containing a dictionary of games happening during the specified day and a list of the
                        results (if any)
    :param start_date:  The start date of the season in format "mm/dd/yyyy"
    :param end_date:    The date of the games in format "mm/dd/yyyy"
    :param season:      The current season in format "yyyy-yy"
    :param nba_teams:   A dictionary containing all of the NBA teams and their IDs
    :return:            A list containing both the home and away team's stats for each game
    """
    games_with_stats = []
    curr_game_num = 0

    # If length of games list is 1, there are no results for these games.
    # If length of games list is 2, there are results for these games.
    if len(games) > 1:
        results = games[1]
    else:
        results = None

    # For each game, get the home team's stats and away team's stats and add them to the current game list
    for home_team, away_team in games[0].items():
        curr_game = [home_team, away_team]
        if results is not None:
            print(curr_game)

        time.sleep(0.01)
        home_stats = get_team_stats(home_team, start_date, end_date, season, nba_teams)
        # Add all of the stats to the current game list
        for stat, stat_type in stats.items():
            curr_game.append(home_stats[stat])

        time.sleep(0.01)
        away_stats = get_team_stats(away_team, start_date, end_date, season, nba_teams)
        # Add all of the stats to the current game list
        for stat, stat_type in stats.items():
            curr_game.append(away_stats[stat])

        # If there are results for the game, binarize the result and add it to the current game list
        if results is not None:
            # If the home team won, there will be a 'W'. Turn the 'W' into a 1
            if results[curr_game_num] == 'W':
                result = 1
            # If the away team won, there will be an 'L'. Turn the 'L' into a 0
            else:
                result = 0
            curr_game.append(result)
            curr_game_num += 1

        games_with_stats.append(curr_game)

    return games_with_stats


def reformat_date(date_str):
    """
    Reformat a date given in format "yyyy-mm-dd" to the format "mm/dd/yyyy"

    :param date_str:    A date string in the format "yyyy-mm-dd"
    :return:            A date string in the format "mm/dd/yyyy"
    """
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:]

    new_date = str(month + "/" + day + "/" + year)
    return new_date


def get_season_start_end(season):
    """
    Gets the start date and end date (or most recent game date if season is still active) of a specified season

    :param season:  The season to get the start and end dates for in the format "yyyy-yy"
    :return:        A list containing the start date and end date of the season
    """
    success = False
    while not success:
        try:
            # Gets all of the games from the season
            games = leaguegamefinder.LeagueGameFinder(season_nullable=season, season_type_nullable='Regular Season',
                                                      league_id_nullable='00')
            success = True
        except:
            print("An exception occurred. Trying again...")
            time.sleep(0.1)

    games_df = games.get_data_frames()[0]  # Puts the games into a DataFrame

    # The start date is found in the last row of the DataFrame
    # The end date is found in the first row of the DataFrame
    # Reformat the dates to be in format "mm/dd/yyyy"
    start_date = reformat_date(games_df.iat[-1, 5])
    end_date = reformat_date(games_df.iat[0, 5])

    return [start_date, end_date]


def get_data(num_seasons, curr_season):
    """
    Creates CSV files for num_seasons seasons. curr_season is the season that happened most recently.
    Example: if curr_season is 22 and num_seasons is 4, CSV files will be created for seasons 2018-19, 2019-20, 2020-21,
    and 2021-22.

    :param num_seasons:     The amount of seasons to create CSV files for
    :param curr_season:     The most recent season to start making CSV files for
    """
    nba_teams = get_teams()

    # Make CSV files for the given amount of seasons
    for i in range(num_seasons):
        season = f"20{curr_season - (i + 1)}-{curr_season - i}"  # Season in format "yyyy-yy"
        start_date, end_date = get_season_start_end(season)

        # Turns the start date and end date into a datetime object
        start_date = datetime.strptime(start_date, '%m/%d/%Y')
        end_date = datetime.strptime(end_date, '%m/%d/%Y')

        season_games_df = get_season_games_df(start_date, end_date, season, nba_teams)
        season_games_df.to_csv(f"games_{season}.csv")


def combine_data(num_seasons, curr_season):
    """
    Combines all of the CSV files into one CSV file

    :param num_seasons:     The amount of seasons to combine
    :param curr_season:     The most recent season to start with
    """
    season = f"20{curr_season - num_seasons}-{curr_season - (num_seasons - 1)}"  # Season in format "yyyy-yy"
    all_data_df = pd.read_csv(f"games_{season}.csv")    # Read in the oldest season's CSV to start
    all_data_df.drop('Unnamed: 0', axis=1, inplace=True)

    # Read in the rest of the seasons in oldest to newest order and add them to the combined DataFrame
    for i in range(num_seasons - 1, 0, -1):
        season = f"20{curr_season - i}-{curr_season - (i - 1)}"
        curr_season_df = pd.read_csv(f"games_{season}.csv")
        curr_season_df.drop('Unnamed: 0', axis=1, inplace=True)
        all_data_df = pd.concat([all_data_df, curr_season_df], ignore_index=True)

    all_data_df.to_csv(f"all_games_20{curr_season - num_seasons}-{curr_season}.csv")


def main(num_seasons=4, curr_season=22):
    """
    Creates CSV files for num_seasons seasons, then combines those CSV files into one CSV file containing every game.
    This takes a very long time to run due to the many API calls.

    :param num_seasons:     The number of seasons to collect data from
    :param curr_season:     The most recent season to collect data from
    """
    get_data(num_seasons, curr_season)

    # Combine all datasets into one
    combine_data(num_seasons, curr_season)

# main()
