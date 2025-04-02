from datetime import datetime, timedelta
import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from database import fetch_data


def compute_pagerank(G, alpha=0.85, tol=1.0e-6, max_iter=100):
    """
    计算 PageRank 值
    :param G: 以 networkx.DiGraph 表示的有向图
    :param alpha: 阻尼因子（默认 0.85）
    :param tol: 迭代收敛阈值
    :param max_iter: 最大迭代次数
    :return: {节点: PageRank 值} 字典
    """
    users = list(G.nodes)
    N = len(users)
    if N == 0:
        return {}

    # 初始化 PageRank 值
    pagerank = {user: 1.0 / N for user in users}
    new_pagerank = pagerank.copy()

    # 预计算每个用户的出度
    out_degree = {user: sum(G[user][neighbor]["weight"] for neighbor in G[user]) if G[user] else 0 for user in users}

    for _ in range(max_iter):
        for user in users:
            new_pagerank[user] = (1 - alpha) / N + alpha * sum(
                pagerank[neighbor] * G[neighbor][user]["weight"] / out_degree[neighbor]
                for neighbor in G.predecessors(user) if out_degree[neighbor] > 0
            )

        # 判断收敛
        if sum(abs(new_pagerank[u] - pagerank[u]) for u in users) < tol:
            break
        pagerank = new_pagerank.copy()

    return pagerank


def analyze_user_interactions_pagerank():
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

    # **使用自定义 PageRank 计算**
    pagerank_scores = compute_pagerank(G)

    # 归一化 PageRank 结果
    scores_values = np.array(list(pagerank_scores.values()))
    vmin, vmax = scores_values.min(), scores_values.max() if len(scores_values) > 0 else (0, 1)

    # 颜色划分
    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.viridis(i / 5) for i in range(6)]

    # 为每个用户分配颜色和大小
    user_colors = [
        mcolors.to_hex(colors[np.digitize(pagerank_scores.get(user_id, 0), bins) - 1])
        for user_id in user_map.keys()
    ]
    user_sizes = [
        np.interp(pagerank_scores.get(user_id, 0), (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON 格式的用户数据
    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": user_sizes[i],
        "color": user_colors[i],
        "pagerank": pagerank_scores.get(user_id, 0)
    } for i, user_id in enumerate(user_map.keys())]

    # 构造边数据
    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}
