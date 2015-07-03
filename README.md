Provides two commands, `nbcatsrc` and `nbdifftoolvim`.

## nbcatsrc

Write to standard output a diffable representation of IPython notebook.

Only cell sources (markdown or code) are preserved.

## nbdifftoolvim

Diff directories LEFT and RIGHT with Vim, using diffable representation of
IPython notebooks.

## nbvalidate

Execute an IPython notebook, and compare output difference with the original.

It produce an HTML report.

For example:

    FOO_HAS_CHANGED=1 nbconvert nbtools/tests/figure.ipynb

produce the HTML report `nbtools/tests/report.html`.
  

## Prerequisites

For using `nbdifftoolvim`, [vim-dirdiff](https://github.com/will133/vim-dirdiff)
Vim plugin must be installed.

Other dependencies come with `conda install`.

## Installation

    conda install -c dfroger nbtools

## Configure git difftool:

    git config --global diff.tool default-difftool
    git config --global difftool.default-difftool.cmd 'nbdifftoolvim $LOCAL $REMOTE'
    git config --global diff.ipynb.textconv nbcatsrc
    git config --global diff.ipynb.cachetextconv true

    echo '*.ipynb diff=ipynb' >> ~/.gitattributes  # in Git repo
    git config --global core.attributesfile ~/.gitattributes

Then you can use:

    git difftool -d

## References:

[Notebook format](http://ipython.org/ipython-doc/dev/notebook/nbformat.html)

