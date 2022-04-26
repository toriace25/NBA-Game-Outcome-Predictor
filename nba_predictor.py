"""
Author Name:    Victoria Scavetta
Date:           4/19/2022
Course:         Concepts in AI

This program predicts the results of NBA games based on each team's stats and past matchups between the teams.

This file (nba_predictor.py) controls the UI and prints the predicted results to the console.
"""

from datetime import datetime, timedelta
import data_processing as dp
import model as m
import pandas as pd
import re


def main():
    """
    This is the main function of the program. It will ask the user to specify a date. The program will then get all of
    the games occurring on that date and for each team playing, get their stats. It will send this DataFrame to the
    model to predict who will win each game. The program will then print the winners to the console.
    """
    print("Hello, welcome to NBA Predictor!")
    date = ""
    season = ""

    success_both = False
    # This while loop will run until the user puts in a valid date
    while not success_both:
        success_date = False
        while not success_date:
            date = input("Please enter a date in the format mm/dd/20yy:\n")

            # Checking validity of the entered date
            if len(date) != 10 or (date[2] != "/" or date[5] != "/") or re.compile(r'[^0-9/]+').search(date) \
                    or date[6:8] != "20" or int(date[0:2]) > 12 or int(date[3:5]) > 31:
                print("Invalid date format. Please try again.")
            elif (date[0:2] == "02" and int(date[3:5]) > 28 and (int(date[6:]) % 4) != 0) or \
                    (date[0:2] == "02" and int(date[3:5]) > 29):
                print("Invalid date format. Please try again.")
            elif (date[0:2] == "04" or date[0:2] == "06" or date[0:2] == "09" or date[0:2] == "11") and \
                    int(date[3:5]) > 30:
                print("Invalid date format. Please try again.")
            else:
                success_date = True

        # Figuring out the season the date belongs to
        # Example: if the date is 04/13/2022 the season will be 2021-22
        # Example: if the date is 10/13/2022 the season will be 2022-23
        if int(date[0:2]) < 10:
            season = f"{int(date[6:]) - 1}-{date[8:]}"
        else:
            season = f"{int(date[6:])}-{int(date[8:]) + 1}"
        print(f"This date belongs to the {season} season.")
        success_both = True

    nba_teams = dp.get_teams()
    games = dp.get_matchups(date, nba_teams)

    # If there are games on the specified date, make the predictions
    if games:
        print("Processing games...")
        previous_day = (datetime.strptime(date, '%m/%d/%Y') - timedelta(days=1)).strftime('%m/%d/%Y')
        season_start = dp.get_season_start_end(season)[0]
        print("Collecting stats...")
        games_stats = dp.combine_games_stats([games], season_start, previous_day, season, nba_teams)
        games_df = pd.DataFrame(games_stats, columns=['HOME_TEAM', 'AWAY_TEAM', 'H_W_PCT', 'H_FG_PCT', 'H_FG3_PCT',
                                                      'H_FT_PCT', 'H_REB', 'H_AST', 'H_TOV', 'H_STL', 'H_BLK',
                                                      'H_PLUS_MINUS', 'H_OFF_RATING', 'H_DEF_RATING', 'H_TS_PCT',
                                                      'A_W_PCT', 'A_FG_PCT', 'A_FG3_PCT', 'A_FT_PCT', 'A_REB',
                                                      'A_AST', 'A_TOV', 'A_STL', 'A_BLK', 'A_PLUS_MINUS',
                                                      'A_OFF_RATING', 'A_DEF_RATING', 'A_TS_PCT'])
        print("Making predictions...")
        games_predictions = m.make_predictions(games_df)

        print("\nThe predictions are in!")
        for index, row in games_predictions.iterrows():
            if row['PREDICTED_RESULT'] == 0:
                print(f"{row['AWAY_TEAM']} will beat {row['HOME_TEAM']}")
            elif row['PREDICTED_RESULT'] == 1:
                print(f"{row['HOME_TEAM']} will beat {row['AWAY_TEAM']}")
    else:
        print("There are no games to predict!")


main()
