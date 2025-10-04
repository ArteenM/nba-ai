# nba-ai
NBA-AI. Stormhacks (fall 2025)

AI Model used to predict outcome of NBA games.


To run development:

    `python3 manage.py runserver`


Required Frameworks:

    `pip install nba_api`

    `pip install djangorestframework requests pandas numpy scikit-learn python-decouple joblib`

To train the model on given data (current data is completely synthetic and illogical. WILL NOT GIVE GOOD RESULTS)
    `python3 train_model.py`

Game statistics are tracked in Game object (home_team, home_score, etc...)
Season statistics are tracked in TeamStats object (wins, losses, etc...)
which are all in models.py.

