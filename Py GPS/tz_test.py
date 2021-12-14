
import datetime
import zoneinfo
import pytz
from timezonefinder import TimezoneFinder

def test1():
	format = '%Y:%m:%d %H:%M:%S %Z %z'

	# Now Datetime
	dt = datetime.datetime.now()
	print(f"{'Now:':<20}", dt.strftime(format))

	dt_local = dt.astimezone()
	print(f"{'Local DateTime:':<20}", dt_local.strftime(format))

	# UTC Now Datetime
	dt_utc = datetime.datetime.now(datetime.timezone.utc)
	print(f"{'Now UTC:':<20}", dt_utc.strftime(format))

	# UTC timezone Datetime
	dt_local_utc = datetime.datetime.now(pytz.utc)
	print(f"{'UTC DateTime:':<20}", dt_local_utc.strftime(format))

	# convert UTC timezone to 'US/Central'
	dt_us_central = dt_local_utc.astimezone(pytz.timezone('US/Central'))
	print(f"{'US Central DateTime:':<20}", dt_us_central.strftime(format))

	# Convert 'US/Central' timezone to US/Eastern
	dt_us_eastern = dt_us_central.astimezone(pytz.timezone('America/New_York'))
	print(f"{'US Eastern DateTime:':<20}", dt_us_eastern.strftime(format))

	# Convert US/Eastern timezone to IST (India) timezone
	dt_ind = dt_us_eastern.astimezone(pytz.timezone('Asia/Kolkata'))
	print(f"{'India DateTime:':<20}", dt_ind.strftime(format))

def test2():
	format = '%Y:%m:%d %H:%M:%S %Z %z'

	# Now Datetime
	dt = datetime.datetime.now()
	print(f"{'Now:':<20s}", dt.strftime(format))

	dt_local = dt.astimezone()
	print(f"{'Local DateTime:':<20}", dt_local.strftime(format))

	# UTC Now Datetime
	dt_utc = datetime.datetime.now(datetime.timezone.utc)
	print(f"{'Now UTC:':<20}", dt_utc.strftime(format))

	# UTC timezone Datetime
	dt_local_utc = datetime.datetime.now(zoneinfo.ZoneInfo('UTC'))
	print(f"{'UTC DateTime:':<20}", dt_local_utc.strftime(format))

	# convert UTC timezone to 'US/Central'
	dt_us_central = dt_local_utc.astimezone(zoneinfo.ZoneInfo('US/Central'))
	print(f"{'US Central DateTime:':<20}", dt_us_central.strftime(format))

	# Convert 'US/Central' timezone to US/Eastern
	dt_us_eastern = dt_us_central.astimezone(zoneinfo.ZoneInfo('America/New_York'))
	print(f"{'US Eastern DateTime:':<20}", dt_us_eastern.strftime(format))

	# Convert US/Eastern timezone to IST (India) timezone
	dt_ind = dt_us_eastern.astimezone(zoneinfo.ZoneInfo('Asia/Kolkata'))
	print(f"{'India DateTime:':<20}", dt_ind.strftime(format))

def test3():
	from zoneinfo import ZoneInfo
	from datetime import datetime, timedelta
	dt = datetime(2020, 10, 31, 12, tzinfo=ZoneInfo("America/Los_Angeles"))
	print(dt)

def print_tz_names():
	import zoneinfo
	print(zoneinfo.available_timezones())

def test_timezone_finder():
	lat = 42.3314
	lon = -83.0458
	tzf = TimezoneFinder()
	tz = tzf.timezone_at(lng=lon, lat=lat)
	print(f'{tz=}')

def main():
	test_timezone_finder()
	test1()
	test2()
	#print_tz_names()

if __name__ == "__main__":
    main()