# Buzzer or LED intensifies as object appraoches
import RPi.GPIO as GPIO
from time import sleep
import datetime
import math

# Define the pins we'll use
LED = 32
BUZZER = 33
DISTTRIGGER = 10
DISTECHO = 8

# Declare variables used in getting the distance from the sensor
# how long the soundwave will be sent for
triggerPulse = 10
distance = 0
# time to clear the trigger pin
clearTime = 2
# speed of sound used to calculate distance
# 340m/s, adjusted as we're using microseconds
speedOfSound = 0.034
# choose which alert method you want
useLED = True
useBuzzer = True

# Lambda functions
# lambda function to sleep for microseconds
usleep = lambda x : sleep(x/1000000.0)

# Setup the GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(DISTTRIGGER, GPIO.OUT)
GPIO.setup(DISTECHO, GPIO.IN)

# setup the pwm objects, and set its initial value. 0 is for off.
pwmLED = GPIO.PWM(LED, 1000)
pwmLED.start(0)
pwmBuzzer = GPIO.PWM(BUZZER, 1000)
pwmBuzzer.start(0)

# function to clear the trigger pin
def clearTrigger():
  # set the trigger pin low and pause for 0.02 seconds 
  # this is just to reset and clear the pin
  GPIO.output(DISTTRIGGER, GPIO.LOW)
  usleep(clearTime)

# sends a soundwave pulse
def pulseTrigger():
  # set the trigger pin high for 10 micro seconds
  GPIO.output(DISTTRIGGER, GPIO.HIGH)
  usleep(triggerPulse)
  GPIO.output(DISTTRIGGER, GPIO.LOW)

# reads the soundwave bouncing off objects and returns the time difference
def readTriggerResponse(): 
  # wait for pulse to start coming back
  while GPIO.input(DISTECHO) == 0:
    pass
  # set the start time when the pulse starts coming back
  start = datetime.datetime.now()

  # wait for the end of the pulse, then stop the timer
  while GPIO.input(DISTECHO) == 1:
    pass
  stop = datetime.datetime.now()

  # pause to make sure we don't get overlap
  sleep(0.002)

  difference = stop-start
  # distance is calculated as time * speed of sound. Since it's there and back, 
  # distance has to be halved for one way travel.
  distance = ((difference.microseconds) * speedOfSound) / 2
  
  return distance

# function to return a value to be used as the PWM signal for the alert
def getAlertIntensity(distance):
  value = int(100 - (math.log(distance, 10)) * 50)
  
  if value > 100:
    return 100
  if value < 0:
    return 0

  return value

while (True):
  # clear the trigger pin
  clearTrigger()

  # send the soundwave pulse to measure
  pulseTrigger()

  # read the response
  distance = readTriggerResponse()

  # light the LED or buzz the buzzer
  alertIntensity = getAlertIntensity(distance)
  if useLED: 
    pwmLED.ChangeDutyCycle(alertIntensity)
  if useBuzzer:
    pwmBuzzer.ChangeDutyCycle(alertIntensity)
  # uncomment this for a print out of what value is being used
  # good for troubleshooting
  # print(getAlertIntensity(distance))
