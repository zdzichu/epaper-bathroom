#!/usr/bin/python

import config

import datetime
import json
import logging
import os
import requests
import time
import urllib.parse

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
            return

        self.validity = 5*60

        if now.minute >= 45:
            self.time_display = f"przed {now.hour+1}"
        elif now.minute >= 15:
            self.time_display = f"wpół do {now.hour+1}"
        else:
            self.time_display = f"po {now.hour}"


class TrafficSegment(DisplaySegment):
    duration = {}

    def update(self):
        now = datetime.datetime.now()

        if now.hour >= 6 and now.hour < 7:
            self.validity = 60
        else:
            self.validity = 60*60
            logging.debug(f"{type(self)}: Not in the morning, skipping update")
            return

        url = "https://maps.googleapis.com/maps/api/directions/json?"
        travel_parameters = {
            "origin": os.getenv("TRAFFIC_FROM"),
            "destination": os.getenv("TRAFFIC_TO"),
            "waypoints": "to be filled",
            "departure_time": int(time.time() + 5*60),   # leave in 5 minutes
            "mode": "driving",
            "key":  os.getenv("GOOGLE_API_KEY")
        }

        for i_point in (1, 2):
            travel_parameters["waypoints"] = f"via:{os.getenv(f'TRAFFIC_{i_point}_THROUGH')}"
            req = requests.get(url=url + urllib.parse.urlencode(travel_parameters))
            if not req.ok:
                logging.info(f"{type(self)}: Google Traffic API call via point {i_point} failed {req.status_code}")
            else:
                response = req.json()
                total_time = 0
                for leg in response["routes"][0]["legs"]:
                    total_time += leg["duration_in_traffic"]["value"]

                self.duration[i_point] = total_time


    def _get_data_text(self):
        if not self.duration:
            return

        ret = "Do Pruszcza\n"
        if self.duration[1] <= self.duration[2]:
            mark1 = " *"
            mark2 = "  "
        else:
            mark1 = "  "
            mark2 = " *"

        ret+= f"{mark1} obwodnicą {round(self.duration[1] / 60)} min\n"
        ret+= f"{mark2} miastem   {round(self.duration[2] / 60)} min"

        return ret


class WeatherSegment(DisplaySegment):
    def mps2kph(self, m_per_s):
        return m_per_s * 3600 / 1000

    def update(self):
        lat = os.getenv("LATITUDE")
        long = os.getenv("LONGITUDE")
        self.validity = 6*60*60

        req = requests.get(f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&appid={os.getenv("OPENWEATHERMAP_API_KEY")}&units=metric&exclude=minutely,hourly,alerts&lang=pl')
        if not req.ok:
            logging.info(f"{type(self)}: OpenWeatherMap API call failed {req.status_code}")
        else:
            response = req.json()
            # current weather
            self.cur_cloud_percent = response["current"]["clouds"]
            # airly probably have better data - from the sensors in the area
            self.cur_temperature = response["current"]["temp"]
            self.cur_temperature_feel = response["current"]["feels_like"]
            self.cur_wind = self.mps2kph(response["current"]["wind_speed"])
            #self.cur_wind_gust = self.mps2kph(response["current"]["wind_gust"])
            self.cur_description = response["current"]["weather"][0]["description"]
            self.cur_description_short = response["current"]["weather"][0]["main"]
            # also "icon" and "id" may be useful

            # forecast for next day
            now = datetime.datetime.now()
            for daily in response["daily"]:
                forecast_date = datetime.datetime.fromtimestamp(daily["dt"])
                tomorrow_date = now + datetime.timedelta(days=1)
                if forecast_date.day == tomorrow_date.day:
                    self.tomorrow_cloud_percent = daily["clouds"]
                    self.tomorrow_temperature = daily["temp"]["day"]
                    self.tomorrow_temperature_feel = daily["feels_like"]["day"]
                    self.tomorrow_wind = self.mps2kph(daily["wind_speed"])
                    self.tomorrow_wind_gust = self.mps2kph(daily["wind_gust"])
                    self.tomorrow_description = daily["weather"][0]["description"]
                    self.tomorrow_description_short = daily["weather"][0]["main"]

    def _get_data_text(self):
        now = datetime.datetime.now()
        if now.hour < 20:
            # current weather
            ret = f"{self.cur_description_short} ({self.cur_description}) \n"
            ret+= f"Wiatr {self.cur_wind:.0f} km/h \n"
            ret+= f"{self.cur_temperature:.0f}°C, odczuwalna {self.cur_temperature_feel:.0f}°C"
            return ret
        else:
            # forecast
            ret = f"Jutro: {self.tomorrow_description_short} ({self.tomorrow_description}) \n"
            ret+= f"Wiatr {self.tomorrow_wind:.0f} km/h, w porywach {self.tomorrow_wind_gust:.0f} km/h \n"
            ret+= f"{self.tomorrow_temperature:.0f}°C, odczuwalna {self.tomorrow_temperature_feel:.0f}°C"
            return ret

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
    config.configure_env()
    logging.basicConfig(level=logging.DEBUG)
    segments = [
           ClockSegment(),
           WeatherSegment(),
           TrafficSegment(),
           AirSegment()
           ]

    for segment in segments:
        print(segment.get_data_text())
        print("---")
