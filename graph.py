import json
import os
from collections import deque


class SocialGraph:
    
    def __init__(self):
        self.users = {}     
        self.adjacency = {}   
        self._next_id = 1


    def add_user(self, name):

        user_id = str(self._next_id)
        self._next_id += 1
        self.users[user_id] = name
        self.adjacency[user_id] = set()
        return user_id

    def remove_user(self, user_id):

        if user_id not in self.users:
            return False
        for friend_id in list(self.adjacency.get(user_id, [])):
            self.adjacency[friend_id].discard(user_id)

        del self.adjacency[user_id]
        del self.users[user_id]
        return True

    def add_friendship(self, id1, id2):

        if id1 not in self.users or id2 not in self.users:
            return False
        if id1 == id2:
            return False
        self.adjacency[id1].add(id2)
        self.adjacency[id2].add(id1)
        return True

    def remove_friendship(self, id1, id2):

        if id1 in self.adjacency and id2 in self.adjacency:
            self.adjacency[id1].discard(id2)
            self.adjacency[id2].discard(id1)
            return True
        return False

    def update_user(self, user_id, new_name):

        if user_id in self.users:
            self.users[user_id] = new_name
            return True
        return False
