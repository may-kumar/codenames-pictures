from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


import codenames
import sys


class customCell(QWidget):
    # triPoints = [QPoint(0,0), QPoint(0,85), QPoint(85,0)]
    clueClicked = pyqtSignal(str)
    viewImage = pyqtSignal(str) 
    arrowKeyPress = pyqtSignal(int, int, str) 



    def __init__(self, cardClass, cellID, spyM, starter, viewType = False, parent = None):


        super(customCell, self).__init__(parent)

        

        self.wid_spa = 0
        self.hit_spa = 0
        self.startTeam = starter


        self.mainLabel = QLabel(parent = self, alignment=Qt.AlignCenter)

        self.viewType = viewType

        self.resize(540, 340)
        self.card = cardClass
        
        if not self.card.words:
        #Aspect ratio has to 536:339 for the image to fit 
            self.imgMap = QPixmap(codenames.getImgPath(cardClass.img))
            self.picSize = (self.imgMap.width(), self.imgMap.height())
            rect = QRect(0,0 , self.picSize[0], self.picSize[1])
            map1 = QBitmap(self.imgMap.size())
            map1.fill(Qt.color0)

            painter = QPainter(map1)
            painter.setRenderHint(QPainter.Antialiasing)

            painter.setBrush(Qt.color1)
            painter.drawRoundedRect(rect ,10,10)

            painter.end()
        
            self.oriPic = QPixmap(self.imgMap)
        
            self.imgMap.setMask(map1)
        
        else:
            self.imgMap = QPixmap(600,300)
            self.imgMap.fill(QColor('#E5B372'))
            
            painter = QPainter(self.imgMap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            painter.drawRoundedRect(QRect(0,0,600,300) ,10,10)
            
            font = QFont()
            font.setFamily("Segoe UI")
            font.setBold(True)
            font.setPointSize(40)
            painter.setFont(font)
            
            painter.drawText(self.imgMap.rect(), Qt.AlignCenter, self.card.img)
            painter.end()
        
            
            
        painter = QPainter(self.imgMap)
        font = QFont()
        font.setFamily("Times")
        font.setBold(True)
        font.setPointSize(30)
        painter.setFont(font)

        painter.drawText(7,35, cellID)
        
            
        
        painter.end()

        self.cellID = cellID

        if self.card.guessed: #This is an already guessed card, let's show it
            self.setGuessColor()
            #set the color

        if spyM: #Guy is the spymaster show the card color
            self.setSpyMColor()

        
        self.mainLabel.setPixmap(self.imgMap)
        self.scale = self.imgMap.height()


    def getCol(self, val1, alpha = 255):
        #           0 is not guessed yet    1 is guessed 
        # colors = {'RED0': QColor(255,102,0), 'RED1': QColor(255,0,0),
        #   'BLUE0': QColor(51, 102, 255), 'BLUE1': QColor(0,0,255),
        #   'GRAY0':QColor(220, 220, 220), 'GRAY1':  QColor("white"), 
        #   'BLACK0':  QColor("black"), 'BLACK1':  QColor("black")}

        colors = {'RED0': QColor(179,39,40, alpha), 'RED1': QColor(255,0,0, alpha),
          'BLUE0': QColor(17,119,159, alpha), 'BLUE1': QColor(0, 0, 255, alpha),
          'GRAY0':QColor(220, 220, 220, alpha), 'GRAY1':  QColor(255,255,255, alpha), 
          'BLACK0':  QColor(0,0,0,alpha), 'BLACK1': QColor(0,0,0,alpha)}

        #if self.card.words:
        #    colors['GRAY0'] = QColor(148, 0, 211, alpha)
        #    colors['GRAY1'] = QColor(128,0,128, alpha)
        
        teamStr = self.card.typeOfCard
        if teamStr[0:4] != 'TEAM':
            return colors[teamStr + val1]

        else:
            if self.startTeam ^ (int(teamStr[4])-1):
                return colors['RED' + val1]
            else:
                return colors['BLUE' + val1]


        # self.mainLabel.setScaledContents(True)
        # print(self.imgMap)

    def resizeEvent(self, e):
        height = self.height()
        width = self.width() 


        self.mainLabel.resize(width, height)
        
        img = self.imgMap.scaled(width, height, Qt.KeepAspectRatio)

        self.wid_spa = width - img.width()
        self.hit_spa = height - img.height()

        
        if self.card.guessed:
            # back = QPixmap(self.size())     
            
            #painter = QPainter(back)
            #painter.setBrush(self.getCol('1'))
            #rect = QRectF(self.wid_spa/2,self.hit_spa/2, width - self.wid_spa, height - self.hit_spa)
            
            painter = QPainter(img)
            painter.setPen(QPen(self.getCol('0'),  1, Qt.SolidLine))
            
            # if self.card.words:
                # painter.setBrush(QBrush(self.getCol('1', 120),  Qt.FDiagPattern))
            # else:
                # painter.setBrush(QBrush(self.getCol('1'),  Qt.DiagCrossPattern))
            
            #painter.setBrush(QBrush(self.getCol('1', 120),  Qt.FDiagPattern))
            
            # painter.drawRoundedRect(0,0, width, height, 10, 10)
            # painter.drawPixmap( QRectF(img.rect()), img, QRectF(img.rect()))
            
            painter.setBrush(QBrush(self.getCol('1', 120),  Qt.DiagCrossPattern))
            
            painter.drawRect(QRectF(img.rect()))
            painter.end()
            
            # img = back

        self.scale = img.height()
        self.mainLabel.setPixmap(img)


    def setGuessColor(self):#Show color on the image

        if self.card.words:
            img = QPixmap(590 , 295)
            r,g,b,_ = self.getCol('1').getRgb()
            img.fill(QColor(r, g, b)) 
            self.imgMap = img
            

        painter = QPainter(self.imgMap)
        painter.setBrush(self.getCol('1'))
        painter.drawPolygon(QPoint(0, 0), QPoint(85,0), QPoint(0, 85))

        font = QFont()
        font.setFamily("Times")
        font.setBold(True)
        font.setPointSize(self.height()/10)
        painter.setFont(font)
        pen = QPen()
        r,g,b,_ = self.getCol('1').getRgb()
        pen.setColor(QColor(255-r, 255-g, 255-b))
        painter.setPen(pen)
        painter.drawText(7,35, self.cellID)

        if self.card.words:
            font = QFont()
            font.setFamily("Segoe UI")
            font.setBold(True)
            font.setPointSize(self.height()/8)
            painter.setFont(font)

            pen.setColor(QColor(255 - r, 255 - g, 255 - b))
            painter.setPen(pen)

            painter.drawText(self.imgMap.rect(), Qt.AlignCenter, self.card.img)
         



        painter.end()

        
        self.resizeEvent(None)


    def setSpyMColor(self):
    
        painter = QPainter(self.imgMap)
        painter.setBrush(self.getCol('0'))
        painter.drawPolygon(QPoint(82, 0), QPoint(115,0) , QPoint(0, 115), QPoint(0, 82)) #Top diag
        # painter.drawPolygon( QPoint(510, 0), QPoint(536, 0),  QPoint(536, 339),  QPoint(510, 339)) #Right
        painter.end()


        back = QPixmap(self.imgMap.size())
        
        painter = QPainter(back)

        
        if self.card.words:
            painter.drawPixmap(QRect( 10, 5, 590, 295), self.imgMap.scaledToHeight(295),  self.imgMap.scaledToHeight(295).rect())
        else:
            painter.drawPixmap(QRect( 15, 10, 506, 320), self.imgMap.scaledToHeight(320),  self.imgMap.scaledToHeight(320).rect())
        
        painter.setPen(QPen(self.getCol('0'), 20))
        painter.setBrush(self.getCol('0', 30))
        
        if self.card.words:
            painter.drawRoundedRect(0,0, 600, 300, 10, 10)
        else:
            painter.drawRoundedRect(0,0, 535, 339, 10, 10)

        painter.end()

        self.imgMap = back

        self.resizeEvent(None)         
        

    def updateCard(self, card, spyM = False):
        self.card = card
        if card.guessed:
            self.setGuessColor()

        if spyM == True:
            self.setSpyMColor()
            
        self.resizeEvent(None) 




    def keyReleaseEvent(self,e):
        arr = []
        if e.key() == Qt.Key_Left:
            arr = [-1,0]
        elif e.key() == Qt.Key_Right:
            arr = [1,0]
        elif e.key() == Qt.Key_Up:
            arr = [0, -1]
        elif e.key() == Qt.Key_Down:
            arr = [0,1]

        else:
            return
        self.arrowKeyPress.emit(arr[0], arr[1], self.cellID)

    def mouseReleaseEvent(self, e):
        if self.viewType or self.card.guessed:
            return 
        if self.card.words:
            self.clueClicked.emit( self.cellID)
        elif e.x() >= self.wid_spa/2 and e.y() >= self.hit_spa/2 and (e.x() + e.y()) < (self.hit_spa/2 +self.wid_spa/2 + 90.0*self.scale/339.0):
            self.clueClicked.emit( self.cellID)
        else:
            self.viewImage.emit( self.cellID)

    # def mouseMoveEvent(self,e):
    #     if e.x() >= self.wid_spa and e.y() >= self.hit_spa and (e.x() + e.y()) < (self.wid_spa + 95.0*self.scale/339.0):
    #         print("IN: ", e.x())


if __name__ == '__main__':
    ImgBoard = codenames.newGame(5)
    # print(ImgBoard)
    app = QApplication(sys.argv)
    # ImgBoard[2][2].guessed = True
    boardScreen = customCell(ImgBoard[2][2], 'A4', True, 1)
    boardScreen.show()
    sys.exit(app.exec_())
