# sql connection imports
import mysql.connector
from mysql.connector import errorcode
# socket communications for TCP/IP
import socket
import json
import threading
import subprocess
import faulthandler
import datetime

# define the IP Address
IP = ''
# define the main port number here
PORT = ''

# Temporary values for the sockets for Unity
UnitySocketForSectionOne = ''

# Temporary values for the sockets for Arduinonarrarator
ArduinoSocketForSectionOneNarrarator = ''
ArduinoSocketForSectionOneThunder = ''


def table_exists(cursor, table_name):
    # Check if the table exists
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None


config = {
    'host': '',
    'user': '',
    'password': '',
    'database': '',
    'autocommit': '',
    'port': '',
}


def main():
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
        return None
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

    # At this point, the database should be avaliable. Will now work on TCP/IP code
    # This will act as a Python server.
    # SQL -> Python and the other way around is already done using the code above :)

    print("[STARTING] Server is starting...")

    # Create a server socket with address family IvP 4 (AF_INET) and socket type TCP (SOCK_STREAM)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the server to an IP address and port number
    server_socket.bind((IP, PORT))
    # Allow the server to listen for 5 active connections
    server_socket.listen(5)

    # Will create a list of all the IP addresses and port numbers

    # Loop that runs and looks for active clients
    print(f"[LISTENING] Server is listening on {IP}:{PORT} \n")

    # For now, it's a continuous loop. In the future, just set a time for like 5 hours
    while True:
        client_socket, address = server_socket.accept()
        # Print the address which client was connected from
        print("Client connected from", address)


        theThread = threading.Thread(target=handleClient, args=(client_socket, address, cursor, conn))
        theThread.start()


        # Print out the number of active connections
        print(f"[Number of ACTIVE Connections] {threading.active_count() - 1} ")
    server_socket.close()


# Process beginning: when the user scans barcode, the "didUserScan" is turned to "yes" and the "current_section" changes to the section
# Then for LIDAR, it goes onto MySQL and gets barcode that "didUserScan" = yes "current_section" = section# (there should only be one!)
# After it does everything, the "didUserScan" is turned to "no". Then the exihibit can begin

# Process ending: once the user finishes the game, Unity should connect to the sewrver. Data is send from Unity, and server sends game code.
# Then "current_section" is set to zero, and other data is saved onto the database. Users are then free to go to other exhibits.

# ID DEFINITION
# ID 1: Barcode scanner for Section One
# ID 2: LIDAR Intrusion Section One (Player gets too close to the exhibit)
# ID 3: LIDAR Occupancy Section One (Begins the game)
# ID 4: Unity connects to retrieve game code at the end of section one
# ID 5: Unity sends live queue to Arduino Section One (NOT NARARRATOR)
# ID 26: Unity sends queue to Arduino nararrator to begin moving jawline OR Dance
# ID 30: (From barcode scanner) add barcode # to database, only use if printer/push button isn't working


# WITHIN each ID case, there should probably be some message sent back to Unity if
# there was an error but the connection is still active
import time


def handleClient(client_socket, address, cursor, conn):
    print(f"[NEW CONNECTION] Client {address} connected.")

    # Check if it's from Unity or not, to save the socket


        # Arduino Section One Narrarator
    if ('' in address):
        global ArduinoSocketForSectionOneNarrarator
        ArduinoSocketForSectionOneNarrarator = client_socket
        # Arduino Section One Thunder
    elif ('' in address):
        global ArduinoSocketForSectionOneThunder
        ArduinoSocketForSectionOneThunder = client_socket
        print("Arduino from Section One Connected")

    connected = True
    while connected:
        # Receive data from the client, up to 1024 bytes
        # data = client_socket.recv(1024).decode('utf-8')
        data = client_socket.recv(2048)
        theData = json.loads(data.decode())
        print("The data sent")
        print(theData)

        # If no data is received or client wants to end connection, stop looping
        if not theData or theData['STATUS'] == 'END':
            print(f"Client {address} has disconnected. ")
            print("")
            connected = False
            break

        # print("recieved from client:" + str(theConverted))
        print(f"[Received from Client {address}] {data}")

        # From Unity Section One Computer
        if ('' in address and theData['PROGRAM'] == 'Unity'):
            global UnitySocketForSectionOne
            UnitySocketForSectionOne = client_socket
            print("Connection from Unity Section One")

        # Will send different messages to different clients, based on their ID numbers
        # cursor and conn are required for MySQL, so its being passed
        case = theData['ID']
        if case == 1:
            if handleIDOne(theData, client_socket, address, cursor, conn) == 1:
                break
        elif case == 2:
            if handleIDTwo(theData, client_socket, address, cursor, conn) == 1:
                break
        elif case == 3:
            if handleIDThree(theData, client_socket, address, cursor, conn) == 1:
                break
        elif case == 4:
            if handleIDFour(theData, client_socket, address, cursor, conn) == 1:
                break
        elif case == 5:
            if handleIDFive(theData, client_socket, address, cursor, conn) == 1:
                break
        elif case == 26:
            if handleIDTwentySix(theData, client_socket, address, cursor, conn) == 1:
                break
        elif case == 30:
            if handleIDThirty(theData, client_socket, address, cursor, conn) == 1:
                break

        # invalid ID is sent
        # currently this case is just ignored and next packet is checked
        else:
            print("Here it is continuing")
            continue

    # if connection was disconnected close socket
    client_socket.close()


#################################################################

def handleIDOne(theData, client_socket, address, cursor, conn):
    try:
        barcodeNumber = theData['BarcodeNumber']

        # For some weird reason, the scanner is picking up an extra digit, so just remove it
        barcodeNumber = barcodeNumber[:-1]
        print(barcodeNumber)

        exists = check_barcode_exists(cursor, barcodeNumber)
        print(f"Barcode {barcodeNumber} exists: {exists}")

        # If it exists, edit the "didUserScan" column in MySQL
        if exists == True:
            update_query = ("UPDATE users SET didUserScan = %s where barcode = %s")
            enter_data = ('yes', barcodeNumber)
            cursor.execute(update_query, enter_data)
            conn.commit()

            update_query_2 = ("UPDATE users SET current_section = %s where barcode = %s")
            enter_data_2 = ('1', barcodeNumber)
            cursor.execute(update_query_2, enter_data_2)
            conn.commit()
        print("ID 1 sucess")
        print("")

    except Exception as e:
        print(e)
        print("Exited by the user")
        return 1


###################################################################
def handleIDTwo(theData, client_socket, address, cursor, conn):
    try:
        # For LIDAR Intrusion, it will simply send a message to Unity And Arduino to stop
        # Can also add a counter that counts how many times a user get too close

        # Unity
        theDataToSend = {
            "displayMessage": "Player too close"
        }

        UnitySocketForSectionOne.send(bytes(json.dumps(theDataToSend), 'utf-8'))

        # Arduino
        theDataToSendArduino = {
            "anim": "Player too close"
        }

        j = json.drumps(theDataToSendArduino).encode('utf-8')

        # Will have try-catch for sending to Arduino
        try:
            ArduinoSocketForSectionOneNarrarator.send(bytes([len(j)]) + j)
        except:
            print("Arduino Secion One Narrarator isn't connected")

        try:
            ArduinoSocketForSectionOneThunder.send(bytes([len(j)]) + j)
        except:
            print("Arduino Secion One Thunder isn't connected")

        print("ID 2 success")
        print("")


    except Exception as e:
        print(e)
        print("Exited by the user")
        return 1

###################################################################
def handleIDThree(theData, client_socket, address, cursor, conn):
    try:
        # For LIDAR Occupancy (this will be called when LIDAR detects someone in the exhibit
        # Will check MySQL if player is at that exhibit (by checking if they scanned.
        # Then send a message to Unity to begin playing the game

        # Queries
        cursor = conn.cursor(buffered=True)
        # Retrieval Query, returns a tuple
        retrieve_query = ("SELECT barcode FROM users "
                          "where didUserScan = %s and current_section = %s")
        cursor.execute(retrieve_query, ('yes', '1',))
        resultFromQuery = cursor.fetchall()

        # Need to convert to string
        dataInString = convertToString(resultFromQuery)

        if dataInString is not None:
            # Now send something to unity
            theDataToSendUnity = {
                "displayMessage": "LIDAR was detected",
                "barcode": dataInString
            }

            UnitySocketForSectionOne.send(bytes(json.dumps(theDataToSendUnity), 'utf-8'))

            # Will also send something to Arduino Narrarator to begin playing
            theDataToSendArduino = {
                "anim": "LIDAR was detected"
            }

            j = json.drumps(theDataToSendArduino).encode('utf-8')

            # Will have try-catch for sending to Arduino
            try:
                ArduinoSocketForSectionOneNarrarator.send(bytes([len(j)]) + j)
            except:
                print("Arduino Secion One Narrarator isn't connected")

            try:
                ArduinoSocketForSectionOneThunder.send(bytes([len(j)]) + j)
            except:
                print("Arduino Secion One Thunder isn't connected")
        else:
            print("Player didn't check in, or barcode scanner stuff isn't working")

        print("ID 3 sucess")
        print("")


    except Exception as e:
        print(e)
        print("Exited by the user")
        return 1

#####################################################################


def handleIDFour(theData, client_socket, address, cursor, conn):
    try:
        # Unity will connect with here. First go to MySQL and get the game code
        cursor = conn.cursor(buffered=True)
        # Retrieval Query, returns a tuple
        retrieve_query = ("SELECT barcode FROM users "
                          "where current_section = %s")
        cursor.execute(retrieve_query, ('1',))
        resultFromQuery = cursor.fetchall()

        # Need to convert to string
        theBarcode = convertToString(resultFromQuery)

        if theBarcode is not None:
            # Now, get the game code for that specific user
            cursor = conn.cursor(buffered=True)
            # Retrieval Query, returns a tuple
            retrieve_query = ("SELECT game_code FROM users "
                              "where barcode = %s")
            cursor.execute(retrieve_query, (theBarcode,))
            resultFromQuery2 = cursor.fetchall()

            # Need to convert to string
            dataInString = convertToString(resultFromQuery2)
            sectionOneNumber = dataInString[0:1]

            # now that it is converted to string, it can now be used in JSON
            theFinalData = {
                "gameCode": sectionOneNumber,
            }

            # Then send it back to Unity
            UnitySocketForSectionOne.send(bytes(json.dumps(theFinalData), 'utf-8'))

            # Now, reset everything
            update_query = ("UPDATE users SET didUserScan = %s where barcode = %s")
            enter_data = ('no', theBarcode)
            cursor.execute(update_query, enter_data)
            conn.commit()

            update_query_2 = ("UPDATE users SET current_section = %s where barcode = %s")
            enter_data_2 = ('0', theBarcode)
            cursor.execute(update_query_2, enter_data_2)
            conn.commit()

            print("complete")
        else:
            print("Something isn't working")

        print("ID 4 success")
        print("")
        return 0

    except Exception as e:
        print(e)
        print("Exited by the user")
        return 1

##################################################################
def handleIDFive(theData, client_socket, address, cursor, conn):
    try:
        # Unity will connect here. Throughout the exhibit, Unity will send data packets to Arduino (NOT NARRARATOR)
        # For now, it'll simply reroute the message from Unity

        j = json.drumps(theData).encode('utf-8')

        # For arduino, will have a try-catch (since arduino connection may be loss)
        try:
            ArduinoSocketForSectionOneThunder.send(bytes([len(j)]) + j)
            #ArduinoSocketForSectionOneThunder.sendall(f"{theQueueNumber}\n".encode())
        except:
            print("Arduino Section One Thunder isn't connected")


        print("ID 5 success")
        print("")
        # Otherwise, if the data was not received, the program has ended
    except Exception as e:
        print(e)
        print("Exited by the user")
        return 1


################################################################

def handleIDTwentySix(theData, client_socket, address, cursor, conn):
    try:
        # Unity will connect here. Throughout the exhibit, Unity will send data packets to Arduino
        # For now, it'll simply reroute the message from Unity
        j = json.drumps(theData).encode('utf-8')
        try:
            ArduinoSocketForSectionOneNarrarator.send(bytes([len(j)]) + j)
        except:
            print("Arduino Section One Narrarator isn't connected")

        print("ID 26 Sucessfull")
        print("")
    except Exception as e:
        print(e)
        print("Exited by the user")
        return 1



####################################################################
def handleIDThirty(theData, client_socket, address, cursor, conn):
    # Barcode Scanner calls this function, it adds barcode number MySQL for the first time
    # Only use this if the barcode printer/push button isn't work
    try:
        barcodeNumber = theData['BarcodeNumber']
        barcodeNumber = barcodeNumber[:-1]
        print(barcodeNumber)

        theCurrTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insert_query = ("INSERT INTO users "
                        "(barcode, current_section, time_printed, finished, game_code, didUserScan) "
                        "VALUES (%s, %s, %s, %s, %s, %s)")
        enter_data = (barcodeNumber, '0', theCurrTime, '0', '0000', 'no')

        cursor.execute(insert_query, enter_data)
        conn.commit()
        print("ID 30 success")
        print("")

    except Exception as e:
        print(e)
        print("Exited by user")
        return 1


###################################################################

# Methods that are not "handleIDs"
def convertToString(theTuple):
    theString = ''

    for item in theTuple:
        theString = theString + "".join(map(str, item))

    return theString


def check_barcode_exists(cursor, barcode):
    query = "SELECT COUNT(*) FROM users WHERE barcode = %s"
    cursor.execute(query, (barcode,))
    result = cursor.fetchone()
    return result[0] > 0  # Returns True if the count is more than 0


# Plays the audio file, the location is specified in the data packet. This will be done in Unity, but will keep the file for now.
def play_audio(audio_file, event):
    print("Playing audio")
    event.wait()
    try:
        powershell_command = rf'(New-Object Media.SoundPlayer "{audio_file}").PlaySync()'
        subprocess.run(["powershell", "-Command", powershell_command], shell=True)
    except subprocess.CalledProcessError as e:
        print("Audio error: " + str(e))


# Insert the LIDAR occupancy event into the log table
def log_lidar_event(cursor, conn, barcode, event_type):
    try:
        insert_query = ("INSERT INTO lidar_occupancy_log (barcode, occupancy_event, event_time) "
                        "VALUES (%s, %s, %s)")
        event_time = datetime.now()
        cursor.execute(insert_query, (barcode, event_type, event_time))
        conn.commit()
        print(f"LIDAR event '{event_type}' logged for player {barcode} at {event_time}.")
    except Exception as e:
        print(f"Log LIDAR event failure: {e}")


# Called for preset lidar event of entering or leaving
def handle_lidar_event(cursor, conn, barcode, entered):
    if entered:
        log_lidar_event(cursor, conn, barcode, 'enter')
    else:
        log_lidar_event(cursor, conn, barcode, 'leave')


# To log the intrusion of a specific barcode
def log_intrusion(cursor, conn, barcode, section):
    try:
        insert_query = ("INSERT INTO intrusion_log (barcode, section, intrusion_time) "
                        "VALUES (%s, %s, %s)")
        intrusion_time = datetime.now()
        cursor.execute(insert_query, (barcode, section, intrusion_time))
        conn.commit()
        print(f"Intrusion logged for player {barcode} in section {section} at {intrusion_time}.")
    except Exception as e:
        print(f"Failed to log intrusion: {e}")


# To log the cloud or tree error for a player in section 1 per barcode
def log_section_1_error(cursor, conn, barcode, error_type):
    try:
        insert_query = ("INSERT INTO section_1_errors (barcode, error_type, error_time) "
                        "VALUES (%s, %s, %s)")
        error_time = datetime.now()
        cursor.execute(insert_query, (barcode, error_type, error_time))
        conn.commit()
        print(f"Logged {error_type} error for player {barcode} in Section 1.")
    except Exception as e:
        print(f"Failed to log Section 1 error: {e}")


# To log the order of flowers or wrong flower, which sequence they faulted, overtaken by storm, if they tried pointing
def log_section_2_error(cursor, conn, barcode, round_num, sequence_num, error_type, max_var_x=None, max_var_y=None, start_time=None, end_time=None):
    try:
        insert_query = ("INSERT INTO section_2_errors_detail (barcode, round_num, sequence_num, error_type, max_variation_x, max_variation_y, round_start_time, round_end_time) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(insert_query, (barcode, round_num, sequence_num, error_type, max_var_x, max_var_y, start_time, end_time))
        conn.commit()
        print(f"Logged {error_type} error for player {barcode} in Section 2, round {round_num}, sequence {sequence_num}.")
    except Exception as e:
        print(f"Failed to log Section 2 error: {e}")
if __name__ == "__main__":
    main()