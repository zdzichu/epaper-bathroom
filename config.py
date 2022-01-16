
import os

def configure_env():
    """ exports environment variables with configuration """

    os.environ["LATITUDE"] = "…"
    os.environ["LONGITUDE"] = "…"

    os.environ["GOOGLE_API_KEY"] = "…"
    os.environ["TRAFFIC_FROM"] = "…+FM"
    #os.environ["TRAFFIC_FROM"] = f"${LATITUDE}-${LONGITUDE}"
    os.environ["TRAFFIC_1_THROUGH"] = "…+4FP"
    os.environ["TRAFFIC_2_THROUGH"] = "…+V9J"
    os.environ["TRAFFIC_TO"] = "…+GX"

    os.environ["AIRLY_API_KEY"] = "…"

    os.environ["OPENWEATHERMAP_API_KEY"] = "…"

