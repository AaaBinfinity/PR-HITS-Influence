from datetime import datetime, timedelta
import networkx as nx
from database import fetch_data

def analyze_messages_hits(days=30):
    """
    根据消息数据和社交社区计算 HITS 算法的 hub 和 authority 值。

    Parameters:
        days (int): 指定分析的时间范围（默认为30天）。

    Returns:
        hub_scores (dict): 包含每个节点的 hub 值。
        authority_scores (dict): 包含每个节点的 authority 值。
        user_map (dict): 用户ID与用户名的映射。
        community_ids (dict): 用户ID与所属社区的映射。
        df_messages (DataFrame): 获取的消息交互数据。
    """

    # 计算时间范围，获取当前日期前 "days" 天的日期
    one_month_ago = datetime.now() - timedelta(days=days)
    one_month_ago_str = one_month_ago.strftime('%Y-%m-%d %H:%M:%S')

    # 获取所有用户信息
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

    # 如果没有消息数据，则返回空数据
    if df_messages.empty:
        print("⚠️ df_messages 为空，没有交互数据")
        return {}, {}, {}, df_messages

    # **创建有向图**（社交网络图）
    G = nx.DiGraph()

    # **构建用户映射表**
    user_map = {row["id"]: row["username"] for _, row in df_users.iterrows()}

    if not user_map:
        print("⚠️ user_map 为空，可能 users 表无数据")
        return {}, {}, {}, df_messages

    # **添加边（消息交互）到图中**
    for _, row in df_messages.iterrows():
        G.add_edge(int(row["sender_id"]), int(row["receiver_id"]), weight=float(row["weight"]))

    # 如果图没有边，返回空数据
    if not G.edges:
        print("⚠️ G.edges 为空，HITS 计算无法进行")
        return {}, {}, user_map, df_messages

    print(f"📊 图包含 {G.number_of_nodes()} 个节点, {G.number_of_edges()} 条边")

    # **检测社区（连通子图）**
    communities = list(nx.weakly_connected_components(G))
    print(f"🔍 检测到 {len(communities)} 个独立社交社区")

    # **独立计算每个社区的 HITS**
    hub_scores = {}
    authority_scores = {}
    community_ids = {}

    for i, community in enumerate(communities):
        subG = G.subgraph(community).copy()  # 获取每个社区的子图
        print(f"📌 计算社区 {i+1}, 包含 {subG.number_of_nodes()} 个节点, {subG.number_of_edges()} 条边")

        try:
            # 计算该子图的 HITS 分数
            hits_scores = nx.hits(subG, max_iter=1000, tol=1e-15, normalized=True)
            sub_hub_scores, sub_authority_scores = hits_scores
        except nx.PowerIterationFailedConvergence:
            # 如果计算未收敛，使用入度和出度替代
            print(f"⚠️ 社区 {i+1} HITS 计算未收敛，改用入度/出度计算")
            sub_hub_scores = {node: subG.out_degree(node, weight="weight") for node in subG.nodes()}
            sub_authority_scores = {node: subG.in_degree(node, weight="weight") for node in subG.nodes()}

        # 合并到总结果中
        hub_scores.update(sub_hub_scores)
        authority_scores.update(sub_authority_scores)

        # 记录每个用户所属的社区ID
        for node in community:
            community_ids[node] = i  # Community ID is the index of the community

    return hub_scores, authority_scores, user_map, community_ids, df_messages


def get_messages_hits_data(days=30):
    """
    返回包含 hub、authority 和 community_id 的节点数据，适用于前端可视化。

    Parameters:
        days (int): 指定分析的时间范围（默认为30天）。

    Returns:
        dict: 包含节点数据（hub、authority、community_id）和边数据（消息交互）。
    """
    # 调用分析函数，获取 HITS 结果
    hub_scores, authority_scores, user_map, community_ids, df_messages = analyze_messages_hits(days)

    # 构造节点数据，每个节点包含 id、用户名、hub 值、authority 值、大小、社区 ID 等信息
    nodes = [
        {
            "id": int(user_id),
            "username": user_map[user_id],
            "authority": round(authority_scores.get(user_id, 0), 6),
            "hub": round(hub_scores.get(user_id, 0), 6),
            "size": int((authority_scores.get(user_id, 0) + hub_scores.get(user_id, 0)) * 1000),
            "community_id": community_ids.get(user_id, -1)  # 默认 -1 表示没有分配社区 ID
        }
        for user_id in user_map.keys()
    ]

    # 构造边数据，表示用户间的消息交互
    edges = [
        {"source": int(row["sender_id"]), "target": int(row["receiver_id"]), "weight": float(row["weight"])}
        for _, row in df_messages.iterrows()
    ]

    # 返回包含节点和边数据的字典
    return {"nodes": nodes, "edges": edges}
