#______ _                       ___  ______________
#| ___ \ |                      |  \/  |  _  | ___ \
#| |_/ / |_   _ _ __ ___   ___  | .  . | | | | |_/ /
#|  __/| | | | | '_ ` _ \ / _ \ | |\/| | | | |  __/
#| |   | | |_| | | | | | |  __/ | |  | \ \/' / |
#\_|   |_|\__,_|_| |_| |_|\___| \_|  |_/\_/\_\_|
#
#
#robot.py
#
#Python interface for Plume MQP robot
#
#Ryan Wiesenberg
#Eric Fast
#Stepthen Harnais

from pycreate import create
import time
import sys
import math
from threading import Thread, Lock
import socket
import pickle
from custom_libs import encoding_TCP as encode
import argparse

class Robot:
	#driving constants
	#cm/s (probably. taken from create.py)
	MAX_SPEED = 50
	MIN_SPEED = -50
	DRIVE_SPEED = 20
	TURN_SPEED = 5
	STOP = 0

	#SENSING A TREND HERE
	#delay for sensor update. Too fast and the encoders get pissy
	SENS_DELAY = .1
	COMMS_DELAY = 1
	ANGMARG = .05

	#robot initialization
	SERIAL_PORT = "/dev/ttyUSB0"

	def __init__(self, id)
		self.id = id

		#position initalization
		self.curpos = [0, 0, 0]	#x,y,theta (cm,cm,rad)
		self.desired = [0, 0]	#x_dot, y_dot

		#desired velocity and theta
		self.veld  = 0
		self.thetad = 0
		self.vel = 0 					#actual velocity

		#time variables
		self.startt = 0
		self.endt = 0
		self.keepRunning = True			#leave while loop

		#encoder tidbits
		self.dist = 0
		self.ang = curpos[2]

		#start in full mode so it can charge and not be a pain
		self.robot = create.Create(SERIAL_PORT, startingMode=3)

		#TODO: 	EKF Thread
		self.robot_thread = threading.Thread(name="robot_thread", target=self.run_robot)
		self.update_sens = threading.Thread(name="update_robot", target=self.update_robot)
		self.comms_thread = threading.Thread(name="comms_thread", target=self.comms)

	#where the buisness happens
	#comms_thread 	~ send/recieve information across TCP/IP
	#robot_thread	~ driving and turning
	#update_sens	~ sensor updates
	def run(self):
		#essentially initializes the threads
		self.robot_thread.start()
		self.update_sens.start()
		self.comms_thread.start()

		#adds them on to the main thread (this one)
		self.robot_thread.join()
		self.update_sens.join()
		self.comms_thread.join()

	#update sensors
	# TODO: things besides encoders maybe?
	def update(self):
		deltadist = 0
		deltaang = 0

		#update time change
		self.endt = time.time()
		deltat = self.endt - self.startt
		self.startt = time.time()

		#calculate encoder bits
		deltadist = self.robot.getSensor("DISTANCE")
		deltaang = self.robot.getSensor("ANGLE")*math.pi/180
		self.dist += deltadist
		self.curpos[2] += deltaang

		#update position bits
		self.curpos[2] = math.fmod(self.curpos[2], (2 * math.pi))
		self.curpos[0] += deltadist*math.cos(self.curpos[2])
		self.curpos[1] += deltadist*math.sin(self.curpos[2])
		self.vel = deltadist/deltat

		return

	#change input velocities to v and theta
	def tCoord(self):
		self.veld = math.sqrt(self.desired[0]**2 + self.desired[1]**2)

		if(self.desired[0] == 0 and self.desired[1] == 0):
			self.thetad = self.curpos[2]
		elif(self.desired[0] == 0 and self.desired[1] > 0):
			self.thetad = math.pi/2
		elif(self.desired[0] == 0 and self.desired[1] < 0):
			self.thetad = math.pi/(-2)
		elif(self.desired[0] > 0):
			self.thetad = math.atan(self.desired[1]/self.desired[0])
		elif(self.desired[0] < 0):
			self.thetad = math.pi + math.atan(self.desired[1]/self.desired[0])

		return

	#movement control
	#decide turn or straight
	def move(self):
		upper = thetad + ANGMARG
		lower = thetad - ANGMARG

		if((self.curpos[2] <= upper) and (self.curpos[2] >= lower)):
			self.drive()
			return True
		elif(self.curpos[2] < lower):
			self.turnCCW()
		elif(self.curpos[2] > upper):
			self.turnCW()
		return False




	###################
	#Driving Functions#
	###################

	#drive desired velocity
	def drive(self):
		self.robot.go(self.veld, 0)
		return

	#turn Counter Clockwise
	def turnCCW(self):
		self.robot.driveDirect(-TURN_SPEED, TURN_SPEED)
		return

	#turn Clockwise
	def turnCW(self):
		self.robot.driveDirect(TURN_SPEED, -TURN_SPEED)
		return

	#stop robot
	def stop(self):
		self.veld = 0
		self.thetad = self.curpos[2]
		return

	#end robot
	def quit(self):
		self.stop()
	 	self.keepRunning = False

		#ET go the fork home
		#TODO:	MAKE THE ROBOT NOT JUST PUSH THE DOCK
		#robot.seekDock()
		return



	##################
	#Thread Functions#
	##################

	#run_robot function for robot_thread
	#just drivey bits
	def run_robot(self):
		while self.keepRunning:
			self.tCoord()
			self.move()

	#update_robot function for update_sens
	#sensors will love me
	def update_robot(self):
		while self.keepRunning:
			self.update()
			time.sleep(SENS_DELAY)

	#comms function for comms thread
	def comms(self):
		global  desired, curpos

		#TCP/IP socket
		#Create a TCP/IP socket
		PORT = 5732
		SERVER_IP = "192.168.0.102"
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# Connect the socket to the port where the server is listening
		server_address = (SERVER_IP, PORT)
		print("connecting to %s port %s" %server_address)
		sock.connect(server_address)

		time.sleep(COMMS_DELAY)

		encode.sendPacket(sock=sock, message=curpos)

		while keepRunning:
			try:
				#recieve message
				rcv = encode.recievePacket(sock=sock)

				print(rcv)

				#determine what to do with message
				if rcv == "out":
					quit()
				else:
					desired[0] = rcv[0]
					desired[1] = rcv[1]


					#send curpos
					encode.sendPacket(sock=sock, message=curpos)
			except:
				pass

		#close socket
		print("Closing Socket")
		sock.close()



############################
#Create and Run Robot on Pi#
############################
parser = argparse.ArgumentParser()
parser.add_argument("id", type=int, help="assign ID to robot")
args = parser.parse_args()
robot(args.id)
robot.run()
