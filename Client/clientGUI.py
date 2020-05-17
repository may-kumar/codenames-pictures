import codenames
import sys
import boardGUI
import socket
import threading
import pickle

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


# def int_to_bytes(x: int, val: int = 0) -> bytes:
#     if val == 0:
#         val = (x.bit_length() + 7) // 8
#     return x.to_bytes(val , 'big')

# def int_from_bytes(xbytes: bytes) -> int:
#     return int.from_bytes(xbytes, 'big')
    

def int_to_bytes(x: int, val: int = 0) -> bytes:
    if val == 0:
        if x != 0:
            val = (x.bit_length() + 7) // 8

    return x.to_bytes(val , 'big')
    
    
def int_from_bytes(xbytes):
    return int.from_bytes(xbytes, 'big')

def sendCon(cliSocket, val, ID, dataPack):
    finalPacket = int_to_bytes(val, 1) + int_to_bytes(ID, 1) + int_to_bytes(len(dataPack), 3) + dataPack
    cliSocket.send(finalPacket)
    
def recvCon(cliSocket):
    hdr = cliSocket.recv(5)
    lenPckt = int_from_bytes(hdr[2:])
    pckt = cliSocket.recv(lenPckt)
    
    # print(hdr)
    type1 = hdr[0]
    clientID = hdr[1]

    return clientID, type1, pckt

def strStrip(ini_string):
    getVals = list([val for val in ini_string if val.isalnum()]) 
    result = "".join(getVals) 
    return result
    


class connectScreen(QWidget):
    def __init__(self, parent = None):
        super(connectScreen, self).__init__(parent)
        self.setWindowTitle("Codenames Pictures Connect")
        #Add stuff for username, host and port


        self.nameTxt = QLineEdit()
        self.addrTxt = QLineEdit('127.0.0.1')
        self.portTxt = QLineEdit('8080')
        self.enterBtn = QPushButton('CONNECT!')
        self.enterBtn.clicked.connect(self.enterClicked)
        
        self.client = None
        self.username = ''
        self.teamN = 0

        flo = QFormLayout(self)
        flo.addRow("Username", self.nameTxt)
        flo.addRow("IP Address",self.addrTxt)
        flo.addRow("Port",self.portTxt)
        flo.addRow(self.enterBtn)

        self.resize(self.sizeHint().width()*1.5,self.sizeHint().height())

    def enterClicked(self):
        username    = strStrip(str(self.nameTxt.text()))
        ipaddress   = str(self.addrTxt.text())
        portno      = int(self.portTxt.text())
        if self.connect_to_server(username, ipaddress, portno) != -1:
            self.gameMainScreen = gameStatus(self.client, self.username, self.teamN, self.clientID)
            self.hide()
            self.gameMainScreen.show()
            


    def connect_to_server(self, name, HOST_ADDR = "127.0.0.1", HOST_PORT = 8080 ):
        self.client = None
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((HOST_ADDR, HOST_PORT))

            
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")
            msg.setInformativeText(str(e))
            msg.setWindowTitle("Error")
            msg.exec_()
            return -1

        # welc  = client.recv(4096)#This is our welcome message
        # welc = welc.decode()

        # clientID = 0
        
        if len(name) > 8:
            name = name[:8]
        
        sendCon(client, 0, 0, name.encode())
        #client.send(name.encode()) # Send name to server after connecting
        
        clientID, type1, recvd = recvCon(client)
        recvd = recvd.decode()

        # if recvd[0] == '0':
        #     print("YOU ARE BLUE TEAM")
        #     self.teamN = 0
        # elif recvd[0] == '1':
        #     print("YOU ARE RED TEAM")
        #     self.teamN = 1     

        self.teamN = int(recvd[0])

        self.client = client
        self.username = recvd[1:]
        self.clientID = clientID
        return 0
        

class gameStatus(QWidget):
    updateUserText = pyqtSignal()
    updateStatusText = pyqtSignal(str, str, QColor) #Username, value, what has he done(lol)
    updateBoardSignal = pyqtSignal(int, int, bool, str)
    
    def __init__(self, client, username, team, clientID, parent = None):
        super(gameStatus, self).__init__(parent)
        self.setWindowTitle("Codenames Pictures Client:" + username)

        self.grid = QGridLayout(self)

        self.userTxtBox = QTextEdit()
        self.userTxtBox.setReadOnly(True)
        self.grid.addWidget(self.userTxtBox, 0, 0, 2, 2)
        

        self.client = client

        self.username = username
        self.teamN = team
        self.clientID = clientID

        self.spymaster = 0
        self.whichTeamsTurn = -1
        self.gameOver = False
        self.startingTeam = -1
        self.scores = [-1,-1]
        
        clientID, type1, users = recvCon(client)
        if type1 == 2:
            self.allUsers = pickle.loads(users) #loaded directly as a pickle dump
        else:
            print('2, something went wrong')
            
            
        clientID, type1, brd = recvCon(client)
        if type1 == 3 and clientID == self.clientID:
            self.fullDims = brd[0]
            self.brd = pickle.loads(brd[1:])
        else:
            print('3, something went wrong')
        
        # print(self.allUsers)
        self.fupdateUsersGrid()

        self.textBox = QTextEdit()
        self.textBox.setReadOnly(True)


        self.grid.addWidget(self.textBox, 0, 3, 4, 4)

        self.joinBluebtn = QPushButton('Join BLUE Team')
        self.joinBluebtn.clicked.connect(lambda:self.chngTeam(0))

        self.joinRedbtn = QPushButton('Join RED Team')
        self.joinRedbtn.clicked.connect(lambda:self.chngTeam(1))

        self.spyMasterbtn = QPushButton('SpyMaster')
        self.spyMasterbtn.clicked.connect(self.becSpyMaster)

        self.showBrd = QPushButton('Show Board')
        self.showBrd.clicked.connect(self.showBoard)

        self.exitBtn = QPushButton('Exit')
        self.exitBtn.clicked.connect(self.close)

        self.grid.addWidget(self.joinBluebtn, 3, 0)
        self.grid.addWidget(self.joinRedbtn, 3, 1)
        self.grid.addWidget(self.spyMasterbtn, 4, 0, 1, 2)

        self.lblColr = QLabel(alignment=Qt.AlignCenter)
        self.lblColr.setStyleSheet("QLabel {background-color : " + ('red' if self.teamN else 'blue') + "; }")

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


        self.scoreGrid = QGridLayout()

        
        self.scoreGrid.addWidget(self.lblColr,0, 0, 1, 3)

        self.scoreGrid.addWidget(self.lblTm1, 1, 0)
        self.scoreGrid.addWidget(self.lblDash, 1, 1)
        self.scoreGrid.addWidget(self.lblTm2, 1, 2)
        self.scoreGrid.addWidget(self.lblTurn, 2, 0, 1,3)

        self.grid.addLayout(self.scoreGrid, 0,2, 4, 1)
        
        self.endTurnBtn =  QPushButton('End Turn')
        self.endTurnBtn.clicked.connect(self.endTurnClick)
        
        self.grid.addWidget(self.endTurnBtn, 4,2)





        self.grid.addWidget(self.showBrd, 4, 3 , 1, 2)
        self.grid.addWidget(self.exitBtn, 4, 5, 1,2)
        
        
        self.updateUserText.connect(self.fupdateUsersGrid)
        self.updateStatusText.connect(self.fupdateStatusTextBox)
        
        self.brdGUI = boardGUI.GameBoardGUI(self.fullDims, self.brd, self.startingTeam, self.cellClick)
        
        self.updateBoardSignal.connect(self.brdGUI.updateCell)
        
        threading._start_new_thread(self.keep_comm, (self.clientID, self.username))
    
    def endTurnClick(self):
        sendCon(self.client, 15, self.clientID, '-'.encode())
        
    def cellClick(self, cellVal):
        # print("clicked button is " + cellVal)
        sendCon(self.client, 9, self.clientID, str(cellVal).encode())


    def showBoard(self):
        self.brdGUI.showMaximized()


    def becSpyMaster(self):
        if self.spymaster == 1 or self.spymaster == -1:
            return #Why the heck did you even click that
        sendCon(self.client, 5, self.clientID, '----'.encode())



    def chngTeam(self, newTm):
        if newTm == self.teamN or self.spymaster == 1:#Ensure you can't change teams when spymaster
            return
        
        sendCon(self.client, 7, self.clientID, str(newTm).encode())



    def keep_comm(self, selfID, user_n):
        colors = [Qt.blue, Qt.red]
        type1 = 0
        while True:#Start a loop to check and see what comes
            try:
                recvID, type1, pckt = recvCon(self.client)
            except Exception as e:
                print(str(e)) 
                print('Disconnected for some reason')
                break
            else:
                # print(type1, pckt)
                if type1 == 1: #Someone has joined yay
                    pckt = pckt.decode()
                    self.allUsers[recvID] = [pckt[1:], int(pckt[0]), 0]
                    self.updateStatusText.emit( self.allUsers[recvID][0], ' has joined', colors[int(pckt[0])])
                    self.updateUserText.emit()

                elif type1 == 2:#Somewhy the full userlist has been sent
                    self.allUsers = pickle.loads(pckt)

                    self.spymaster = self.allUsers[selfID][2]
                    self.teamN = self.allUsers[selfID][1]
                    #Update our own credentials
                    self.lblColr.setStyleSheet("QLabel {background-color : " + ('red' if self.teamN else 'blue') + "; }")

                    self.updateUserText.emit()
                    #Update the userGrid
                    
                elif type1 == 3: #The full board has been sent
                    self.fullDims = pckt[0]
                    self.brd = pickle.loads(pckt[1:])
                    self.brdGUI.updateGridValues(self.fullDims, self.brd)
                    
                elif type1 == 4: #This is the fullBoard; became spymaster
                    self.fullDims = pckt[0]
                    self.brd = pickle.loads(pckt[1:])
                    self.updateStatusText.emit( 'You', ' have received your spymaster board', colors[self.allUsers[recvID][1]])
                    self.brdGUI.updateGridValues(self.fullDims, self.brd, True)
                    
                elif type1 == 6: #There is a new spymaster  
                    pckt = pckt.decode()
                    if pckt == 'ACKN':
                        self.allUsers[recvID][2] = 1   #Someone has just become spymaster  
                        if recvID == selfID: #We only have become new spymaster lol
                            self.spymaster = 1 #Will receive our own board soon
                         
                        self.updateStatusText.emit( self.allUsers[recvID][0], ' has become spymaster!!', colors[self.allUsers[recvID][1]])
                        self.updateUserText.emit()
                        
                    elif pckt == 'NACK':
                        if recvID == selfID: #We have been rejected ouch
                            # self.spymaster = -1
                            self.updateStatusText.emit( 'Your', ' spymaster request has been rejected', colors[self.allUsers[recvID][1]])
                        pass #Someone else has been rejected
                        
                elif type1 == 8:#Someone has changed teams
                    self.allUsers[recvID][1] = int(pckt.decode()[0])
                    self.updateStatusText.emit( self.allUsers[recvID][0], ' has changed teams. (Traitor!)', colors[self.allUsers[recvID][1]])
                    self.updateUserText.emit()
                    if recvID == selfID: #We have chnaged teams amazing
                        self.teamN = int(pckt.decode()[0])
                        self.lblColr.setStyleSheet("QLabel {background-color : " + ('red' if self.teamN else 'blue') + "; }")
                    
                elif type1 == 10: #Someone has clicked on a clue

                    i,j = boardGUI.strarev(pckt[0:2].decode())
                    colValueType = pckt[2:].decode()
                    self.brd[i][j].typeOfCard = colValueType
                    
                    self.brd[i][j].guessed = True
                    self.updateBoardSignal.emit(i, j, True, colValueType)
                    
                    if colValueType[0:4] == 'TEAM':
                        if self.startingTeam ^ (int(colValueType[4])-1):
                            colValueType = 'RED'
                        else:
                            colValueType = 'BLUE'
                            
                    self.updateStatusText.emit( self.allUsers[recvID][0], ' has clicked on ' + pckt[0:2].decode(), colors[self.allUsers[recvID][1]])
                    self.updateStatusText.emit( 'It was ' + colValueType , ' ', QColor(colValueType))
                    

                    
                elif type1 == 11: #Next teams turn
                    self.whichTeamsTurn = pckt[0]
                    self.updateStatusText.emit( self.allUsers[recvID][0], ' has ended turn', colors[self.allUsers[recvID][1]])
                    self.updateStatusText.emit(('RED' if self.whichTeamsTurn else 'BLUE') +  ' teams turn', ' ', colors[self.whichTeamsTurn])
                    self.lblTurn.setText(('RED' if self.whichTeamsTurn else 'BLUE') + '\nTURN')
                    
                elif type1 == 12: #Game stats
                    lors = ['BLUE', 'RED']
                    
                    self.whichTeamsTurn = pckt[0]
                    
                    
                    if self.startingTeam == -1: #New game
                        self.startingTeam = pckt[3]
                        self.brdGUI.updateGridValues(self.fullDims, self.brd, False, self.startingTeam)
                    
                    self.scores[self.startingTeam] = pckt[1]
                    self.scores[self.startingTeam^1] = pckt[2]
                    
                    # print(self.scores, self.startingTeam, self.whichTeamsTurn)
                    
                    
                    self.lblTm1.setStyleSheet("QLabel {color : " + lors[self.startingTeam].lower() + "; }")
                    self.lblTm1.setText(str(pckt[1]))

                    self.lblTm2.setStyleSheet("QLabel {color : " + lors[self.startingTeam^1].lower() + "; }")
                    self.lblTm2.setText(str(pckt[2]))
                    
                    if not self.gameOver:
                        self.lblTurn.setStyleSheet("QLabel {color : " + lors[self.whichTeamsTurn].lower() + "; }")
                        self.lblTurn.setText(lors[self.whichTeamsTurn] + '\nTURN')
                    del lors

                    

                elif type1 == 13: #Game is over
                    winner = pckt[0]
                    pckt = pckt[1:]

                    lors = ['BLUE', 'RED']

                    self.gameOver = True
                    self.brd = pickle.loads(pckt) #This is final board
                    self.updateStatusText.emit('GAME OVER', ' ', QColor('purple'))
                    self.updateStatusText.emit(lors[winner] + ' TEAM', ' WINS', colors[winner])
                    self.brdGUI.updateGridValues(self.fullDims,self.brd, True) #Show the full board to everyone

                    self.lblTurn.setStyleSheet("QLabel {color : " + lors[winner].lower() + "; }")
                    self.lblTurn.setText(lors[winner] + '\nWIN')
                    del lors

                elif type1 == 14: #A new game has started
                    self.fullDims = pckt[0]
                    self.brd = pickle.loads(pckt[1:])
                    self.updateStatusText.emit('NEW GAME', '(New board has been received)', QColor('purple'))

                    self.spymaster = 0
                    self.whichTeamsTurn = -1
                    self.gameOver = False
                    self.startingTeam = -1
                    self.scores = [-1,-1]
            

                elif type1 == 254: #Someone else has quit
                    self.updateStatusText.emit( self.allUsers[recvID][0], ' has quit.', colors[self.allUsers[recvID][1]])
                    popedVal = self.allUsers.pop(recvID, None)
                    if not popedVal:
                        print("Nexer existed nope")
                    del popedVal

                    self.updateUserText.emit()

                elif type1 == 253: #The server has closed
                    self.updateStatusText.emit('The server', ' has been closed.', QColor('purple'))
                    break

        if type1 != 253:
            self.updateStatusText.emit( 'ERROR: ', "Communications has been broken", colors[1])
            # print("Communications has been broken")

    def fupdateUsersGrid(self):
        
        self.userTxtBox.setPlainText(' ')
        
        i = [0,0]
        redTm =  []
        blueTm = []
        # print(self.allUsers)

        for idc, users in self.allUsers.items():
            strUser = users[0]
            if users[2] == 1:#This is a spymaster
                strUser = '{' + strUser + '}'


            if users[1] == 0:
                blueTm.append(strUser)
            elif users[1] == 1:
                redTm.append(strUser)

            i[users[1]] += 1

        # txt = '<table style="width:100%">\n'
        for i in range(max(len(redTm), len(blueTm))):
            ret = '  '
            blt = '  '
            if i < len(redTm):
                ret = redTm[i]
            if i < len(blueTm):
                blt = blueTm[i]

            self.userTxtBox.setTextColor(Qt.blue)
            self.userTxtBox.insertPlainText(blt + "\t\t")
            self.userTxtBox.setTextColor(Qt.red)
            self.userTxtBox.insertPlainText(ret + "\r\n")


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

        self.textBox.setTextColor(teamColor)
        self.textBox.insertPlainText(user_n)
        self.textBox.setTextColor(Qt.black)
        self.textBox.insertPlainText(val)
        self.textBox.insertPlainText("\r\n")
        
    def closeEvent(self, e):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.brdGUI.close()
            sendCon(self.client, 255, self.clientID,'exit'.encode())
            self.client.shutdown(socket.SHUT_RDWR)
            self.client.close()
            e.accept()
        else:
            e.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    connectScreen = connectScreen()
    connectScreen.show()
    sys.exit(app.exec_())


# if __name__ == '__main__':
#     ImgBoard = codenames.newGame()
#     # print(ImgBoard)
#     app = QApplication(sys.argv)
#     boardScreen = boardGUI.GameBoardGUI(ImgBoard)
#     boardScreen.show()
#     sys.exit(app.exec_())


