import codenames
import sys
import socket
import threading
import pickle
import random

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def int_to_bytes(x: int, val: int = 0) -> bytes:
    if val == 0:
        if x != 0:
            val = (x.bit_length() + 7) // 8
            
    return x.to_bytes(val , 'big')

def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def sendCon(cliSocket, val, ID_x, dataPack):
    finalPacket = int_to_bytes(val, 1) + int_to_bytes(ID_x, 1) + int_to_bytes(len(dataPack), 3) + dataPack
    cliSocket.send(finalPacket)

def sendConAll(ID_x, val, pckt):
    for idc, users in clientsList.items():
        if users[0] != 'TEAM':
            try:
                sendCon(users[0], val, ID_x, pckt)
            except Exception as e:
                print("sendConAll has failed, Error:", e)
                print("Username: ", users[1])

def recvCon(cliSocket):
    hdr = cliSocket.recv(5)
    if not hdr:
        cliSocket.close()
        print("Communications not working")
        return 'FAIL', 'FAIL', 'FAIL'.encode()
    lenPckt = int_from_bytes(hdr[2:])
    pckt = cliSocket.recv(lenPckt)
    
    type1 = hdr[0]
    clientID = hdr[1]
    # print(hdr)
    return clientID, type1 , pckt

def strStrip(ini_string):
    getVals = list([val for val in ini_string if val.isalnum()]) 
    result = "".join(getVals) 
    return result
    
def fusersList():
    userList = {}
    for idc, cli in clientsList.items():
        userList[idc] = [cli[1], cli[3], cli[4]]
    return userList

def strarev(strVal):
    i = int(strVal[1]) - 1
    j = ord(strVal[0]) - 65
    return i, j

server = None
clientsList = {}
clientsList[-2] = ['TEAM', 'BLUE',-1, 0, 0]
clientsList[-1] = ['TEAM', 'RED',-1, 1,  0]
#Follows socket, username, address, team, spymaster
 
# clientsList = [['TEAM', 'BLUE',-1, 0, 0, -1],['TEAM', 'RED',-1, 1, 0, -1]]    #Follows socket, username, address, team, spymaster, ID no
# usersList = [['red1', 0, 0], ['blue1', 1, 0],['red2', 0, 0], ['blue2', 1, 0],['red3', 0, 0], ['blue3', 1, 0],['redma', 0, 1], ['bluema', 1, 1]]  

startingTeam = -1
whichTeamsTurn = -1
gameOver = False
scores = [0,0]
fullDims = 4

spyMastersA = [-1 , -1 ]


class serverScreen(QWidget):

    updateUserText = pyqtSignal()
    updateStatusText = pyqtSignal(str, str, QColor) #Username, value, what has he done(lol)

    def __init__(self, parent = None):
        super(serverScreen, self).__init__(parent)
        self.setWindowTitle("Codenames Pictures Server")
        self.grid = QGridLayout(self)

        self.usersTxtBox = QTextEdit()
        self.usersTxtBox.setReadOnly(True)
        self.grid.addWidget(self.usersTxtBox, 0, 0, 2, 2)
        self.fupdateUsersTextBox()

        self.textStaBox = QTextEdit()
        self.textStaBox.setReadOnly(True)
        # self.defCol = self.textStaBox.textColor()
        self.grid.addWidget(self.textStaBox, 0, 3, 4, 4)

        startServerbtn = QPushButton("Start Server")
        startServerbtn.clicked.connect(self.start_server)
        self.grid.addWidget(startServerbtn, 4, 0)


        newBoardbtn = QPushButton("New Board")
        self.grid.addWidget(newBoardbtn, 4, 1)
        newBoardbtn.clicked.connect(self.initializeNewGame)

        self.lblTm1  = QLabel('x', alignment=Qt.AlignCenter)
        self.lblTm1.setFont(QFont("Arial", 20,  QFont.Bold))
        self.lblTm1.setStyleSheet("QLabel {color : green; }")

        self.lblDash = QLabel('-', alignment=Qt.AlignCenter)
        self.lblDash.setFont(QFont("Arial", 20,  QFont.Bold))

        self.lblTm2  = QLabel('x', alignment=Qt.AlignCenter)
        self.lblTm2.setFont(QFont("Arial", 20,  QFont.Bold))
        self.lblTm2.setStyleSheet("QLabel {color : green; }")

        self.lblTurn = QLabel('UNKNO\nTURN', alignment=Qt.AlignCenter)
        self.lblTurn.setFont(QFont("Arial", 20,  QFont.Bold))
        self.lblTurn.setStyleSheet("QLabel {color : purple; }")

        self.dimsChkBox = QCheckBox("5x5 Board?")
        
        self.scoreGrid = QGridLayout()
        
        
        self.scoreGrid.addWidget(self.dimsChkBox, 0, 0, 1, 3)
        
        self.scoreGrid.addWidget(self.lblTm1, 1, 0)
        self.scoreGrid.addWidget(self.lblDash, 1, 1)
        self.scoreGrid.addWidget(self.lblTm2, 1, 2)
        self.scoreGrid.addWidget(self.lblTurn, 2, 0, 1,3)

        self.grid.addLayout(self.scoreGrid, 0,2, 4, 1)

        btnRandomizeTeams = QPushButton("Randomize Teams")
        self.grid.addWidget(btnRandomizeTeams, 4, 3, 1, 2)
        btnRandomizeTeams.clicked.connect(self.randomizeTeams)

        endServerbtn = QPushButton("End Server")
        self.grid.addWidget(endServerbtn, 4, 5, 1, 2)
        endServerbtn.clicked.connect(self.close)

        self.updateUserText.connect(self.fupdateUsersTextBox)
        self.updateStatusText.connect(self.fupdateStatusTextBox)


    def start_server(self):
        HOST_PORT = 8080
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', HOST_PORT))
        server.listen(10)
        
        self.textStaBox.append("Host: " + socket.gethostbyname(socket.gethostname()))
        self.textStaBox.append("Port: " + str(HOST_PORT) + '\r\n')
        

        self.initializeNewGame()

        #Will start  new thread to accept new clients
        threading._start_new_thread(self.accept_clients, (server,0))

    def initializeNewGame(self):
        global spyMastersA
        global whichTeamsTurn
        global startingTeam
        global gameOver
        global clientsList
        global scores
        global fullDims
        
        if self.dimsChkBox.isChecked():
            fullDims = 5
        else:
            fullDims = 4
            

        self.curFullBoardx = codenames.newGame(fullDims) #Make a board to play with
        self.curHidBoardx = codenames.getCleanBoard(self.curFullBoardx)

        whichTeamsTurn = random.randint(0, 1)
        startingTeam = whichTeamsTurn
        # This just decided starting team, 0 is blue, 1 is red
        colors = ['BLUE', 'RED']

        self.lblTm1.setStyleSheet("QLabel {color : " + colors[startingTeam].lower() + "; }")
        self.lblTm1.setText('9')

        self.lblTm2.setStyleSheet("QLabel {color : " + colors[startingTeam^1].lower() + "; }")
        self.lblTm2.setText('8')

        self.lblTurn.setStyleSheet("QLabel {color : " + colors[whichTeamsTurn].lower() + "; }")
        self.lblTurn.setText(colors[whichTeamsTurn] + '\nTURN')
        
        
        
        scores[startingTeam] =   9 if fullDims == 5 else 8
        scores[startingTeam^1] = 8 if fullDims == 5 else 7



        for val in spyMastersA:
            if val != -1:
                clientsList[val][4] = 0
        spyMastersA = [-1 , -1 ]
        gameOver = False


        sendConAll(0,14, int_to_bytes(fullDims) + pickle.dumps(self.curHidBoardx,  protocol = -1))
        sendConAll(0, 2, pickle.dumps(fusersList(), protocol = -1))
        #DONE: We also have to tell everyone newGame and show everyone the new board

        self.sendGameStats()

    def sendGameStats(self, toAll = -1):
        global spyMastersA
        global whichTeamsTurn
        global startingTeam
        global gameOver
        global clientsList
        global scores

        pckt = int_to_bytes(whichTeamsTurn, 1) + int_to_bytes(scores[startingTeam], 1) + int_to_bytes(scores[startingTeam^1], 1) + int_to_bytes(startingTeam, 1)

        if toAll == -1:
            sendConAll(0,12, pckt)
        else:
            sendCon(clientsList[toAll][0], 12, toAll, pckt)
            
        #update out own board also
        lors = ['BLUE', 'RED']
                    
        self.lblTm1.setText(str(scores[startingTeam]))
        self.lblTm2.setText(str(scores[startingTeam^1]))
        
        if not gameOver:
            self.lblTurn.setStyleSheet("QLabel {color : " + lors[whichTeamsTurn].lower() + "; }")
            self.lblTurn.setText(lors[whichTeamsTurn] + '\nTURN')
            
        del lors
        
    def randomizeTeams(self):
        global spyMastersA
        global whichTeamsTurn
        global gameOver
        global clientsList


        leng = len(clientsList) - 2
        if leng == 0:
            return 
        if leng < 0:
            print("Not supposed to happen, the cliestsList does not have original members")
        tm1 = leng//2
        tm2 = leng - tm1
        arr = tm1*[0] + tm2*[1]
        random.shuffle(arr)

        i = 0
        for idc in clientsList:
            if idc < 0:
                continue
            clientsList[idc][3] = arr[i]
            clientsList[idc][4] = 0
            i += 1

        spyMastersA = [-1 , -1 ]

        sendConAll(0,2, pickle.dumps(fusersList(), protocol = -1))
        self.updateUserText.emit()
        
    def accept_clients(self, the_server, y):
        global spyMastersA
        global whichTeamsTurn
        global gameOver
        global clientsList

        i = 0 
        colors = [Qt.blue, Qt.red]
        while True:
            client, addr = the_server.accept()
            print("Accepted from ", addr)
        
            clientID, type1, client_name  = recvCon(client)
            
            if type1 == 'FAIL':
                print("Nothing was received")
                continue
                
            if type1 != 0:
                print("Something has gone wrong connecting")
                print(clientID, type1, client_name)
                continue
            
            
            #This is correct let's move on
            
            client_name = strStrip(client_name.decode())
            # self.prnt(client_name + ' has connected.')
            
            clientsList[i] = [client, client_name, addr, i % 2, 0]
            sendConAll(i,1, (str(i%2) + str(client_name)).encode())

            #client.send(pickle.dumps(fusersList(), protocol = -1))
            sendCon(client, 2, i, pickle.dumps(fusersList(), protocol = -1))
            #client.send(pickle.dumps(self.curHidBoardx,  protocol = -1))
            sendCon(client, 3, i, int_to_bytes(fullDims) +  pickle.dumps(self.curHidBoardx,  protocol = -1))

            self.updateUserText.emit()
            self.updateStatusText.emit( client_name, ' has joined', colors[i%2])
            #Keep accepting new connections and all
            self.sendGameStats(i)


            #Now we need to start a new thread to keep communication with the client
            threading._start_new_thread(self.keep_comm,(client, client_name, i % 2, i))
            i += 1

    def keep_comm(self, cli, user_n, teamN, idVal):
        global spyMastersA
        global whichTeamsTurn
        global startingTeam
        global gameOver
        global clientsList
        global scores
        
        
        colors = [Qt.blue, Qt.red]

        while True:#Start a loop to check and see what comes
            try:
                recvID, type1, pckt = recvCon(cli)
            except OSError as e:
                print(str(e))
                print(user_n + ' has broken')
                break
            else:
                pckt = pckt.decode()
                if pckt == 'FAIL':
                    print('This connection failed, RecvdID:', recvID,' , TYPE Recevied:', type1)
                # print(pckt)
                
                if pckt == "exit" or type1 == 255: 
                    break
                    
                elif type1 == 7: #Has changed teams
                    clientsList[idVal][3] = int(pckt[0])
                    self.updateStatusText.emit(user_n, ' has changed teams. (Traitor!)', colors[clientsList[idVal][3]])
                    self.updateUserText.emit()
                    sendConAll(recvID, 8, str(pckt[0]).encode())
                    
                elif type1 == 5: #Has tried to become spymaster
                    if spyMastersA[clientsList[idVal][3]] == -1:  #Meaning not assigned yet for this team
                        clientsList[idVal][4] = 1
                        spyMastersA[clientsList[idVal][3]] = idVal
                        self.updateStatusText.emit( user_n, ' has become spymaster.', colors[clientsList[idVal][3]])
                        self.updateUserText.emit()
                        sendConAll(recvID, 6, 'ACKN'.encode())
                        sendCon(cli, 4, recvID,int_to_bytes(fullDims) +  pickle.dumps(self.curFullBoardx,  protocol = -1))
                    else:
                        self.updateStatusText.emit( user_n, ' failed to become spymaster.', colors[clientsList[idVal][3]])
                        sendConAll(recvID, 6, 'NACK'.encode())
                
                elif type1 == 9: #Has clicked on a clue
                    if gameOver:
                        continue
                    if whichTeamsTurn != clientsList[idVal][3]: # Current team member has not selected this
                        continue
                    if clientsList[idVal][4] == 1:#check if spymaster
                        continue
                        
                    self.updateStatusText.emit(user_n, ' has clicked on ' + pckt, colors[clientsList[idVal][3]])
                    i,j = strarev(pckt)
                    
                    if self.curHidBoardx[i][j].guessed:#This card has already been guessed
                        continue
                    
                    
                    
                    self.curHidBoardx[i][j].guessed = True
                    self.curFullBoardx[i][j].guessed = True
                    
                    self.curHidBoardx[i][j].typeOfCard = self.curFullBoardx[i][j].typeOfCard
                    
                    sendConAll(recvID, 10, pckt.encode() + self.curFullBoardx[i][j].typeOfCard.encode())
                    
                    colValueType = self.curFullBoardx[i][j].typeOfCard
                    
                    if colValueType[0:4] == 'TEAM':
                        if startingTeam ^ (int(colValueType[4])-1):
                            colValueType = 'RED'
                        else:
                            colValueType = 'BLUE'
                    
                    self.updateStatusText.emit( 'It was ' + colValueType, ' '  , QColor(colValueType))
                    
                    #DONE: Check game stats and send
                    
                    if colValueType == 'RED':
                        scores[1] -= 1
                        colValueType = 1
                    elif colValueType == 'BLUE':
                        scores[0] -= 1
                        colValueType = 0
                    elif colValueType == 'BLACK':
                        gameOver = True
                        winner = whichTeamsTurn^1
                        
                    
                    if scores[0] == 0:
                        gameOver = True
                        winner = 0
                    
                    if scores[1] == 0:
                        gameOver = True
                        winner = 1
                        
                    
                    if gameOver:
                        pckt = int_to_bytes(winner,1) + pickle.dumps(self.curFullBoardx,  protocol = -1)
                        sendConAll(0, 13, pckt)
                        
                        lors = ['BLUE', 'RED']
                        self.lblTurn.setStyleSheet("QLabel {color : " + lors[winner].lower() + "; }")
                        self.lblTurn.setText(lors[winner] + '\nWIN')
                        del lors
                    else:
                        if colValueType == 'GRAY' or colValueType != whichTeamsTurn: #wrong team selected yeah:
                            whichTeamsTurn = whichTeamsTurn^1 #Other teams turn now
                            sendConAll(recvID, 11, int_to_bytes(whichTeamsTurn, 1))
                    
                    self.sendGameStats()
                    
                    
                elif type1 == 15: #Has clicked on End Turn
                    if gameOver:
                        continue
                    if whichTeamsTurn != clientsList[idVal][3]: # Current team member has not selected this
                        continue
                    if clientsList[idVal][4] == 1:#check if spymaster
                        continue
                    
                    whichTeamsTurn = whichTeamsTurn^1 #Other teams turn now
                    sendConAll(recvID, 11, int_to_bytes(whichTeamsTurn, 1))
                    self.sendGameStats()
                    
        #This guy has disonnected, remove him from everything!!!!
        
        self.updateStatusText.emit( user_n, ' has quit.', colors[clientsList[idVal][3]])
        

        if spyMastersA[clientsList[idVal][3]] == idVal:
            spyMastersA[clientsList[idVal][3]] = -1
        
        popedVal = clientsList.pop(idVal, None)
        
        if not popedVal:
            print("this guy doesn't exist,we out of here")

        self.updateUserText.emit()
        sendConAll(idVal, 254, 'exit'.encode())
        


    def fupdateUsersTextBox(self):
        self.usersTxtBox.clear()

        redTm =  []
        blueTm = []
        # print(clientsList)
        for idc, users in clientsList.items():
            strUser = users[1]
            if users[4] == 1:#This is a spymaster
                strUser = '{' + strUser + '}'

            strUser = str(idc) + ': ' + strUser
            
            if users[3] == 0:
                blueTm.append(strUser)
            elif users[3] == 1:
                redTm.append(strUser)

        # txt = '<table style="width:100%">\n'
        for i in range(max(len(redTm), len(blueTm))):
            ret = '  '
            blt = '  '
            if i < len(redTm):
                ret = redTm[i]
            if i < len(blueTm):
                blt = blueTm[i]

            self.usersTxtBox.setTextColor(Qt.blue)
            self.usersTxtBox.insertPlainText(blt + "\t\t")
            self.usersTxtBox.setTextColor(Qt.red)
            self.usersTxtBox.insertPlainText(ret + "\t\r\n")

        # print("WORKED")
        #     txt = txt + '<tr>\n'
        #     txt = txt + '<td>' + blt + '</td>\n'
        #     txt = txt + '<td>' + ret + '</td>\n'
        #     txt = txt + '</tr>\n'
        # txt = txt + '</table>'
        # self.usersTxtBox.setHtml(txt)

    def fupdateStatusTextBox(self, user_n, val, teamColor):
        #Actions required
        # -Someone has joined
        # -Someone has left
        # -Someone has become spymaster
        # -Someone has change teams
        # -Someone clicked on something
        self.textStaBox.insertPlainText('(' + QTime.currentTime().toString(Qt.DefaultLocaleLongDate) + ') : ')
        self.textStaBox.setTextColor(teamColor)
        self.textStaBox.insertPlainText(user_n)
        self.textStaBox.setTextColor(Qt.black)
        self.textStaBox.insertPlainText(val)
        self.textStaBox.insertPlainText("\r\n")
        
    def closeEvent(self, e):
        #Close all sockets here
        sendConAll(0, 253, 'BYE'.encode())
        for idc, cl in clientsList.items():
            if cl[0] != 'TEAM':
                cl[0].shutdown(socket.SHUT_RDWR)
                cl[0].close()
        e.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    serverG = serverScreen()
    serverG.show()
    sys.exit(app.exec_())
