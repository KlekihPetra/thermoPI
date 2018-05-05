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

t_sp = 22.0


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

dev = '/sys/bus/w1/devices/10-000802b60060/w1_slave'

gp.setmode(gp.BCM)
gp.setup(1, gp.OUT)
gp.output(1, gp.LOW)
heating = 'OFF'
heat_dict={'OFF':0, 'ON':1}

def read_temp():
    f = open(dev, 'r')
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


dt = time.localtime()
lcd = connect_lcd()
c, db = connect_db()

t_0 = time.time()

while True:

	# Check buttons

    if time.time() - t_0 > 5.0:
	    t = read_temp()
	    
	    tm = time.localtime()
	    
	    timestamp='%4i-%02i-%02i %02i:%02i:%02i' % (tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec) 
	    
	    # Print temperature
	    lcd.clear()
	    line = 'T = %4.1f\n' % (float(t))
	    #print line
	    lcd.message(line)

	    print('Temperatura w komorze: %5.2f C, grzanie: %s' % (float(t), heating))

	    if float(t) < (t_sp - 1.0):
	        gp.output(1, gp.HIGH)
	        heating = 'ON'
	        
	    elif float(t) > (t_sp + 1.0):
	        gp.output(1, gp.LOW)
	        heating = 'OFF'

	    command='INSERT INTO Temperatura (T, Heat) VALUES(%5.2f, %d);' % (float(t), heat_dict[heating])
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






