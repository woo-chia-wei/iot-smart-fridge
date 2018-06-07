# import necessary packages
import RPi.GPIO as GPIO
import Adafruit_DHT
from Lcd import *
from imutils.video import VideoStream
from pyzbar import pyzbar
import cv2
import imutils
import multiprocessing as mp
import API
import datetime
import time
# setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# GPIO pin number
pin_op_sensor = 17  # optical_path_sensor. GPIO17, no.11
pin_ht_sensor = 23  # humidity_temperature_sensor. GPIO23, no.16
pin_led_green = 19  # GPIO19, no.35
pin_led_red = 26  # GPIO26, no.37
pin_buzzer = 10 # GPIO10, no.19
door_close_time = time.time()
# Initialize LCD
lcd = Lcd()
lcd.clear()
#
def get_pin_state(pin):
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin)

def set_pin_state(pin, state):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, state)

def beep(pin, x_time):
    GPIO.setup(pin, GPIO.OUT)
    Buzz = GPIO.PWM(pin,200)
    Buzz.start(60)
    time.sleep(x_time)
    Buzz.stop()
#
def sensor_task():
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_ht_sensor)
        if humidity is not None and temperature is not None:
            sensor_data = {
                'timestamp': int(time.time()*1000),
                'temperature': float(temperature),
                'humidity':float(humidity/100.0)
            }
            # upload sensor data
            API.upload_sensor_data(sensor_data)
            print(datetime.datetime.now(), 'uploaded sensor data')

def monitor_door():
    global door_close_time
    while True:
        door_is_closed = get_pin_state(pin_op_sensor)
        if door_is_closed == 0:
            time_interval = time.time() - door_close_time
            # light on
            if time_interval < 60:
                set_pin_state(pin_led_green, GPIO.HIGH)
                set_pin_state(pin_led_red, GPIO.LOW)
            else:
                set_pin_state(pin_led_green, GPIO.LOW)
                set_pin_state(pin_led_red, GPIO.HIGH)
            # lcd display
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_ht_sensor)
            lcd.display_string(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
            if humidity is not None and temperature is not None:
                lcd.display_string(("Temperature:  " + str(temperature) + "*C"),2)
                lcd.display_string(("Humidity:     " + str(humidity) + " %"),3)
        else:
            door_close_time = time.time()
            # light off
            set_pin_state(pin_led_green, GPIO.LOW)
            set_pin_state(pin_led_red, GPIO.LOW)
            # lcd clear
            lcd.clear()

def monitor_camera():
    vs = None
    while True:
        camera_status = 1 if get_pin_state(pin_op_sensor) == 0 else 0
        if camera_status == 1:
            if vs == None:
                vs = VideoStream(usePiCamera=True).start()
                time.sleep(1.0)
            # print("[INFO] .......starting video stream...")
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            #cv2.imshow("QRcode Scanner", frame)
            #key = cv2.waitKey(1) & 0xFF
            qrcodes = pyzbar.decode(frame)
            for qrcode in qrcodes:
                qrcodeData = qrcode.data.decode("utf-8")
                beep(pin_buzzer, 0.3)
                ingredient = {
                    'qrcode': qrcodeData
                }
                # check item name and status
                item_name_status = API.check_qr_code(qrcodeData)
                item_name = "{:<6}".format(str(item_name_status[0]))
                print("3...", datetime.datetime.now(), item_name_status)
                # remove/add item
                if item_name_status[1] == True:
                    API.remove_ingredient(ingredient)
                    #lcd.display_string("Removed item: " + str(item_name_status[0]), 4)
                    lcd.display_string("Removed item: " + str(item_name), 4)
                elif item_name_status[1] == False:
                    API.add_ingredient(ingredient)
                    #lcd.display_string("Added   item: " + str(item_name_status[0]), 4)
                    lcd.display_string("Added item: " + str(item_name), 4)
                else:
                    pass
        else:
            if vs is not None:
                #print("[INFO] cleaning up...")
                #cv2.destroyAllWindows()
                vs.stop()
                vs = None
# setup & run a list of processes
targets = [sensor_task, monitor_door, monitor_camera]
for i in targets:
    mp.Process(target=i,args=()).start()
