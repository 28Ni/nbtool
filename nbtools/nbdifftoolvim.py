#!/usr/bin/env python

"""
Diff directories LEFT and RIGHT with vim, using diffable representation of
IPython notebooks.
"""

import argparse
import os
from os.path import join, splitext, relpath, isdir
import subprocess

def parse_command_line():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('left', metavar='LEFT',
                       help='Left directory to compare')
    parser.add_argument('right', metavar='RIGHT',
                       help='Right directory to compare')
    return parser.parse_args()

def nbcatsrc(src_filepath, dst_filepath):
    cmd = 'nbcatsrc %s > %s' % (src_filepath, dst_filepath)
    subprocess.check_call(cmd, shell=True)

def mirror_path(left_or_right):
    return join(left_or_right, 'mirror')

def create_mirror(left_or_right):
    """
    Create mirror of left/right directory, with diffable notebook.

    Notebook cell sources are copied, but output at stripped.  Other files are
    hard linked.

    Because notebook are copied and other files are hard linked, changes in
    mirrors are reflected only for other files. So if left or right is working
    directory, only changes to other files are copied back. Original notebooks
    are not overriden with the diffable representation.
    """
    rootname = lambda filename: splitext(filename)[0]
    ext = lambda filename: splitext(filename)[1]

    mirror = mirror_path(left_or_right)

    for src_dirpath, ignored_dirs, src_filenames in os.walk(left_or_right):
        for src_filename in src_filenames:
            src_filepath = join(src_dirpath, src_filename)

            dst_dirpath = join(mirror, relpath(src_dirpath, left_or_right))
            if not isdir(dst_dirpath):
                os.makedirs(dst_dirpath)

            if ext(src_filename) == '.ipynb':
                dst_filename = rootname(src_filename) + '_diffable.ipynb'
                dst_filepath = join(dst_dirpath, dst_filename)
                nbcatsrc(src_filepath, dst_filepath)
            else:
                dst_filename = src_filename
                dst_filepath = join(dst_dirpath, dst_filename)
                os.link(src_filepath, dst_filepath)
    return mirror

def vim_dirdiff(left, right):
    cmd = '''vim -f '+next' '+execute "DirDiff" ''' \
          """argv(0) argv(1)' %s %s '+syntax off'""" \
          % (left, right)
    subprocess.check_call(cmd, shell=True)

def main():
    args = parse_command_line()
    mirror_left = create_mirror(args.left)
    mirror_right = create_mirror(args.right)
    vim_dirdiff(mirror_left, mirror_right)

if __name__ == '__main__':
    main()

