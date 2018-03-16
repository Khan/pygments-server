# pygments-server
A simple server that provides HTTP access to `pygmentize` 

We use phabricator, which calls out to `pygmentize` to
syntax-highlight code in diffs.  Each block of code gets its own call
to `pygmentize`, which can add up; Python startup is fairly expensive.

Enter pygments-server, which is a long-running server that
pygmentizes.  It takes source code via POST and returns highlighted
source code in the response body.
