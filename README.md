This repo contains some of the code files that I worked on for the Electronic ARTrium project. Electronic ARTrium is an interactive video-game exhibit that has four minigames for players to complete. Each minigame has its own section with TV screen, computers, speakers, LIDAR devices (detect if player is too close to screen) and Arduino aminatronics. All these components need to be synched with one another by Ethernet communications. In addition, a ticketing system was created to keep track of user players by involving barcode tickets that are printed and used to start each minigame, along with storing data from the barcode tickets to a MySQL database.

The actual Electronic ARTrium is private access and has significantly more files, so I created this repo to showcase what I worked on specifically, which was mainly related to Ethernet networking, databases, and the ticketing system mentioned above. 

This repo has three folders with code files: Python Server, Barcode Scanner, and Barcode Printer / Arduino Push Button. 

For the Python Server, it involves Ethernet commuinications by re-routing data between Unity and Arduino aminatronics using TCP/IP. The server also frequently interacts with the exhibits MySQL database. Each minigame has it's own section that 


For security reasons, all of the IP Addresses and port numbers have been removed. 
