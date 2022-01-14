#!/usr/bin/python

import datetime
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
    """ between 0600 and 0700 returns true time, then approximation """
    
    def _get_data_text(self):

        now = datetime.datetime.now()

        if now.hour >= 6 and now.hour < 7:
            self.validity = 60
            return f"{now.hour}:{now.minute}"

        self.validity = 5*60

        if now.minute >= 45:
            return f"przed {now.hour+1}"
        elif now.minute >= 15:
            return f"wpół do {now.hour+1}"
        else:
            return f"po {now.hour}"


class TrafficSegment(DisplaySegment):
    pass


class WeatherSegment(DisplaySegment):
    pass


class AirSegment(DisplaySegment):
    pass


if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG)
   segments = [
           ClockSegment()
           ]

   for segment in segments:
       print(segment.get_data_text())
