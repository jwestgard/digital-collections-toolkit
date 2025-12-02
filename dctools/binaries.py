from collections import namedtuple
from collections.abc import Collection
from pathlib import Path
from re import match


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
            item_match = match(self.item_pattern, f.stem)
            member_match = match(self.member_pattern, f.stem)
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
            self.contents.add(
                self.File(relpath = f.relative_to(root),
                          base = f.stem,
                          item = item,
                          ext = f.suffix,
                          seq = seq,
                          usage = usage
                          )
                )

    def __iter__(self):
        return iter(self.contents)

    def __len__(self):
        return len(self.contents)

    def __contains__(self, other):
        if other in self.contents:
            return True
        else:
            return False

    def as_object_tree(self):
        results = []
        for f in self.contents:
            item = Item.from_registry(f.item)
            if f.seq is not None:
                page = Page.from_registry(f.base)
                page.files.append(f)
                if page not in item.pages:
                    item.pages.append(page)
            if item not in results:
                results.append(item)
        return results

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

    def get_members(self, id, next_id=None):
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
            elif next_id is not None:
                limit = int(next_id.split('-')[2])
                page_range = [i for i in range(start, limit)]
                files = sorted(
                    [f for f in self.contents if f.item == id and f.seq in page_range]
                    )
            else:
                files = []
        return files

    def get_item_level(self, item):
        return [
            str(f.relpath) for f in self.contents if f.item == item and f.seq is None
            ]
