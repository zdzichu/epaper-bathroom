#!/usr/bin/python

import json
import logging
import os
import requests
import time

class DisplaySegment:
    """ validity - time in seconds how long the data is useful """
    last_refresh = 0
    validity = 1

    def update(self):
        pass

    def get_data_text(self):
        """ returns text formatted data """

        now = time.time()
        if self.last_refresh + self.validity < now:
            logging.debug(f"Data from {self.last_refresh} older than {self.validity} seconds, refreshing")
            self.update()
            self.last_refresh = now

        return self._get_data_text()

    def _get_data_text(self):
        """ real function to return true text formatted data """
        pass


class ClockSegment(DisplaySegment):
    pass


class TrafficSegment(DisplaySegment):
    pass


class WeatherSegment(DisplaySegment):
    pass


class AirSegment(DisplaySegment):
    pass


if __name__ == "__main__":
    pass
