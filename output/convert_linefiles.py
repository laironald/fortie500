import re
import sys

filename = sys.argv[1]

f = open(filename, "rb")
data = []
for x in f:
    for y in re.split(r"[\r\n]+", x):
        if len(y):
            data.append(y)
f = None

g = open(filename, "wb")
for x in data:
    g.write(x)
    g.write("\n")
g = None
