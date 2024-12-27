# The import above is a created variable from pyserial. It does what it name says: get all of the devices connected to serial ports
#Imporanrt: for the barcode scanners, make sure to open the manual and then set it to USB COM (page 6) by scanning that specific barcode on the manual
# or else the program wont work
import serial.tools.list_ports
import time

# Imports for Ethernet
import socket
import json

# Will use to copy the barcode number from the output and transfer it to a string variable
import pyperclip as pc

def theMainFunction() :

    # Will first have a function to retrieve all of the devices connected to COM ports in the computer.
    # It will use the created variable above and will put everything in a list
    def getThePorts():

        ports = serial.tools.list_ports.comports()

        return ports

    # The next step is finding which COM port the barcode scanner is connected to. This is because the COM port will be different everytime, as it is based on where the user connects the scanner
    # After checking the device manager, the scanner name in the computer is "Prolific USB-to-Serial", and the COM number is followed right after
    # Will use the naming format to find the port
    # The function below finds the port number and returns a string (not necessary, but it's nice to have). The import is the list of ports from above

    def findThePort(listOfPorts) :

        # Will first initialize the string variable to be returned. Will set it to "none" as the default value
        theFinalPort = 'None'
        # Will create a variable to get the length of the list
        theLengthOfList = len(listOfPorts)

        # Next, use a for loop to go through the list, convert everything to a string, and use pattern mattching to see if the scanner name is in the list (indiciating if it's connected)
        for i in range(0, theLengthOfList):
            tempPort = theListOfPorts[i]
            stringPort = str(tempPort)

            # Will now do the pattern matching
            if 'Prolific USB-to-Serial Comm Port' in stringPort:
                # If found, the string will be split in order to only get the "COM#" portion
                splitPort = stringPort.split(' ')
                theFinalPort = (splitPort[0])

        return theFinalPort

    def sendAndRecieveInfo(theBarcodeNumber):
        theDataToSend = {
            "BarcodeNumber": theBarcodeNumber,
            "ID": 9,
            "Status": "Good"
        }

        client_socket.send(bytes(json.dumps(theDataToSend), 'utf-8'))
    #Where main code starts

    # Connect to the server computer
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('', ))


    # Ports for the barcode scanner
    theListOfPorts = getThePorts()
    connectPort = findThePort(theListOfPorts)

    if connectPort != 'None':
        #Now, we can activate the serial, and the main code will go here
        ser = serial.Serial(connectPort, baudrate = 9600, timeout = 1)
        print ('Connected to ' + connectPort)

        # The next step is reading values from the barcode scanner in a certain number of time

        while True:
        #while time.time() < timeLasted:

            if ser.in_waiting:
                print("From Barcode Scanner #1")

                # The code below will retrieve the barcode number from the barcode scanner
                packet = ser.readline()

                # Using pyperclip, will convert the barcode number from the output to a string variable (can be changed if necessary)
                temp = str(packet.decode('utf'))
                pc.copy(temp)
                theBarcodeNumber = pc.paste()
                print("The barcode number is: " + theBarcodeNumber)

                sendAndRecieveInfo(theBarcodeNumber)
    else:
        print('Connection ISSUE!!!')



theMainFunction()
