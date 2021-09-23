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

    def getPhantom(self):
        for char in self.game_state["characters"]:
            if char["color"] == self.game_state["fantom"]:
                return char

    def printAnswerSelection(self):
        fantom_logger.debug("|")
        fantom_logger.debug("Phantom answers")
        fantom_logger.debug(f"question type ----- {self.question}")
        fantom_logger.debug(f"data -------------- {self.possible_answer}")
        fantom_logger.debug(f"response index ---- {self.response_index}")
        fantom_logger.debug(f"response ---------- {self.possible_answer[self.response_index]}")
        fantom_logger.debug("|")

    def selectCharacter(self):
        if ("red" in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor("red")
        elif (self.game_state["fantom"] in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor(self.game_state["fantom"])
        else:
            self.response_index = randint(0, len(self.possible_answer) - 1)
        self.selected_character = self.possible_answer[self.response_index]


    def selectPositionPhantom(self):


        reachable_empty_room = []
        room_with_one_suspect = []
        room_with_mult_suspect = []
        total_suspect_grouped = 0

        for room in range(0, 10):
            status = self.getRoomStatus(room)
            fantom_logger.debug(status)
            if status["charact_nb"] == 0 and room in self.possible_answer: reachable_empty_room.append(room)
            if status["charact_nb"] == 1 and status["suspect_nb"] == 1 : room_with_one_suspect.append(room)
            if status["suspect_nb"] >= 1:
                room_with_mult_suspect.append(room)
                total_suspect_grouped += status["suspect_nb"]

        fantom_logger.debug(f"reachable_empty_room :{reachable_empty_room}   room_with_one_suspect:{room_with_one_suspect}  room_with_mult_suspect: {room_with_mult_suspect} with a total of : {total_suspect_grouped}")
        # if there is more isolated suspect than grouped suspect
        if (len(room_with_one_suspect) > total_suspect_grouped and len(reachable_empty_room) > 0):
            #if the shadow room is reachable
            #and there is multiple suspect in the shadow room
            #and the blue character will not be played later this turn
            if ((self.game_state["shadow"] in self.possible_answer) and self.getSuspecNbInRoom(self.game_state["shadow"]) > 1 and "blue" not in self.getActiveCardsColors()):
                self.response_index = self.possible_answer.index(self.game_state["shadow"])
            else:
                self.response_index = self.possible_answer.index(choice(reachable_empty_room))
        # the oposite
        elif (len(room_with_one_suspect) < total_suspect_grouped):
            self.response_index = self.possible_answer.index(self.getMostFilledWithSuspectRoom(self.possible_answer))
        else:
            self.response_index = randint(0, len(self.possible_answer) - 1)


    def selectPositionNotPhantomSuspect(self):

        phantom = self.getPhantom()
        phantom_status = self.getRoomStatus(phantom["position"])

        ## Special case
        #if the character is in the same room as phantom
        #we considere that at the end of the turn we will not be in the same room anymore
        if (phantom["position"] == self.selected_character["position"]):
            phantom_status["suspect_nb"] -= 1

        fantom_logger.debug(phantom_status)
        reachable_empty_room = []
        reachable_filled_room = []
        fantom_logger.debug("-")
        for room in self.possible_answer:
            status = self.getRoomStatus(room)
            fantom_logger.debug(status)
            if status["charact_nb"] == 0 : reachable_empty_room.append(room)
            else: reachable_filled_room.append(room)

        fantom_logger.debug(f"reachable_empty_room :{reachable_empty_room}  reachable_filled_room: {reachable_filled_room} shadow room: {self.game_state['shadow']}")
        fantom_logger.debug(f"""fantom can scream ?:{phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]}""")

        # if the phantom can scream
        if (phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]):
            if (len(reachable_empty_room) > 0):
                self.response_index = self.possible_answer.index(choice(reachable_empty_room))
            elif (self.game_state["shadow"] in self.possible_answer):
                self.response_index = self.possible_answer.index(self.game_state["shadow"])
            else:
                self.response_index = randint(0, len(self.possible_answer) - 1)

        # if the phantom cannot scream
        elif (len(reachable_filled_room)):
            self.response_index = self.possible_answer.index(self.getMostFilledWithSuspectRoom(reachable_filled_room))
        else:
            self.response_index = randint(0, len(self.possible_answer) - 1)

    def selectPositionNotPhantomNotSuspect(self):
        phantom = self.getPhantom()
        phantom_status = self.getRoomStatus(phantom["position"])
        character_status = self.getRoomStatus(self.selected_character["position"])

        if (phantom["position"] == self.selected_character["position"]):
            phantom_status["innocent_nb"] -= 1

        fantom_logger.debug(phantom_status)
        reachable_empty_or_innocent_room = []
        reachable_suspect_room = []
        fantom_logger.debug("-")
        for room in self.possible_answer:
            status = self.getRoomStatus(room)
            fantom_logger.debug(status)
            if status["charact_nb"] == status["innocent_nb"] : reachable_empty_or_innocent_room.append(room)
            if status["charact_nb"] == status["suspect_nb"] == 1: reachable_suspect_room.append(room)

        fantom_logger.debug(f"reachable_empty_or_innocent_room :{reachable_empty_or_innocent_room}  reachable_suspect_room: {reachable_suspect_room} shadow room: {self.game_state['shadow']}")
        fantom_logger.debug(f"""fantom can scream ?:{phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]}""")

        # if the phantom can scream
        if (phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]):
            if (self.game_state["shadow"] in self.possible_answer and "blue" not in self.getActiveCardsColors()):
                self.response_index = self.possible_answer.index(self.game_state["shadow"])
            elif (character_status["suspect_nb"] == 1 and character_status["charact_nb"] == 2 and len(reachable_empty_or_innocent_room) > 0):
                self.response_index = self.possible_answer.index(choice(reachable_empty_or_innocent_room))
            else:
                self.response_index = randint(0, len(self.possible_answer) - 1)

        # if the phantom cannot scream
        else:
            if (len(reachable_suspect_room) > 0):
                self.response_index = self.possible_answer.index(choice(reachable_suspect_room))
            else:
                self.response_index = randint(0, len(self.possible_answer) - 1)


    def selectPosition(self):
        """
         the phantom player must have a max of suspect in the same state (scream or no scream)
         so we choose a room acording that statement
        """
        fantom_logger.debug(self.getPhantom())
        #if the selected character to move is the phantom
        if (self.selected_character["color"] == self.game_state["fantom"]):
            self.selectPositionPhantom()
        #if it's anybody else
        elif (self.selected_character["suspect"] == True):
            fantom_logger.debug("I am not the phantom and suspect")
            self.selectPositionNotPhantomSuspect()
        else:
            fantom_logger.debug("I am not the phantom and not suspect")
            self.selectPositionNotPhantomNotSuspect()





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
        try :
            while self.end is not True:
                received_message = protocol.receive_json(self.socket)
                if received_message:
                    self.handle_json(received_message)
                else:
                    fantom_logger.debug("Phantom: My job here is done.")
                    self.end = True
        except ConnectionResetError:
            return



if __name__ == '__main__':
    fantom_logger.debug("hello I am the phantom.")
    p = Phantom()
    p.connect()
    p.run()
    p.disconnect()
