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
    'folder':     "📁",
    'text':       "📄",
    'chart':      "📊",
    'music':      "🎵",
    'video':      "🎬",
    'photo':      "📷",
    'iso':        "💿",
    'compressed': "🗜 ",
    'application':"⚙ ",
}

# Note that the order matters!
_LS_MIMETYPE_ICONS = [
    ('inode/directory', 'folder'),
    ('text/*', 'text'),
    ('image/*', 'photo'),
    ('audio/*', 'music'),
    ('video/*', 'video'),
    ('application/vnd.oasis.opendocument.spreadsheet', 'chart'),
    ('application/x-iso9660-image', 'iso'),
    ('application/zip', 'compressed'),
    ('application/*', 'application')
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

    #TODO quote names

    if show_icons:
        mimetype = magic.detect_from_filename(path).mime_type
        name = "{} {}".format(_icon_from_mimetype(mimetype), name)
        width += _LS_ICON_WIDTH + 1

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
    with os.scandir() as iterator:
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

    # max_width + 1 to add a space between columns
    column_count = term_size.columns // (max_width + 1)

    if column_count == 0:
        #TODO truncate names
        print("TOO LONG!!")
        /usr/bin/ls
        return

    row_count = math.ceil(len(entries) / column_count)
    columns = [[] for i in range(column_count)]

    # Generate the columns
    for index, (name, width) in enumerate(entries):
        columns[index % column_count].append(name + (" " * (max_width - width)))

    # Show the rows
    for row in range(row_count):
        line = []
        for col in range(column_count):
            if row < len(columns[col]):
                line.append(columns[col][row])
            else:
                line.append(" " * max_width)
        print(" ".join(line))


def _ls(args):
    """
    My custom ls function.

    It adds icons like LSD, but also tweaks colors/display in order to have
    ntfs volumes not be a green mess.

    It also displays a tree structure when called with the recursive flag.
    """
    #TODO parse args
    _list_directory(".")


aliases['ls'] = _ls
