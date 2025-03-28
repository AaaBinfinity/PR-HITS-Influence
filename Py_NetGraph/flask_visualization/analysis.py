import networkx as nx
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd

from database import fetch_data  # 确保数据库连接和查询函数正确


def analyze_friends():
    """获取好友关系数据并计算节点属性，包含所有用户"""
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

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

    # 添加边
    for _, row in df_friends.iterrows():
        G.add_edge(row["user_id"], row["friend_id"])

    # 计算好友数量
    degrees = {node: G.degree(node) for node in G.nodes()}

    # 让所有用户都参与计算（包括没有好友的）
    for user_id in user_map.keys():
        if user_id not in degrees:
            degrees[user_id] = 0  # 无好友

    degree_values = list(degrees.values())
    vmin, vmax = min(degree_values), max(degree_values)

    # 🎨 颜色划分
    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.Paired(i / 5) for i in range(6)]

    node_colors = [
        mcolors.to_hex(colors[np.digitize(degrees[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    node_sizes = [
        np.interp(degrees[user_id], (vmin, vmax), (600, 5000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON
    nodes = [{"id": int(user_id), "username": user_map[user_id], "size": node_sizes[i], "color": node_colors[i],
              "degree": degrees[user_id]}
             for i, user_id in enumerate(user_map.keys())]

    edges = [{"source": int(u), "target": int(v)} for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}


def analyze_messages():
    """获取消息互动数据并计算节点属性，包含所有用户"""
    query_users = "SELECT id, username FROM users"
    df_users = fetch_data(query_users)

    query_messages = """
        SELECT m.sender_id, u1.username AS sender_name,
               m.receiver_id, u2.username AS receiver_name,
               COUNT(*) as weight
        FROM messages m
        JOIN users u1 ON m.sender_id = u1.id
        JOIN users u2 ON m.receiver_id = u2.id
        GROUP BY m.sender_id, m.receiver_id
    """
    df_messages = fetch_data(query_messages)

    # 构建有向图
    G = nx.DiGraph()
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    # 添加边
    for _, row in df_messages.iterrows():
        G.add_edge(row["sender_id"], row["receiver_id"], weight=row["weight"])

    # 计算活跃度（入度+出度）
    node_activity = {node: sum(d["weight"] for _, _, d in G.edges(node, data=True)) for node in G.nodes()}

    # 确保所有用户都包含，即使没发过消息
    for user_id in user_map.keys():
        if user_id not in node_activity:
            node_activity[user_id] = 0  # 没有发送/接收消息

    activity_values = list(node_activity.values())
    vmin, vmax = min(activity_values), max(activity_values)

    # 🎨 颜色划分
    bins = np.linspace(vmin, vmax, 6)
    colors = [cm.viridis(i / 5) for i in range(6)]

    node_colors = [
        mcolors.to_hex(colors[np.digitize(node_activity[user_id], bins) - 1])
        for user_id in user_map.keys()
    ]

    node_sizes = [
        np.interp(node_activity[user_id], (vmin, vmax), (1000, 6000))
        for user_id in user_map.keys()
    ]

    # 构造 JSON
    nodes = [{
        "id": int(user_id),
        "username": user_map[user_id],
        "size": node_sizes[i],
        "color": node_colors[i],
        "activity": node_activity[user_id]
    } for i, user_id in enumerate(user_map.keys())]

    edges = [{
        "source": int(u),
        "target": int(v),
        "weight": G[u][v]["weight"]
    } for u, v in G.edges()]

    return {"nodes": nodes, "edges": edges}


def analyze_by_timestamp():
    """获取消息互动数据并计算时间序列属性"""
    query = "SELECT timestamp FROM messages"
    df_time = fetch_data(query)

    # 处理时间数据
    df_time["timestamp"] = pd.to_datetime(df_time["timestamp"])

    # 按时间戳分组，统计每个时间点的消息数量
    msg_count = df_time.groupby(df_time["timestamp"]).size()

    # 平滑处理：使用滚动平均
    window_size = 10  # 设置窗口大小
    msg_count_smoothed = msg_count.rolling(window=window_size, min_periods=1).mean()

    # 归一化时间戳，用于 JSON 输出
    timestamps = msg_count.index.astype(str).tolist()
    smoothed_values = msg_count_smoothed.tolist()

    # 构造 JSON 结果
    time_series = [{"timestamp": timestamps[i], "count": smoothed_values[i]} for i in range(len(timestamps))]

    return {"time_series": time_series}


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

    # 构造 JSON 结果
    friend_data = [
        {"user_id": int(user), "friend_count": int(count), "color": color_map[count]}
        for user, count in friend_counts.items()
    ]

    return {
        "friend_data": friend_data,
        "stats": {"mean_friends": mean_friends, "median_friends": median_friends}
    }
