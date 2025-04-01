import heapq
from database import fetch_data  # 确保数据库连接和查询函数正确

def dijkstra_shortest_path(graph, start, end):
    """
    使用 Dijkstra 算法计算最短路径。
    :param graph: 图结构（邻接表表示），键为节点，值为字典，表示邻接节点及其权重。
    :param start: 起始节点 ID。
    :param end: 目标节点 ID。
    :return: 最短路径（节点列表）和路径代价。
    """
    queue = [(0, start, [])]  # 最小堆队列，存储 (当前路径代价, 当前节点, 访问路径)
    visited = set()  # 记录已访问的节点，避免重复遍历

    while queue:
        cost, node, path = heapq.heappop(queue)  # 取出当前代价最小的节点

        if node in visited:
            continue  # 跳过已访问的节点
        visited.add(node)  # 标记节点为已访问
        path = path + [node]  # 更新路径

        if node == end:
            return path, cost  # 找到目标节点，返回路径及代价

        for neighbor, weight in graph.get(node, {}).items():  # 遍历当前节点的邻居
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))  # 加入最小堆

    return None, float("inf")  # 若未找到路径，返回 None 和无穷大代价


def analyze_Djs(start_user, end_user):
    """
    计算两个用户之间的最短路径。
    :param start_user: 起始用户的用户名。
    :param end_user: 目标用户的用户名。
    :return: 包含最短路径信息的字典。
    """
    # 1. 查询用户信息，获取用户 ID
    query = "SELECT id, username FROM users"
    df_users = fetch_data(query)  # 从数据库获取用户数据

    if df_users.empty:
        return {"error": "用户数据为空"}  # 若数据库无数据，则返回错误信息

    # 2. 创建用户名到用户 ID 的映射
    username_to_id = {row["username"]: row["id"] for _, row in df_users.iterrows()}

    # 3. 确保起始用户和目标用户都存在于数据库
    if start_user not in username_to_id or end_user not in username_to_id:
        return {"error": "起始用户或目标用户不存在"}

    start_user_id = username_to_id[start_user]
    end_user_id = username_to_id[end_user]

    # 4. 查询好友关系数据
    query = "SELECT user_id, friend_id FROM friends"
    df_friends = fetch_data(query)

    if df_friends.empty:
        return {"error": "好友数据为空"}

    # 5. 构建用户社交网络图（无向图）
    graph = {}
    for _, row in df_friends.iterrows():
        user_a, user_b = int(row["user_id"]), int(row["friend_id"])
        if user_a not in graph:
            graph[user_a] = {}
        if user_b not in graph:
            graph[user_b] = {}

        graph[user_a][user_b] = 1  # 设定权重为 1，表示好友关系
        graph[user_b][user_a] = 1

    print("Graph:", graph)  # 调试用，打印构建的图

    # 6. 使用 Dijkstra 算法计算最短路径
    shortest_path, cost = dijkstra_shortest_path(graph, start_user_id, end_user_id)

    if not shortest_path:
        return {"error": "未找到路径"}  # 若未找到路径，返回错误信息

    # 7. 计算路径的步骤数和跳过的用户数
    steps = len(shortest_path) - 1  # 计算路径中的步数
    skipped_users = len(shortest_path) - 2  # 跳过的用户数（不包括起始和目标用户）

    return {
        "path": shortest_path,  # 最短路径（用户 ID 列表）
        "cost": cost,  # 最短路径的总代价
        "steps": steps,  # 总步数
        "skipped_users": skipped_users  # 跳过的用户数
    }
