
class Alert:
    """Alert data"""

    def __init__(self):
        self._alerts = {}  # alerts dict because bot alerting is an infinite loop

    def alert_off(self, pair: str):
        self._alerts[pair] = False

    def alert_on(self, pair: str):
        self._alerts[pair] = True

    def del_alert(self, pair: str):
        del self._alerts[pair]

    def get_alert(self, pair: str) -> bool:
        return self._alerts[pair]

    def init_alerts(self, pair_pool: dict):
        for pair in pair_pool.keys():
            self.alert_off(pair)

    @staticmethod
    def alert_status(data: dict) -> bool:
        week, month = data[7], data[30]
        alert = False

        if week['volume'][0] > 140 and (week['price'] > 125 or week['price'] < 75):
            alert = True

        elif month['volume'][0] > 125 or month['price'] > 125 or month['price'] < 75:
            alert = True

        return alert

    def alert_watch(self, pair: str, alert_status: bool) -> bool:
        alert = False

        if alert_status and not self.get_alert(pair):
            self.alert_on(pair)
            alert = True

        return alert
