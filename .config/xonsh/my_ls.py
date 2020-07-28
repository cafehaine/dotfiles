import argparse
from collections import namedtuple
from fnmatch import fnmatch
import math
import os
import shutil
import stat
from typing import List

import magic

NameWidth = namedtuple('NameWidth', ['name', 'width'])

# Technically only 1, but kitty uses 2 "cells" for each emoji.
_LS_ICON_WIDTH = 2

_LS_ICONS = {
    'default':    "❔",
    'error':      "🚫",
    'folder':     "📁",
    'text':       "📄",
    'chart':      "📊",
    'music':      "🎵",
    'video':      "🎬",
    'photo':      "📷",
    'iso':        "💿",
    'compressed': "🗜 ",
    'application':"⚙ ",
    'rich_text':  "📰",
    'java':       "☕",
    'windows':    "🍷",
    'python':     "🐍",
    'php':        "🐘",
    'linux':      "🐧",
}

_LS_COLUMN_SPACING = 2

# Note that the order matters!
_LS_MIMETYPE_ICONS = [
    ('inode/directory', 'folder'),
    # Rich text
    ('application/pdf', 'rich_text'),
    ('application/vnd.oasis.opendocument.text', 'rich_text'),
    ('application/msword', 'rich_text'),
    ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'rich_text'),
    ('text/html', 'rich_text'),
    # Tabular data/charts
    ('application/vnd.oasis.opendocument.spreadsheet', 'chart'),
    ('application/vnd.ms-excel', 'chart'),
    ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'chart'),
    ('text/csv', 'chart'),
    # Java
    ('application/java-archive', 'java'),
    ('application/x-java-applet', 'java'),
    # Misc
    ('application/x-iso9660-image', 'iso'),
    ('application/zip', 'compressed'),
    ('application/x-dosexec', 'windows'),
    ('text/x-script.python', 'python'),
    ('text/x-php', 'php'),
    ('application/x-pie-executable', 'linux'),
    # Generics
    ('text/*', 'text'),
    ('application/*', 'application'),
    ('image/*', 'photo'),
    ('audio/*', 'music'),
    ('video/*', 'video'),
]


def _icon_from_mimetype(mimetype: str) -> str:
    """
    Return the emoji for a mimetype.
    """
    for pattern, icon_name in _LS_MIMETYPE_ICONS:
        if fnmatch(mimetype, pattern):
            return _LS_ICONS[icon_name]
    return _LS_ICONS['default']


def _format_direntry_name(entry: os.DirEntry, show_icons: bool = True) -> NameWidth:
    """
    Return a string containing a bunch of ainsi escape codes as well as the "width" of the new name.
    """
    path = entry.path if not entry.is_symlink() else os.readlink(entry.path)

    width = len(entry.name)
    name = entry.name

    if show_icons:
        icon = _LS_ICONS['error']

        try:
            # This is twice as fast as the "intended method"
            # magic.detect_from_filename(path).mime_type
            # since the "intended method" seems to run the matching twice
            mimetype = magic.mime_magic.file(path).split('; ')[0]
            icon = _icon_from_mimetype(mimetype)
        except:
            pass

        name = "{}{}".format(icon, name)
        width += _LS_ICON_WIDTH

    need_reset = False

    # if entry is a directory, add a trailing '/'
    if entry.is_dir():
        width += 1
        name = name + "/"

    # if entry is a symlink, underline it
    if entry.is_symlink():
        name = "\033[4m" + name
        need_reset = True

    # if entry is executable, make it bold (ignores directories as those must be executable)
    if not entry.is_dir() and os.access(path, os.X_OK):
        name = "\033[1m" + name
        need_reset = True

    if need_reset:
        name = name + "\033[0m"

    return NameWidth(name, width)


def _direntry_lowercase_name(entry: os.DirEntry) -> str:
    """
    Return the lowercase name for a DirEntry.

    This is used to sort list of DirEntry by name.
    """
    return entry.name.lower()


def _get_entries(path: str, show_hidden: bool) -> List[os.DirEntry]:
    """
    Return the list of DirEntrys for a path, sorted by name, directories first.
    """
    files = []
    directories = []
    try:
        with os.scandir(path) as iterator:
            for entry in iterator:
                # Skip entries that start with a '.'
                if not show_hidden and entry.name.startswith('.'):
                    continue

                if entry.is_dir():
                    directories.append(entry)
                else:
                    files.append(entry)
    except PermissionError:
        pass

    files.sort(key = _direntry_lowercase_name)
    directories.sort(key = _direntry_lowercase_name)
    return directories + files


def _get_column_width(entries: List[NameWidth], columns: int, column: int) -> int:
    """
    Return the width for a specific column when the layout uses a specified count of columns.
    """
    max_width_col = 0
    for i in range(column, len(entries), columns):
        if entries[i].width > max_width_col:
            max_width_col = entries[i].width
    return max_width_col


def _compute_width_for_columns(entries: List[NameWidth], columns: int) -> int:
    """
    Return the width occupied by the entries when using the specified column
    count.
    """
    # fetch the max width for each columns
    column_max_widths = []
    for col in range(columns):
        column_max_widths.append(_get_column_width(entries, columns, col))

    return sum(column_max_widths) + (columns - 1) * _LS_COLUMN_SPACING


def _determine_column_count(entries: List[NameWidth], term_width: int) -> int:
    """
    Return the number of columns that should be used to display the listing.
    """
    max_column_count = 1
    min_width = min(entries, key=lambda e: e.width).width

    #TODO This could probably be smaller.
    for i in range(term_width // min_width):
        if _compute_width_for_columns(entries, i) < term_width:
            max_column_count = max(i, max_column_count)

    return max_column_count


def _list_directory(path: str, show_hidden: bool = False) -> None:
    """
    Display a listing for a single directory.
    """
    direntries = _get_entries(path, show_hidden)

    if not direntries:
        print("[no files]")
        return

    entries = [_format_direntry_name(direntry) for direntry in direntries]

    term_size = shutil.get_terminal_size()

    column_count = _determine_column_count(entries, term_size.columns)

    row_count = math.ceil(len(entries) / column_count)
    columns = [[] for i in range(column_count)]

    # Generate the columns
    for index, (name, width) in enumerate(entries):
        column_index = index % column_count
        column_width = _get_column_width(entries, column_count, column_index)
        if column_index == column_count - 1:
            columns[column_index].append(name)
        else:
            columns[column_index].append(name + (" " * (column_width - width)))


    # Show the rows
    for row in range(row_count):
        line = []
        for col in range(column_count):
            if row < len(columns[col]):
                line.append(columns[col][row])
        print((" " * _LS_COLUMN_SPACING).join(line))


def _tree_list(path: str, show_hidden: bool = False, prefix: str = "") -> None:
    """
    Recursively prints a tree structure of the filesystem.
    """
    #TODO handle properly "loops" of symlinks.
    direntries = _get_entries(path, show_hidden)
    for index, direntry in enumerate(direntries):
        is_last_entry = index == len(direntries) - 1
        entry_prefix = prefix + ("╰─" if is_last_entry else "├─")
        print("{}{}".format(entry_prefix, _format_direntry_name(direntry).name))
        if direntry.is_dir():
            _tree_list(direntry.path, show_hidden, prefix + ("  " if is_last_entry else "│ "))



_ls_parser = argparse.ArgumentParser()
_ls_parser.add_argument('paths', type=str, nargs='*', default=['.'], help="The directories to list")
_ls_parser.add_argument("-a", "--all", help="Don't hide entries starting with .", action="store_true")
_ls_format_group = _ls_parser.add_mutually_exclusive_group()
#_ls_format_group.add_argument("-l", help="Long listing format", action="store_true")
_ls_format_group.add_argument("-R", "--recursive", help="Show in a tree format", action="store_true")


def _ls(args):
    """
    My custom ls function.

    It adds icons like LSD, but also tweaks colors/display in order to have
    ntfs volumes not be a green mess.

    It also displays a tree structure when called with the recursive flag.
    """
    arguments = _ls_parser.parse_args(args)
    for path in arguments.paths:
        if arguments.recursive:
            _tree_list(path, arguments.all)
        else:
            _list_directory(path, arguments.all)


aliases['ls'] = _ls
