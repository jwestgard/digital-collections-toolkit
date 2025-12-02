#!/usr/bin/env python3

import csv
import sys

from avalon import Batch, Item, BinarySet

metadata = sys.argv[1]
filescsv = sys.argv[2]
outputfile = sys.argv[3]


if __name__ == "__main__":

    batch = Batch().from_csv(metadata)

    lookup = {}
    with open(filescsv) as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            lookup.setdefault(row['FILENAME'], row['PATH'])

    with open(outputfile, 'w') as handle:
        writer = csv.writer(handle)
        writer.writerow(batch.headers)
        filecol = headers.index('File')
        for row in data:
            filename = row[3] + '-0001.mp4'
            row[filecol] = lookup[filename]
            writer.writerow(row)

    print(testcsv.title)
    print(testcsv.contact)
    print(len(testcsv.contents))
    for n, item in enumerate(testcsv.contents, 1):
        print(f"\nITEM #{n}:")
        print("=============")
        print(item)
