from datetime import datetime
from pysolar import solar
from pytz import timezone

dt = datetime.strptime('2020-04-25 16:00:00', '%Y-%m-%d %H:%M:%S').replace(tzinfo = timezone('UTC'))
solar_angle = solar.get_altitude(40., 116., dt)
print(solar_angle)