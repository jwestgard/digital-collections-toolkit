#!/usr/bin/env python3

from .binaries import FileSet
from .archelon import Item, Page
import click
import pathlib
import sys


def walk_tree(root):
    root_path = pathlib.Path(root)
    return [p for p in root_path.rglob("*")]


@click.command()
@click.argument('root')
def validate(root):
    sys.stderr.write(f'Searching directory: {root}\n')
    fileset = FileSet(root)
    for f in fileset:
        i = Item.from_registry(f.item)
        if f.seq is not None:
            p = Page.from_registry(f.base)
            p.files.append(f)
            i.pages.append(p)
        else:
            i.files.append(f)
        
    for k, v in Item._registry.items():
        print(v.summarize())
        for p in sorted(v.pages):
            print(f"  ({p.seq}) {p.summarize()}")

    #print(len(Item._registry))