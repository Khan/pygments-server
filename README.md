# pygments-server
A simple server that provides HTTP access to `pygmentize` 

We use phabricator, which calls out to `pygmentize` to
syntax-highlight code in diffs.  Each block of code gets its own call
to `pygmentize`, which can add up; Python startup is fairly expensive.

Enter pygments-server, which is a long-running server that
pygmentizes.  It takes source code via POST and returns highlighted
source code in the response body.

## Using pygments-server with phabricator

You can use the pygments server as a drop-in replacement for the
"pygmentize" binary on your phabricator machine.  This will let you
colorize Phabricator diffs using less CPU, with no other cost.

1. Clone the pygments-server repo somewhere on your Phabricator
   server machine.  For the below, I will assume you ran
   `git clone https://github.com/Khan/pygments-server` in `$HOME`.

2. Run `cd ~/pygments-server && make deps` on your Phabricator server
   machine.

3. Start the pygments-server.  The best way to do this is to
   use an init script such as upstart.  You can use
   `pygments-server/pygments-server.conf` as an example.  If
   you are on an upstart-based system (such as ubuntu) you can
   do
   ```
   sudo install pygments-server/pygments-server.conf /etc/init/
   sudo start pygments-server
   ```
   You may need to edit the init script if `$HOME` for you is not
   `/home/ubuntu`.  And you will probably want to change the
   location of the logs files.

4. Replace the default `pygmentize` binary with our script that uses
   the server:
   ```
   [ -L /usr/bin/pygmentize] || sudo mv /usr/bin/pygmentize /usr/bin/pygmentize.orig
   [ -L /usr/local/bin/pygmentize] || sudo mv /usr/local/bin/pygmentize /usr/local/bin/pygmentize.orig
   sudo ln -snf $HOME/pygments-server/pygmentize /usr/bin/
   sudo ln -snf $HOME/pygments-server/pygmentize /usr/local/bin/
   ```

5. OPTIONAL: install a logrotate script for the pygments-server logs:
   ```
   sudo install -m 644 $HOME/pygments-server/pygments-server.logrotate /etc/logrotate.d/pygments-server
   ```

6. Make sure the pygments config option is turned on in your
   Phabricator config:
   https://secure.phabricator.com/book/phabricator/article/differential_faq/#how-can-i-enable-syntax

7. Run `arc diff` on your next change and admire all the pretty
   colors!
