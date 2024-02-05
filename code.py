import time
from os import getenv
import board
import busio
from digitalio import DigitalInOut
import neopixel
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_matrixportal.network as network
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.matrixportal import MatrixPortal
import displayio
from adafruit_display_text import label

def utc_to_nyc(utc_time):
    offset = -4  # Change this value to -5 during Standard Time
    return utc_time + offset * 3600

print("ESP32 SPI webclient test")

secrets = {}
for token in ["ssid", "password"]:
    if getenv("CIRCUITPY_WIFI_" + token.upper()):
        secrets[token] = getenv("CIRCUITPY_WIFI_" + token.upper())
for token in ["aio_username", "aio_key"]:
    if getenv("CIRCUITPY_" + token.upper()):
        secrets[token] = getenv("CIRCUITPY_" + token.upper())

if not secrets:
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in settings.toml, please add them there!")
        raise

esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

if "SCK1" in dir(board):
    spi = busio.SPI(board.SCK1, board.MOSI1, board.MISO1)
else:
    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
matrix = Matrix()
display = matrixportal.display

text = "00:00:00"
text_area = label.Label(matrixportal.graphics.FONT, text=text, color=0xFFFFFF)
text_area.x = display.width // 2 - text_area.bounding_box[2] // 2
text_area.y = display.height // 2 - text_area.bounding_box[3] // 2
matrixportal.graphics.splash.append(text_area)

network.connect()

counter = 0

while True:
    try:
        print("Posting data...", end="")
        data = counter
        feed = "test"
        payload = {"value": data}
        response = wifi.post(
            "https://io.adafruit.com/api/v2/"
            + secrets["aio_username"]
            + "/feeds/"
            + feed
            + "/data",
            json=payload,
            headers={"X-AIO-KEY": secrets["aio_key"]},
        )
        print(response.json())
        response.close()
        counter = counter + 1
        print("OK")
    except OSError as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue

    try:
        response = wifi.get("https://io.adafruit.com/api/v2/time/seconds")
        current_utc_time = int(response.text)
        response.close()

        nyc_time = utc_to_nyc(current_utc_time)

        hours = (nyc_time // 3600) % 24
        minutes = (nyc_time // 60) % 60
        seconds = nyc_time % 60
        text_area.text = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

        display.refresh()

        time.sleep(1)

    except OSError as e:
        print("Failed to get time, retrying\n", e)
        wifi.reset()
        continue