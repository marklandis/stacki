#
# @copyright@
# @copyright@
#

ROLLROOT = ../../..
include $(STACKBUILD)/etc/CCRules.mk

build:

install::
	# Install WSGI File
	mkdir -p $(ROOT)/var/www/cgi-bin
	$(INSTALL) -m0644 cgi-bin/wsgi.py $(ROOT)/var/www/cgi-bin/

	# Install Django Setup files
	mkdir -p $(ROOT)/opt/stack/share/stack/bin
	$(INSTALL) -m0700 setup/* $(ROOT)/opt/stack/share/stack/bin/

	# Install REST API Files
	mkdir -p $(ROOT)/$(PY.STACK)/stack/restapi
	$(INSTALL) -m0644 restapi/* $(ROOT)/$(PY.STACK)/stack/restapi/

	# Install Command line and pylib
	mkdir -p $(ROOT)/$(PY.STACK)/stack/commands
	$(INSTALL) -m0644 pylib/*.py $(ROOT)/$(PY.STACK)/stack/
	(					\
		cd command;			\
		find . -type f -name \*.py |	\
		cpio -pudv $(ROOT)/$(PY.STACK)/stack/commands;	\
	)
	find $(ROOT)/$(PY.STACK)/stack/commands -name "*.py" | gawk	\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  

	# Install Sudoers file
	mkdir -p $(ROOT)/etc/sudoers.d
	$(INSTALL) -m0400 conf/stacki_ws.sudo $(ROOT)/etc/sudoers.d/stacki_ws

	# Install Apache Config file
	mkdir -p $(ROOT)/etc/httpd/conf.d
	$(INSTALL) -m0644 conf/stacki_ws.httpd $(ROOT)/etc/httpd/conf.d/stacki_ws.conf

	# Install syslog file
	mkdir -p $(ROOT)/etc/rsyslog.d/
	$(INSTALL) -m0644 conf/stacki_ws.syslog $(ROOT)/etc/rsyslog.d/stacki_ws.conf

clean::