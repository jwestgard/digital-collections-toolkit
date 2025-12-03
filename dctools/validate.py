from .binaries import FileSet
from .archelon import Item, Page
import click
import csv
import sys


@click.command()
@click.argument('root')
def validate(root):
    #sys.stderr.write(f'Searching directory: {root}\n')
    fileset = FileSet(root)
    for file in fileset:
        item = Item.from_registry(file.item)
        if file.seq is not None:
            page = Page.from_registry(file.base)
            page.files.add(file)
            item.pages.add(page)
        else:
            item.files.add(file)

    writer = csv.writer(sys.stdout)
    writer.writerow(["id","item_files","tif","hocr","xml"])

    for item in sorted(Item._registry.values()):
        writer.writerow([
        	item.identifier,
        	len(item.files)
        	])
        for page in sorted(item.pages):
        	writer.writerow([
        		page.identifier,
        		None, # "Item files" column
        		page.count('.tif'),
        		page.count('.hocr'),
        		page.count('.xml')
        		])
