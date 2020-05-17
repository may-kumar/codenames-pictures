import random
from enum import Enum
import os
from copy import deepcopy

NUM_CARDS = 25
SIZE = 5

class CardType5(Enum):
    TEAM1 = 9
    TEAM2 = 8
    BLACK = 1
    GRAY = 7

class CardType4(Enum):
    TEAM1 = 8
    TEAM2 = 7
    BLACK = 1
    GRAY = 4

#Card class
class Card:
    #initializes
    def __init__(self, img, typeOfCard, guessed):
        self.img = img
        self.typeOfCard = typeOfCard
        self.guessed = guessed

    def __repr__(self):  
        return "[Image:% s Color:% s, % s]" % (self.img, self.typeOfCard, self.guessed)
    
    #prints the card's image name
    # def printWord(self):
    #     print('{0: ^15}'.format(self.img), end="")

    # def printType(self):
    #     print('{0: ^15}'.format(self.typeOfCard), end = "")
        
    

def getImgPath(imgName):
    return os.path.join(getImgDirectory(),imgName)
    
def getImgDirectory():
    path = os.getcwd() 
    parent = os.path.dirname(path) 
    return os.path.join(parent, 'output')
    

def loadImageSet():
    image_set = os.listdir(getImgDirectory())
    return image_set

def selectImgs(image_set, sizeVal):
	
    chosenImgs = []
    randNums = random.sample(range(len(image_set)), NUM_CARDS)

    index = 0
    if sizeVal == 5:
        for i in CardType5:
            num = i.value
            while num > 0:
                chosenImgs.append(Card(image_set[randNums[index]],i.name, False))
                num -= 1
                index += 1
    elif sizeVal == 4:
        for i in CardType4:
            num = i.value
            while num > 0:
                chosenImgs.append(Card(image_set[randNums[index]],i.name, False))
                num -= 1
                index += 1
    
    random.shuffle(chosenImgs)
    return chosenImgs

def newGame(sizeVal):
    cardSet = selectImgs(loadImageSet(), sizeVal)
    board = [[0,0,0,0,0], [0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    if sizeVal == 5:
        board.append([0,0,0,0,0])
    i = 0
    
    

    for i in range(0, sizeVal):
        for j in range(0,5):
            board[i][j] = cardSet[i*5 + j]
    # for cards in cardSet:
    #     board[i//SIZE][i%SIZE] = cards
    #     print((i//SIZE),i%SIZE, cards)
    #     i = i + 1
    return board
    
def getCleanBoard(board): #Returns board without anything in it
    newBrd = deepcopy(board)

    for row in newBrd:
        for card in row:
            if card.guessed == False:
                card.typeOfCard = 'GRAY'
            
    return newBrd