#!/usr/bin/env python3


import json

from typing import Tuple
from random import randint, choice
from globals import passages, colors, pink_passages, before, after, logger, mandatory_powers



class BasePlayer():

    def __init__(self):
        self.data = {}
        self.question = {}
        self.possible_answer = {}
        self.game_state = {}

    def getActiveCards(self):
        return self.game_state["active character_cards"]

    def getActiveCardsColors(self):
        return [elem["color"] for elem in self.game_state["active character_cards"]]

    def getIndexOfColor(self, color):
        return self.getActiveCardsColors().index(color)

    def getAdjacentRooms(self, charact):
        if charact["color"] == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[charact["position"]] if set([room, charact["position"]]) != set(self.game_state["blocked"])]

    def getAdjacentRoomsByRoomNb(self, roomNb, charact):
        if charact["color"] == "pink":
            active_passages = pink_passages
        else:
            active_passages = passages
        return [room for room in active_passages[roomNb] if set([room, roomNb]) != set(self.game_state["blocked"])]


    def getCharacterNbInRoom(self, roomNb):
        return len([charact for charact in self.game_state["characters"] if charact["position"] == roomNb])

    def getSuspecNbtInRoom(self, roomNb):
        return len([charact for charact in self.game_state["characters"] if charact["position"] == roomNb and charact["suspect"] == True])

    def getInnocentNbInRoom(self, roomNb):
        return len([charact for charact in self.game_state["characters"] if charact["position"] == roomNb and charact["suspect"] == False])

    def getCharactersInRoom(self, roomNb):
        return [charact for charact in self.game_state["characters"] if charact["position"] == roomNb]


    def getPossibleMovement(self, charact):
        nbCharact = self.getNbOfCharacterInRoom(charact["position"])

        big_room_list = [self.getAdjacentRooms(charact)]
        for i in range(1, nbCharact):
            tmp_rooms = []
            for roomNb in big_room_list[i-1]:
                tmp_rooms += self.getAdjacentRoomsByRoomNb(roomNb, charact)
            big_room_list.append(tmp_rooms)

        room_list = []
        for l in big_room_list:
            for r in l:
                room_list.append(r)

        room_list = list(set(room_list))
        if charact["position"] in room_list:
            room_list.remove(charact["position"])
        return room_list

    def getRoomStatus(self, roomNb):
        status = {}
        status["roomNb"] = roomNb
        status["charact_nb"] = self.getCharacterNbInRoom(roomNb)
        status["innocent_nb"] = self.getInnocentNbInRoom(roomNb)
        status["suspect_nb"] = self.getSuspecNbtInRoom(roomNb)
        status["new_innocent_if_no_scream"] = (1 if (status["charact_nb"] == status["suspect_nb"] == 1) else 0) if (self.game_state["shadow"] != roomNb) else status["suspect_nb"]
        status["new_innocent_if_scream"] = (status["suspect_nb"] if (status["charact_nb"] > 1) else 0) if (self.game_state["shadow"] != roomNb) else 0
        return status

    def getGameStatus(self) :
        status_list = []
        tniins = 0
        tniis = 0
        ti = 0
        ts = 0
        for i in range(0, 9):
            tmp_status = self.getRoomStatus(i)
            tniins += tmp_status["new_innocent_if_no_scream"]
            tniis += tmp_status["new_innocent_if_scream"]
            ti += tmp_status["innocent_nb"]
            ts += tmp_status["suspect_nb"]
            status_list.append(tmp_status)
        status = {}
        status["total_innocent"] = ti
        status["total_suspect"] = ts
        status["total_new_innocent_if_no_scream"] = tniins
        status["total_new_innocent_if_scream"] = tniis
        status["rooms"] = status_list
        return status
