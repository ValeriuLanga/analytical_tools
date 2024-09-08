import pandas as pd
import numpy as np

from data_sourcing import crypto_market_data, utils
from models.base_model_runner import ModelRunnerBase

class ModelRunner(ModelRunnerBase):

    def __init__(self, data: pd.DataFrame, models: dict): 
        super().__init__(data)
        self.__models = models

    def run_models(self) -> pd.DataFrame:
        self._compute_ln_returns_and_direction()
        lag_cols = self._create_lags(5)
        bin_cols = self._create_bins(lag_cols)

        self._fit_models(bin_cols, self.__models)
        self._derive_positions(bin_cols, self.__models)
        strat_returns_cols = self._evaluate_strats(self.__models)

        return self._data[strat_returns_cols].sum().apply(np.exp)

    def _create_bins(self, laggings_cols: list[str], bins=[0]) -> list[str]:
        """Puts the returns in their coresponding bins

        Returns
        -------
        list[str]
            a list with all the newly added bins
        """

        cols_bin = []

        for col in laggings_cols:
            col_bin = col + '_bin'
            self._data[col_bin] = np.digitize(self._data[col], bins=bins)

            cols_bin.append(col_bin)

        return cols_bin


    def _fit_models(self, bin_columns: list[str], models: dict) -> None:
        """Fits the models to the provided data
        
        All models suppliec in 'models' are used
        """
        for model_name in models.keys():
            models[model_name].fit(self._data[bin_columns], self._data['direction'])


    def _derive_positions(self, bin_columns: list[str], models: dict) -> None:
        """Creates columns for the positions that each model takes

        """
        
        for model in models.keys():
            self._data['pos_' + model] = models[model].predict(self._data[bin_columns])


    def _evaluate_strats(self, models: dict) -> list[str]:
        """Evaluates the returns that each of the models made
        
        Returns
        -------
        list[str]
            a list with all the column names that hold the models' performance
        """

        performance_cols = []

        for model in models.keys():
            col = 'strat_' + model
            self._data[col] = self._data['pos_' + model] * self._data['returns']

            performance_cols.append(col)

        performance_cols.insert(0, 'returns')

        return performance_cols