import csv
import sys


class Item:

    _registry = {}

    def __init__(self, identifier):
        self.identifier = identifier
        self.files = []
        self.pages = []

    @classmethod
    def from_registry(cls, identifier):
        """ Returns the object with the supplied identifier or creates and registers a
               new object if none exists with the supplied identifier. """
               
        if identifier not in cls._registry:
            cls._registry[identifier] = cls(identifier)
        return cls._registry[identifier]

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __repr__(self):
        return f"Item Object ({self.identifier})"

    def count(self, ext):
        return f"{len([f for f in self.files if f.ext == ext])} {ext.strip('.')}"

    def summarize(self):
        exts = set(f.ext for f in self.files)
        file_counts = ", ".join(sorted([self.count(ext) for ext in exts]))
        return f"{self.identifier}: {file_counts}"


class Page:

    _registry = {}

    def __init__(self, identifier):
        self.identifier = identifier
        self.seq = int(identifier.split('-')[-1])
        self.files = []

    @classmethod
    def from_registry(cls, identifier):
        """ Returns the object with the supplied identifier or creates and registers a 
            new object if none exists with the supplied identifier. """

        if identifier not in cls._registry:
            cls._registry[identifier] = cls(identifier)
        return cls._registry[identifier]

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __repr__(self):
        return f"Page Object ({self.identifier})"

    def count(self, ext):
        return f"{len([f for f in self.files if f.ext == ext])} {ext}"

    def summarize(self):
        exts = set(f.ext for f in self.files)
        file_counts = ", ".join(sorted([self.count(ext) for ext in exts]))
        return f"{self.identifier}: {file_counts}"



class MetadataCsv:

    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as handle:
            reader = csv.DictReader(handle)
            self.fieldnames = reader.fieldnames
            self.rows = [row for row in reader]

    def add_files_column(self, files):
        if 'FILES' not in self.fieldnames:
            self.fieldnames.append('FILES')
        for row in self.rows:
            sys.stderr.write(f"Working on {row['Identifier']}\n")
            item = Item.from_registry(row)
            item.get_members_and_files(files)
            if not 'FILES' in row:
                entries = []
                for n, page in enumerate(sorted(item.pages), 1):
                    entries.append(f"{item.label} {n}:" + ";".join(
                        [f"{f.usage}{f.relpath}" for f in page.files]
                        ))
                row['FILES'] = ";".join(entries)

    def add_item_files_column(self, files):
        if 'ITEM_FILES' not in self.fieldnames:
            self.fieldnames.append('ITEM_FILES')
        for row in self.rows:
            if not 'ITEM_FILES' in row or row['ITEM_FILES'] == '':
                row['ITEM_FILES'] = ';'.join(
                    files.get_item_level(row['Identifier'])
                    )

    def write(self):
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=self.fieldnames, 
            extrasaction='ignore'
            )
        writer.writeheader()
        for row in self.rows:
            writer.writerow(row)

