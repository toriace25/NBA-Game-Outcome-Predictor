"""
Author Name:    Victoria Scavetta
Date:           4/19/2022
Course:         Concepts in AI

This program predicts the results of NBA games based on each team's stats and past matchups between the teams.

This file (model.py) creates the model that will be able to predict the results of NBA games.
"""

import pandas as pd
from sklearn.metrics import accuracy_score, make_scorer, confusion_matrix
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from xgboost import XGBClassifier
import pickle
from os.path import exists


def create_model():
    """
    Create an XGBoost model that can predict the result of NBA games

    :return:    The XGBoost model
    """
    # Read in the CSV containing all of the games
    games_df = pd.read_csv("all_games_2018-22.csv")
    games_df.drop('Unnamed: 0', axis=1, inplace=True)

    # Drop non-numeric columns
    games_df.drop(columns=['HOME_TEAM', 'AWAY_TEAM', 'DATE'], axis=1, inplace=True)

    # Create the XGBoost model
    clf = XGBClassifier(objective='binary:logistic', use_label_encoder=False)

    # Define search space for grid search
    search_space = [
        {
            'n_estimators': [100, 150, 200],
            'learning_rate': [0.1, 0.2, 0.3],
            'max_depth': [2, 3, 4],
            'nthread': [11, 12, 13]
        }
    ]

    # Cross-validation with 10 splits
    kfold = KFold(n_splits=10, random_state=42, shuffle=True)

    # AUC and accuracy will be the important scores for grid search
    scoring = {'AUC': 'roc_auc', 'Accuracy': make_scorer(accuracy_score)}

    # x is all of the columns except for the result column
    # y is the result column
    x = games_df.drop(columns='RESULT')
    y = games_df['RESULT']

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42, shuffle=True, stratify=y)

    # Define grid search
    grid = GridSearchCV(
        clf,
        param_grid=search_space,
        cv=kfold,
        scoring=scoring,
        refit='AUC',
        verbose=1,
        n_jobs=-1
    )

    model = grid.fit(x_train, y_train)

    # Make predictions on test data
    predict = model.predict(x_test)
    predictions = [round(value) for value in predict]

    # Evaluate predictions
    print(f'Best AUC Score: {model.best_score_}')
    print(f'Accuracy: {accuracy_score(y_test, predictions) * 100}%')
    print(confusion_matrix(y_test, predictions))
    print(model.best_params_)

    # Save the model for future use
    pickle.dump(model, open("nba.pickle.dat", "wb"))

    return model


def make_predictions(games):
    """
    Makes predictions on a given set of NBA games.

    :param games:   A DataFrame containing NBA games and each teams stats
    :return:        The original DataFrame with an additional column containing the predicted results
    """
    # If the model has already been created and saved, load it in. Otherwise, create the model
    if exists("nba.pickle.dat"):
        model = pickle.load(open("nba.pickle.dat", "rb"))
    else:
        model = create_model()

    games_df = games.copy()  # Copy the DataFrame so we don't lose the non-numeric columns in the next step
    games_df.drop(columns=['HOME_TEAM', 'AWAY_TEAM'], axis=1, inplace=True)
    games['PREDICTED_RESULT'] = model.predict(games_df)

    return games
