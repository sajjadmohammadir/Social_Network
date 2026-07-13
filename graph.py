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



    def get_friends(self, user_id):
        
        if user_id not in self.users:
            return []
        return [
            {"id": fid, "name": self.users[fid]}
            for fid in self.adjacency.get(user_id, set())
        ]

    def are_connected(self, id1, id2):
        
        if id1 not in self.users or id2 not in self.users:
            return False
        return id2 in self.adjacency.get(id1, set())

    def are_reachable(self, id1, id2):
        
        if id1 not in self.users or id2 not in self.users:
            return False
        if id1 == id2:
            return True
        
        visited = set()
        queue = deque([id1])
        visited.add(id1)
        
        while queue:
            current = queue.popleft()
            if current == id2:
                return True
            for neighbor in self.adjacency.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False



    def shortest_path(self, id1, id2):
        
        if id1 not in self.users or id2 not in self.users:
            return []
        if id1 == id2:
            return [id1]

        visited = {id1}
        queue = deque([(id1, [id1])])

        while queue:
            current, path = queue.popleft()
            for neighbor in self.adjacency.get(current, set()):
                if neighbor == id2:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def shortest_path_with_names(self, id1, id2):
        path_ids = self.shortest_path(id1, id2)
        return [
            {"id": uid, "name": self.users.get(uid, "Unknown")}
            for uid in path_ids
        ]




    def suggest_friends(self, user_id):
        
        if user_id not in self.users:
            return []

        direct_friends = self.adjacency.get(user_id, set())
        suggestions = {}  # {candidate_id: mutual_count}

        for friend_id in direct_friends:
            for fof in self.adjacency.get(friend_id, set()):
                if fof != user_id and fof not in direct_friends:
                    suggestions[fof] = suggestions.get(fof, 0) + 1

        
        sorted_suggestions = sorted(
            suggestions.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {
                "id": sid,
                "name": self.users[sid],
                "mutual_friends": count,
                "mutual_names": [
                    self.users[f]
                    for f in direct_friends
                    if sid in self.adjacency.get(f, set())
                ]
            }
            for sid, count in sorted_suggestions
        ]

   

    def find_groups(self):
        
        visited = set()
        groups = []

        for user_id in self.users:
            if user_id not in visited:
                group = []
                stack = [user_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        group.append({
                            "id": current,
                            "name": self.users[current]
                        })
                        for neighbor in self.adjacency.get(current, set()):
                            if neighbor not in visited:
                                stack.append(neighbor)
                groups.append(group)

        
        groups.sort(key=len, reverse=True)
        return groups