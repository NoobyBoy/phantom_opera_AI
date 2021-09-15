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
set up fantom logging
"""
fantom_logger = logging.getLogger()
fantom_logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# file#!/usr/bin/env python3

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



class Phantom(BasePlayer):

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
        fantom_logger.debug("|\n|")
        fantom_logger.debug("Phantom answers")
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

    def selectPosition(self):
        self.response_index = 0

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
        # import pdb; pdb.set_trace()
        response = self.answer()
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
