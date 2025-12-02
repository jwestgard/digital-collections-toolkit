#!/usr/bin/env python3

from collections import namedtuple
from collections.abc import Collection
import csv
from pathlib import Path
import re
import sys


class Item:

    _registry = {}

    image_formats = [
            "http://vocab.lib.umd.edu/form#photographs",
            "http://vocab.lib.umd.edu/form#slides_photographs",
            "http://vocab.lib.umd.edu/form#architectural_drawings",
            "http://vocab.lib.umd.edu/form#art",
            "http://vocab.lib.umd.edu/form#paintings",
            "http://vocab.lib.umd.edu/form#sculpture"
            ]
    paged_formats = [
            "http://vocab.lib.umd.edu/form#personal_correspondence",
            "http://vocab.lib.umd.edu/form#manuscripts",
            "http://vocab.lib.umd.edu/form#drawings",
            "http://vocab.lib.umd.edu/form#records",
            "http://vocab.lib.umd.edu/form#fanzines",
            "http://vocab.lib.umd.edu/form#essays",
            "http://vocab.lib.umd.edu/form#programs",
            "http://vocab.lib.umd.edu/form#diaries",
            "http://vocab.lib.umd.edu/form#scores",
            "http://vocab.lib.umd.edu/form#transcripts",
            "http://vocab.lib.umd.edu/form#poetry",
            "http://vocab.lib.umd.edu/form#business_correspondence",
            "http://vocab.lib.umd.edu/form#periodicals",
            "http://vocab.lib.umd.edu/form#books",
            "http://vocab.lib.umd.edu/form#newspaper_clippings",
            "http://vocab.lib.umd.edu/form#catalogs",
            "http://vocab.lib.umd.edu/form#newsletters",
            "http://vocab.lib.umd.edu/form#sheet_music",
            "http://vocab.lib.umd.edu/form#pamphlets",
            "http://vocab.lib.umd.edu/form#drama",
            "http://vocab.lib.umd.edu/form#rosters",
            "http://vocab.lib.umd.edu/form#reports",
            "http://vocab.lib.umd.edu/form#cookbooks",
            "http://vocab.lib.umd.edu/form#press_releases",
            "http://vocab.lib.umd.edu/form#speeches",
            "http://vocab.lib.umd.edu/form#research_notes",
            "http://vocab.lib.umd.edu/form#chapbooks",
            "http://vocab.lib.umd.edu/form#manuscripts_publication"
            ]
    front_back_formats = [
            "http://vocab.lib.umd.edu/form#prints",
            "http://vocab.lib.umd.edu/form#posters",
            "http://vocab.lib.umd.edu/form#maps",
            "http://vocab.lib.umd.edu/form#diplomas",
            "http://vocab.lib.umd.edu/form#certificates",
            "http://vocab.lib.umd.edu/form#advertisements",
            "http://vocab.lib.umd.edu/form#ephemera",
            "http://vocab.lib.umd.edu/form#postcards",
            "http://vocab.lib.umd.edu/form#invitations",
            "http://vocab.lib.umd.edu/form#fliers_ephemera",
            "http://vocab.lib.umd.edu/form#property_records"
            ]

    def __init__(self, metadata):
        self.identifier = metadata['Identifier']
        self.metadata = metadata
        self.pages = []
        self.set_label()

    @classmethod
    def from_registry(cls, metadata):
        """
        Returns the object with the supplied identifier or creates and registers a 
        new object if none exists with the supplied identifier.
        """
        identifier = metadata['Identifier']
        if identifier not in cls._registry:
            cls._registry[identifier] = cls(metadata)
        return cls._registry[identifier]

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __repr__(self):
        return f"Item Object ({self.identifier})"

    def get_members_and_files(self, fileset):
        files = fileset.get_members(self.identifier, self.metadata['next_id'])
        for f in files:
            page = Page.from_registry(f.base)
            page.files.append(f)
            if page not in self.pages:
                self.pages.append(page)

    def set_label(self):
        format = self.metadata['Format']
        if format in self.image_formats:
            self.label = "Image"
        elif format in self.paged_formats:
            self.label = "Page"
        elif format in self.front_back_formats:
            self.label = "Front/Back"
        else:
            self.label = None


class Page:

    _registry = {}

    def __init__(self, identifier):
        self.identifier = identifier
        self.files = []

    @classmethod
    def from_registry(cls, identifier):
        """
        Returns the object with the supplied identifier or creates and registers a 
        new object if none exists with the supplied identifier.
        """
        if identifier not in cls._registry:
            cls._registry[identifier] = cls(identifier)
        return cls._registry[identifier]

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __repr__(self):
        return f"Page Object ({self.identifier})"


class ArchelonBatchCsv:

    def __init__(self, path):
        self.path = path
        with open(self.path, 'r') as handle:
            reader = csv.DictReader(handle)
            self.fieldnames = reader.fieldnames
            self.rows = [row for row in reader]
            for n in range(len(self.rows)):
                row = self.rows[n]
                try:
                    row['next_id'] = self.rows[n+1]['Identifier']
                except IndexError:
                    row['next_id'] = None

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
        writer = csv.DictWriter(sys.stdout,
                                fieldnames=self.fieldnames, 
                                extrasaction='ignore')
        writer.writeheader()
        for row in self.rows:
            writer.writerow(row)


class FileSet(Collection):

    File = namedtuple("File", ['relpath', 'base', 'item', 'ext', 'seq', 'usage'])

    item_pattern = r"^[a-z]+?-\d{6}$"
    member_pattern = r"^([a-z]+?-\d{6})-(\d{4})$"

    use_ext = {".tif": "<preservation>",
               ".jpg": "<preservation>",
               ".hocr": "<ocr>",
               ".xml": "<ocr>"}

    def __init__(self, root):
        self.contents = set()
        files = [p for p in Path(root).rglob("*") if p.is_file()]

        for f in files:
            item_match = re.match(self.item_pattern, f.stem)
            member_match = re.match(self.member_pattern, f.stem)
            if item_match:
                item = f.stem
                seq = None
            elif member_match:
                item = member_match.group(1)
                seq = int(member_match.group(2))
            else:
                item = None
                seq = None
            try:
                usage = self.use_ext[f.suffix]
            except KeyError:
                usage = None
            self.contents.add(self.File(relpath = f.relative_to(root),
                                        base = f.stem,
                                        item = item,
                                        ext = f.suffix,
                                        seq = seq,
                                        usage = usage
                                        ))

    def __iter__(self):
        return iter(self.contents)

    def __len__(self):
        return len(self.contents)

    def __contains__(self, other):
        if other in self.contents:
            return True
        else:
            return False

    def get_best_images(self, item_files):
        ''' Given a set of item-level files, return all tiffs or all jpegs plus 
            all ancillary files. '''
        all_pages = set([f.base for f in item_files])
        tiffs = set([f for f in item_files if f.ext == '.tif'])
        jpegs = set([f for f in item_files if f.ext == '.jpg'])
        non_image = set([f for f in item_files if f.ext not in ['.tif', '.jpg']])
        if set([f.base for f in tiffs]) == all_pages:
            return tiffs.union(non_image)
        elif set([f.base for f in jpegs]) == all_pages:
            return jpegs.union(non_image)
        else:
            return non_image

    def get_members(self, id, next_id):
        parts = id.split('-')
        if len(parts) == 2:
            files = sorted(
                [f for f in self.contents if f.item == id and f.seq is not None]
                )
        elif len(parts) == 3:
            id = "-".join(parts[:2])
            start = int(parts[2])
            if "-".join(next_id.split('-')[:2]) != id:
                files = sorted(
                    [f for f in self.contents if f.item == id and f.seq >= start]
                    )
            else:
                limit = int(next_id.split('-')[2])
                page_range = [i for i in range(start, limit)]
                files = sorted(
                    [f for f in self.contents if f.item == id and f.seq in page_range]
                    )
        return files

    def get_item_level(self, item):
        return [
            str(f.relpath) for f in self.contents if f.item == item and f.seq is None
            ]


if __name__ == "__main__":

    inputcsv = ArchelonBatchCsv(sys.argv[1])
    sys.stderr.write(f"Read {len(inputcsv.rows)} lines of metadata\n")
    fileset = FileSet(sys.argv[2])
    sys.stderr.write(f"Found {len(fileset)} files\n")
    inputcsv.add_files_column(fileset)
    inputcsv.add_item_files_column(fileset)
    inputcsv.write()
