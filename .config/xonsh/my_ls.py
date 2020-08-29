import argparse
from collections import namedtuple
from enum import Enum, auto
from fnmatch import fnmatch
import grp
import math
import os
import pwd
import shutil
import stat
import time
from typing import List, Union

import magic
from xonsh.proc import STDOUT_CAPTURE_KINDS

NameWidth = namedtuple('NameWidth', ['name', 'width'])

class ColumnAlignment(Enum):
    LEFT = auto()
    RIGHT = auto()
    IGNORE = auto()
    #TODO CENTERED = auto()


_LS_STAT_FILE_TYPE_ICONS = {
    stat.S_IFSOCK: "🌐",
    stat.S_IFLNK:  "🔗",
    stat.S_IFREG:  "📄",
    stat.S_IFBLK:  "💾",
    stat.S_IFDIR:  "📁",
    stat.S_IFCHR:  "🖶 ",
    stat.S_IFIFO:  "🚿",
}

# Technically only 1, but kitty uses 2 "cells" for each emoji.
_LS_ICON_WIDTH = 2
#TODO This should be determined per-icon with wcwidth

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
    'stylesheet': "🎨",
    'contacts':   "📇",
    'calendar':   "📅",
    'config':     "🔧",
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
    ('text/vcard', 'contacts'),
    ('text/calendar', 'calendar'),
    # Generics
    ('text/*', 'text'),
    ('application/*', 'application'),
    ('image/*', 'photo'),
    ('audio/*', 'music'),
    ('video/*', 'video'),
]

_LS_EXTENSION_ICONS = [
    # Text
    ({'txt', 'log'}, 'text'),
    ({'json', 'xml', 'ini', 'conf', 'rc', 'cfg', 'vbox', 'vbox-prev'}, 'config'),
    # Photo
    ({'jpe', 'jpg', 'jpeg', 'png', 'apng', 'gif', 'bmp', 'ico', 'tif', 'tiff', 'tga', 'webp', 'xpm', 'xcf', 'svg'}, 'photo'),
    # Music
    ({'flac', 'ogg', 'mp3', 'wav'}, 'music'),
    # Video
    ({'avi', 'mp4'}, 'video'),
    # Rich text
    ({'pdf', 'odt', 'doc', 'docx', 'html', 'htm', 'xhtm', 'xhtml', 'md', 'rtf', 'tex'}, 'rich_text'),
    # Tabular data/charts
    ({'ods', 'xls', 'xlsx', 'csv'}, 'chart'),
    # Programming languages
    ({'jar', 'jad'}, 'java'),
    ({'py'}, 'python'),
    ({'php'}, 'php'),
    ({'css', 'less', 'colorscheme', 'theme', 'xsl'}, 'stylesheet'),
    # Compressed files
    ({'zip', '7z', 'rar', 'gz', 'xz'}, 'compressed'),
    # Executables
    ({'exe', 'bat', 'cmd', 'dll'}, 'windows'),
    ({'so', 'elf', 'sh', 'xsh', 'zsh', 'ksh', 'pl'}, 'linux'),
    # Misc
    ({'iso', 'cue'}, 'iso'),
    ({'vcard'}, 'contacts'),
    ({'ics'}, 'calendar'),
]


def _format_size(size: int) -> str:
    """
    Format a binary size using the IEC units.
    """
    units = ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi"]
    unit_index = 0

    while size > 1024 and unit_index < len(units) - 1:
        unit_index += 1
        size /= 1024

    return "{:.1f}{}B".format(size, units[unit_index])


def _icon_from_mimetype(mimetype: str) -> str:
    """
    Return the emoji for a mimetype.
    """
    for pattern, icon_name in _LS_MIMETYPE_ICONS:
        if fnmatch(mimetype, pattern):
            return _LS_ICONS[icon_name]
    return _LS_ICONS['default']


def _icon_for_direntry(entry: os.DirEntry, real_path: str) -> str:
    """
    Return the emoji for a direntry.

    First tries to determine the emoji using the file extension, and then falls
    back to using mimetypes.
    """
    if entry.is_dir(follow_symlinks=True):
        return _LS_ICONS['folder']

    # Extension based matching
    _, extension = os.path.splitext(entry.name)
    extension = extension[1:].lower() # remove leading '.' and use lowercase

    for extensions, icon_name in _LS_EXTENSION_ICONS:
        if extension in extensions:
            return _LS_ICONS[icon_name]

    # Fall back to mimetype matching
    icon = _LS_ICONS['error']
    try:
        # This is twice as fast as the "intended method"
        # magic.detect_from_filename(path).mime_type
        # since the "intended method" seems to run the matching twice
        mimetype = magic.mime_magic.file(real_path).split('; ')[0]
        icon = _icon_from_mimetype(mimetype)
    except:
        pass
    return icon


def _format_direntry_name(entry: os.DirEntry, show_target: bool = True) -> NameWidth:
    """
    Return a string containing a bunch of ainsi escape codes as well as the "width" of the new name.
    """
    path = entry.path if not entry.is_symlink() else os.readlink(entry.path)
    width = len(entry.name)
    name = entry.name
    # if we need to send the ainsi reset sequence
    need_reset = False

    # Show the icon
    icon = _icon_for_direntry(entry, path)
    name = "{}{}".format(icon, name)
    width += _LS_ICON_WIDTH

    # if entry is a directory, add a trailing '/'
    if entry.is_dir():
        width += 1
        name = name + "/"

    # if entry is a symlink, underline it
    if entry.is_symlink():
        if show_target:
            # Show "source -> target" (with some colors)
            target = os.readlink(entry.path)
            name = "\033[4m{}\033[0m \033[96m->\033[0m {}".format(name, target)
            width += 4 + len(target)
        else:
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


def _get_column_width(entries: List[Union[NameWidth, str]], columns: int, column: int) -> int:
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

    entries = [_format_direntry_name(direntry, False) for direntry in direntries]

    term_size = shutil.get_terminal_size()

    column_count = _determine_column_count(entries, term_size.columns)

    row_count = math.ceil(len(entries) / column_count)
    columns = [[] for i in range(column_count)]

    # Generate the columns
    for index, entry in enumerate(entries):
        column_index = index % column_count
        columns[column_index].append(entry)

    _show_table(columns)


def _tree_list(path: str, show_hidden: bool = False, prefix: str = "") -> None:
    """
    Recursively prints a tree structure of the filesystem.
    """
    direntries = _get_entries(path, show_hidden)
    for index, direntry in enumerate(direntries):
        is_last_entry = index == len(direntries) - 1
        entry_prefix = prefix + ("╰─" if is_last_entry else "├─")
        print("{}{}".format(entry_prefix, _format_direntry_name(direntry, True).name))
        if direntry.is_dir() and not direntry.is_symlink():
            _tree_list(direntry.path, show_hidden, prefix + ("  " if is_last_entry else "│ "))


def _column_max_width(column: List[Union[NameWidth, str]]) -> int:
    """
    Return the maximum width for a column.
    """
    max_width = 0
    for cell in column:
        if isinstance(cell, NameWidth):
            max_width = max(max_width, cell.width)
        elif isinstance(cell, str):
            max_width = max(max_width, len(cell))

    return max_width


def _show_table(columns: List[List[Union[NameWidth, str]]], column_alignments: List[ColumnAlignment] = None) -> None:
    """
    Display a table in the terminal.
    """
    if column_alignments is None:
        column_alignments = [ColumnAlignment.LEFT for column in columns]

    column_max_widths = [_column_max_width(column) for column in columns]

    max_row = len(max(columns, key=lambda col: len(col)))

    for row in range(max_row):
        row_text = []
        for index, col in enumerate(columns):
            last_column = index == len(columns) - 1
            text_value = ""
            length = 0
            if len(col) > row:
                cell = col[row]
                if isinstance(cell, NameWidth):
                    text_value = cell.name
                    length = cell.width
                else:
                    text_value = cell
                    length = len(cell)

            if length < column_max_widths[index]:
                alignment = column_alignments[index]
                to_pad = column_max_widths[index] - length
                if alignment == ColumnAlignment.LEFT and not last_column:
                    text_value = text_value + " " * to_pad
                elif alignment == ColumnAlignment.RIGHT:
                    text_value = " " * to_pad + text_value
                elif alignment == ColumnAlignment.IGNORE:
                    pass
            row_text.append(text_value)

        print((" " * _LS_COLUMN_SPACING).join(row_text))


def _format_mode(mode: int) -> str:
    """
    Format the mode from the stat structure for a file.
    """
    file_type = stat.S_IFMT(mode)
    permissions = mode - file_type
    return "{}{:4o}".format(_LS_STAT_FILE_TYPE_ICONS[file_type], permissions)


def _long_list(path: str, show_hidden: bool = False) -> None:
    """
    Display the long list format for a directory.
    """
    #TODO less "hardcoded" way with a separate function for each column?
    direntries = _get_entries(path, show_hidden)
    columns = [[],[],[],[],[],[],[]]
    for direntry in direntries:
        stat = direntry.stat()
        stat_no_follow = direntry.stat(follow_symlinks=False)
        #TODO better format than just octal base
        columns[0].append(_format_mode(stat_no_follow.st_mode))
        columns[1].append(str(stat.st_nlink))
        columns[2].append(pwd.getpwuid(stat.st_uid)[0])
        columns[3].append(grp.getgrgid(stat.st_gid)[0])
        columns[4].append(_format_size(stat.st_size))
        #TODO better format (today, a year ago..)
        columns[5].append(time.strftime("%x %X", time.gmtime(stat.st_mtime)))
        columns[6].append(_format_direntry_name(direntry, True).name)

    _show_table(columns, [
        ColumnAlignment.IGNORE,
        ColumnAlignment.RIGHT,
        ColumnAlignment.LEFT,
        ColumnAlignment.LEFT,
        ColumnAlignment.RIGHT,
        ColumnAlignment.LEFT,
        ColumnAlignment.LEFT
        ])

_ls_parser = argparse.ArgumentParser()
_ls_parser.add_argument('paths', type=str, nargs='*', default=['.'], help="The directories to list")
_ls_parser.add_argument("-a", "--all", help="Don't hide entries starting with .", action="store_true")
_ls_format_group = _ls_parser.add_mutually_exclusive_group()
_ls_format_group.add_argument("-l", help="Long listing format", action="store_true")
_ls_format_group.add_argument("-R", "--recursive", help="Show in a tree format", action="store_true")


def _ls(args, stdin, stdout, stderr, spec):
    """
    My custom ls function.

    It adds icons like LSD, but also tweaks colors/display in order to have
    ntfs volumes not be a green mess.

    It also displays a tree structure when called with the recursive flag.
    """
    if spec.captured in STDOUT_CAPTURE_KINDS or not spec.last_in_pipeline:
        # If not running from a terminal, use system's "ls" binary.
        #TODO use xonsh's subprocess infrastructure
        @(["/usr/bin/env", "ls"] + args)
        return

    arguments = _ls_parser.parse_args(args)
    for index, path in enumerate(arguments.paths):
        if len(arguments.paths) > 1:
            print("{}:".format(path))

        if arguments.recursive:
            _tree_list(path, arguments.all)
        elif arguments.l:
            _long_list(path, arguments.all)
        else:
            _list_directory(path, arguments.all)

        if len(arguments.paths) > 1 and index != len(arguments.paths) - 1:
            print()


aliases['ls'] = _ls
