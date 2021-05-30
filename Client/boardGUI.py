
import codenames
import sys

from functools import partial

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from customCell import customCell

def stra(i,j):
    return str(chr(65 + j)) + str(i + 1)

def strarev(strVal):
    i = int(strVal[1]) - 1
    j = ord(strVal[0]) - 65
    return i, j

class GameBoardGUI(QWidget):

    updateGridSignal = pyqtSignal()
    gridCellClicked = pyqtSignal(str)
    
    
    def __init__(self, dims, ImgBoard, startTeam, caller_method_click, parent = None): #ImgBoard, whch team started
        super(GameBoardGUI, self).__init__(parent)
        
        self.updateGridValues(dims, ImgBoard, False, startTeam)
        self.startingTeam = startTeam
        self.fullDims = dims

        self.setWindowTitle("Codenames Pictures Board")
        self.screenShape = QDesktopWidget().screenGeometry()
        self.resize(self.screenShape.width(), self.screenShape.height())
        
        self.grid = QGridLayout(self)
        self.cell = {}
        
        self.updateGrid()
        
        self.setLayout(self.grid)
        
        self.updateGridSignal.connect(self.updateGrid)
        self.gridCellClicked.connect(caller_method_click)

    def updateGridValues(self, dims, ImgBoard, spyBrd = False, startTeam = -1):
        self.ImgBoard = ImgBoard
        self.spyMaster = spyBrd
        self.fullDims = dims
        
        if startTeam != -1:
            self.startingTeam = startTeam
        
        self.updateGridSignal.emit()
        
    def updateGrid(self): # Is called whene there is a newBoard, a gameOver or becomes Spymaster
        while self.grid.count():
            child = self.grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if self.fullDims == 4:
            for j in range(0,5):
                cellID = stra(4,j)
                if cellID in self.cell:
                    del self.cell[cellID]
        
        
        for i in range(0, self.fullDims):
            for j in range(0,5):

                cellID = stra(i,j)
                if cellID in self.cell:
                    del self.cell[cellID]
                
                self.cell[cellID] = customCell(self.ImgBoard[i][j], cellID, self.spyMaster, self.startingTeam)

                self.cell[cellID].resize(self.width()/5 - 10, self.height()/5 - 20)
                self.grid.addWidget(self.cell[cellID],i,j)
                
                self.cell[cellID].resizeEvent(None)
                
                self.cell[cellID].viewImage.connect(self.shwImg)
                self.cell[cellID].clueClicked.connect(self.clueClicked)
        
        
        
        
    def updateCell(self, i, j, guessed, cardType):
        self.ImgBoard[i][j].guessed = guessed
        self.ImgBoard[i][j].typeOfCard = cardType
        self.cell[stra(i,j)].updateCard(self.ImgBoard[i][j])
        
    def arrowKey(self, j, i, cellVal):
        x,y = strarev(str(cellVal))
        if x+i>=0 and x+i<self.fullDims and y+j>=0 and y+j<5:
            self.shwImg(stra(x+i, y+j))

    def shwImg(self, cellVal):
        i, j = strarev(str(cellVal))
        # imgViewer = imgView( pathImg, stra(i, j), self.ImgBoard[i][j],self)

        self.imgViewer = customCell(self.ImgBoard[i][j], cellVal, self.spyMaster,self.startingTeam,  True)
        self.imgViewer.setWindowTitle(self.ImgBoard[i][j].img + ' || cell: ' + cellVal )
        self.imgViewer.arrowKeyPress.connect(self.arrowKey)
        self.imgViewer.show()

    def clueClicked(self, cellVal):
        self.gridCellClicked.emit(cellVal)

    def keyReleaseEvent(self,e):
        if e.key() == Qt.Key_F and e.modifiers() == Qt.ShiftModifier:       
            if self.windowState() & Qt.WindowFullScreen:
                self.showMaximized()
            else:
                self.showFullScreen()

        else:
            return
            


if __name__ == '__main__':
    def x(strVal):
        print(strVal)
        i,j = strarev(strVal)
        GUI.updateCell(i,j, True, ImgBoard[i][j].typeOfCard)
        
    dims = 4
    ImgBoard = codenames.newGame(dims, 1)
    #ImgBoard = codenames.getCleanBoard(ImgBoard)
    # print(ImgBoard)
    app = QApplication(sys.argv)

    ImgBoard[2][2].guessed = True

    ImgBoard[1][2].guessed = True
    GUI = GameBoardGUI(dims, ImgBoard,1,  x)

    #GUI.updateGridValues(dims, ImgBoard, sys.argv[1] == '1')
    GUI.showMaximized()
    sys.exit(app.exec_())

