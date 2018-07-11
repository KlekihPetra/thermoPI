#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi or BeagleBone Black.
import time

import Adafruit_CharLCD as LCD
import RPi.GPIO as gp

import os
import glob
import MySQLdb as db

###################
# Temperature setpoint
###################

t_sp = 25.0

# Read interval [s]
read_interval = 10.0


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

##################################
# 1 wire thermometer identifiers
#
# 10-000802b60060 - auxiliary sensor
#
# 10- - chamber
#
# 10-000802b5e41f - komora
#####################################

sensors_dict = {'aux':'/sys/bus/w1/devices/10-000802b60060/w1_slave',
		'chamber':'/sys/bus/w1/devices/10-000802b5e41f/w1_slave'}

# set pin referencing mode to BCM (as opposed to BOARD)
gp.setmode(gp.BCM)

# set GPIO pins as outputs
# GPIO_1 - heating
# GPIO_2 - pump
# GPIO_3 - cooler
gp.setup(1, gp.OUT)
gp.setup(2, gp.OUT)
gp.setup(3, gp.OUT)

# deactivate all outputs
gp.output(1, gp.LOW)
gp.output(2, gp.LOW)
gp.output(3, gp.LOW)

heating = 'OFF'
pump = 'OFF'
cooling = 'OFF'

heat_dict={'OFF':0, 'ON':1}

def read_temp(location):
    f = open(sensors_dict[location], 'r')
    lines = f.readlines()
    f.close()
    return float(lines[1].split('t=')[1])/1000.0

def connect_lcd():
    # Raspberry Pi pin configuration:
    lcd_rs        = 25  # Note this might need to be changed to 21 for older revision Pi's.
    lcd_en        = 24
    lcd_d4        = 23
    lcd_d5        = 17
    lcd_d6        = 21
    lcd_d7        = 22
    lcd_backlight = 4

    #   Define LCD column and row size for 16x2 LCD.
    lcd_columns = 16
    lcd_rows    = 2


    # Initialize the LCD using the pins above.
    lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
    return lcd

def connect_db():
    con=db.connect(host='77.55.192.216', user='Fox', passwd='yukka31', db='Komora')
    c=con.cursor()
    return c, con

def get_timestamp():
	tm = time.localtime()
	return '%4i-%02i-%02i %02i:%02i:%02i' % (tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)

def lcd_temperature(t):
	lcd.clear()
	line = 'T = %4.1f\n' % (float(t))
	#print line
	lcd.message(line)
	return


# Get current time
# time.localtime() returns time.struct_time(tm_year=2018, tm_mon=7, tm_mday=1, tm_hour=13, tm_min=24, tm_sec=42, tm_wday=6, tm_yday=182, tm_isdst=1)
dt = time.localtime()

# Establish connection to LCD
lcd = connect_lcd()

# Establish connection to the remote db
c, db = connect_db()

# Get current time (UNIX format)
t_0 = time.time()

while True:

	# Check buttons

    # Read sensors 
    if time.time() - t_0 > read_interval:
	    
	    # Read temperature in the chamber and time the read sequence

	    t_start = time.time()
	    
	    t_chamber = read_temp('chamber')
	    
	    t_stop = time.time()
	    t_read = t_stop - t_start
            #print t_start, t_stop
	    print('It took %3.1f seconds to read from the sensor.' % (t_read) )


	    # Read ambient temperature
	    # Read coolant temperature
	    
	    timestamp = get_timestamp()
	    
	    # Print chamber temperature
	    lcd_temperature(t_chamber)

	    print('%s: chamber temperature: %5.2f C, heater: %s, cooler: %s' % (timestamp, t_chamber, heating, cooling))
            # Only cooling implemented, cooler always on
	    if float(t_chamber) < (t_sp - 1.0):
	    	#Chamber temperature is low. If mode is COOL --> wait. If mode is HEAT:
	        gp.output(2, gp.LOW)
	        cooling = 'OFF'
	        
	    elif float(t_chamber) > (t_sp + 1.0):
	    	# Chamber temperature is high. If mode is HEAT, wait. If mode is COOL:
	        gp.output(2, gp.HIGH)
	        cooling = 'ON'


	    # put readings to the db
	    command='INSERT INTO Temperatura (T, Heat) VALUES(%5.2f, %d);' % (float(t_chamber), heat_dict[heating])
	    try:
	        c.execute(command)
	        db.commit()
	    except:
	        # log the event in a file:
	        err=open('/home/pi/Prog/err.txt', 'a')
	        err.write('Connection lost at %s.\n' % (timestamp))
	        err.close()
	        # reconnect to the db
	        c, db = connect_db()

	    t_0 = time.time()





