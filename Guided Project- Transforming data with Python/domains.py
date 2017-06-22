import read
import collections

df = read.load_data()

df.dropna(subset=["url"], axis=0)

def extract_url(row):
    temp = str(row["url"])
    #print(temp.split("."))
    
    row["url"] = temp[len(temp)-2] + "." + temp[len(temp)-1]
    return row

    

df.apply(extract_url, axis=1)

domains = df["url"].value_counts()

for i, (name, row) in enumerate(domains.items()):
    print("{0}: {1}".format(name, row))
    if i > 100:
        break
    