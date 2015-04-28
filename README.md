Provides two commands, `nbcatsrc` and `nbdifftoolvim`.

## nbcatsrc

Write to standard output a diffable representation of IPython notebook.

Only cell sources (markdown or code) are preserved.

## nbdifftoolvim

Diff directories LEFT and RIGHT with Vim, using diffable representation of
IPython notebooks.

## Prerequisites

The [vim-dirdiff](https://github.com/will133/vim-dirdiff) Vim plugin must be installed.

## Installation

    python setup.py install

## Configure git difftool:

    echo '*.ipynb diff=ipynb' >> .gitattributes  # in Git repo
    git config diff.tool default-difftool
    git config difftool.default-difftool.cmd 'difftool-vim $LOCAL $REMOTE'
    git config diff.ipynb.textconv nbcatsrc

## References:

[Notebook format](http://ipython.org/ipython-doc/dev/notebook/nbformat.html)
