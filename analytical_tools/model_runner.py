import pandas as pd
import numpy as np

from data_sourcing import crypto_market_data, utils


class ModelRunner():

    def __init__(self, data: pd.DataFrame, models: dict): 
        self.__data = data.copy()   # SettingWithCopyWarning if we don't copy the values in our own instance
        self.__models = models

    def run_models(self) -> pd.DataFrame:
        self.__data['returns'] = np.log(self.__data['close'] / self.__data['close'].shift(1))
        self.__data['direction'] = np.sign(self.__data['returns'])

        lag_cols = self.__create_lags(5)
        self.__data = self.__data.dropna()
        bin_cols = self.__create_bins(lag_cols)
        self.__fit_models(bin_cols, self.__models)
        self.__derive_positions(bin_cols, self.__models)
        strat_returns_cols = self.__evaluate_strats(self.__models)

        return self.__data[strat_returns_cols].sum().apply(np.exp)

    def __create_lags(self, lags: int) -> list[str]:
        """Creates lagging returns columns

        Lagging returns will be added to the data frame.
        
        Returns
        -------
        list[str]
            a list with all the newly added lagging returns columns
        """

        cols = []

        for lag in range(1, lags + 1):
            col = "lag_{}".format(lag)
            self.__data[col] = self.__data['returns'].shift(lag)

            cols.append(col)
        
        return cols

    def __create_bins(self, laggings_cols: list[str], bins=[0]) -> list[str]:
        """Puts the returns in bins

        Returns
        -------
        list[str]
            a list with all the newly added bins
        """

        cols_bin = []

        for col in laggings_cols:
            col_bin = col + '_bin'
            self.__data[col_bin] = np.digitize(self.__data[col], bins=bins)

            cols_bin.append(col_bin)

        return cols_bin


    def __fit_models(self, bin_columns: list[str], models: dict) -> None:
        """Fits the models to the provided data
        
        All models suppliec in 'models' are used
        """
        for model_name in models.keys():
            models[model_name].fit(self.__data[bin_columns], self.__data['direction'])


    def __derive_positions(self, bin_columns: list[str], models: dict) -> None:
        """Creates columns for the positions that each model takes

        """
        
        for model in models.keys():
            self.__data['pos_' + model] = models[model].predict(self.__data[bin_columns])


    def __evaluate_strats(self, models: dict) -> list[str]:
        """Evaluates the returns that each of the models made
        
        Returns
        -------
        list[str]
            a list with all the column names that hold the models' performance
        """

        performance_cols = []

        for model in models.keys():
            col = 'strat_' + model
            self.__data[col] = self.__data['pos_' + model] * self.__data['returns']

            performance_cols.append(col)

        performance_cols.insert(0, 'returns')

        return performance_cols