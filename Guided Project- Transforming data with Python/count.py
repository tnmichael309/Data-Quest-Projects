import read
import collections

df = read.load_data()

headline_string = ""

for h in df["headline"].items():
   headline_string += str(h[1]) + " "
    

headline_string_arr = headline_string.split(" ")

for hs in headline_string_arr:
    hs = hs.lower()
    
c = collections.Counter(headline_string_arr)

most_common_word = c.most_common(100)  

for mc in most_common_word:
    print(mc[0])
