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

    # 构建无向图（每个用户为一个节点，好友关系为一条边）
    G = nx.Graph()

    # 创建一个用户映射，将用户ID与用户名进行关联
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    # 在图中添加边（好友关系）
    for _, row in df_friends.iterrows():
        G.add_edge(row["user_id"], row["friend_id"])

    # 使用 Louvain 算法进行社区划分
    partition = community_louvain.best_partition(G)

    # 将每个社区的用户进行分组
    community_map = defaultdict(list)
    for user_id, community_id in partition.items():
        community_map[community_id].append(user_id)

    # 处理没有分配到社区的用户（如果有的话）
    default_community = len(community_map)  # 设置默认社区的ID
    for user_id in user_map.keys():
        if user_id not in partition:
            partition[user_id] = default_community  # 将未分配社区的用户分配到默认社区
            community_map[default_community].append(user_id)

    # 为每个社区分配不同的颜色（颜色生成基于HSV色轮）
    colors = [
        '#' + ''.join([hex(int(c * 255))[2:].zfill(2) for c in colorsys.hsv_to_rgb(i / len(community_map), 1, 1)])
        for i in range(len(community_map))
    ]

    # 构造节点数据（每个用户的社区ID和对应的颜色）
    nodes = [
        {"id": int(user_id), "username": user_map.get(user_id, "未知用户"),
         "community": partition.get(user_id), "color": colors[partition[user_id]]}
        for user_id in user_map.keys()
    ]

    # 构造边数据，表示好友关系的连接
    edges = [{"source": int(u), "target": int(v)} for u, v in G.edges()]

    # 返回分析结果：节点数据、边数据、社区映射、每个社区的颜色
    return {"nodes": nodes, "edges": edges, "community_map": community_map, "colors": colors}

