#!/usr/bin/env python3

import csv
import os


class Batch:
    """ Class representing a batch of items to be loaded to Avalon. """

    def __init__(self, objects=None, batchtitle=None, batchcontact=None):
        self.title = batchtitle
        self.contact = batchcontact
        if objects:
            self.contents = [Item(*obj) for obj in objects]

    @classmethod
    def from_csv(cls, filepath):
        """ Populate a Batch object using the contents of an existing Avalon CSV. """
        
        with open(filepath) as handle:
            title, contact = handle.readline().strip().split(',')[:2]
            fields = handle.readline().strip().split(',')
            reader = csv.reader(handle.read().split('\n'))
            items = [list(zip(fields, row)) for row in reader if row]

        return cls(items, batchtitle=title, batchcontact=contact)

    def serialize(self, outputpath):
        """ Write the batch metadata into a CSV file at the specified path. """
        pass


class Item:
    """ Class representing the metadata for a single digital object in an Avalon 
            batch load. """

    def __init__(self, *args):
        self.metadata = dict()
        for key, value in args:
            if value and value != "":
                self.metadata.setdefault(key, []).append(value)

    def __repr__(self):
        lines = []
        for key, values in self.metadata.items():
            lines.append(f"{key.upper()}: {'; '.join([v for v in values])}")
        return "\n".join(lines)


class BinarySet:
    """ Class representing a directory tree containing binaries. """

    def __init__(self, filepath):
        self.filepath = filepath



