import serial
import math
import xbox
import time

serialPath = '/dev/ttyUSB0'
serialBaud = 115200
serialByte = 8
serialTimeout = None

###....serial configurations....###
ser = serial.Serial(serialPath, baudrate=serialBaud, bytesize=serialByte, timeout=serialTimeout)
time.sleep(2)
ser.write(b'M17\r')
ser.write(b'G91\r')

homex = 0
homey = 19.5
homez = 134
xyz = [homex, homey, homez]
xyzMove = [0,0,0]

gripperStatus = 0

###....movement configurations....###
stepsDistance = 1 #mm per step
turnDegree = 1 #angle per turn
stepsSpeed = 50 #speed of stepper in mm/s 
moveFreq = 50/1000 #frequency (in s) for sending command

cmdDistanceSpeed = str(stepsDistance) + " F" + str(stepsSpeed) + "\r"

###....joystick configurations....###
joy = xbox.Joystick()

def home(start):
	global xyz
	if start == 1:
		xyz = [homex, homey, homez]
		sendGcode("G28\r")

def moveTurn(leftX):
	global xyz
	xyMove = [0,0]
	if leftX >= 0.2 or leftX <= -0.2:
		hp = math.sqrt(xyz[0]**2 + xyz[1]**2)
		orad = math.asin(xyz[0]/hp)
		if leftX >= 0.2:
			nrad = orad + math.radians(turnDegree)
		if leftX <= 0.2:
			nrad = orad - math.radians(turnDegree)
		xyMove[0] = math.sin(nrad)*hp - xyz[0]
		xyMove[1] = math.cos(nrad)*hp - xyz[1]
		xyz[0] = xyz[0] + xyMove[0]
		xyz[1] = xyz[1] + xyMove[1]
		gcode = "G1 X" + str(xyMove[0]) + " Y" + str(xyMove[1]) + " F"+ str(stepsSpeed) + "\r"
		time.sleep(moveFreq/12)
		sendGcode(gcode)

def moveFwdBack(leftY):
	global xyz
	xyMove = [0,0]
	if leftY >= 0.2 or leftY <= -0.2:
		hp = math.sqrt(xyz[0]**2 + xyz[1]**2)
		if leftY >= 0.2:
			hpratio = (hp + stepsDistance) / hp
		if leftY <= 0.2:
			hpratio = (hp - stepsDistance) / hp	
		xyMove[0] = xyz[0] * hpratio - xyz[0]
		xyMove[1] = xyz[1] * hpratio - xyz[1]
		xyz[0] = xyz[0] + xyMove[0]
		xyz[1] = xyz[1] + xyMove[1]
		gcode = "G1 X" + str(xyMove[0]) + " Y" + str(xyMove[1]) + " F"+ str(stepsSpeed) + "\r"
		sendGcode(gcode)

def moveUpDown(rightY):
	global xyz
	if rightY > 0.2:
		xyz[2] = xyz[2] + stepsDistance
		sendGcode("G1 Z" + str(cmdDistanceSpeed))

	if rightY < -0.2:
		xyz[2] = xyz[2] - stepsDistance
		sendGcode("G1 Z-" + str(cmdDistanceSpeed))

def activateGripper(A):
	global gripperStatus
	if A == 1:
		if gripperStatus == 0:
			ser.write(b"M3\r")
			gripperStatus = 1
		elif gripperStatus == 1:
			ser.write(b"M5\r")
			gripperStatus = 0
		time.sleep(0.5)

def sendGcode(gcode):
	print(gcode)
	ser.write(gcode.encode())
	time.sleep(moveFreq)

while True:
	if ser.in_waiting > 0:
		print(ser.readline())
	moveTurn(joy.leftX())
	moveFwdBack(joy.leftY())
	moveUpDown(joy.rightY())
	activateGripper(joy.A())
	home(joy.Start())
	print(xyz)	


