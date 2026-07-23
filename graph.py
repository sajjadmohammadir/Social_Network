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
        suggestions = {}  

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




    def users_with_most_friends(self):
        
        if not self.users:
            return []

        max_friends = max(len(friends) for friends in self.adjacency.values())

        return [
            {
                "id": uid,
                "name": self.users[uid],
                "friend_count": len(self.adjacency[uid])
            }
            for uid in self.users
            if len(self.adjacency[uid]) == max_friends
        ]



    def mutual_friends(self, id1, id2):

        if id1 not in self.users or id2 not in self.users:
            return []

        mutual = self.adjacency.get(id1, set()) & self.adjacency.get(id2, set())
        return [
            {"id": mid, "name": self.users[mid]}
            for mid in mutual
        ]


    def network_stats(self):

        total_users = len(self.users)
        total_edges = sum(len(f) for f in self.adjacency.values()) // 2
        avg_relations = (2 * total_edges / total_users) if total_users > 0 else 0

        groups = self.find_groups()
        largest_group = groups[0] if groups else []

        most_connected = None
        max_friends = -1
        for uid in self.users:
            count = len(self.adjacency[uid])
            if count > max_friends:
                max_friends = count
                most_connected = {"id": uid, "name": self.users[uid], "friend_count": count}

        return {
            "total_users": total_users,
            "total_friendships": total_edges,
            "avg_relationships": round(avg_relations, 2),
            "largest_group": largest_group,
            "largest_group_size": len(largest_group),
            "most_connected_user": most_connected,
            "num_groups": len(groups)
        }



    def distances_from_user(self, user_id):
        if user_id not in self.users:
            return []

        distances = {}
        visited = {user_id}
        queue = deque([(user_id, 0)])

        while queue:
            current, dist = queue.popleft()
            distances[current] = dist
            for neighbor in self.adjacency.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

        result = []
        for uid in self.users:
            if uid != user_id:
                dist = distances.get(uid, float('inf'))
                result.append({
                    "id": uid,
                    "name": self.users[uid],
                    "distance": dist if dist != float('inf') else "∞ (unreachable)"
                })

        def sort_key(item):
            d = item["distance"]
            if d == "∞ (unreachable)":
                return (1, 0)
            return (0, d)

        result.sort(key=sort_key)
        return result

    def find_key_person(self):

        if len(self.users) < 3:
            return None

        centrality = {uid: 0.0 for uid in self.users}

        for source in self.users:
            
            distances = {}
            sigma = {uid: 0 for uid in self.users}
            predecessors = {uid: [] for uid in self.users}
            sigma[source] = 1
            distances[source] = 0
            queue = deque([source])
            order = []  # BFS order

            while queue:
                current = queue.popleft()
                order.append(current)
                for neighbor in self.adjacency.get(current, set()):
                    
                    if neighbor not in distances:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)
                    
                    if distances.get(neighbor) == distances[current] + 1:
                        sigma[neighbor] += sigma[current]
                        predecessors[neighbor].append(current)

           
            dependency = {uid: 0.0 for uid in self.users}
            
           
            for w in reversed(order):
                for v in predecessors[w]:
                    if sigma[w] > 0:
                        dependency[v] += (sigma[v] / sigma[w]) * (1 + dependency[w])
                if w != source:
                    centrality[w] += dependency[w]

        
        if len(self.users) > 2:
            norm = 1.0 / ((len(self.users) - 1) * (len(self.users) - 2))
            for uid in centrality:
                centrality[uid] *= norm

        
        key_person_id = max(centrality, key=centrality.get)
        return {
            "id": key_person_id,
            "name": self.users[key_person_id],
            "centrality_score": round(centrality[key_person_id], 4),
            "friend_count": len(self.adjacency[key_person_id])
        }

    def detect_communities(self):

        if not self.users:
            return []


        communities = {uid: i for i, uid in enumerate(self.users)}
        total_edges = sum(len(f) for f in self.adjacency.values()) // 2
        
        if total_edges == 0:
            return [{"community": 0, "members": [
                {"id": uid, "name": self.users[uid]} for uid in self.users
            ]}]

        changed = True
        iterations = 0
        max_iterations = 100

        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            
            for uid in self.users:
                best_community = communities[uid]
                best_gain = 0
                
                neighbor_communities = set()
                for friend in self.adjacency.get(uid, set()):
                    neighbor_communities.add(communities[friend])
                
                for comm in neighbor_communities:
                    if comm == communities[uid]:
                        continue
                    
                    edges_to_comm = sum(
                        1 for f in self.adjacency.get(uid, set())
                        if communities[f] == comm
                    )
                    
                    current_comm_edges = sum(
                        1 for f in self.adjacency.get(uid, set())
                        if communities[f] == communities[uid]
                    )
                    
                    gain = edges_to_comm - current_comm_edges
                    if gain > best_gain:
                        best_gain = gain
                        best_community = comm
                
                if best_community != communities[uid]:
                    communities[uid] = best_community
                    changed = True

        community_groups = {}
        for uid, comm_id in communities.items():
            if comm_id not in community_groups:
                community_groups[comm_id] = []
            community_groups[comm_id].append({
                "id": uid,
                "name": self.users[uid]
            })

        return [
            {"community_id": cid, "members": members, "size": len(members)}
            for cid, members in community_groups.items()
        ]



    def optimal_spread(self, k):
      
        if not self.users:
            return {"selected_users": [], "spread_details": []}

        k = min(k, len(self.users))
        selected = []
        remaining = set(self.users.keys())

        for _ in range(k):
            best_user = None
            best_new_reach = -1

            for candidate in remaining:
             
                test_set = set(selected) | {candidate}
                reached = self._simulate_spread(test_set)
                new_reach = len(reached)
                
                if new_reach > best_new_reach:
                    best_new_reach = new_reach
                    best_user = candidate

            if best_user:
                selected.append(best_user)
                remaining.discard(best_user)


        spread_info = self._simulate_spread_detailed(selected)

        return {
            "selected_users": [
                {"id": uid, "name": self.users[uid]} for uid in selected
            ],
            "total_reached": spread_info["total_reached"],
            "rounds_needed": spread_info["rounds"],
            "spread_details": spread_info["details"]
        }

    def _simulate_spread(self, seed_users):
        """Simulate information spread from seed users. Time: O(V + E)"""
        reached = set(seed_users)
        current_layer = set(seed_users)
        
        while current_layer:
            next_layer = set()
            for user in current_layer:
                for friend in self.adjacency.get(user, set()):
                    if friend not in reached:
                        reached.add(friend)
                        next_layer.add(friend)
            current_layer = next_layer
        
        return reached

    def _simulate_spread_detailed(self, seed_users):
        """Simulate spread with round-by-round details. Time: O(V + E)"""
        reached = set(seed_users)
        current_layer = set(seed_users)
        details = [{"round": 0, "newly_informed": [
            {"id": uid, "name": self.users[uid]} for uid in seed_users
        ]}]
        round_num = 0

        while current_layer:
            round_num += 1
            next_layer = set()
            for user in current_layer:
                for friend in self.adjacency.get(user, set()):
                    if friend not in reached:
                        reached.add(friend)
                        next_layer.add(friend)
            
            if next_layer:
                details.append({
                    "round": round_num,
                    "newly_informed": [
                        {"id": uid, "name": self.users[uid]} for uid in next_layer
                    ]
                })
            current_layer = next_layer

        return {
            "total_reached": len(reached),
            "rounds": round_num,
            "details": details
        }