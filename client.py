#!/usr/bin/env python2

import threading 
import gtk
import gobject
import socket
import re
import time
import datetime

# Tell gobject to expect calls from multiple threads
gobject.threads_init()

class MainWindow(gtk.Window):

	def __init__(self):
	# Intialise base gtk windwow class
		super(MainWindow,self).__init__()
	
		#Create controls
		self.set_title("IM Client")
		vbox = gtk.VBox()
		hbox = gtk.HBox()
		self.username_label = gtk.Label()
		self.text_entry = gtk.Entry()
		send_button = gtk.Button("Send")
		self.text_buffer = gtk.TextBuffer()
		text_view = gtk.TextView(self.text_buffer)
	
		# Connect events
		self.connect("destroy",self.graceful_quit)
		send_button.connect("clicked",self.send_message)
	
		# Activate event when user presses ENTER
		self.text_entry.connect("activate",self.send_message)
	
		# Do layout
		vbox.pack_start(text_view)
		hbox.pack_start(self.username_label,expand = False)
		hbox.pack_start(self.text_entry)
		hbox.pack_end(send_button,expand = False)
		vbox.pack_end(hbox,expand = False)
		
		# Show ourselves
		self.add(vbox)
		self.show_all()

		#Go through the configuration process
		self.configure()
	
	def ask_for_info(self,question):
	# Show a message box with a text entry and returns
		dialog = gtk.MessageDialog(parent = self,type = gtk.MESSAGE_QUESTION,flags = gtk.DIALOG_MODAL | gtk.DIALOG_DSTROY_WITH_PARENT,buttons = gtk.BUTTONS_OK_CANCEL,message_format = question)
		entry = gtk.Entry()
		entry.show()
		dialog.vbox.pack_end(entry)
		response_text = entry.get_text()
		dialog.destroy()
		if response == gtk.RESPONSE_OK:
			return response_text
		else:
			return None

	def configure(self):
	#Performs the steps to connect to the server
	#Show a dialog box asking for server address followed by a port
		server = self.ask_for_info("server_address:port")
		
		#Regex that crudely matches an IP address and a port number
		regex = re.search('^(\d+\.\d+\.\d+\.\d+):(\d+)$',server)
		address = regex.group(1).strip()
		port = regex.group(2).strip()
		
		#Ask for a username
		self.username = self.ask_for_info("username")
		self.username_label.set_text(self.username)
	
		#Attempt to connect to the server and then start listening
		self.network = Networking(self,self.username,address,int(port))
		self.network.listen()

	def add_text(self,new_text):
		#Add text to the text view
		text_with_timestamp = "{0} {1}".format(datetime.datetime.now(),new_text)
		
		#Get the position of the end of the text buffer,so we know where to insert new text
		end_itr = self.text_buffer.get_end_iter()

		#Add a new text at the end of the buffer
		self.text_buffer.insert(end_itr,text_with_timestamp)

	def send_message(self,widget):
		#Clear the text entry and send the message to the server
		#we dont need to display it as it will be echoed back to the each client,including us
		new_text = self.text.entry.get_text()
		self.text_entry.set_text("")
		message = "{0} says: {1}\n".format(self.username,new_text)
		self.network.send(message)

	def graceful_quit(self,widget):
	#When the application is closed, tell GTK to quit,then tell the server we are quitting and tidy up the network
		gtk.main_quit()
		self.network.send("QUIT")
		self.network.tidy_up()

class Networking():
	def __init__(self,window,username,server,port):
		
		#Set up the networking class
		self.window = window
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.socket.connect((server,port))
		self.listening = True
		
		#Tell the server that a new user has joined
		self.send("USERNAME {0}".foramt(username))
		
	def listener(self):
	# A fnc run as a thread that listens for new messages
		while self.listening:
			data = ""
			try:
				data = self.socket.recv(1024)
			except socket.error:
				"Unable to recieve data"
			self.handle_msg(data)
			time.sleep(0.1)

	def listen(self):
		#Start the listening thread
		self.listen_thread = threading.Thread(target=self.listener)
		
		#Stop the child thread from keeping the application open
		self.listen_thread.daemon = True
		self.listen_thread.start()
	
	def send(self,message):
		#Send a message to the server
		print "Sending: {0}".format(message)
		try:
			self.socket.sendall(message)
		except socket.error:
			print "Unable to send message"
		
	def tidy_up(self):
		self.listening = False
		self.socket.close()
		gobject.idle_add(self.window.add_text,"Server has quit.\n")
	
	def handle_msg(self,data):
		if data == "QUIT":
			self.tidy_up()

		elif data == "":
			self.tidy_up(
)
		else:
			gobject.idle_add(seslf.window.add_text,data)


if __name__ == "__main_":
	MainWindow()
	gtk.main()
