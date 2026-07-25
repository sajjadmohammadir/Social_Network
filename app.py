"""
Social Network Analysis - Web Application
Flask-based GUI for the social network graph.
"""

from flask import Flask, render_template, request, jsonify
from graph import SocialGraph
import os

app = Flask(__name__)
graph = SocialGraph()

DATA_FILE = os.path.join(os.path.dirname(__file__), "social_network.json")


def save():
    graph.save_to_json(DATA_FILE)


def load():
    if os.path.exists(DATA_FILE):
        graph.load_from_json(DATA_FILE)
    else:
        graph.load_example()
        save()


# =====================================================
# PAGE ROUTES
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")


# =====================================================
# API ROUTES
# =====================================================

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(graph.get_all_users())


@app.route("/api/users", methods=["POST"])
def api_add_user():
    data = request.json
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    uid = graph.add_user(name)
    save()
    return jsonify({"id": uid, "name": name})


@app.route("/api/users/<user_id>", methods=["PUT"])
def api_update_user(user_id):
    data = request.json
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Name is required"}), 400
    if graph.update_user(user_id, name):
        save()
        return jsonify({"success": True})
    return jsonify({"error": "User not found"}), 404


@app.route("/api/users/<user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    if graph.remove_user(user_id):
        save()
        return jsonify({"success": True})
    return jsonify({"error": "User not found"}), 404


@app.route("/api/friendships", methods=["POST"])
def api_add_friendship():
    data = request.json
    id1, id2 = data.get("user1"), data.get("user2")
    if graph.add_friendship(id1, id2):
        save()
        return jsonify({"success": True})
    return jsonify({"error": "Invalid users"}), 400


@app.route("/api/friendships", methods=["DELETE"])
def api_remove_friendship():
    data = request.json
    id1, id2 = data.get("user1"), data.get("user2")
    if graph.remove_friendship(id1, id2):
        save()
        return jsonify({"success": True})
    return jsonify({"error": "Invalid users"}), 400


# =====================================================
# ANALYSIS API ROUTES
# =====================================================

@app.route("/api/friends/<user_id>", methods=["GET"])
def api_get_friends(user_id):
    """1. List friends of a user"""
    friends = graph.get_friends(user_id)
    return jsonify({
        "user": {"id": user_id, "name": graph.get_user_name(user_id)},
        "friends": friends,
        "count": len(friends)
    })


@app.route("/api/connected", methods=["GET"])
def api_are_connected():
    """2. Check if two users are connected"""
    id1 = request.args.get("user1")
    id2 = request.args.get("user2")
    if not id1 or not id2:
        return jsonify({"error": "Both user1 and user2 are required"}), 400
    direct = graph.are_connected(id1, id2)
    reachable = graph.are_reachable(id1, id2)
    return jsonify({
        "user1": {"id": id1, "name": graph.get_user_name(id1)},
        "user2": {"id": id2, "name": graph.get_user_name(id2)},
        "directly_connected": direct,
        "reachable": reachable
    })


@app.route("/api/shortest-path", methods=["GET"])
def api_shortest_path():
    """3. Find shortest path between two users"""
    id1 = request.args.get("user1")
    id2 = request.args.get("user2")
    if not id1 or not id2:
        return jsonify({"error": "Both user1 and user2 are required"}), 400
    path = graph.shortest_path_with_names(id1, id2)
    return jsonify({
        "user1": {"id": id1, "name": graph.get_user_name(id1)},
        "user2": {"id": id2, "name": graph.get_user_name(id2)},
        "path": path,
        "length": len(path) - 1 if path else "∞",
        "found": len(path) > 0
    })


@app.route("/api/suggest-friends/<user_id>", methods=["GET"])
def api_suggest_friends(user_id):
    """4. Suggest friends"""
    suggestions = graph.suggest_friends(user_id)
    return jsonify({
        "user": {"id": user_id, "name": graph.get_user_name(user_id)},
        "suggestions": suggestions
    })


@app.route("/api/groups", methods=["GET"])
def api_groups():
    """5. List groups"""
    groups = graph.find_groups()
    return jsonify({"groups": groups, "count": len(groups)})


@app.route("/api/most-friends", methods=["GET"])
def api_most_friends():
    """6. Users with most friends"""
    return jsonify({"users": graph.users_with_most_friends()})


@app.route("/api/mutual-friends", methods=["GET"])
def api_mutual_friends():
    """7. Mutual friends"""
    id1 = request.args.get("user1")
    id2 = request.args.get("user2")
    if not id1 or not id2:
        return jsonify({"error": "Both user1 and user2 are required"}), 400
    mutual = graph.mutual_friends(id1, id2)
    return jsonify({
        "user1": {"id": id1, "name": graph.get_user_name(id1)},
        "user2": {"id": id2, "name": graph.get_user_name(id2)},
        "mutual_friends": mutual,
        "count": len(mutual)
    })


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """8. Network statistics"""
    return jsonify(graph.network_stats())


@app.route("/api/distances/<user_id>", methods=["GET"])
def api_distances(user_id):
    """9. Distances from user to all others"""
    distances = graph.distances_from_user(user_id)
    return jsonify({
        "user": {"id": user_id, "name": graph.get_user_name(user_id)},
        "distances": distances
    })


@app.route("/api/key-person", methods=["GET"])
def api_key_person():
    """Bonus 1: Key person (betweenness centrality)"""
    result = graph.find_key_person()
    return jsonify({"key_person": result})


@app.route("/api/communities", methods=["GET"])
def api_communities():
    """Bonus 2: Community detection"""
    communities = graph.detect_communities()
    return jsonify({"communities": communities, "count": len(communities)})


@app.route("/api/spread", methods=["POST"])
def api_spread():
    """Bonus 3: Optimal information spread"""
    data = request.json
    k = data.get("k", 1)
    result = graph.optimal_spread(k)
    return jsonify(result)


@app.route("/api/load-example", methods=["POST"])
def api_load_example():
    """Load example network"""
    graph.load_example()
    save()
    return jsonify({"success": True, "users": graph.get_all_users()})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset the network"""
    graph.__init__()
    save()
    return jsonify({"success": True})


# =====================================================
# START
# =====================================================

if __name__ == "__main__":
    load()
    app.run(host="0.0.0.0", port=5000, debug=True)
