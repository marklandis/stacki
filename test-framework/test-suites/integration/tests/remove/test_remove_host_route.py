import json
from textwrap import dedent


class TestRemoveHostRoute:
	def test_invalid_host(self, host):
		result = host.run('stack remove host route test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_no_args(self, host):
		result = host.run('stack remove host route')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {address=string} [syncnow=string]
		''')

	def test_no_host_matches(self, host):
		result = host.run('stack remove host route a:test address=127.0.0.3')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {address=string} [syncnow=string]
		''')

	def test_no_address(self, host):
		result = host.run('stack remove host route frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "address" parameter is required
			{host ...} {address=string} [syncnow=string]
		''')

	def test_no_syncnow(self, host, revert_routing_table, revert_etc):
		# Add a route with sync now so it is added to the routing table
		result = host.run(
			'stack add host route frontend-0-0 '
			'address=127.0.0.3 gateway=127.0.0.3 syncnow=true'
		)
		assert result.rc == 0

		# Confirm it is in the DB
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '127.0.0.3',
				'host': 'frontend-0-0',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '127.0.0.3',
				'source': 'H',
				'subnet': None
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

		# Also check that the test route is in our routing table
		result = host.run('ip route list')
		assert result.rc == 0
		assert '127.0.0.3 via 127.0.0.3' in result.stdout

		# Now remove it from the the DB, but don't sync
		result = host.run('stack remove host route frontend-0-0 address=127.0.0.3')
		assert result.rc == 0

		# Confirm it is no longer in the DB
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

		# Make sure it is still in the routing table
		result = host.run('ip route list')
		assert result.rc == 0
		assert '127.0.0.3 via 127.0.0.3' in result.stdout

	def test_with_syncnow(self, host, revert_routing_table, revert_etc):
		# Add a route with sync now so it is added to the routing table
		result = host.run(
			'stack add host route frontend-0-0 '
			'address=127.0.0.3 gateway=127.0.0.3 syncnow=true'
		)
		assert result.rc == 0

		# Confirm it is in the DB
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': '127.0.0.3',
				'host': 'frontend-0-0',
				'interface': None,
				'netmask': '255.255.255.255',
				'network': '127.0.0.3',
				'source': 'H',
				'subnet': None
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

		# Also check that the test route is in our routing table
		result = host.run('ip route list')
		assert result.rc == 0
		assert '127.0.0.3 via 127.0.0.3' in result.stdout

		# Now remove it from the the DB and sync
		result = host.run(
			'stack remove host route frontend-0-0 address=127.0.0.3 syncnow=true'
		)
		assert result.rc == 0

		# Confirm it is no longer in the DB
		result = host.run('stack list host route frontend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.0',
				'network': '224.0.0.0',
				'source': 'G',
				'subnet': 'private'
			},
			{
				'gateway': None,
				'host': 'frontend-0-0',
				'interface': 'eth1',
				'netmask': '255.255.255.255',
				'network': '255.255.255.255',
				'source': 'G',
				'subnet': 'private'
			}
		]

		# Make sure it is gone from the routing table
		result = host.run('ip route list')
		assert result.rc == 0
		assert '127.0.0.3 via 127.0.0.3' not in result.stdout
