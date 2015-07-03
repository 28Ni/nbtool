#!/usr/bin/env python

"""
Execute an IPython notebook, and compare output difference with the original.

It produce an HTML report
"""

import os
import argparse
import tempfile
import shutil
import contextlib
import subprocess
import textwrap
import re
import traceback

import ghdiff
import jinja2
from matplotlib.testing import compare as mpl_compare

# Come from nbconvert/nbconvert/preprocessors/tests/test_execute.py
addr_pat = re.compile(r'0x[0-9a-f]{7,12}')

class RST(object):
    """ A reStructuredText file, plus images it includes """

    def __init__(self, rst_filepath, image_dirpath, image_filenames):
        self.rst_filepath  = rst_filepath
        self.image_dirpath = image_dirpath
        self.image_filenames = image_filenames

        self.text = open(self.rst_filepath).read()
        self.text = re.sub(addr_pat, '<HEXADDR>', self.text)

    def __str__(self):
        return textwrap.dedent("""\
            RST file: {self.rst_filepath}
            Images directory: {self.image_dirpath}
            Image files: {self.image_filenames}""").format(self=self)

def read_image(directory, filename):
    filepath = os.path.join(directory, filename)
    return open(filepath, 'rb').read().encode('base64').replace('\n','')

class UncomparableImages(object):
    """Images that matplotlib can not compare (different size, ...)"""

    def __init__(self, filename, actual_dir, expected_dir, traceback):
        self.filename = filename
        self.actual_dir = actual_dir
        self.expected_dir = expected_dir
        self.traceback = traceback

        self.actual_image = read_image(actual_dir, filename)
        self.expected_image = read_image(expected_dir, filename)

class DifferentImages(object):
    """Image that matplotlib compared different"""

    def __init__(self, filename, actual_dir, expected_dir, error):
        self.filename = filename
        self.actual_dir = actual_dir
        self.expected_dir = expected_dir
        self.error = error

        rootname, ext = os.path.splitext(filename)
        diff_filename = rootname + '-failed-diff' + ext

        self.actual_image = read_image(actual_dir, filename)
        self.expected_image = read_image(expected_dir, filename)
        self.diff_image = read_image(expected_dir, diff_filename)


class ImageDifferences(object):
    """ Store differences between images """

    def __init__(self, only_in_actual, only_in_expected):
        self.only_in_actual = only_in_actual
        self.only_in_expected = only_in_expected
        self.uncomparable = []
        self.different = []

@contextlib.contextmanager  
def chdir(dirname=None):  
    curdir = os.getcwd()  
    try:  
        if dirname is not None:  
            os.chdir(dirname)  
        yield  
    finally:  
        os.chdir(curdir)

def parse_command_line():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('notebook', 
        help="Input notebook file to validate")

    return parser.parse_args()

def convert_to_rst(notebook, outdir, execute=False):
    if execute:
        args = ['ipython', 'nbconvert', '--execute', '--to', 'rst', notebook]
    else:
        args = ['ipython', 'nbconvert', '--to', 'rst', notebook]
    os.mkdir(outdir)
    with chdir(outdir):
        subprocess.check_call(args)

    rst_basename = os.path.basename(notebook)
    rst_rootname = os.path.splitext(rst_basename)[0]
    rst_filename =  rst_rootname + '.rst'
    rst_filepath = os.path.join(outdir, rst_filename)
    image_dirpath = os.path.join(outdir, '%s_files' % rst_rootname)
    image_filenames = os.listdir(image_dirpath)

    return RST(rst_filepath, image_dirpath, image_filenames) 

def diff_rst(actual_rst, expected_rst):
    return ghdiff.diff(actual_rst.text, expected_rst.text)

def compare_images(actual_rst, expected_rst):
    actual_images = set(actual_rst.image_filenames)
    expected_images = set(expected_rst.image_filenames)

    only_in_actual = actual_images - expected_images
    only_in_expected = expected_images - actual_images

    image_differences = ImageDifferences(only_in_actual, only_in_expected)

    for filename in actual_images.intersection(expected_images):
        actual = os.path.join(actual_rst.image_dirpath, filename)
        expected = os.path.join(expected_rst.image_dirpath, filename)
        try:
            error = mpl_compare.compare_images(actual, expected, 0.001)
        except:
            tb = traceback.format_exc()
            image_differences.uncomparable.append(
                UncomparableImages(
                    filename,
                    actual_rst.image_dirpath,
                    expected_rst.image_dirpath,
                    tb,
            ))
        else:
            if error:
                image_differences.different.append(
                    DifferentImages(
                        filename,
                        actual_rst.image_dirpath,
                        expected_rst.image_dirpath,
                        error,
                ))

    return image_differences


def write_report(name, diff, image_differences, reportfile):
    env = jinja2.Environment(loader=jinja2.PackageLoader('nbtools','templates'))
    template = env.get_template('report.html')
    report = template.render(
        name = name,
        diff = diff,
        only_in_actual = image_differences.only_in_actual,
        only_in_expected = image_differences.only_in_expected,
        different_images = image_differences.different,
        uncomparable_images = image_differences.uncomparable,
    )
    with open(reportfile,'w') as f:
        f.write(report)

def main():
    args = parse_command_line()
    notebook = os.path.abspath(args.notebook)
    reportfile = os.path.realpath('report.html')

    workdir = tempfile.mkdtemp()
    expected_dir = os.path.join(workdir, 'expected')
    actual_dir = os.path.join(workdir, 'actual')
    
    actual_rst = convert_to_rst(notebook, actual_dir, execute=True)
    expected_rst = convert_to_rst(notebook, expected_dir)

    diff = diff_rst(actual_rst, expected_rst)
    image_differences = compare_images(actual_rst, expected_rst)

    write_report(args.notebook, diff, image_differences, reportfile)
    print reportfile

    shutil.rmtree(workdir)

if __name__ == '__main__':
    main()
