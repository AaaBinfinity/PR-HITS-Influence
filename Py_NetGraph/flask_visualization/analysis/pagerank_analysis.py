"""
PageRank
"""
from datetime import datetime, timedelta
import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from database import fetch_data


def analyze_messages_pagerank():
    """
    使用 PageRank 算法计算用户的传播性，基于最近一个月的消息互动数据。
    返回节点（用户）和边（互动关系）的数据，包含 PageRank 评分、颜色和大小等信息。
    """
    # 计算最近一个月的时间范围
    one_month_ago = datetime.now() - timedelta(days=30)
    one_month_ago_str = one_month_ago.strftime('%Y-%m-%d %H:%M:%S')

    # 查询所有用户信息
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    # 查询最近一个月的消息互动数据
    query_messages = f"""
        SELECT m.sender_id, u1.username AS sender_name,
               m.receiver_id, u2.username AS receiver_name,
               COUNT(*) as weight
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        WHERE m.timestamp >= '{one_month_ago_str}'
        GROUP BY m.sender_id, m.receiver_id
    """
    df_messages = fetch_data(query_messages)

    # 构建有向图
    G = nx.DiGraph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    # 添加带权重的边（消息传播）
    for _, row in df_messages.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"], weight=row["weight"])

    # 确保所有用户都作为节点
    G.add_nodes_from(df_users['id'])

    # 计算 PageRank 值
    pagerank_scores = nx.pagerank(G, weight='weight')

    # 归一化 PageRank 结果
    scores_values = np.array(list(pagerank_scores.values()))
    vmin, vmax = scores_values.min(), scores_values.max() if len(scores_values) > 0 else (0, 1)

    # 颜色划分
    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.viridis(i / 5) for i in range(6)]

    # 为每个节点分配颜色和大小
    node_colors = [
        mcolors.to_hex(colors[np.digitize(pagerank_scores.get(user_id, 0), bins) - 1])
        for user_id in user_map.keys()
    ]
    node_sizes = [
        np.interp(pagerank_scores.get(user_id, 0), (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON 格式的节点数据
    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": node_sizes[i],
        "color": node_colors[i],
        "pagerank": pagerank_scores.get(user_id, 0)
    } for i, user_id in enumerate(user_map.keys())]

    # 构造边数据
    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}