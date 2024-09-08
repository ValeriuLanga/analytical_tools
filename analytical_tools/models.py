from sklearn import linear_model
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

from data_sourcing import crypto_market_data, utils
from models.model_runner import BinaryFeaturesModelRunner, DigitizedFeaturesModelRunne, LongOnlyDigitizedFeaturesModelRunne
import sys

if __name__ == '__main__':

    C = 1 # Inverse of regularization strength
    models = {
        'log_reg': linear_model.LogisticRegression(C=C),
        'gauss_nb': GaussianNB(),
        'svm': SVC(C=C),
        # these take quite a bit to run 
        # 'dnn_lbfgs': MLPClassifier(solver='lbfgs', 
        #             alpha=1e-5,
        #             hidden_layer_sizes=3 * [500],
        #             random_state=1,
        #             max_iter=1000),
        # 'dnn_adam': MLPClassifier(solver='adam', 
        #             alpha=1e-5,
        #             hidden_layer_sizes=3 * [500],
        #             random_state=1,
        #             max_iter=1000),
        # 'dnn_sgd': MLPClassifier(solver='sgd', 
        #             alpha=1e-5,
        #             hidden_layer_sizes=3 * [500],
        #             random_state=1,
        #             max_iter=1000),
        }   
    
    # load up data
    sol_data = crypto_market_data.load_archived_market_data(
            'SOL-USD',
            start_date='2023-07-21',
            end_date='2024-07-21'
            )

    sol_data = sol_data.set_index('start')
    sol_data = sol_data.sort_index()

    # instantiate model runner
    model_runners = [
        BinaryFeaturesModelRunner(sol_data, models),
        DigitizedFeaturesModelRunne(sol_data, models),
        LongOnlyDigitizedFeaturesModelRunne(sol_data, models)
    ]

    for model_runner in model_runners:
        returns = model_runner.run_models()
        print(model_runner.__class__.__name__)
        print(returns)
        print(25 * '-')

    # now let's run a train-test split
    train, test = train_test_split(sol_data, test_size=0.5, random_state=100)
    train = train.copy().sort_index()
    test = test.copy().sort_index()

    
    # TODO: find a clean way to train the models on one data set and then compute returns on the other
    # currently because of the one-shot design of the runners they'll run on whatever they got trained
    # which obviously overfits the models but also makes it hard(er) to easily test 


    # for model_runner in model_runners:
    #     model_runner.set_data(train)
    #     model_runner.