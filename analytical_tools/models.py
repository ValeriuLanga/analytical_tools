from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from data_sourcing import crypto_market_data, utils
from models.model_runner import ModelRunner
import sys

if __name__ == '__main__':

    C = 1 # Inverse of regularization strength
    models = {
        'log_reg': linear_model.LogisticRegression(C=C),
        'gauss_nb': GaussianNB(),
        'svm': SVC(C=C)
        }   
    
    # load up data
    sol_data = crypto_market_data.load_archived_market_data(
            'SOL-USD',
            start_date='2023-07-21',
            end_date='2024-07-21'
            )

    sol_data = sol_data.set_index('start')
    sol_data = sol_data.sort_index()

    # instance for SOL
    model_runner = ModelRunner(sol_data, models)
    returns = model_runner.run_models()
    print(returns)