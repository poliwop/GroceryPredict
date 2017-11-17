Setup instructions:
- Change filepaths in
- Navigate to the desired db folder in the shell (I just use root folder for the project), and create a database: "sqlite3 GroceryPredict.db"
- Run DBSetup.py

Script descriptions:

MovingAverages.py
Contains a function which takes a training DF and testing DF and returns predictions for the testing DF, using a model that's basically the moving averages kernel from Kaggle.

RunModel.py
Queries the DB to build a training set and testing set, then calls MovingAverages DF. Currently it assumes that the test DF will actually also be from training data, and therefore that it will be possible to compute the score, which it does. Outputs results to a new table in DB (note that if the results table already exists it will overwrite it).

scoreQuery.py
Has functions for scoring results of a run, assuming the test DF is one in which we have answers (i.e. is actually pulled from the training set).

writeSolnFile.py
Writes a solution file from a results table that can be submitted to Kaggle.

explore.py
I don't think I ever finished this, not sure what it was going to do.

config.py
A config file. After getting this from the repository we will need to edit to our specific paths. It will be kind of a pain that this file will need to differ on our systems, but this should contain all those differences in one file.