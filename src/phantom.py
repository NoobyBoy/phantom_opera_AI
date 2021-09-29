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

    def phantomCanScream(self):
        phantom = self.getPhantom()
        phantom_status = self.getRoomStatus(phantom["position"])
        return (phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"])


    def charachCanScream(self, charac):
        character_status = self.getRoomStatus(charac["position"])
        return (character_status["charact_nb"] == 1 or charac["position"] == self.game_state["shadow"])

    def printAnswerSelection(self):
        fantom_logger.debug("|")
        fantom_logger.debug("Phantom answers")
        fantom_logger.debug(f"question type ----- {self.question}")
        fantom_logger.debug(f"data -------------- {self.possible_answer}")
        fantom_logger.debug(f"response index ---- {self.response_index}")
        fantom_logger.debug(f"response ---------- {self.possible_answer[self.response_index]}")
        fantom_logger.debug("|")

    def compareWithPhantom(self, charac):
        phantom = self.getPhantom()
        phantom_status = self.getRoomStatus(phantom["position"])
        character_status = self.getRoomStatus(charac["position"])
        if (phantom["position"] == charac["position"]):
            if (charac["suspect"] == True): phantom_status["suspect_nb"] -= 1
            else: phantom_status["innocent_nb"] -= 1
        p_can_scream = phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]
        c_can_scream = character_status["charact_nb"] == 1 or charac["position"] == self.game_state["shadow"]
        return p_can_scream == c_can_scream

    def characterChoicePriority(self, characList):
        priority = ["red", "grey", "purple", "black", "white", "brown", "pink", "blue"]
        for color in priority:
            for charac in characList:
                if (color == charac["color"]):
                    return charac

    def selectCharacter(self):
        if (self.game_state["fantom"] in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor(self.game_state["fantom"])
        elif ("red" in self.getActiveCardsColors()):
            self.response_index = self.getIndexOfColor("red")
        elif (len(self.getSuspectPlayable()) > 0):
            sp = self.getSuspectPlayable()
            ssp = [sus for sus in sp if self.compareWithPhantom(sus) == True]
            if (len(ssp) > 0):
                self.response_index = self.possible_answer.index(self.characterChoicePriority(ssp))
            else:
                self.response_index = self.possible_answer.index(self.characterChoicePriority(sp))
        else:
            self.response_index = self.possible_answer.index(self.characterChoicePriority(self.possible_answer))
        self.selected_character = self.possible_answer[self.response_index]

    def nbSuspectMoveFromThisRoom(self, roomNb):
        return len([char for char in self.game_state["active character_cards"] if char["position"] == roomNb and char["suspect"] == True])

    def selectPositionPhantom(self):
        reachable_empty_room = []
        room_with_one_suspect = []
        room_with_mult_suspect = []
        total_suspect_grouped = 0

        for room in range(0, 10):
            status = self.getRoomStatus(room)
            fantom_logger.debug(status)
            if status["charact_nb"] == 0 and room in self.possible_answer: reachable_empty_room.append(room)
            if status["charact_nb"] == 1 and status["suspect_nb"] == 1 and self.nbSuspectMoveFromThisRoom(room) == 0 : room_with_one_suspect.append(room)
            if status["suspect_nb"] > 1:
                if (status["suspect_nb"] > self.nbSuspectMoveFromThisRoom(room)):
                    room_with_mult_suspect.append(room)
                    total_suspect_grouped += status["suspect_nb"]
                if (status["suspect_nb"] == self.nbSuspectMoveFromThisRoom(room) + 1):
                    room_with_one_suspect.append(room)
                if (status["suspect_nb"] == self.nbSuspectMoveFromThisRoom(room) and room in self.possible_answer):
                    reachable_empty_room.append(room)



        fantom_logger.debug(f"reachable_empty_room :{reachable_empty_room}   room_with_one_suspect:{room_with_one_suspect}  room_with_mult_suspect: {room_with_mult_suspect} with a total of : {total_suspect_grouped}")
        fantom_logger.debug(f"{self.possible_answer}")
        # if there is more isolated suspect than grouped suspect
        if (len(room_with_one_suspect) > total_suspect_grouped and len(reachable_empty_room) > 0):
            #if the shadow room is reachable
            #and there is multiple suspect in the shadow room
            #and the blue character will not be played later this turn
            if ((self.game_state["shadow"] in self.possible_answer) and self.getSuspecNbInRoom(self.game_state["shadow"]) > 1 and "grey" not in self.getActiveCardsColors()):
                self.response_index = self.possible_answer.index(self.game_state["shadow"])
            elif (len(reachable_empty_room) > 0):
                self.response_index = self.possible_answer.index(choice(reachable_empty_room))
            else:
                randint(0, len(self.possible_answer) - 1)
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
            else:
                if (status["charact_nb"] > self.nbSuspectMoveFromThisRoom(room)):
                    reachable_filled_room.append(room)
                else:
                    reachable_empty_room.append(room)


        if (self.game_state["shadow"] in reachable_filled_room and "grey" not in self.getActiveCardsColors()):
            reachable_filled_room.remove(self.game_state["shadow"])
            reachable_empty_room.append(self.game_state["shadow"])

        fantom_logger.debug(f"reachable_empty_room :{reachable_empty_room}  reachable_filled_room: {reachable_filled_room} shadow room: {self.game_state['shadow']}")
        fantom_logger.debug(f"""fantom can scream ?:{phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]}""")

        # if the phantom can scream
        if (phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]):
            if (self.game_state["shadow"] in self.possible_answer and "grey" not in self.getActiveCardsColors()):
                self.response_index = self.possible_answer.index(self.game_state["shadow"])
            if (len(reachable_empty_room) > 0):
                self.response_index = self.possible_answer.index(choice(reachable_empty_room))
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
            if status["charact_nb"] == status["suspect_nb"] == 1 and self.nbSuspectMoveFromThisRoom(room) == 0: reachable_suspect_room.append(room)

        fantom_logger.debug(f"reachable_empty_or_innocent_room :{reachable_empty_or_innocent_room}  reachable_suspect_room: {reachable_suspect_room} shadow room: {self.game_state['shadow']}")
        fantom_logger.debug(f"""fantom can scream ?:{phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]}""")

        # if the phantom can scream
        if (phantom_status["charact_nb"] == 1 or phantom["position"] == self.game_state["shadow"]):
            if (self.game_state["shadow"] in self.possible_answer and "grey" not in self.getActiveCardsColors()):
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
        if (self.selected_character["color"] == "purple"):
            if (self.selected_character["color"] == self.game_state["fantom"] and self.game_state["num_tour"] == 1):
                self.response_index = 0
            else:
                self.response_index = 1 if (self.selectPurplePower(True)) else 0
        elif (self.selected_character["color"] == "black"):
            self.response_index = 1 if self.selectBlackPower() else 0
        elif (self.selected_character["color"] == "white"):
            self.response_index = 1 if self.selectWhitePower(True) else 0
        elif (self.selected_character["color"] == "brown"):
            self.response_index = 1 if self.selectBrownPower(True) else 0
        else:
            self.response_index = 0

    def selectPurplePowerPhantom(self, checkIfUsable=False):
        reachable_empty_room = []
        room_with_one_suspect = []
        total_suspect_grouped = 0

        fantom_logger.debug(self.possible_answer)
        for room in range(0, 10):
            status = self.getRoomStatus(room)
            fantom_logger.debug(status)
            if status["charact_nb"] == 0 and room in self.possible_answer: reachable_empty_room.append(room)
            if status["charact_nb"] == 1 and status["suspect_nb"] == 1 and self.nbSuspectMoveFromThisRoom(room) == 0 : room_with_one_suspect.append(room)
            if status["suspect_nb"] > 1 and room != self.game_state["shadow"]:
                if (status["suspect_nb"] > self.nbSuspectMoveFromThisRoom(room)):
                    total_suspect_grouped += status["suspect_nb"]
                if (status["suspect_nb"] == self.nbSuspectMoveFromThisRoom(room) + 1):
                    room_with_one_suspect.append(room)
                if (status["suspect_nb"] == self.nbSuspectMoveFromThisRoom(room)):
                    reachable_empty_room.append(room)

            if (len(room_with_one_suspect) > total_suspect_grouped):
                for charac in self.game_state["characters"]:
                    if (charac["suspect"] == False and charac["color"] != "purple"):
                        status = self.getRoomStatus(charac["position"])
                        if (status["innocent_nb"] == status["charact_nb"] == 1):
                            if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                            return True
                        if (charac["position"] == self.game_state["shadow"]):
                            if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                            return True
                return False #1.
            else:
                for charac in self.game_state["characters"]:
                    if (charac["suspect"] == False and charac["color"] != "purple"):
                        status = self.getRoomStatus(charac["position"])
                        if (status["charact_nb"] > 1):
                            if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                            return True
                return False #2.

    def selectPurplePower(self, checkIfUsable=False):
        """
            Pruple: Can swap position with another character
                     1. Useless when phantom can scream -> purple not innocent but no innocent alone or no innocent in dark
                     2. Useless when phantom cannot scream -> purple not innocent but no group
                     3. Useless when phantom can scream -> purple innocent and alone or in shadow but no grouped suspect outside shadow
                     4. Useless when phantom can scream -> purple innocent and not alone
                     5. Useless when phantom cannot scream -> purple innocent alone
                     6. Useless when phantom cannot scream -> purple innocent not alone but no suspect alone
        """
        if (self.selected_character["color"] == self.game_state["fantom"]):
            self.selectPurplePowerPhantom(checkIfUsable)
        elif (self.selected_character["suspect"]):
            if (self.phantomCanScream()):
                for charac in self.game_state["characters"]:
                    if (charac["suspect"] == False and charac["color"] != "purple"):
                        status = self.getRoomStatus(charac["position"])
                        if (status["innocent_nb"] == status["charact_nb"] == 1):
                            if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                            return True
                        if (charac["position"] == self.game_state["shadow"]):
                            if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                            return True
                return False #1.
            else:
                for charac in self.game_state["characters"]:
                    if (charac["suspect"] == False and charac["color"] != "purple"):
                        status = self.getRoomStatus(charac["position"])
                        if (status["charact_nb"] > 1):
                            if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                            return True
                return False #2.

        else:
            p_status = self.getRoomStatus(self.selected_character["position"])
            if (self.phantomCanScream()):
                if (p_status["charact_nb"] == 1 or self.selected_character["position"] == self.game_state["shadow"]):
                    for charac in self.game_state["characters"]:
                        if (charac["suspect"] == True and charac["color"] != "purple"):
                            status = self.getRoomStatus(charac["position"])
                            if (status["charact_nb"] > 1 and charac["position"] != self.game_state["shadow"]):
                                if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                                return True
                    return False #3.
                else:
                    return False #4.
            else:
                if (p_status["charact_nb"] == 1 or self.selected_character["position"] == self.game_state["shadow"]):
                    return False #5.
                else:
                    for charac in self.game_state["characters"]:
                        if (charac["suspect"] == True and charac["color"] != "purple"):
                            status = self.getRoomStatus(charac["position"])
                            if (status["charact_nb"] == 1 or charac["position"] == self.game_state["shadow"]):
                                if (checkIfUsable == False): self.response_index = self.possible_answer.index(charac["color"])
                                return True
                    return False #6.

    def selectBrownPower(self, checkIfUsable=False):
        """
            Brown: Move other characters with him
            1. Useless when phantom can scream -> Brown cannot reach shadow
            A. Usefull when phantom can scream -> Brown can reach shadow
            B. Usefull when phantom cannot scream
        """
        if (checkIfUsable == False):
            if (self.game_state["fantom"] in self.possible_answer):
                self.response_index = self.possible_answer.index(self.game_state["fantom"])
            else:
                sus_list = []
                for col in self.possible_answer:
                    if (self.getCharacterByColor(col)["suspect"] == True):
                        sus_list.append(col)
                if (len(sus_list) > 0):
                    self.response_index = self.possible_answer.index(choice(sus_list))
                else:
                    self.response_index = randint(0, len(self.possible_answer) - 1)

        else:
            if (self.phantomCanScream()):
                if (self.game_state["shadow"] in self.getPossibleMovement(self.selected_character)):
                    return True #A.
                return False #1.
            else:
                return True #B.

    def selectGreyPower(self):
        """
            Grey: Move the 'Electrical problem' token
        """
        empty_room = []
        room_with_one_suspect = []
        room_with_mult_suspect = []
        total_suspect_grouped = 0
        room_with_most_sus = 0
        most_sus = 0
        phantom = self.getPhantom()
        phantom_status = self.getRoomStatus(phantom["position"])
        for room in range(0, 10):
            status = self.getRoomStatus(room)
            fantom_logger.debug(status)
            if status["charact_nb"] == 0 : empty_room.append(room)
            if status["charact_nb"] == 1 and status["suspect_nb"] == 1 : room_with_one_suspect.append(room)
            if status["suspect_nb"] > 1:
                if (status["suspect_nb"] > most_sus and room != self.game_state["shadow"]) :
                    most_sus = status["suspect_nb"]
                    room_with_most_sus = room
                room_with_mult_suspect.append(room)
                total_suspect_grouped += status["suspect_nb"]

        if (phantom_status["charact_nb"] == 1) :
            if (most_sus != 0):
                self.response_index = self.possible_answer.index(room_with_most_sus)
            else:
                self.response_index = randint(0, len(self.possible_answer) - 1)
        else:
            tsg = total_suspect_grouped - phantom_status["suspect_nb"] #suspect grouped minus suspect with phantom
            tsa = len(room_with_one_suspect) + phantom_status["suspect_nb"] #suspect alone plus suspect with phantom
            if (phantom["position"] != self.game_state["shadow"] and tsa > tsg):
                self.response_index = self.possible_answer.index(phantom["position"])
            else:
                other_room = empty_room + room_with_one_suspect
                if (self.game_state["shadow"] in other_room): other_room.remove(self.game_state["shadow"])
                if (len(other_room) > 0):
                    self.response_index = self.possible_answer.index(choice(other_room))
                else:
                    if (phantom["position"] in self.possible_answer): self.possible_answer.remove(phantom["position"])
                    self.response_index =  self.possible_answer.index(choice(self.possible_answer))

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

    def selectWhitePower(self, checkIfUsable=False):
        """
            White: Move the other characters from the room
            1. Useless when white is alone
            2. Useless when phantom cannot scream -> suspect and not alone
            3. Usefull when phantom cannot scream -> white is not suspect and no alone suspect in adjacent room

            A. Usefull when phantom can scream -> White is suspect and not alone and not in dark
            B. Usefull when phantom can scream -> White is not suspect and not alone and not in dark
            C. Usefull when phantom cannot scream -> white is not suspect and have alone suspect in adjacent room
        """
        if (checkIfUsable == False):
            to_move = self.question.replace("white character power move ", "")
            fantom_logger.debug(to_move)
            char_to_move = self.getCharacterByColor(to_move)
            empty_room = []
            filled_room = []
            alone_suspect = []
            for room in self.possible_answer:
                status = self.getRoomStatus(room)
                if (status["charact_nb"] == 0 or room == self.game_state["shadow"]): empty_room.append(room)
                else: filled_room.append(room)
                if (status["charact_nb"] == status["suspect_nb"] == 1): alone_suspect.append(room)

            if (self.phantomCanScream()):
                if (char_to_move["suspect"] == True and len(empty_room) > 0):
                    self.response_index = self.possible_answer.index(choice(empty_room)) #A. B.
                elif(char_to_move["suspect"] == False and len(filled_room) > 0):
                    self.response_index = self.possible_answer.index(choice(filled_room)) #A. B.
                else:
                    self.response_index = randint(0, len(self.possible_answer) - 1) #A. B.
            else:
                if (len(alone_suspect) > 0):
                    self.response_index = self.possible_answer.index(choice(filled_room)) #C.
                else:
                    self.response_index = randint(0, len(self.possible_answer) - 1) #not susposed to happen (just for security)

        else:
            if (self.getRoomStatus(self.selected_character["position"])["charact_nb"] == 1):
                return False #1.
            if (self.phantomCanScream() and self.selected_character["position"] != self.game_state["shadow"]):
                return True #A. B.
            else:
                if (self.selected_character["suspect"] == False) :
                    for room in self.getAdjacentRooms(self.selected_character):
                        status = self.getRoomStatus(room)
                        if (status["charact_nb"] == status["suspect_nb"] == 1):
                            return True #C.
                return False #2. 3.

    def selectBlackPower(self):
        """
            Black: Move the other characters to the room
            1. Useless when phantom can scream -> Black is not in shadow
            2. Useless when phantom cannot scream -> black in shadow
            A. Usefull when phantom can scream -> Black is in shadow
            B. Usefull when phantom cannot scream -> Black is not in shadow
        """
        if (self.phantomCanScream()):
            if (self.selected_character["position"] == self.game_state["shadow"]):
                return True #A.
            return False #1.
        else:
            if (self.selected_character["position"] == self.game_state["shadow"]):
                return False #2.
            return True #B.

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
