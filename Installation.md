<h1>Installation</h1>

<ol>
	<li>I’ve tested on Python 3.9, suspect it’ll run if you’re close to that version.</li>
	<li>You’ll need the VPX standalone app binary. 

		<ol>
			<li>Nightly builds are available from the vpinball GitHub actions page. Try the right one of these for your architecture: <a href="https://github.com/vpinball/vpinball/actions/runs/8236483547">https://github.com/vpinball/vpinball/actions/runs/8236483547</a></li>
			<li>Depending on your OS security settings, you may not be able to run unsigned applications. Right click on the VPinballX application and choose “open” from the list. If that doesn’t work, you’ll need to modify your macOS security settings to allow unsigned apps to run.</li>
		</ol></li>
	<li>You’ll need a directory with one or more .vpx table files.</li>
	<li>If any of your .vpx tables require a ROM, put the ROM zip file in your .pinmame/roms directory. To open a finder window on .pinmame/roms, run this command in Terminal:

<pre><code>open ~/.pinmame/roms</code></pre>

		<p>You can then drag the rom.zip file(s) into the roms directory window.</p></li>
	<li>Download the repository for Flipper Fiend:</li>
	<li>Alternately, clone with git:</li>
	<li><code>cd flipper-fiend</code></li>
	<li>Create a python venv:

		<p> <code>python -m venv venv</code></p></li>
	<li> Activate the venv:

		<p><code>. venv</code></p></li>
	<li>Install requirements

		<p><code>pip install -r requirements.txt</code></p></li>
	<li>Run the application

		<p><code>python main.py</code></p></li>
</ol>


