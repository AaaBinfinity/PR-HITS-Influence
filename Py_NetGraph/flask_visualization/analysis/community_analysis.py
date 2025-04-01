"""
社区分析
"""
import colorsys
from collections import defaultdict
import networkx as nx
from community import community_louvain
from database import fetch_data


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

