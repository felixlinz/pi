import RPi.GPIO as GPIO
import time

# use the Broadcom SOC channel
GPIO.setmode(GPIO.BCM)

# set the pins as output
GPIO.setup(14, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

try:
    while True:

        GPIO.output(14, GPIO.HIGH)
        GPIO.output(15, GPIO.HIGH)
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(18, GPIO.HIGH)
        # wait for 5 seconds
        time.sleep(100)

        
        GPIO.output(14, GPIO.LOW)
        GPIO.output(15, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(18, GPIO.LOW)
        
        # wait for 5 seconds
        time.sleep(10)
except KeyboardInterrupt:
    # reset the GPIO pins
    GPIO.cleanup()
