
class Alert:
    """Alert data"""

    def __init__(self):
        self._alerts = {}  # alerts dict because bot alerting is an infinite loop
        self._alertwatch = False  # alert status because the same

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

    def get_alertwatch(self) -> bool:
        return self._alertwatch

    def set_alertwatch(self, status=True):
        self._alertwatch = status

    @staticmethod
    def alert_status(pair: str, data: dict) -> bool:
        """Alerts config"""
        week, month = data[pair][7], data[pair][30]

        volume_alert = week['volume'][0] > 140 or month['volume'][0] > 175
        price_alert = (week['price'] > 125 or week['price'] < 75) or (month['price'] > 140 or month['price'] < 60)
        conditions = volume_alert, price_alert

        alert = True if any(conditions) else False

        return alert

    def alert_watch(self, pair: str, alert_status: bool) -> bool:
        alert = False

        if alert_status and not self.get_alert(pair):
            self.alert_on(pair)
            alert = True

        return alert
