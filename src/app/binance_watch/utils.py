import os
import time
import pandas


class Support:
    """Logic support"""

    def __init__(self):
        self._current_pair = ''  # current pair for alert
        self._pair_pool = {}  # pair pool for pairs in marketwatch

    def set_current_pair(self, pair: str):
        self._current_pair = pair

    def get_current_pair(self) -> str:
        return self._current_pair

    def get_pair_pool(self) -> dict:
        return self._pair_pool

    def set_pair(self, pair: str):
        self._pair_pool[pair] = pair

    def del_pair(self, pair: str):
        del self._pair_pool[pair]

    def get_pair(self, pair: str) -> str:
        return self._pair_pool[pair]

    def find_csv(self, path: str) -> bool:
        for file in os.walk(path):
            for csv_file in file[2]:
                if csv_file.find('csv') != -1:
                    pair = csv_file.split('.')[0]
                    self.set_pair(pair)
                    return True
                else:
                    return False

    @classmethod
    def read_history(cls, pair: str, path: str) -> pandas.DataFrame:
        try:
            with open(os.path.join(path, f'{pair}.csv')) as file:
                history = pandas.read_csv(file)
                return history
        except Exception as e:
            time.sleep(1)
            raise e

    @classmethod
    def create_csv(cls, pair: str, history: pandas.DataFrame, path: str):
        csv_file = f'{pair}.csv'
        history.to_csv(os.path.join(path, csv_file))

    @classmethod
    def del_csv(cls, pair: str, path: str):
        os.remove(os.path.join(path, f'{pair}.csv'))
