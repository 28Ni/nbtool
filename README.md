# nbtool
Tool for managin IPython notebooks

Install:

    python setup.py install

Configure git difftool:

    echo '*.ipynb diff=ipynb' >> .gitattributes  # in Git repo
    git config diff.tool default-difftool
    git config difftool.default-difftool.cmd 'difftool-vim $LOCAL $REMOTE'
    git config diff.ipynb.textconv nbcatsrc


Reference:
    [Notebook format](http://ipython.org/ipython-doc/dev/notebook/nbformat.html)
