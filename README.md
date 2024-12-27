This repo contains some of the code files that I worked on for the Electronic ARTrium project. Electronic ARTrium is an interactive video-game exhibit that has four minigames for players to complete. Each minigame has its own section with TV screen, computers, speakers, LIDAR devices (detect if player is too close to screen) and Arduino aminatronics. All these components need to be synched with one another by Ethernet communications. In addition, a ticketing system was created to keep track of user players by involving barcode tickets that are printed and used to start each minigame, along with storing data from the barcode tickets to a MySQL database.

The actual Electronic ARTrium is private access and has significantly more files, so I created this repo to showcase what I worked on specifically, which was mainly related to Ethernet networking, databases, and the ticketing system mentioned above. 

This repo has three folders with code files: Python Server, Barcode Scanner, and Barcode Printer / Arduino Push Button. 

For the Python Server, it involves Ethernet commuinications by re-routing data between Unity(program to write video game on screen), Arduino aminatronics, LIDAR, barcode scanners, and other devices using TCP/IP. The server also frequently interacts with the exhibits MySQL database. 

For the Barcode Scanner, the code involves sending the barcode number scanned by a physical device (that was bought). 

For the Barcode Printer / Arduino Push Button, it involves both a physical receipt printer (that was bought) and an Arduino Push Button (that was made by other students). The code files handle both devices so that when a player pushes a button, a physical ticket is printed (and a new MySQL entry is added) 

For security reasons, all of the IP Addresses and port numbers have been removed. 
