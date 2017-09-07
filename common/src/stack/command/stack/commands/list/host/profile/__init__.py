# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import sys
import string
from xml.sax import make_parser
import stack.commands
import stack.gen
from stack.exception import *

class implementation(stack.commands.Implementation):

	def generator(self):
		pass

	def chapter(self, generator, profile):
		profileType = generator.getProfileType()

		profile.append('<chapter name="main">')
		for line in generator.generate(profileType):
			profile.append(line)
		profile.append('</chapter>')

	def run(self, x):

		(xmlinput, profileType, chapter) = x

		profile     = []
		generator   = self.generator()

		generator.setProfileType(profileType)
		generator.parse(xmlinput)

		profile.append('<profile type="%s">' % generator.getProfileType())

		profile.append('<chapter name="stacki">')
		for line in generator.generate('stacki'):
			profile.append('%s' % line)
		profile.append('</chapter>')

		profile.append('<chapter name="debug">')
		for line in generator.generate('debug'):
			profile.append(line)
		profile.append('</chapter>')

		self.chapter(generator, profile)

		profile.append('</profile>')

		if chapter:
			parser  = make_parser()
			handler = stack.gen.ProfileHandler()

			parser.setContentHandler(handler)
			for line in profile:
				parser.feed('%s\n' % line)

			profile = handler.getChapter(chapter)

		for line in profile:
			self.owner.addOutput('', line)



class Command(stack.commands.list.host.command):
	"""
	Outputs a XML wrapped installer profile for the given hosts.

	If no hosts are specified the profiles for all hosts are listed.
	
	If input is fed from STDIN via a pipe, the argument list is
	ignored and XML is read from STDIN.  This command is used for
	debugging the Stacki configuration graph.

	<arg optional='1' type='string' name='host'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host profile backend-0-0'>
	Generates a Kickstart profile for backend-0-0.
	</example>

	<example cmd='list host xml backend-0-0 | stack list host profile'>
	Does the same thing as above but reads XML from STDIN.
	</example>

	"""

	MustBeRoot = 1

	def run(self, params, args):

		(profile, chapter) = self.fillParams([
			('profile', 'native'),
			('chapter', None) ])

		xmlinput  = ''
		osname    = None

		# If the command is not on a TTY, then try to read XML input.

		if not sys.stdin.isatty():
			for line in sys.stdin.readlines():
				if line.find('<stack:profile stack:os="') == 0:
					osname = line.split()[1][9:].strip('"')
				xmlinput += line
		if xmlinput and not osname:
			raise CommandError(self, "OS name not specified in profile")

		self.beginOutput()

		# If there's no XML input, either we have TTY, or we're running
		# in an environment where TTY cannot be created (ie. apache)

		if not xmlinput:
			hosts = self.getHostnames(args)
			if len(hosts) != 1:
				raise ArgUnique(self, 'host')
			host = hosts[0]

			osname	 = self.db.getHostOS(host)
			xmlinput = self.command('list.host.xml', [ host ])

			self.runImplementation(osname, (xmlinput, profile, chapter))

		# If we DO have XML input, simply parse it.

		else:
			self.runImplementation(osname, (xmlinput, profile, chapter))

		self.endOutput(padChar='')
