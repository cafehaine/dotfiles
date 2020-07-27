import argparse
from fnmatch import fnmatch
import math
import os
import shutil
import stat
from typing import List, Tuple

import magic

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
}

_LS_COLUMN_SPACING = 2

# Note that the order matters!
_LS_MIMETYPE_ICONS = [
    ('inode/directory', 'folder'),
    ('image/*', 'photo'),
    ('audio/*', 'music'),
    ('video/*', 'video'),
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

    ('application/x-iso9660-image', 'iso'),
    ('application/zip', 'compressed'),
    ('application/*', 'application'),

    ('text/*', 'text'),
]

def _icon_from_mimetype(mimetype: str) -> str:
    """
    Return the emoji for a mimetype.
    """
    for pattern, icon_name in _LS_MIMETYPE_ICONS:
        if fnmatch(mimetype, pattern):
            return _LS_ICONS[icon_name]
    return _LS_ICONS['default']

def _format_direntry_name(entry: os.DirEntry, show_icons: bool = True) -> Tuple[str, int]:
    """
    Return a string containing a bunch of ainsi escape codes as well as the "width" of the new name.
    """
    path = entry.path if not entry.is_symlink() else os.readlink(entry.path)

    width = len(entry.name)
    name = entry.name

    if show_icons:
        icon = _LS_ICONS['error']

        try:
            mimetype = magic.detect_from_filename(path).mime_type
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

    return (name, width)


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
    with os.scandir(path) as iterator:
        for entry in iterator:
            # Skip entries that start with a '.'
            if not show_hidden and entry.name.startswith('.'):
                continue

            if entry.is_dir():
                directories.append(entry)
            else:
                files.append(entry)

    files.sort(key = _direntry_lowercase_name)
    directories.sort(key = _direntry_lowercase_name)
    return directories + files


def _list_directory(path: str, show_hidden: bool = False) -> None:
    """
    Display a listing for a single directory.
    """
    direntries = _get_entries(path, show_hidden)

    if not direntries:
        print("[no files]")
        return

    entries = [_format_direntry_name(direntry) for direntry in direntries]

    max_width = max([entry[1] for entry in entries])
    term_size = shutil.get_terminal_size()

    #TODO "brute force" the layout (looks like coreutils' ls does it this way)

    # max_width + 1 to add a space between columns
    column_count = term_size.columns // (max_width + _LS_COLUMN_SPACING)

    if column_count == 0:
        column_count = 1

    row_count = math.ceil(len(entries) / column_count)
    columns = [[] for i in range(column_count)]

    # Generate the columns
    for index, (name, width) in enumerate(entries):
        # Don't pad with spaces on last column
        if index % column_count == column_count - 1:
            columns[index % column_count].append(name)
        else:
            columns[index % column_count].append(name + (" " * (max_width - width)))


    # Show the rows
    for row in range(row_count):
        line = []
        for col in range(column_count):
            if row < len(columns[col]):
                line.append(columns[col][row])
        print((" " * _LS_COLUMN_SPACING).join(line))


_ls_parser = argparse.ArgumentParser()
_ls_parser.add_argument('paths', type=str, nargs='*', default=['.'], help="The directories to list")
_ls_parser.add_argument("-a", "--all", help="Don't hide entries starting with .", action="store_true")
#TODO
#_ls_format_group = _ls_parser.add_mutually_exclusive_group()
#_ls_format_group.add_argument("-l", help="Long listing format", action="store_true")
#_ls_format_group.add_argument("-R", "--recursive", help="Show in a tree format", action="store_true")


def _ls(args):
    """
    My custom ls function.

    It adds icons like LSD, but also tweaks colors/display in order to have
    ntfs volumes not be a green mess.

    It also displays a tree structure when called with the recursive flag.
    """
    arguments = _ls_parser.parse_args(args)
    for path in arguments.paths:
        _list_directory(path, arguments.all)


aliases['ls'] = _ls
