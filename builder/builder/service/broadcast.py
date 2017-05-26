# Send UDP broadcast packets
import os, sys
import time
import subprocess, psutil, tempfile, portalocker
import socket
import uuid
import logging
from ..util import util

# Initialize logging
logger = util.setup_log_folder(__name__)

def start():
	sys.stdout.write('Starting broadcast service.')
	current_file_path = os.getcwdu()
	p = subprocess.Popen(['builder', 'run', 'broadcast'], cwd=current_file_path)
	sys.stdout.write(' OK.\n')

	# Log status
	logger.info('Started broadcast service.')

def stop():
	sys.stdout.write('Stopping broadcast service.')

	# Log status
	logger.info('Stopped broadcast service.')

	# Locate pidfile (if it exists)
	current_dir = os.getcwd()
	pidfile_path = os.path.join(tempfile.gettempdir(), '%s.pid' % __name__)

	# Read pid from pidfile
	pidfile = open(pidfile_path, "r")
	content = pidfile.readlines()
	pidfile.close()
	content = [x.strip() for x in content] # remove whitespace characters like `\n` at the end of each line
	# print content
	pid = int(content[0])

	# Kill process
	util.kill_proc_tree(pid)

	# Delete pidfile
	os.remove(pidfile_path)

	# Status
	sys.stdout.write(' OK.\n')

def run(port=4445, broadcast_address='192.168.1.255', broadcast_timeout=2000):

	addresses = util.get_inet_addresses()

	# Write pid into pidfile
	current_dir = os.getcwd()
	pidfile_path = os.path.join(tempfile.gettempdir(), '%s.pid' % __name__)
	# TODO: get name of file for naming "builder.<filename>.pid"
	# TODO: tempfile.NamedTemporaryFile(prefix='builder.broadcast.', suffix='.pid').name
	pidfile = open(pidfile_path, "w+")
	#portalocker.lock(pidfile, portalocker.LOCK_EX) # lock the pidfile
	pidfile.write('%s' % os.getpid())
	pidfile.close()

	device_uuid = uuid.uuid4()

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#s.bind(('', 0))
	s.bind(('', port))
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	s.setblocking(0)
	#s.settimeout(2)

	# "\f<content_length>\t<content_checksum>\t<content_type>\t<content>"
	# e.g., "\f52	16561	text	announce device 002fffff-ffff-ffff-4e45-3158200a0015"
	# data = "\f52\t16561\ttext\tannounce device 002fffff-ffff-ffff-4e45-3158200a0015";
	# data = "\f52\t33439\ttext\tannounce device f1aceb8b-e8e9-4cda-b29c-de7bc7cc390f"
	broadcast_message = "announce device %s" % device_uuid

	while True:

		current_time = 0
		response_start_time = int(round(time.time() * 1000))

		while current_time - response_start_time < broadcast_timeout:
			try:
				#data, fromaddr = s.recvfrom(1000)
				#print "Response from %s:%s: %s" % (fromaddr[0], fromaddr[1], data)
				message, fromaddr = s.recvfrom(1000)
				if not fromaddr[0] in addresses:
					# Log status
					#logger.info("Response from %s:%s: %s" % (fromaddr[0], fromaddr[1], message))
					# print "Response from %s:%s: %s" % (fromaddr[0], fromaddr[1], message)

					if message.startswith("announce"):
						# Log status
						logger.info("Response from %s:%s: %s" % (fromaddr[0], fromaddr[1], message))
						# print "Response from %s:%s: %s" % (fromaddr[0], fromaddr[1], message)
					elif message.startswith("echo"):
						response_message = message[len("echo") + 1:] # remove "echo " from start of string
						print response_message
						serverSocket.sendto(response_message, address)

			except:
				# TODO: Log exception!
				None

			current_time = int(round(time.time() * 1000))

		# Send periodic broadcast
		s.sendto(broadcast_message, (broadcast_address, port)) # Works

	s.close()

if __name__ == "__main__":
	run()
