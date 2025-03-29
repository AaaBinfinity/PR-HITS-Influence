import heapq
from database import fetch_data  # 确保数据库连接和查询函数正确


def dijkstra_shortest_path(graph, start, end):
    """使用 Dijkstra 算法查找最短路径"""
    queue = [(0, start, [])]  # (当前代价, 当前节点, 访问路径)
    visited = set()

    while queue:
        cost, node, path = heapq.heappop(queue)

        if node in visited:
            continue
        visited.add(node)
        path = path + [node]

        if node == end:
            return path, cost  # 找到最短路径

        for neighbor, weight in graph.get(node, {}).items():
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight, neighbor, path))

    return None, float("inf")  # 没有路径

def analyze_Djs(start_user, end_user):
    """计算两个用户之间的最短路径"""
    # 获取用户 ID
    query = "SELECT id, username FROM users"
    df_users = fetch_data(query)

    if df_users.empty:
        return {"error": "用户数据为空"}

    # 创建用户名到用户ID的映射
    username_to_id = {row["username"]: row["id"] for _, row in df_users.iterrows()}

    # 确保提供的用户名存在
    if start_user not in username_to_id or end_user not in username_to_id:
        return {"error": "起始用户或目标用户不存在"}

    start_user_id = username_to_id[start_user]
    end_user_id = username_to_id[end_user]

    # 获取好友数据
    query = "SELECT user_id, friend_id FROM friends"
    df_friends = fetch_data(query)

    if df_friends.empty:
        return {"error": "好友数据为空"}

    # 构建图
    graph = {}
    for _, row in df_friends.iterrows():
        user_a, user_b = int(row["user_id"]), int(row["friend_id"])
        if user_a not in graph:
            graph[user_a] = {}
        if user_b not in graph:
            graph[user_b] = {}

        graph[user_a][user_b] = 1
        graph[user_b][user_a] = 1

    print("Graph:", graph)  # 调试

    # 计算最短路径
    shortest_path, cost = dijkstra_shortest_path(graph, start_user_id, end_user_id)

    if not shortest_path:
        return {"error": "未找到路径"}

    # 计算步骤数和跳过的用户数
    steps = len(shortest_path) - 1
    skipped_users = len(shortest_path) - 2  # 减去起始和目标用户

    return {
        "path": shortest_path,
        "cost": cost,
        "steps": steps,
        "skipped_users": skipped_users
    }
