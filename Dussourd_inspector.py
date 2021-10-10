#!/usr/bin/env python3

"""
    The inspector class


"""

import sys
sys.path.insert(1, 'Dussourd_src')

import json
import logging
import os
import socket
from logging.handlers import RotatingFileHandler
import protocol

from Dussourd_BasePlayer import *

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up inspector logging
"""
inspector_logger = logging.getLogger()
inspector_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file#!/usr/bin/env python3

if os.path.exists("./logs/inspector.log"):
    os.remove("./logs/inspector.log")
file_handler = RotatingFileHandler('./logs/inspector.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
inspector_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
inspector_logger.addHandler(stream_handler)




class Inspector(BasePlayer):

    charPriority = ["grey", "brown", "purple", "white", "pink", "black", "blue"]
    charCanScream = []
    NoPowerRoom = 0
    playerPowerRoom = 0
    splitChar = False #true if we want to split them, false if we want them together

    def __init__(self):
        BasePlayer.__init__(self)
        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((host, port))

    def disconnect(self):
        self.socket.close()

    def printAnswerSelection(self):
        inspector_logger.debug("|\n|")
        inspector_logger.debug("Inspector answers")
        inspector_logger.debug(f"question type ----- {self.question}")
        inspector_logger.debug(f"data -------------- {self.possible_answer}")
        inspector_logger.debug(f"response index ---- {self.response_index}")
        inspector_logger.debug(f"response ---------- {self.possible_answer[self.response_index]}")

    def CanScream(self):#fill a list with all characters who can  scream
        """
            Check how many people can scream and list them, the goal is to have at least 2 people who can scream
            A character can scream if he's suspect, and alone or in the room without power
            The goal is to know if we have enough suspect who can scream to assemble people or if we need to split them
        """
        self.charCanScream.clear()
        for charact in self.game_state["characters"]:
            if charact["suspect"] == True:
                if self.getCharacterNbInRoom(charact["position"]) == 1 or charact["position"] == self.game_state["shadow"]:
                    self.charCanScream.append(charact)

    def getNbInRoom(self):
        """
            Count if there are some group or not to choose a strategy (Split or Together functions) and return the number with the more people in it
            retourne le numéro de salle avec le plus de personne
        """
        nb = 0
        nbRoom = 0
        for i in range(9):
            a = self.getCharacterNbInRoom(i)
            if a > nb:
                nb = a
                nbRoom = i
        return nbRoom

    def splitCharacters(self):#split the selected character and answer directly
        """
            Count the number of characters in the possibles answers and return the room with the less character in it
        """
        nb = 8
        indexToReturn = 0
        for i in self.possible_answer:
            if self.getCharacterNbInRoom(i) < nb:
                indexToReturn = self.possible_answer.index(i)
                nb = self.getCharacterNbInRoom(i)
        self.response_index = indexToReturn


    def togetherCharacters(self): ## Bring characters together and answer directly
        """
            Count the number of characters in the possibles answers and return the room with the more character in it
        """
        nb = 0
        indexToReturn = 0
        for i in self.possible_answer:
            if self.getCharacterNbInRoom(i) > nb:
                indexToReturn = self.possible_answer.index(i)
                nb = self.getCharacterNbInRoom(i)
        self.response_index = indexToReturn

    def ChooseStrategy(self): # function where we decide which strategy we will use
        """
            3 cas (choisir en priorité un suspect):
            il est suspect et peut crier (si assez de cas comme lui, le regrouper, sinon tout seul),
            il est suspect mais ne peut pas crier (si assez de sus qui peuvent crier, l'empêcher de crier, sinon le faire crier)
            il est innocent (il y a assez de sus qui crient, random sinon en fonction de la couleur, faire en sorte qu'il puisse crier) done
        """
        screamPlayable = []
        susplayable = self.getSuspectPlayable()

        if susplayable == 0: # if there is no sus in the choice of character
            if len(self.charCanScream) > 2: # if there is more than 2 char who can scream, we try to reduce this number
                self.splitChar = False
                self.returnCharacter(self.getInnocentPlayable())
            else:                           # else we split them to create more char who can scream
                self.splitChar = True
                self.returnCharacter(self.getInnocentPlayable())

        for char in susplayable:
            if char in self.charCanScream:
                screamPlayable.append(char)

        if len(self.charCanScream) > 2 and len(screamPlayable) != 0: # If there is more than 2 char who can scream, we want to reduce the number to 2 so we try to create a group
            self.splitChar = False
            self.returnCharacter(screamPlayable) # choose a character in the list of char who can scream according to the priority list

        if len(self.charCanScream) < 2 and len(susplayable) != 0: # if there is not enough char who can scream, we try to split them
            self.splitChar = True
            self.returnCharacter(susplayable) #choose a character in the list of suspect char according to the priority list


    def returnCharacter(self, charlist):
        for char in charlist:
            for priority in self.charPriority:
                if priority == char["color"]:
                    self.response_index = self.getIndexOfColor(priority)

    def getAllSus(self): # function which return all suspect
        susList = []
        for charact in self.game_state["characters"]:
            if charact["suspect"] == True:
                susList.append(charact)
        return susList

    def getAllInno(self):
        innoList = []
        for charact in self.game_state["characters"]:
            if charact["suspect"] == False:
                innoList.append(charact)
        return innoList

    def CharactCanScream(self, charact):#return true or false if the character can scream or not
        """
            check if a given character can scream
        """
        if charact in self.charCanScream:
            return True
        else:
            return False

    def makeStrategyChoice(self):
        """
            get infos for all rooms to know if inspector separate people or assemble them
            If there is a group of 3 or more, we split people
            If there is no group of 3 or more people, we assemble them
        """
        if self.splitChar:
            self.splitCharacters()
        else:
            self.togetherCharacters()


    def selectCharacter(self):
        self.ChooseStrategy()
        if ("red" in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor("red")


        else:
            self.response_index = randint(0, len(self.possible_answer) - 1)

    def selectPosition(self):
        self.makeStrategyChoice()

    def selectActivationOfpower(self):
        print(self.possible_answer)
        self.response_index = 0

    def selectPurplePower(self):
        """
            Purple: Can swap position with another character

            If purple innocent => change position with suspect who cannot scream if there is not enough suspect who can scream
            else, change position with character who can scream so he can't scream anymore

            if purple sus => if there is enough suspect who can scream, go where purple cannot scream
            else, change with innocent alone
        """
        purple = self.getCharacterByColor("purple")
        answer = 0
        if purple["suspect"]:
            if len(self.charCanScream) > 2:
                for i in self.getAllInno():
                    if self.getInnocentNbInRoom(i[position]) > 1:
                        answer = self.getIndexOfColor(i)
            if len(self.charCanScream) < 2:
                for i in self.getAllInno():
                    if self.getInnocentNbInRoom(i[position]) == 1 and self.getCharacterNbInRoom(i[positon] == 1):
                        answer = self.getIndexOfColor(i)
        else: #Purple is innocent
            if len(self.charCanScream) > 2:
                answer = self.getIndexOfColor(self.CharactCanScream)
            elif len(self.charCanScream) < 2:
                for i in self.getAllSus():
                    if self.getSuspecNbInRoom(i[position]) > 1:
                        answer = self.getIndexOfColor(i)
        self.response_index = answer


    def selectBrownPower(self):
        """
            Brown: Move other characters with him => if 1 or 2 suspect with him, move, if possible,
            in the room with no light if there is nobody in the room
        """
        brown = self.getCharacterByColor("brown")
        roomList = self.getPossibleMovement(brown)

        self.response_index = 0


    def selectGreyPower(self):
        """
            Grey: Move the 'Electrical problem' token
            => check if there is a group and how many suspect are inside,
            if there is 1 or 2 suspects, move the 'problem' in the room
        """
        print("Select Grey Power", self.possible_answer)
        answer = -1
        for i in range(len(self.possible_answer)-1):
            print(i)
            a = self.getCharacterNbInRoom(i)
            if a > 1:
                nb = self.getSuspecNbInRoom(i)
                if nb == 1:
                    answer = i
        if answer == -1:
            answer = randint(0, len(self.possible_answer) - 1)
        self.response_index = answer


    def selectBluePowerRoom(self):
        """
            Blue: Move the 'lock' token (room)
            Select a room without anybody
        """
        answer = 0
        for i in self.possible_answer:
            if self.getCharacterNbInRoom(i) == 0:
                answer = i

        self.response_index = answer


    def selectBluePowerExit(self):
        """
            Blue: Move the 'lock' token (exit)
        """
        print("BluePowerExit answer ", self.possible_answer)
        self.response_index = 0


    def selectWhitePower(self): ## check si combien de suspects/innocents composent un groupe, essayer de regrouper les innocents et de split les suspects s'il y en a moins de 2
        """
            White: Move the other characters from the room => use the power if the strategy is to split and if there is 1 suspect in the group
        """
        self.response_index = 0


    def answer(self):
        if (self.question == "select character"):
            NoPowerRoom = self.game_state["shadow"]
            self.CanScream()
            self.selectCharacter()
        if (self.question == "select position"):
            self.selectPosition()
        if ("activate" in self.question and "power" in self.question):
            self.selectActivationOfpower()
        if (self.question == "purple character power"):
            self.selectPurplePower()
        if (self.question == "brown character power"):
            self.selectBrownPower()
        if (self.question == "grey character power"):
            self.selectGreyPower()
        if (self.question == "blue character power room"):
            self.selectBluePowerRoom()
        if (self.question == "blue character power exit"):
            self.selectBluePowerExit()
        if ("white character power move" in self.question):
            self.selectWhitePower()
        self.printAnswerSelection()
        return self.response_index


    def handle_json(self, msg):
        self.data = json.loads(msg)
        self.question = self.data["question type"]
        self.possible_answer = self.data["data"]
        self.game_state = self.data["game state"]
        response = self.answer()
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)
        self.data.clear();


    def run(self):

        try :
            while self.end is not True:
                received_message = protocol.receive_json(self.socket)
                if received_message:
                    self.handle_json(received_message)
                else:
                    inspector_logger.debug("Inspector: My job here is done.")
                    self.end = True
        except ConnectionResetError:
            return


if __name__ == '__main__':
    inspector_logger.debug("hello I am the Inspector.")
    i = Inspector()
    i.connect()
    i.run()
    i.disconnect()
