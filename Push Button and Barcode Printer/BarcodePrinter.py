# Imports for MySQL
import mysql.connector
from mysql.connector import errorcode

# Imports for Barcode Printer
from socket import *
import time
from escpos.printer import Network
from random import randint, randrange
from datetime import datetime

config = {
    'host': '',
    'user': '',
    'password': '',
    'database': '',
    'autocommit': '',
    'port': '',
}

# Function that checks if MySQL table exists
def table_exists(cursor, table_name):
    # Check if the table exists
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None

# Function that makes the list of random numbers that'll be used
def makeListOfNumbers(theMaxNum):
    for i in range(theMaxNum):
        randNumber = randrange(100000000000, 1000000000000)
        randNumber = str(randNumber)
        #print(randNumber)
        theListOfNumbers.append(randNumber)

# Function that adds barcode number to MySQL
# In the future, add logic to check if the number already exists in the database
def addToMySQL(barcodeNumber, cursor, conn):
    # Get the current time
    theCurrTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generate a random number code
    theNumberCode = randrange(0, 10000)
    insert_query = ("INSERT INTO users "
                    "(barcode, current_section, time_printed, finished, game_code, didUserScan) "
                    "VALUES (%s, %s, %s, %s, %s, %s)")
    enter_data = (barcodeNumber, '0', theCurrTime, '0', theNumberCode, 'no')

    cursor.execute(insert_query, enter_data)
    conn.commit()

# Function that makes and prints the physical barcode image
def printing(counter):
    # Print
    number = theListOfNumbers[counter]
    kitchen.text("Welcome to Bee My Guide!\n")
    kitchen.barcode(number, 'EAN13', 64, 2, '', '')
    kitchen.cut()

    # Get number and add to MySQL by calling function
    addToMySQL(number, cursor, conn)



# First part of the code will connect to MySQL
# Try connecting to the database
try:
    conn = mysql.connector.connect(**config)
    print("Connection established")
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with the user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    #return None
else:
    cursor = conn.cursor()

# Testing to see if the database has an instance of the artrium. If one does not exist then we can create one
if table_exists(cursor, 'users'):
    print(f"The database exists.")
else:
    print(f"The database does not exist.")
    print("Creating Database Instance...")
    with open('SQL/createTable.sql', 'r') as sql_file:
        result_iterator = cursor.execute(sql_file.read(), multi=True)
        for res in result_iterator:
            print("Running query: ", res)  # Will print out a short representation of the query
            print(f"Affected {res.rowcount} rows")
        # conn.commit()

# At this point, table is good

# Now, let's set up the random numbers for the barcode
# Can make this number whatever you want. During live exhibit, make it super large
theListOfNumbers = []
makeListOfNumbers(10)
counter = 0

# Now, Deals with setting up the barcode printer
# Printer IP Address
kitchen = Network('')

# Defind who you are talking to (must match arduino IP and port)
address = ('', )

# Set Up the Socket
client_socket = socket(AF_INET, SOCK_DGRAM)
# only wait 1 second for a resonse
client_socket.settimeout(1)

# Main Loop, now listens for when the button is pressed
while True:
    # Set data to Blue Command
    data = bytes("high", 'utf-8')
    # send command to arduino
    client_socket.sendto(data, address)
    try:
        # Read response from arduino
        rec_data, addr = client_socket.recvfrom(2048)
        # 255 means that the button was pressed
        if rec_data == b'255':
            print('printing!')
            printing(counter)
            counter = counter + 1
    except:
        pass




