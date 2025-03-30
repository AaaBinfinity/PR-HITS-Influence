import colorsys
from datetime import datetime, timedelta
from collections import defaultdict
import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from community import community_louvain
from database import fetch_data  # 确保数据库连接和查询函数正确


def analyze_friends():
    """获取好友关系数据并计算节点属性，包含所有用户"""
    # 查询所有用户信息
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    # 查询好友关系数据
    query_friends = """
        SELECT f.user_id, u1.username AS user_name_1, 
               f.friend_id, u2.username AS user_name_2
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        JOIN users u2 ON f.friend_id = u2.id
    """
    df_friends = fetch_data(query_friends)

    # 构建无向图
    G = nx.Graph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}  # 记录所有用户

    # 添加边（好友关系）
    for _, row in df_friends.iterrows():
        G.add_edge(row["user_id"], row["friend_id"])

    # 计算每个用户的好友数量
    degrees = {node: G.degree(node) for node in G.nodes()}

    # 确保所有用户都参与计算（包括没有好友的）
    for user_id in user_map.keys():
        if user_id not in degrees:
            degrees[user_id] = 0  # 无好友

    degree_values = list(degrees.values())
    vmin, vmax = min(degree_values), max(degree_values)

    # 🎨 颜色划分

    bins = np.linspace(vmin, vmax, 6)

    colors = [cm.Paired(i / 5) for i in range(6)]

    # 为每个节点分配颜色
    node_colors = [
        mcolors.to_hex(colors[np.digitize(degrees[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    # 为每个节点分配大小
    node_sizes = [
        np.interp(degrees[user_id], (vmin, vmax), (600, 5000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON 格式的节点数据
    nodes = [{"id": int(user_id), "username": user_map[user_id], "size": node_sizes[i], "color": node_colors[i],
              "degree": degrees[user_id]}
             for i, user_id in enumerate(user_map.keys())]

    # 构造边数据
    edges = [{"source": int(u), "target": int(v)} for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}

def analyze_centrality():
    """计算用户中心性（接收消息的数量）"""
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

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

    # 添加边
    for _, row in df_messages.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"], weight=row["weight"])

    # 计算中心性（接收消息的数量）
    node_centrality = {node: sum(d["weight"] for _, _, d in G.in_edges(node, data=True)) for node in G.nodes()}

    # 确保所有用户都包含，即使没有接收消息
    for user_id in user_map.keys():
        if user_id not in node_centrality:
            node_centrality[user_id] = 0

    centrality_values = list(node_centrality.values())
    vmin, vmax = min(centrality_values), max(centrality_values)

    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.viridis(i / 5) for i in range(6)]

    node_colors = [
        mcolors.to_hex(colors[np.digitize(node_centrality[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    node_sizes = [
        np.interp(node_centrality[user_id], (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": node_sizes[i],
        "color": node_colors[i],
        "centrality": node_centrality[user_id]
    } for i, user_id in enumerate(user_map.keys())]

    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}

def analyze_messages():
    """获取消息互动数据并计算节点属性，包含所有用户"""
    # 查询所有用户信息
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    # -- 查询近一个月的消息互动数据
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

    # 计算每个用户的活跃度（入度+出度）
    node_activity = {node: sum(d["weight"] for _, _, d in G.edges(node, data=True)) for node in G.nodes()}

    # 确保所有用户都包含，即使没有发送或接收消息
    for user_id in user_map.keys():
        if user_id not in node_activity:
            node_activity[user_id] = 0  # 没有发送/接收消息

    activity_values = list(node_activity.values())
    vmin, vmax = min(activity_values), max(activity_values)

    # 🎨 颜色划分
    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.viridis(i / 5) for i in range(6)]

    # 为每个节点分配颜色
    node_colors = [
        mcolors.to_hex(colors[np.digitize(node_activity[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    # 为每个节点分配大小
    node_sizes = [
        np.interp(node_activity[user_id], (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON 格式的节点数据
    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": node_sizes[i],
        "color": node_colors[i],
        "activity": node_activity[user_id]
    } for i, user_id in enumerate(user_map.keys())]

    # 构造边数据
    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}


def analyze_friend_distribution():
    """计算好友数量的分布，并返回 JSON 结果"""
    # 获取好友关系数据
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

    # 颜色映射
    bins = np.linspace(friend_counts.min(), friend_counts.max(), 6)
    colors = [cm.Blues(i / 5) for i in range(6)]  # 6 级颜色
    color_map = {count: mcolors.to_hex(colors[np.digitize(count, bins) - 1]) for count in friend_counts}

    # 构造 JSON 格式的好友数据
    friend_data = [
        {"user_id": int(user), "friend_count": int(count), "color": color_map[count]}
        for user, count in friend_counts.items()
    ]

    return {
        "friend_data": friend_data,
        "stats": {"mean_friends": mean_friends, "median_friends": median_friends}
    }


def analyze_messages_pagerank():
    """使用 PageRank 算法计算用户传播性（仅采集最近一个月的数据）"""

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

def analyze_messages_hits(days=30):
    """按社交社区独立计算 HITS 算法的 hub 和 authority 值"""

    # 计算时间范围
    one_month_ago = datetime.now() - timedelta(days=days)
    one_month_ago_str = one_month_ago.strftime('%Y-%m-%d %H:%M:%S')

    # 获取所有用户
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    # 获取最近 days 天的消息数据
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

    if df_messages.empty:
        print("⚠️ df_messages 为空，没有交互数据")
        return {}, {}, {}, df_messages

    # **创建有向图**
    G = nx.DiGraph()

    # **构建用户映射表**
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    if not user_map:
        print("⚠️ user_map 为空，可能 users 表无数据")
        return {}, {}, {}, df_messages

    # **添加边（消息交互）**
    for _, row in df_messages.iterrows():
        G.add_edge(int(row["sender_id"]), int(row["receiver_id"]), weight=float(row["weight"]))

    if not G.edges:
        print("⚠️ G.edges 为空，HITS 计算无法进行")
        return {}, {}, user_map, df_messages

    print(f"📊 图包含 {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")

    # **检测社区（连通子图）**
    communities = list(nx.weakly_connected_components(G))
    print(f"🔍 检测到 {len(communities)} 个独立社交社区")

    # **独立计算 HITS**
    hub_scores = {}
    authority_scores = {}

    for i, community in enumerate(communities):
        subG = G.subgraph(community).copy()
        print(f"📌 计算社区 {i+1}, 包含 {subG.number_of_nodes()} 个节点, {subG.number_of_edges()} 条边")

        try:
            hits_scores = nx.hits(subG, max_iter=1000, tol=1e-15, normalized=True)
            sub_hub_scores, sub_authority_scores = hits_scores
        except nx.PowerIterationFailedConvergence:
            print(f"⚠️ 社区 {i+1} HITS 计算未收敛，改用入度/出度计算")
            sub_hub_scores = {node: subG.out_degree(node, weight="weight") for node in subG.nodes()}
            sub_authority_scores = {node: subG.in_degree(node, weight="weight") for node in subG.nodes()}

        # 合并到总结果
        hub_scores.update(sub_hub_scores)
        authority_scores.update(sub_authority_scores)

    return hub_scores, authority_scores, user_map, df_messages



def get_messages_hits_data(days=30):
    """返回包含 hub 和 authority 的数据"""
    hub_scores, authority_scores, user_map, df_messages = analyze_messages_hits(days)

    nodes = [
        {
            "id": int(user_id),
            "username": user_map[user_id],
            "authority": round(authority_scores.get(user_id, 0), 6),
            "hub": round(hub_scores.get(user_id, 0), 6),
            "size": int((authority_scores.get(user_id, 0) + hub_scores.get(user_id, 0)) * 1000)
        }
        for user_id in user_map.keys()
    ]

    edges = [
        {"source": int(row["sender_id"]), "target": int(row["receiver_id"]), "weight": float(row["weight"])}
        for _, row in df_messages.iterrows()
    ]

    return {"nodes": nodes, "edges": edges}

def analyze_community():
    """获取用户社区划分数据"""
    # 查询所有用户信息
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    # 查询好友关系数据
    query_friends = """
        SELECT f.user_id, u1.username AS user_name_1, 
               f.friend_id, u2.username AS user_name_2
        FROM friends f
        JOIN users u1 ON f.user_id = u1.id
        JOIN users u2 ON f.friend_id = u2.id
    """
    df_friends = fetch_data(query_friends)

    # 构建无向图
    G = nx.Graph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}  # 记录所有用户

    # 添加边（好友关系）
    for _, row in df_friends.iterrows():
        G.add_edge(row["user_id"], row["friend_id"])

    # 使用 Louvain 算法进行社区划分
    partition = community_louvain.best_partition(G)

    # 为每个社区分配颜色和用户
    community_map = defaultdict(list)
    for user_id, community_id in partition.items():
        community_map[community_id].append(user_id)

    # 处理没有分配到社区的用户
    default_community = len(community_map)  # 设置一个默认社区ID
    for user_id in user_map.keys():
        if user_id not in partition:
            partition[user_id] = default_community  # 将未分配社区的用户分配到默认社区
            community_map[default_community].append(user_id)

    # 为每个社区分配颜色
    colors = [
        '#' + ''.join([hex(int(c * 255))[2:].zfill(2) for c in colorsys.hsv_to_rgb(i / len(community_map), 1, 1)])
        for i in range(len(community_map))
    ]
    # 构造节点数据和边数据
    nodes = [
        {"id": int(user_id), "username": user_map.get(user_id, "未知用户"),
         "community": partition.get(user_id), "color": colors[partition[user_id]]}
        for user_id in user_map.keys()
    ]
    edges = [{"source": int(u), "target": int(v)} for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges, "community_map": community_map, "colors": colors}



