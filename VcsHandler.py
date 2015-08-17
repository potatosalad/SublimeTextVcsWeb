# -*- mode: python; tab-width: 4; indent-tabs-mode: 1; st-rulers: [70] -*-
# vim: ts=4 sw=4 ft=python noet

import errno
import os
import sublime
import subprocess
import re

try:
	from .VcsHelper import GitHelper, HgHelper, SvnHelper
except ValueError:
	from VcsHelper import GitHelper, HgHelper, SvnHelper

class VcsHandler(object):
	def __init__(self, view, exc_path):
		self.view = view
		self.exc_path = exc_path
		vcs_helper = self.get_vcs_helper()
		self.vcs_tree = vcs_helper.vcs_tree(self.view)
		self.vcs_dir = vcs_helper.vcs_dir(self.vcs_tree)
		self.vcs_path = vcs_helper.vcs_file_path(self.view, self.vcs_tree)

	def branch(self, context = {}):
		if context is False:
			return False
		args = self.get_branch_args()
		stdout, stderr = self.run_command(args)
		if stderr and bool(stderr.strip()):
			print('Vcs Web: Branch command failed with: %r' % (stderr))
			return False
		return self.parse_branch(stdout.strip().decode('utf-8'), context)

	def parse_branch(self, raw, context = {}):
		if not raw:
			return False
		context['branch'] = raw
		return context

	def remote(self, context = {}):
		if context is False:
			return False
		args = self.get_remote_args()
		stdout, stderr = self.run_command(args)
		if stderr and bool(stderr.strip()):
			print('Vcs Web: Remote command failed with: %r' % (stderr))
			return False
		return self.parse_remote(stdout.strip().decode('utf-8'), context)

	def parse_remote(self, raw, context = {}):
		match = None
		for regex in self.get_vcs_regex():
			match = regex.search(raw)
			if match:
				break
		if not match:
			return False
		context.update(match.groupdict())
		context['file'] = self.vcs_path
		context['file_basename'] = os.path.basename(self.vcs_path)
		return context

	def revision(self, context = {}):
		if context is False:
			return False
		args = self.get_revision_args()
		stdout, stderr = self.run_command(args)
		if stderr and bool(stderr.strip()):
			print('Vcs Web: Revision command failed with: %r' % (stderr))
			return False
		return self.parse_revision(stdout.strip().decode('utf-8'), context)

	def parse_revision(self, raw, context = {}):
		if not raw:
			return False
		context['revision'] = raw
		return context

	def run_command(self, args):
		print(args)
		startupinfo = None
		if os.name == 'nt':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		try:
			proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, cwd=self.vcs_tree)
		except OSError as e:
			print('Vcs Web: Failed to run command %r: %r' % (args[0], e))
			if e.errno == errno.ENOENT:
				print('Vcs Web: The path can be customized in settings if necessary.')
			return ''
		except Exception as e:
			print('Vcs Web: Failed to run command %r: %r' % (args[0], e))
			return ''

		return proc.communicate()

class GitHandler(VcsHandler):
	def get_vcs_helper(self):
		return GitHelper

	def get_vcs_regex(self):
		host_regex = r'(?P<host>([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*)'
		protocol_regex = r'^((ftp|ftps|git|http|https|rsync|ssh)://)((?P<user>[^@]+)@)?%s(:\d+)?/(?P<path>[^\.]+)(?:\.git)?$' % (host_regex)
		scp_regex = r'^((?P<user>[^@]+)@)?%s:(?P<path>[^\.]+)(?:\.git)?$' % (host_regex)
		regex = [
			re.compile(protocol_regex),
			re.compile(scp_regex)
		]
		return regex

	def get_branch_args(self):
		args = [
			self.exc_path,
			'--git-dir=' + self.vcs_dir,
			'--work-tree=' + self.vcs_tree,
			'rev-parse',
			'--abbrev-ref',
			'--quiet',
			'HEAD'
		]
		return args

	def get_remote_args(self):
		args = [
			self.exc_path,
			'--git-dir=' + self.vcs_dir,
			'--work-tree=' + self.vcs_tree,
			'config',
			'--get',
			'remote.origin.url'
		]
		return args

	def get_revision_args(self):
		args = [
			self.exc_path,
			'--git-dir=' + self.vcs_dir,
			'--work-tree=' + self.vcs_tree,
			'rev-parse',
			'--quiet',
			'HEAD'
		]
		return args

class HgHandler(VcsHandler):
	def get_vcs_helper(self):
		return HgHelper

	def get_vcs_regex(self):
		host_regex = r'(?P<host>([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*)'
		protocol_regex = r'^((http|https|ssh)://)((?P<user>[^@]+)@)?%s(:\d+)?/(?P<path>[^\.]+)(?:\.git)?$' % (host_regex)
		scp_regex = r'^((?P<user>[^@]+)@)?%s:(?P<path>[^\.]+)(?:\.git)?$' % (host_regex)
		regex = [
			re.compile(protocol_regex),
			re.compile(scp_regex)
		]
		return regex

	def get_branch_args(self):
		args = [
			self.exc_path,
			'--repository',
			self.vcs_tree,
			'--quiet',
			'id',
			'--branch'
		]
		return args

	def get_remote_args(self):
		args = [
			self.exc_path,
			'--repository',
			self.vcs_tree,
			'paths',
			'default'
		]
		return args

	def get_revision_args(self):
		args = [
			self.exc_path,
			'--repository',
			self.vcs_tree,
			'--quiet',
			'id',
			'--id'
		]
		return args

class SvnHandler(VcsHandler):
	def get_vcs_helper(self):
		return SvnHelper

	def get_vcs_regex(self):
		host_regex = r'(?P<host>([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*)'
		protocol_regex = r'^((http|https|svn|svn\+ssh|svn_ssh)://)((?P<user>[^@]+)@)?%s(:\d+)?/(?P<path>[^\.]+)(?:\.git)?$' % (host_regex)
		regex = [
			re.compile(protocol_regex)
		]
		return regex

	def get_remote_args(self):
		args = [
			self.exc_path,
			'info',
			'--xml',
			self.vcs_tree
		]
		return args

	def branch(self, context = {}):
		if context is False:
			return False
		context['branch'] = ''
		return context

	def parse_remote(self, raw, context = {}):
		from xml.dom import minidom
		doc = minidom.parseString(raw)
		urls = doc.getElementsByTagName('root')
		url = urls[0].firstChild.data
		return super(SvnHandler, self).parse_remote(url, context)

	def revision(self, context = {}):
		if context is False:
			return False
		context['revision'] = ''
		return context
