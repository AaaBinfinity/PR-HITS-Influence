"""
消息分析相关
"""

import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from database import fetch_data


def analyze_messages():
    """
    获取消息互动数据并计算社交网络图的节点属性，包含所有用户。
    主要计算用户活跃度（发送和接收的消息数），并生成适用于可视化的 JSON 结构。

    Returns:
        dict: 包含节点（用户）和边（消息互动）的数据，适用于前端可视化。
    """
    # 查询所有用户信息
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    # 查询近一个月的消息互动数据
    query_messages = """
        SELECT m.sender_id, u1.username AS sender_name,
               m.receiver_id, u2.username AS receiver_name,
               COUNT(*) as weight
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        WHERE m.timestamp >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        GROUP BY m.sender_id, m.receiver_id
    """
    df_messages = fetch_data(query_messages)

    # 构建有向图
    G = nx.DiGraph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    # 添加边（消息发送和接收）
    for _, row in df_messages.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"], weight=row["weight"])

    # 计算每个用户的活跃度（出度+入度的加权和）
    node_activity = {
        node: sum(d["weight"] for _, _, d in G.edges(node, data=True))
        for node in G.nodes()
    }

    # 确保所有用户都包含，即使没有发送或接收消息
    for user_id in user_map.keys():
        if user_id not in node_activity:
            node_activity[user_id] = 0  # 没有消息记录

    # 计算活跃度范围
    activity_values = list(node_activity.values())
    vmin, vmax = min(activity_values), max(activity_values)

    # 🎨 颜色划分（按活跃度分层）
    bins = np.linspace(vmin, vmax, 6)  # 6个颜色层级
    colors = [cm.viridis(i / 5) for i in range(6)]

    # 为每个用户分配颜色（活跃度越高颜色越深）
    node_colors = [
        mcolors.to_hex(colors[np.digitize(node_activity[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    # 为每个节点分配大小（映射到 1000 ~ 6000）
    node_sizes = [
        np.interp(node_activity[user_id], (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON 结构的节点数据
    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": node_sizes[i],
        "color": node_colors[i],
        "activity": node_activity[user_id]
    } for i, user_id in enumerate(user_map.keys())]

    # 构造 JSON 结构的边数据（消息互动）
    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}

def analyze_friend_distribution():
    """
    计算好友数量的分布，并返回 JSON 结果。
    统计每个用户的好友数量，计算均值和中位数，并分配可视化颜色。

    Returns:
        dict: 包含好友数据和统计信息（均值与中位数）。
    """
    # 查询好友关系数据
    query = """
        SELECT f.user_id, u.username AS user_name
        FROM friends f
        JOIN users u ON f.user_id = u.id
    """
    df_friends = fetch_data(query)

    # 计算每个用户的好友数量
    friend_counts = df_friends["user_id"].value_counts()

    # 计算均值和中位数
    mean_friends = friend_counts.mean()
    median_friends = friend_counts.median()

    # 颜色映射（按好友数量分层）
    bins = np.linspace(friend_counts.min(), friend_counts.max(), 6)
    colors = [cm.Blues(i / 5) for i in range(6)]  # 6 级颜色
    color_map = {
        count: mcolors.to_hex(colors[np.digitize(count, bins) - 1])
        for count in friend_counts
    }

    # 构造 JSON 结构的好友数据
    friend_data = [
        {"user_id": int(user), "friend_count": int(count), "color": color_map[count]}
        for user, count in friend_counts.items()
    ]

    return {
        "friend_data": friend_data,
        "stats": {"mean_friends": mean_friends, "median_friends": median_friends}
    }
