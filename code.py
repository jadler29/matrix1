# Add these imports at the beginning of your code
import adafruit_matrixportal.network as network
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.matrixportal import MatrixPortal
import displayio
from adafruit_display_text import label

# Add this function to convert UTC time to NYC time
def utc_to_nyc(utc_time):
    offset = -4  # Change this value to -5 during Standard Time
    return utc_time + offset * 3600

# Initialize the MatrixPortal
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
matrix = Matrix()
display = matrixportal.display

# Define font and text properties
text = "00:00:00"
text_area = label.Label(matrixportal.graphics.FONT, text=text, color=0xFFFFFF)
text_area.x = display.width // 2 - text_area.bounding_box[2] // 2
text_area.y = display.height // 2 - text_area.bounding_box[3] // 2
matrixportal.graphics.splash.append(text_area)

# Connect to WiFi
network.connect()

# Replace the while loop with the following updated loop:
while True:
    try:
        # Get the current time from Adafruit IO
        response = wifi.get("https://io.adafruit.com/api/v2/time/seconds")
        current_utc_time = int(response.text)
        response.close()

        # Convert UTC time to NYC time
        nyc_time = utc_to_nyc(current_utc_time)

        # Format the time string
        hours = (nyc_time // 3600) % 24
        minutes = (nyc_time // 60) % 60
        seconds = nyc_time % 60
        text_area.text = "{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds)

        # Update the display
        display.refresh()

        # Wait for 1 second
        time.sleep(1)

    except OSError as e:
        print("Failed to get data, retrying\n", e)
        wifi.reset()
        continue