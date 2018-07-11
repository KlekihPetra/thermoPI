# thermoPI
Automatic temperature control system for a microbrewery.
therm.py --> main script. Reads temperature from DS1820 sensors and stores the readings in mySQL. Controls heating and cooling.
So far only cooling has been implemented. The cooler is olways on. When temperature in the chamber exceeds the setpoint value, pump turns on.

Execute the script in the backround as root, preferably on startup.
/etc/rc.local --> sudo python /../../therm.py & (add sleep 15 at the beginning of the rc.local to allow for networking to start up).

If the connection to the db is lost, error handler restores the connection and log the event in a txt file
