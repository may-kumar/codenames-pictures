# codenames-pictures
A small GUI made using PyQt5 to play codenames pictures

## Usage
Any images to be used should be in the output folder.  
Words to be used should be put in output.txt file.  

The server reads only filenames from the image folder, so both parties need to have the same output folder. The words are sent from the server itself, so for an only words game, only the server requires output.txt.  

The directory structure should be the same as here, otherwise it will not be able to find the files required.

### Server
Start the server by running serverGUI from the server folder, and clicking on start server. To make the program connectable from outside your local network, set-up [port forwarding](https://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/) on your router.
The server doesn't act as client, so if you wish to play you'll have to start a client instance and connect to this server.

### Client
Run the clientGUI from the client folder. Enter your username, the IP address and port number where the server is running and yay!!!

## Libraries Used:
sys, socket, threading, pickle, PyQt5  
