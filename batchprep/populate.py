#!/usr/bin/env python3

from avalon import Batch, Item, BinarySet
import sys

"""
filesbase = sys.argv[2]
lookup = {}
with open(filesbase) as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        lookup.setdefault(row['FILENAME'], row['PATH'])


with open(sys.argv[3], 'w') as handle:
    writer = csv.writer(handle)
    writer.writerow(headers)
    filecol = headers.index('File')
    for row in data:
        filename = row[5] + '-0001.mp4'
        row[filecol] = lookup[filename]
        writer.writerow(row)
"""


if __name__ == "__main__":

    testcsv = Batch().from_csv(sys.argv[1])
    print(testcsv.title)
    print(testcsv.contact)
    print(len(testcsv.contents))
    for n, item in enumerate(testcsv.contents, 1):
        print(f"\nITEM #{n}:")
        print("=============")
        print(item)



