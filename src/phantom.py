#!/usr/bin/env python3


import json
import logging
import os
import socket
from logging.handlers import RotatingFileHandler
import protocol

from typing import Tuple
from random import randint, choice
from globals import passages, colors, pink_passages, before, after, logger, mandatory_powers

host = "localhost"
port = 12000
# HEADERSIZE = 10

"""
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file
if os.path.exists("./logs/fantom.log"):
    os.remove("./logs/fantom.log")
file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
fantom_logger.addHandler(file_handler)
# stream
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
fantom_logger.addHandler(stream_handler)



class Phantom():

    def __init__(self):

        self.end = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data = {};

    def connect(self):
        self.socket.connect((host, port))

    def disconnect(self):
        self.socket.close()

    def getActiveCards(self):
        return self.data["game state"]["active character_cards"]

    def getActiveCardsColors(self):
        return [elem["color"] for elem in self.data["game state"]["active character_cards"]]

    def getIndexOfColor(self, color):
        return self.getActiveCardsColors().index(color)

    def printAnswerSelection(self):
        fantom_logger.debug("|\n|")
        fantom_logger.debug("fantom answers")
        fantom_logger.debug(f"question type ----- {self.data['question type']}")
        fantom_logger.debug(f"data -------------- {self.possible_answer}")
        fantom_logger.debug(f"response index ---- {self.response_index}")
        fantom_logger.debug(f"response ---------- {self.possible_answer[self.response_index]}")

    def selectCharacter(self):
        if ("red" in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor("red")
        else:
            self.response_index = randint(0, 3)
        self.printCharacterSelection()

    def selectPostion(self):
        self.response_index = 0

    def selectActavationOfpower(self):
        self.response_index = 0

    def selectPurplePower(self):
        """
            Pruple: Can swap postion with another character
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
        question = self.data['question type']
        if (question == "select character"):
            self.selectCharacter()
        if (question == "select position"):
            self.selectPostion()
        if ("activate" in question and "power" in question):
            self.selectActavationOfpower()
        if (question == "purple character power"):
            self.selectPurplePower()
        if (question == "brown character power"):
            self.selectBrownPower()
        if (question == "grey character power"):
            self.selectGreyPower()
        if (question == "blue character power room"):
            self.selectBluePowerRoom()
        if (question == "blue character power exit"):
            self.selectBluePowerExit()
        if ("white character power move" in question):
            self.selectWhitePower()
        self.printAnswerSelection()
        return self.response_index


    def handle_json(self, msg):
        self.data = json.loads(msg)
        self.possible_answer = self.data["data"]
        response = self.answer()
        # import pdb; pdb.set_trace()
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)
        self.data.clear();


    def run(self):

        while self.end is not True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                self.handle_json(received_message)
            else:
                fantom_logger.debug("My job here is done.")
                self.end = True



if __name__ == '__main__':
    fantom_logger.debug("hello I am the phantom.")
    p = Phantom()
    p.connect()
    p.run()
    p.disconnect()
