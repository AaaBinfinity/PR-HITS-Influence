"""
用户中心性分析相关
"""
import colorsys
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from community import community_louvain
from database import fetch_data


def analyze_centrality():
    """计算用户中心性（接收消息的数量）"""
    # 查询所有用户信息
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)


    # 查询消息数据，计算每个用户接收到的消息数量
    query_messages = """
        SELECT m.sender_id, u1.username AS sender_name,
               m.receiver_id, u2.username AS receiver_name,
               COUNT(*) AS weight
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        WHERE m.timestamp >= DATE_SUB(NOW(), INTERVAL 1 MONTH)  -- 仅查询最近 1 个月的数据
        GROUP BY m.sender_id, m.receiver_id
    """
    df_messages = fetch_data(query_messages)

    # 构建有向图
    G = nx.DiGraph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    # 添加边（消息数据）
    for _, row in df_messages.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"], weight=row["weight"])

    # 计算每个用户的中心性（接收消息的数量）
    node_centrality = {node: sum(d["weight"] for _, _, d in G.in_edges(node, data=True)) for node in G.nodes()}

    # 确保所有用户都包含，即使没有接收消息
    for user_id in user_map.keys():
        if user_id not in node_centrality:
            node_centrality[user_id] = 0

    centrality_values = list(node_centrality.values())
    vmin, vmax = min(centrality_values), max(centrality_values)

    # 🎨 颜色划分
    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.viridis(i / 5) for i in range(6)]

    # 为每个节点分配颜色
    node_colors = [
        mcolors.to_hex(colors[np.digitize(node_centrality[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    # 为每个节点分配大小
    node_sizes = [
        np.interp(node_centrality[user_id], (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON 格式的节点数据
    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": node_sizes[i],
        "color": node_colors[i],
        "centrality": node_centrality[user_id]
    } for i, user_id in enumerate(user_map.keys())]

    # 构造边数据
    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}
