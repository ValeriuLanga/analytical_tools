from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class ModelRunnerBase(ABC):


    def __init__(self, data: pd.DataFrame):
        self._data = data.copy()   # SettingWithCopyWarning if we don't copy the values in our own instance


    def _compute_ln_returns_and_direction(self) -> None:
        self._data['returns'] = np.log(self._data['close'] / self._data['close'].shift(1))
        self._data['direction'] = np.sign(self._data['returns'])


    def _create_lags(self, lags: int) -> list[str]:
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
            self._data[col] = self._data['returns'].shift(lag)

            cols.append(col)
        
        self._data = self._data.dropna()
        return cols


    @abstractmethod
    def run_models(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def _create_bins(self, laggings_cols: list[str], bins=[0]) -> list[str]:
        """Puts the returns in their coresponding bins

        Returns
        -------
        list[str]
            a list with all the newly added bins
        """
        pass

    
    @abstractmethod
    def _fit_models(self, bin_columns: list[str], models: dict) -> None:
        """Fits the models to the provided data
        
        All models suppliec in 'models' are used
        """
        pass

    
    @abstractmethod
    def _derive_positions(self, bin_columns: list[str], models: dict) -> None:
        """Creates columns for the positions that each model takes

        """
        pass
    
    @abstractmethod
    def _evaluate_strats(self, models: dict) -> list[str]:
        """Evaluates the returns that each of the models made
        
        Returns
        -------
        list[str]
            a list with all the column names that hold the models' performance
        """
        pass