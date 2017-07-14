#!/usr/bin/env python2

import threading
import socket
import re
import signal
import sys 
import time

class Server():

	def __init__(self,port):
        	# Create a scoket and bind it to a port
		self.listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.listener.bind(('',port))
		self.listener.listen(1)
		print "Listening on port{0}".format(port)
	        	
		# Used to store all of the client sockets
		# we have for,for echoing them
		self.client_sockets = []
		
		# Run the fnc self.signal_handler when Ctrl+C is pressed
		signal.signal(signal.SIGINT,self.signal_handler)
		signal.signal(signal.SIGTERM,self.signal_handler)

	def run(self):
		while True:
			# Listening for clients and create a ClientThread
			# for each new client
			print "Listening for more clients"
			try:
				(client_socket,client_address) = self.listener.accept()
			except socket.error:
				sys.exit("Could not accept anymore connections")
	
			self.client_sockets.append(client_socket)
	
			print "Starting client thread for {0}".format(client_address)
			client_thread = ClientListener(self,client_socket,client_address)
			client_thread.start()
	
			time.sleep(0.1)

	def echo(self,data):
	# Send a message to each socket in self.client_socket
		print "echoing: {0}".format(data)
		for socket in self.client_sockets:
			# Try to echo all clients
			try:
				socket.sendall(data)
			except socket.error:
				print "Unable to send a message"
	
	def remove_socket(self,socket):
	# Remove the specified socket from the client_sockets list
		self.client_sockets.remove(socket)
	
	def signal_handler(self,sigmal,frame):
	# Run when CTRL+C is pressed
		print "Tidying up"
		# Stop listening for new connections
		self.listener.close()
		# Let each client know we are quitting
		self.echo("QUIT")


class ClientListener(threading.Thread):

	def __init__(self,server,socket,address):
		# Initialize the Thread base class
		super(ClientListener,self).__init__()
		# Store the values that have been passed to the constructor
		self.server = server
		self.address = address
		self.socket = socket
		self.listening = True
		self.username = "No Username"

	def run(self):
		# The thread's loop to recieve and process messages
		while self.listening:
			data = ""
			try:
				data = self.socket.recv(1024)
			except socket.error:
				"Unable to recieve data"
			self.handle_msg(data)
			time.sleep(0.1)
		# While loop has ended
		print "Ending client thread for {0}".format(self.address)

	def quit(self):
	# Tidy up and end the thread
		self.listening = False
		self.socket.close()
		self.server.remove_socket(self.socket)
		self.server.echo("{0} has quit.\n".format(self.username))
	
	def handle_msg(self,data):
	# Print and then process the message we've just recieved
		print"{0} sent: {1}".foramt(self.address,data)
		# Use regular expressions to test for a message like "USERNAME __"
		username_result = re.search('^USERNAME (.*)$',data)
		if username_result:
			self.username = username_result.group(1)
			self.server.echo("{0} has joined.\n".format(self.username))
		elif data == "QUIT":
			# If the client has sent QUIT then close the thread
			self.quit()
		elif data == "":
			# The socket at the other end is probably closed
			self.quit()
		else:
			# It's a normal message so echo it to everyone
			self.server.echo(data)

if __name__ == "__main__":
	# Start a server on port 59091
	server = Server(59091)
	server.run()
