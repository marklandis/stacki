# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

from __future__ import print_function
import os
import sys
import stack
import stack.commands

class Implementation(stack.commands.Implementation):
	"""
	Copy a native redhat (meaning Rocks) roll.
	"""
	
	def run(self, args):

		(clean, prefix, info) = args

		name = info.getRollName()
		vers = info.getRollVersion()
		arch = info.getRollArch()
		OS   = info.getRollOS()

		# Get the destination, ie. where should the roll be put.
		# This is always rolls_directory/roll_name/
		roll_dir = os.path.join(prefix, name)
		specific_roll_dir = os.path.join(roll_dir, vers, OS, arch)


		# Clean out the existing roll directory if asked
		
		if clean and os.path.exists(specific_roll_dir):
			print('Cleaning %s version %s ' % (name, vers), end=' ')
			print('for %s from the pallets directory' % arch)
			os.system('/bin/rm -rf %s' % specific_roll_dir)
			os.makedirs(specific_roll_dir)

		# Finally copy the roll to the HD
		sys.stdout.write('Copying %s to pallets ...' % name)
		sys.stdout.flush()
		cwd = os.getcwd()
		os.chdir(os.path.join(self.owner.mountPoint, name))
		## CHECK FOR OLD FORMAT ##
		p1 = os.path.join(vers, arch, 'RedHat')
		if os.path.exists(p1):
			# Get the RPMS
			os.chdir(p1)
			os.system('find RPMS -type f ! -name TRANS.TBL | ' +\
				'cpio -mpud %s' % specific_roll_dir)

			# Get the XML file from the roll
			os.chdir(os.path.join(self.owner.mountPoint, name, vers, arch))
			os.system('find * -prune -type f -name roll-*.xml | ' +\
				'cpio -mpud %s' % specific_roll_dir)
		else:
			## END CHECK FOR OLD FORMAT ##
			os.system('find . ! -name TRANS.TBL -print | cpio -mpud %s' %
				  roll_dir)

			if stack.release == '7.x':
				#
				# check for LiveOS
				#
				liveosdir = os.path.join(self.owner.mountPoint,
					'LiveOS')

				if os.path.exists(liveosdir):
					os.chdir(self.owner.mountPoint)
					os.system('find LiveOS ! -name TRANS.TBL ' +
						' -print | cpio -mpud ' +
						'%s' % specific_roll_dir)

				#
				# check for images
				#
				imagesdir = os.path.join(self.owner.mountPoint,
					'images')

				if os.path.exists(imagesdir):
					os.chdir(self.owner.mountPoint)
					os.system('find images ! -name TRANS.TBL ' +
						' -print | cpio -mpud ' +
						'%s' % specific_roll_dir)

		# after copying the roll, make sure everyone (apache included)
		# can traverse the directories
		os.system('find %s -type d -exec chmod a+rx {} \;' % roll_dir)
		os.chdir(cwd)
