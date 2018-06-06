# import necessary packages
import datetime
import time
import Adafruit_DHT
import RPi.GPIO as GPIO
from Board import *
from Lcd import *
from Sensor import *
from imutils.video import VideoStream
from pyzbar import pyzbar
import cv2
import imutils
import multiprocessing as mp
import API
# setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# GPIO pin number
pin_op_sensor = 17  # optical_path_sensor. GPIO17, no.11
pin_th_sensor = 23  # temperature_humidity_sensor. GPIO23, no.16
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
        humi, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_th_sensor)
        if humi is not None and temp is not None:
            timestamp = '{0:.0f}'.format(time.time()*1000.0)
            humidity = '{0:.1f}'.format(humi/100.0)
            temperature = '{0:.1f}'.format(temp*1.0)
            sensor_data = {
                'timestamp': timestamp,
                'temperature': temperature,
                'humidity': humidity
            }
            print("1...", datetime.datetime.now(), sensor_data)
            API.upload_sensor_data(sensor_data)
            print(datetime.datetime.now(), 'uploaded sensor data')
            #time.sleep(0.5)

def monitor_door():
    global door_close_time
    while True:
        door_is_closed = get_pin_state(pin_op_sensor)
        if door_is_closed == 0:
            time_interval = time.time() - door_close_time
            print("2...", datetime.datetime.now(), "door is open")
            # light on
            if time_interval < 60:
                set_pin_state(pin_led_green, GPIO.HIGH)
                set_pin_state(pin_led_red, GPIO.LOW)
            else:
                set_pin_state(pin_led_green, GPIO.LOW)
                set_pin_state(pin_led_red, GPIO.HIGH)
            # lcd display
            print("2...", datetime.datetime.now(), "lcd on...")
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, pin_th_sensor)
            lcd.display_string(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),1)
            if humidity is not None and temperature is not None:
                lcd.display_string(("Temperature: " + str(temperature) + "*C"),2)
                lcd.display_string(("Humidity:    " + str(humidity) + "%"),3)
                print("2...", datetime.datetime.now(), humidity, temperature)
        else:
            print(datetime.datetime.now(), 'door is closed')
            door_close_time = time.time()
            # light off
            set_pin_state(pin_led_green, GPIO.LOW)
            set_pin_state(pin_led_red, GPIO.LOW)
            # lcd clear
            lcd.clear()
        time.sleep(0.5)

def monitor_camera():
    vs = None
    while True:
        camera_status = 1 if get_pin_state(pin_op_sensor) == 0 else 0
        if camera_status == 1:
            if vs == None:
                print("3...", datetime.datetime.now(), "camera on...")
                vs = VideoStream(usePiCamera=True).start()
                time.sleep(1.0)
            # print("[INFO] .......starting video stream...")
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            #cv2.imshow("QRcode Scanner", frame)
            #key = cv2.waitKey(1) & 0xFF
            qrcodes = pyzbar.decode(frame)
            # print(datetime.datetime.now())
            for qrcode in qrcodes:
                qrcodeData = qrcode.data.decode("utf-8")
                beep(pin_buzzer, 0.3)
                ingredient = {
                    'qrcode': qrcodeData
                }
                print("3...", datetime.datetime.now(), ingredient)
                item_name_status = API.check_qr_code(qrcodeData)
                print("3...", datetime.datetime.now(), item_name_status)
                if item_name_status[1] == True:
                    API.remove_ingredient(ingredient)
                    lcd.display_string("Removed item: " + str(item_name_status[0]),4)
                elif item_name_status[1] == False:
                    API.add_ingredient(ingredient)
                    lcd.display_string("Added item: " + str(item_name_status[0]), 4)
                else:
                    pass
        else:
            if vs is not None:
                print("[INFO] cleaning up...")
                print(datetime.datetime.now())
                #cv2.destroyAllWindows()
                vs.stop()
                vs = None
# setup & run a list of processes
targets = [sensor_task, monitor_door, monitor_camera]
#jobs = []
for i in targets:
    mp.Process(target=i,args=()).start()
#p.join()
