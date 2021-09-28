#!/usr/bin/env python3


import json
import logging
import os
import socket
from logging.handlers import RotatingFileHandler
import protocol

from BasePlayer import *

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

    def getInfoCharacter(self):
        print("All infos for all cards")
        for i in self.possible_answer:
            print(i)
            L = self.getPossibleMovement(i)
            print(L)
            print("room status")
            for j in L:
                print(self.getRoomStatus(j))

    def getNbInRoom(self):
        nb = 0
        nbRoom = 0
        for i in range(9):
            a = self.getCharacterNbInRoom(i)
            if a > nb:
                nb = a
                nbRoom = i
        return nbRoom

    def splitCharacters(self):
        print("split characters")
        nb = 8
        indexToReturn = 0
        for i in self.possible_answer:
            if self.getCharacterNbInRoom(i) < nb:
                indexToReturn = self.possible_answer.index(i)
                nb = self.getCharacterNbInRoom(i)
        print("index to return = ", indexToReturn)
        self.response_index = indexToReturn


    def togetherCharacters(self):
        print("Bring characters together")
        nb = 0
        indexToReturn = 0
        for i in self.possible_answer:
            if self.getCharacterNbInRoom(i) > nb:
                indexToReturn = self.possible_answer.index(i)
                nb = self.getCharacterNbInRoom(i)
        print("index to return = ", indexToReturn)
        self.response_index = indexToReturn

    
    def makeStrategyChoice(self): ## get infos for all rooms to know if inspector separate people or to assemble them
        if self.getCharacterNbInRoom(self.getNbInRoom()) > 3:
            self.splitCharacters()
        else:
            self.togetherCharacters()
        print("Possible answer are:")
        print(self.possible_answer)
        

    def selectCharacter(self):
        if ("red" in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor("red")
        else:
            self.response_index = randint(0, len(self.possible_answer) - 1)

    def selectPosition(self):
        print(self.response_index)
        self.makeStrategyChoice()
        ##self.response_index = 0

    def selectActavationOfpower(self):
        self.response_index = 0

    def selectPurplePower(self):
        """
            Pruple: Can swap position with another character
        """
        self.response_index = 0

    def selectBrownPower(self):
        """
            Brown: Move other characters with him
        """
        self.response_index = 0


    def selectGreyPower(self):
        """
            Grey: Move the 'Electrical problem' token
        """
        self.response_index = 0


    def selectBluePowerRoom(self):
        """
            Blue: Move the 'lock' token (room)
        """
        self.response_index = 0


    def selectBluePowerExit(self):
        """
            Blue: Move the 'lock' token (exit)
        """
        self.response_index = 0


    def selectWhitePower(self):
        """
            White: Move the other characters from the room
        """
        self.response_index = 0


    def answer(self):
        if (self.question == "select character"):
            self.selectCharacter()
        if (self.question == "select position"):
            self.selectPosition()
        if ("activate" in self.question and "power" in self.question):
            self.selectActavationOfpower()
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
