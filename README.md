# VcsWeb

Generates links to remote web services for [git](http://git-scm.com/), [hg](http://mercurial.selenic.com/), and [svn](http://subversion.apache.org/).

**NOTE:** The plugin has been tested on Sublime Text 2 and 3.

## Installation

After installation, the plugin should be picked up automatically.  If not, restart Sublime Text.

#### Sublime Text 2

```bash
cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
git clone git://github.com/potatosalad/SublimeTextVcsWeb.git "VCS Web"
```

#### Sublime Text 3

```bash
cd ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/
git clone git://github.com/potatosalad/SublimeTextVcsWeb.git "VCS Web"
```

## Configuration

By default [bitbucket.org](http://bitbucket.org) and [github.com](http://github.com) are included in the `VcsWeb.sublime-settings` file:

```json
{
	"vcs_hosts": {
		"bitbucket.org": {
			"oneline": "#cl-%(line_begin)s",
			"multiline": "#cl-%(line_begin)s",
			"link": "https://bitbucket.org/%(path)s/src/%(branch)s/%(file)s",
			"permalink": "https://bitbucket.org/%(path)s/src/%(revision)s/%(file)s",
			"blame": "https://bitbucket.org/%(path)s/annotate/%(branch)s/%(file)s",
			"blame_permalink": "https://bitbucket.org/%(path)s/annotate/%(revision)s/%(file)s",
			"history": "https://bitbucket.org/%(path)s/history-node/%(branch)s/%(file)s",
			"history_permalink": "https://bitbucket.org/%(path)s/history-node/%(revision)s/%(file)s"
		},
		"github.com": {
			"oneline": "#L%(line_begin)s",
			"multiline": "#L%(line_begin)s-L%(line_end)s",
			"link": "https://github.com/%(path)s/blob/%(branch)s/%(file)s",
			"permalink": "https://github.com/%(path)s/blob/%(revision)s/%(file)s",
			"blame": "https://github.com/%(path)s/blame/%(branch)s/%(file)s",
			"blame_permalink": "https://github.com/%(path)s/blame/%(revision)s/%(file)s",
			"history": "https://github.com/%(path)s/commits/%(branch)s/%(file)s",
			"history_permalink": "https://github.com/%(path)s/commits/%(revision)s/%(file)s"
		}
	},
	"vcs_paths": {
		"git": "git",
		"hg": "hg",
		"svn": "svn"
	}
}
```

## Usage

There are 3 main ways to use the plugin:

1. Right-click on the text of a saved file and select from the `VCS Web` options
2. Select text in a saved file and press ⌘\\ (OS X default, changeable in the `.sublime-keymap` file)
3. Press ⌘⇧P (OS X default) and search for `VCS Web` commands
