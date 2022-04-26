# NBA-Game-Outcome-Predictor

This program predicts the results of NBA games based on past team statistics and results. The file data_processing.py
contains all the necessary functions needed to collect statistics for the training dataset and future games. The file
model.py contains the function that creates the XGBoost classifier model and trains it. It also contains the function
that allows the model to make predictions on new data. The file nba_predictor.py starts the program and allows the user
to have the model make predictions on games happening on a specified date.

## How to make predictions
To start making predictions, run nba_predictor.py. The program will print instructions to the console. The user will be
prompted to input a date in the format "mm/dd/20yy". If the user puts in a bad input, the program will ask the user for
new input until the user inputs a date in the proper format. If there are no games happening on that specific date, the
program will print a message saying there are no games to predict and the program will end. If there are games happening
on that date, it will collect the stats for each team playing on that date and have the model make predictions on which
team will win each game. Once the predictions are complete, the program will print, line by line, which team will win.

## Sample run
```
Hello, welcome to NBA Predictor!
Please enter a date in the format mm/dd/20yy:
04/18/2022
This date belongs to the 2021-22 season.
Processing games...
Collecting stats...
Making predictions...

The predictions are in!
Philadelphia 76ers will beat Toronto Raptors
Dallas Mavericks will beat Utah Jazz
Golden State Warriors will beat Denver Nuggets
```
