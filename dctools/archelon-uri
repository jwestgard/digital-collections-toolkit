from urllib.parse import quote
import csv
import sys


ARCHELON = "https://archelon.lib.umd.edu/catalog/"

with open(sys.argv[1]) as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        fedora2uri = row['uri']
        archelonuri = ARCHELON + quote(fedora2uri, safe=':')
        print(f"{row['id']},{archelonuri}")

