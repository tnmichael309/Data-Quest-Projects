from dateutil.parser import parse
import read
import collections

df = read.load_data()

def get_sub_hour(row):
    return parse(row["submission_time"]).hour
    
    
df["sub_hour"] = df.apply(get_sub_hour, axis=1)
print(df["sub_hour"].value_counts())

