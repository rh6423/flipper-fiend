<h1>Status report</h1>

<p>Much of this info will move elsewhere in the repo as things move along. The code here isn’t fully functional yet. If you want to play with a semi-functional app, here’s what you need to know.</p>

<p>I’m testing on a MacBook Pro M1 with 32GB. Haven’t tested on Intel at all yet. I have Homebrew installed and all sorts of pip and microconda stuff. You may need to install PySide6 and/or PyQT6 to get this going today (although a redistributable, self-contained Python package is in the MVP roadmap).</p>

<p>main.py is mostly functional as a library/launcher view. Requires some initial configuration, so it calls firstrun.py to set that up. It depends on a valid config.csv, so it calls gamemanager and scantables to set that up. This part isn’t done yet, and I created the example config.csv by hand for my local config. If you do the same, the launcher should work for you.</p>


