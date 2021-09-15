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
