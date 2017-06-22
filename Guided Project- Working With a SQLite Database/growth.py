import sqlite3
import pandas as pd
import math
conn = sqlite3.connect('factbook.db')

df = pd.read_sql_query("SELECT * from facts;", conn)

print(type(df["population"][0]))

df = df[(df["area_land"] > 0) & (df["population"] >= 0.0)]
#df = df[df["population"] > 0.0]

def cal_final_pop(row):
    return row["population"]*(math.e**(row["population_growth"]*35))

df["2050_pop"] = df.apply(cal_final_pop, axis=1)
df.sort_values("2050_pop", ascending=False, inplace=True);
print(df.head(10))
