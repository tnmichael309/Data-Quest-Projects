import sqlite3
import pandas as pd
import math
conn = sqlite3.connect('factbook.db')

area_land = conn.execute("SELECT SUM(area_land) from facts WHERE area_land != \"\";").fetchone()[0]
area_water = conn.execute("SELECT SUM(area_water) from facts WHERE area_water != \"\";").fetchone()[0]

print(type(area_land))
print(area_land/area_water)