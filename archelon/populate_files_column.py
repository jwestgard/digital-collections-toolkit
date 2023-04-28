#!/usr/bin/env python3

import csv
import sys


class ArchelonBatchCsv:

    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as handle:
            self.data = [row for row in csv.DictReader(handle)]

    def add_files_column(self, filelist):
        for row in self.data:
            if not 'FILES' in row:
                row['FILES'] = ';'.join(
                    [f for f in filelist if f.startswith(row['Identifier'])]
                    )
                # print(f"{row['Identifier']},{row['FILES']}")

    def write(self):
        fieldnames = list(set().union(*[d.keys() for d in self.data]))
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in self.data:
            writer.writerow(row)


def read_files(filelist):
    with open(filelist) as handle:
        return [line.strip() for line in handle.readlines()]



if __name__ == "__main__":
    inputcsv = ArchelonBatchCsv(sys.argv[1])
    inputcsv.add_files_column(read_files(sys.argv[2]))
    inputcsv.write()
