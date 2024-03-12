<h1>Status report</h1>

<p>Much of this info will move elsewhere in the repo as things move along. Flipper Fiend is mostly functional today, but it does require a bit of Python know-how. There will be a beta version packaged as a self-contained app in the near future. Meanwhile, if you're ok pip installing dependencies and want to try it out, here’s what you need to know.</p>

<p>The Game Manager screen is still a work in progress. Edit ffiend.csv directly to manage your games after initial scaning.

<p>Scan Tables module works, but doesn't read config.csv and looks for command line arguments instead. This is next on my list of things to fix.

<p>I’m testing on a MacBook Pro M1 with 32GB. Haven’t tested on Intel at all yet. I have Homebrew installed and all sorts of pip and microconda stuff. 

<p>main.py is mostly functional as a library/launcher view. Requires some initial configuration, so it calls firstrun.py to set that up. It depends on a valid config.csv, so it calls gamemanager and scantables to set that up. This part isn’t done yet, and I created the example config.csv by hand for my local config. If you do the same, the launcher should work for you.</p>

<p>puplookup.csv is included for testing and development here. It will be downloaded at install from the source so it's current.</p>
