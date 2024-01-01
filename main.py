import urequests as requests
import json
import network
import secrets
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
from galactic import GalacticUnicorn
import jpegdec, math, ntptime, time
import _thread

blink=0
machine.freq(200000000)
rtc = machine.RTC()
year, month, day, wd, hour, minute, second, _ = rtc.datetime()
last_second = second
blink = 0
galactic = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)
#Timer global variables
last_time_sync = time.time()
last_cheerlight_check = time.time()
utc_offset = 0


WHITE = graphics.create_pen(255, 255, 255)
BLACK = graphics.create_pen(0, 0, 0)
BACKGROUND_COLOUR = graphics.create_pen(10, 0, 96) # Blue
OUTLINE_COLOUR = (0, 0, 0)
MESSAGE_COLOUR = (255, 255, 255)
BG_COLOUR = graphics.create_pen(0, 0, 0)
TEXT_COLOUR = graphics.create_pen(50, 0, 255)

city = 'Colchester'
country_code = 'UK'
#example
#city = 'Lahore'
#country_code = 'PAK'
width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

NTP_DELTA = 2208988800
host = "0.uk.pool.ntp.org"

open_weather_map_api_key = secrets.API_KEY

def clear_display():
    # does what it says on the tin
    graphics.set_pen(BG_COLOUR)
    graphics.clear()
    galactic.update(graphics)

def connect_to_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    while not station.isconnected() and station.status() >= 0:
        print("Waiting to connect:")
        clear_display()
        graphics.set_pen(TEXT_COLOUR)
        graphics.text("Connecting", 1, 2, 0, scale=1);
        galactic.update(graphics)
        time.sleep(1)
    if(station.isconnected()):
        network_config = station.ifconfig()
        ip = network_config[0]
        print("Connected:" + ip)
        clear_display()
        # draw the text
        graphics.set_pen(TEXT_COLOUR)
        graphics.text("Active", 5, 2, 0, scale=1); 
    
        # update the display
        galactic.update(graphics)
        time.sleep(5)
        try:
            ntptime.settime()
        except OSError:
            pass


def outline_text(text, x, y):
    graphics.set_pen(BLACK)
    graphics.text(text, x - 1, y - 1, -1, 1)
    graphics.text(text, x, y - 1, -1, 1)
    graphics.text(text, x + 1, y - 1, -1, 1)
    graphics.text(text, x - 1, y, -1, 1)
    graphics.text(text, x + 1, y, -1, 1)
    graphics.text(text, x - 1, y + 1, -1, 1)
    graphics.text(text, x, y + 1, -1, 1)
    graphics.text(text, x + 1, y + 1, -1, 1)

    graphics.set_pen(WHITE)
    graphics.text(text, x, y, -1, 1)
    
def redraw_weather():
    while True:
        #set your unique OpenWeatherMap.org URL
        open_weather_map_url = 'http://api.openweathermap.org/data/2.5/weather?q=' + city + ',' + country_code + '&APPID=' + open_weather_map_api_key
        weather_data = requests.get(open_weather_map_url)
        # Location (City and Country code)
        location = weather_data.json().get('name')    
        # Weather Description
        description = weather_data.json().get('weather')[0].get('main')
        weather_icon = weather_data.json().get('weather')[0].get('icon')       
        print(description)
        print(weather_icon)
        icon=weather_icon+'.jpg'
        raw_temperature = weather_data.json().get('main').get('temp')-273.15
        temperature = str(round(raw_temperature)) + '°'
        print(temperature)
        graphics.set_pen(BACKGROUND_COLOUR)
        for x in range(11,30):
            for y in range(0,height):
                graphics.pixel(x, y)
        j = jpegdec.JPEG(graphics)
        j.open_file(icon)
        j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
        graphics.set_font("bitmap8")
        #graphics.set_pen(WHITE)
        outline_text(temperature,13, 2)
        galactic.update(graphics)
        time.sleep(120)
        #sync_time_if_reqd()

def redraw_display_if_reqd():
    global year, month, day, wd, hour, minute, second, last_second, blink

    year, month, day, wd, hour, minute, second, _ = rtc.datetime()
    
    if second != last_second:
        hour += utc_offset
        if hour < 0:
            hour += 24
        elif hour >= 24:
            hour -= 24

        #set_background()
        graphics.set_pen(BACKGROUND_COLOUR)
        for x in range(30,width):
            for y in range(0,height):
                graphics.pixel(x, y)
        
        if blink == 0:
            clock = "{:02}:{:02}".format(hour, minute)
            blink = 1
        else:
            clock = "{:02}|{:02}".format(hour, minute)
            blink = 0
        graphics.set_font("bitmap8")     
        outline_text(clock, 32, 2)
        last_second = second

def redraw_time():
    #sync_time()
    while True:
        if galactic.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
            galactic.adjust_brightness(+0.01)

        if galactic.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
            galactic.adjust_brightness(-0.01)
            
        if  galactic.is_pressed(GalacticUnicorn.SWITCH_A):
            galactic.set_brightness(0)
        
        if galactic.is_pressed(GalacticUnicorn.SWITCH_B):
            galactic.set_brightness(0.5)
        
        #sync_time_if_reqd()
        redraw_display_if_reqd()
        galactic.update(graphics)
        time.sleep(0.1)
            
#while True:
galactic.set_brightness(0.1)

#set_background()
connect_to_wifi()
second_thread = _thread.start_new_thread(redraw_time, ())
redraw_weather()
