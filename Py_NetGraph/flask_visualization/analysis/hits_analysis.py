import numpy as np
import networkx as nx
from datetime import datetime, timedelta
from database import fetch_data

def hits_algorithm(G, max_iter=100, tol=1e-8):
    """
    计算用户消息交互网络中的 HITS 算法，得到 hub 和 authority 分数。
    """
    users = list(G.nodes())
    num_users = len(users)
    if num_users == 0:
        return {}, {}

    user_index = {user: i for i, user in enumerate(users)}
    index_user = {i: user for user, i in user_index.items()}

    hub_values = np.ones(num_users)
    authority_values = np.ones(num_users)

    adjacency_matrix = np.zeros((num_users, num_users))
    for sender, receiver, data in G.edges(data=True):
        if sender in user_index and receiver in user_index:
            adjacency_matrix[user_index[sender], user_index[receiver]] = data.get("weight", 1)

    adjacency_matrix_T = adjacency_matrix.T

    for _ in range(max_iter):
        new_authority_values = np.dot(adjacency_matrix_T, hub_values)
        new_hub_values = np.dot(adjacency_matrix, authority_values)

        norm_authority = np.linalg.norm(new_authority_values, 2)
        norm_hub = np.linalg.norm(new_hub_values, 2)

        if norm_authority > 0:
            new_authority_values /= norm_authority
        if norm_hub > 0:
            new_hub_values /= norm_hub

        diff = np.linalg.norm(new_hub_values - hub_values, 2) + np.linalg.norm(new_authority_values - authority_values, 2)
        hub_values, authority_values = new_hub_values, new_authority_values

        if diff < tol:
            break

    hub_scores = {index_user[i]: round(hub_values[i], 6) for i in range(num_users)}
    authority_scores = {index_user[i]: round(authority_values[i], 6) for i in range(num_users)}

    return hub_scores, authority_scores

def analyze_messages_hits(days=30):
    """
    分析用户消息交互数据，计算 HITS 算法的 hub 和 authority 值。
    """
    start_time = datetime.now() - timedelta(days=days)
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    query_messages = f"""
        SELECT m.sender_id, u1.username AS sender_name,
               m.receiver_id, u2.username AS receiver_name,
               COUNT(*) as weight
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        WHERE m.timestamp >= '{start_time_str}'
        GROUP BY m.sender_id, m.receiver_id
    """
    df_messages = fetch_data(query_messages)

    if df_messages.empty:
        print("⚠️ 没有消息交互数据")
        return {}, {}, {}, {}, df_messages

    message_graph = nx.DiGraph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    if not user_map:
        print("⚠️ 用户数据为空")
        return {}, {}, {}, {}, df_messages

    for _, row in df_messages.iterrows():
        message_graph.add_edge(int(row["sender_id"]), int(row["receiver_id"]), weight=float(row["weight"]))

    if not message_graph.edges:
        print("⚠️ 没有有效的消息交互")
        return {}, {}, user_map, {}, df_messages

    print(f"📊 消息网络包含 {message_graph.number_of_nodes()} 个用户, {message_graph.number_of_edges()} 条消息交互")

    communities = list(nx.weakly_connected_components(message_graph))
    print(f"🔍 发现 {len(communities)} 个独立社交社区")

    hub_scores, authority_scores, community_ids = {}, {}, {}

    for i, community in enumerate(communities):
        subgraph = message_graph.subgraph(community).copy()
        print(f"📌 计算社区 {i+1}, 包含 {subgraph.number_of_nodes()} 个用户, {subgraph.number_of_edges()} 条消息交互")

        sub_hub_scores, sub_authority_scores = hits_algorithm(subgraph)

        hub_scores.update(sub_hub_scores)
        authority_scores.update(sub_authority_scores)

        for user in community:
            community_ids[user] = i

    return hub_scores, authority_scores, user_map, community_ids, df_messages

def get_messages_hits_data(days=30):
    """
    获取用户消息交互数据，包括 hub、authority 和 community_id，用于前端可视化。
    """
    hub_scores, authority_scores, user_map, community_ids, df_messages = analyze_messages_hits(days)

    nodes = [
        {
            "id": int(user_id),
            "username": user_map[user_id],
            "authority": authority_scores.get(user_id, 0),
            "hub": hub_scores.get(user_id, 0),
            "size": int((authority_scores.get(user_id, 0) + hub_scores.get(user_id, 0)) * 1000),
            "community_id": community_ids.get(user_id, -1)
        }
        for user_id in user_map.keys()
    ]

    edges = [
        {"source": int(row["sender_id"]), "target": int(row["receiver_id"]), "weight": float(row["weight"])}
        for _, row in df_messages.iterrows()
    ]

    return {"nodes": nodes, "edges": edges}
