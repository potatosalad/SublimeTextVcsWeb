# -*- mode: python; tab-width: 4; indent-tabs-mode: 1; st-rulers: [70] -*-
# vim: ts=4 sw=4 ft=python noet

import os
import sublime
import sublime_plugin

try:
	from .VcsHelper import GitHelper, HgHelper, SvnHelper
except ValueError:
	from VcsHelper import GitHelper, HgHelper, SvnHelper

try:
	from .VcsHandler import GitHandler, HgHandler, SvnHandler
except ValueError:
	from VcsHandler import GitHandler, HgHandler, SvnHandler

class VcsWebCommand(sublime_plugin.TextCommand):
	def run(self, edit, permalink = False, mode = 'blob'):
		if not self.on_disk():
			return

		settings = sublime.load_settings('VcsWeb.sublime-settings')
		vcs_hosts = settings.get('vcs_hosts', {})
		vcs_paths = settings.get('vcs_paths', {
			'git': 'git',
			'hg': 'hg',
			'svn': 'svn'
		})

		key = None
		if GitHelper.is_git_repository(self.view):
			key = 'git'
			klass = GitHandler
		elif HgHelper.is_hg_repository(self.view):
			key = 'hg'
			klass = HgHandler
		elif SvnHelper.is_svn_repository(self.view):
			key = 'svn'
			klass = SvnHandler

		# print('key: %s' % (key))
		handler = None
		if key is not None:
			try:
				path = vcs_paths[key]
			except (KeyError, TypeError):
				print('Vcs Web: Invalid path for %s executable in settings. Using default.' % key)
				path = key
			handler = klass(self.view, path)
			print('vcs_tree: %s vcs_dir: %s vcs_path: %s' % (handler.vcs_tree, handler.vcs_dir, handler.vcs_path))

		# If no handler found then either the view does not represent a
		# file on disk (e.g. not yet saved) or the file is not in a supported
		# VCS repository.
		if handler is not None:
			selection = self.view.sel()[0]
			line_begin = self.view.rowcol(selection.begin())[0] + 1
			line_end = self.view.rowcol(selection.end())[0] + 1
			if line_begin == line_end:
				line_end = None
			context = {'line_begin': line_begin, 'line_end': line_end}
			context = handler.remote(context)
			context = handler.branch(context)
			context = handler.revision(context)
			if context is not False:
				host = vcs_hosts[context['host']]
				tkey = None
				if mode == 'blob':
					if permalink == True:
						tkey = 'permalink'
					else:
						tkey = 'link'
				elif mode == 'blame':
					if permalink == True:
						tkey = 'blame_permalink'
					else:
						tkey = 'blame'
				elif mode == 'history':
					if permalink == True:
						tkey = 'history_permalink'
					else:
						tkey = 'history'
				else:
					print('Vcs Web: Unknown mode: %s' % mode)
				template = host[tkey]
				if mode != 'history':
					if context['line_end'] is not None:
						if 'multiline' in host:
							template = template + host['multiline']
					else:
						if 'oneline' in host:
							template = template + host['oneline']
				full_link = template % (context)
				sublime.set_clipboard(full_link)
				sublime.status_message('Copied %s to clipboard.' % full_link)
				print('Vcs Web: Copied %s to clipboard.' % full_link)
				self.view.window().run_command('open_url', {"url": full_link})

	def is_enabled(self):
		return self.on_disk()

	def on_disk(self):
		# if the view is saved to disk
		if self.view.file_name() is not None and len(self.view.file_name()) > 0:
			return True
		else:
			return False
