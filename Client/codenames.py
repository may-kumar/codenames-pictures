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
    def __init__(self, img, typeOfCard, guessed, words):
        self.img = img
        self.typeOfCard = typeOfCard
        self.guessed = guessed
        self.words = words
        

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

def loadWordSet():
    path = os.getcwd() 
    parent = os.path.dirname(path) 
    file = os.path.join(parent, 'output.txt')

    words = []
    with open(file) as f:
        for line in f:
            for word in line.split(','):
                words.append(word.strip())
    
    return words
        
def selectCards(full_set, sizeVal, words):
	
    chosenCards = []
    randNums = random.sample(range(len(full_set)), NUM_CARDS)

    index = 0
    if sizeVal == 5:
        for i in CardType5:
            num = i.value
            while num > 0:
                chosenCards.append(Card(full_set[randNums[index]],i.name, False, words))
                num -= 1
                index += 1
    elif sizeVal == 4:
        for i in CardType4:
            num = i.value
            while num > 0:
                chosenCards.append(Card(full_set[randNums[index]],i.name, False, words))
                num -= 1
                index += 1
    
    random.shuffle(chosenCards)
    return chosenCards

def newGame(sizeVal, words = False):
    cardSet = selectCards(loadWordSet() if words else loadImageSet(), sizeVal, words)
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