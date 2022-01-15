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
            logging.debug(f"{type(self)}: Data from {self.last_refresh} older than {self.validity} seconds, refreshing")
            self.update()
            self.last_refresh = now

        return self._get_data_text()

    def _get_data_text(self):
        """ real function to return true text formatted data """
        pass


class ClockSegment(DisplaySegment):
    """ between 0600 and 0700 returns true time, then approximation """

    time_display = ""

    def _get_data_text(self):
        return f"Czas: {self.time_display}"

    def update(self):
        now = datetime.datetime.now()

        if now.hour >= 6 and now.hour < 7:
            self.validity = 60
            self.time_display = f"{now.hour}:{now.minute}"

        self.validity = 5*60

        if now.minute >= 45:
            self.time_display = f"przed {now.hour+1}"
        elif now.minute >= 15:
            self.time_display = f"wpół do {now.hour+1}"
        else:
            self.time_display = f"po {now.hour}"


class TrafficSegment(DisplaySegment):
    pass


class WeatherSegment(DisplaySegment):
    pass


class AirSegment(DisplaySegment):

    def text_gauge(self, value, start=0, end=200, length=20):
        if length < 3:
            return "[]"
        per_character = (end - start) / (length - 2)
        middle = (end - start) / 2
        fill_char = "+"

        gauge = "["
        for i in range(0, length - 2):
            gauge += fill_char
            if i * per_character > value:
                fill_char = " "
            elif i * per_character >= middle:
                fill_char = "!"
        gauge += "]"

        return gauge

    def _get_data_text(self):
        ret = f"{self.text_gauge(value=self.percent_pm25)} PM2,5: {self.percent_pm25}% ; "
        ret+= f"{self.text_gauge(value=self.percent_pm10)} PM10: {self.percent_pm10}% \n "
        ret+= f"{self.description} / {self.advice}"
        return ret

    def update(self):
        lat = os.getenv("LATITUDE")
        long = os.getenv("LONGITUDE")
        self.validity = 30*60

        headers = {
                "Accept": "application/json",
                "Accept-Language": "pl",
                "apikey": os.getenv("AIRLY_API_KEY")
        }

        req = requests.get(f"https://airapi.airly.eu/v2/measurements/point?lat={lat}&lng={long}&l=pl",
                headers=headers)
        logging.debug(f'{type(self)}: API calls left for today: {req.headers["X-RateLimit-Remaining-day"]}')
        if not req.ok:
            logging.info(f"{type(self)}: AIRLY API call failed {req.status_code}")
        else:
            response = req.json()
            self.description = response["current"]["indexes"][0]["description"]
            self.advice = response["current"]["indexes"][0]["advice"]

            for pollutants in response["current"]["standards"]:
                if pollutants["pollutant"] == "PM25":
                    self.percent_pm25 = pollutants["percent"]
                elif pollutants["pollutant"] == "PM10":
                    self.percent_pm10 = pollutants["percent"]

            for measurement in response["current"]["values"]:
                if measurement["name"] == "TEMPERATURE":
                    self.temperature = measurement["value"]

if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG)
   segments = [
           ClockSegment(),
           AirSegment()
           ]

   for segment in segments:
       print(segment.get_data_text())
       print("---")
