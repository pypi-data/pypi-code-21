#
# This file is part of CAVIAR.
#
# CAVIAR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CAVIAR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CAVIAR.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Network module.
"""

import caviar.network.http
import caviar.network.ssh

# TODO Test coverage
def http_resource(protocol, host, port, auth, headers):

	"""
	Create an HTTP resource from root path.
	
	:param str protocol:
	   HTTP protocol, such as 'http' and 'https'.
	:param str host:
	   Host.
	:param str port:
	   Port.
	:param auth:
	   Authentication specification.
	:param dict headers:
	   Common headers. Each entry contains a list of values. 
	   
	:rtype:
	   caviar.network.http.HTTPResource
	:return:
	   The created resource.
	"""
	
	return caviar.network.http.HTTPResource(
		[],
		protocol,
		host,
		port,
		auth,
		headers
	)
	
# TODO Test coverage
def ssh_session_factory(ssh_client, private_key_path):

	"""
	Create an SSH session factory.
	
	:param SSHClient ssh_client:
	   SSH client implementation.
	:param str private_key_path:
	   Path of local private key file.
	   
	:rtype:
	   ssh.SSHSessionFactory
	:return:
	   The created SSH session factory.
	"""
	
	return caviar.network.ssh.SSHSessionFactory(ssh_client, private_key_path)

