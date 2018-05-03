# thermoPI
Automatic temperature control system for a microbrewery.
therm.py --> main script. Reads temperature from DS1820 sensors and stores the readings in mySQL. Controls heating and cooling.

Execute the script in the backround as root, preferably on startup.
/etc/rc.local --> sudo python /../../therm.py & (add sleep 15 at the beginning of the rc.local to allow for networking to start up).
