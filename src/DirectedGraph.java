import java.io.*;
import java.util.*;

public class DirectedGraph {
    private final Map<Integer, Map<Integer, Integer>> graph = new HashMap<>();

    // 获取用户数量
    public int getUserCount(String filePath) {
        Set<Integer> users = new HashSet<>(); // 用于存储唯一用户 ID

        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            br.readLine(); // 跳过表头
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length != 3) continue;

                try {
                    int sender = Integer.parseInt(parts[0].trim());
                    int receiver = Integer.parseInt(parts[1].trim());

                    // 将发送者和接收者都加入到用户集合中
                    users.add(sender);
                    users.add(receiver);
                } catch (NumberFormatException e) {
                    System.out.println("解析数字失败，跳过此行：" + line);
                }
            }
        } catch (IOException e) {
            System.out.println("加载文件时发生错误：" + e.getMessage());
        }

        return users.size(); // 返回唯一用户数量
    }

    // 读取 CSV 并构建有向图
    public void loadGraphFromCSV(String filePath) {
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            br.readLine(); // 跳过表头
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length != 3) continue;

                try {
                    int sender = Integer.parseInt(parts[0].trim());
                    int receiver = Integer.parseInt(parts[1].trim());
                    int weight = Integer.parseInt(parts[2].trim());

                    if (sender == receiver) {
                        System.out.println("跳过自我发送记录：用户 " + sender + " -> " + receiver);
                        continue;
                    }

                    graph.putIfAbsent(sender, new HashMap<>());
                    graph.get(sender).put(receiver, weight);
                } catch (NumberFormatException e) {
                    System.out.println("解析数字失败，跳过此行：" + line);
                }
            }
            System.out.println("图数据加载成功！");
        } catch (IOException e) {
            System.out.println("加载文件时发生错误：" + e.getMessage());
        }
    }

    // 获取图数据
    public Map<Integer, Map<Integer, Integer>> getGraph() {
        return graph;
    }

    // 打印有向图
    public void printGraph() {
        if (graph.isEmpty()) {
            System.out.println("图为空，无法打印数据！");
            return;
        }

        System.out.println("\n------ 当前社交网络图 ------");
        for (Map.Entry<Integer, Map<Integer, Integer>> entry : graph.entrySet()) {
            int sender = entry.getKey();
            System.out.print("用户 " + sender + " -> ");
            for (Map.Entry<Integer, Integer> edge : entry.getValue().entrySet()) {
                System.out.print("[" + edge.getKey() + " (" + edge.getValue() + ")] ");
            }
            System.out.println();
        }
    }

    // 查询某个用户的聊天对象
    public void queryUser(int userId) {
        // 检查用户 ID 是否存在于图中
        // 如果用户不存在，则说明该用户没有发送过消息记录
        if (!graph.containsKey(userId)) {
            System.out.println("用户 " + userId + " 没有发送过消息记录。");
            return;
        }

        // 输出该用户的聊天记录
        System.out.println("\n------ 用户 " + userId + " 的聊天记录 ------");

        // 遍历该用户与其他用户的聊天记录
        // graph.get(userId) 返回该用户的聊天对象及消息数 (Map<Integer, Integer>)
        // entry.getKey() 是聊天对象的用户 ID，entry.getValue() 是与该用户的消息数
        for (Map.Entry<Integer, Integer> entry : graph.get(userId).entrySet()) {
            System.out.println("  -> 用户 " + entry.getKey() + "，消息数：" + entry.getValue());
        }
    }

    // 录入新的聊天记录
    public void addMessage(int sender, int receiver, int messageCount) {
        // 如果发送者和接收者是同一个人，输出错误提示
        if (sender == receiver) {
            System.out.println("错误：不能发送消息给自己！");
            return;
        }

        // 如果消息数量小于等于 0，输出错误提示
        if (messageCount <= 0) {
            System.out.println("错误：消息次数必须大于 0！");
            return;
        }

        // 如果发送者还没有聊天记录，初始化一个新的 HashMap
        graph.putIfAbsent(sender, new HashMap<>());

        // 更新发送者与接收者之间的消息记录
        // graph.get(sender) 获取发送者的聊天记录，put(receiver, messageCount) 更新或添加接收者和消息数
        graph.get(sender).put(receiver, messageCount);

        // 输出成功信息，告知消息记录已经被录入
        System.out.println("成功录入消息记录：用户 " + sender + " -> 用户 " + receiver + "，消息数：" + messageCount);
    }

    // 使用 Dijkstra 算法计算最短路径
    public void shortestPath(int startUser, int endUser) {
        // 检查起始用户和结束用户是否存在于图中
        if (!graph.containsKey(startUser)) {
            System.out.println("错误：用户 " + startUser + " 不在图中！");
            return;
        }
        if (!graph.containsKey(endUser)) {
            System.out.println("错误：用户 " + endUser + " 不在图中！");
            return;
        }

        // **优先队列（PriorityQueue）：用于选择当前已知的最短路径节点**
        // **数据结构：最小堆（Min-Heap），底层基于二叉堆实现**
        // - 存储格式：`{用户ID, 距离}`
        // - 每次弹出当前距离最短的用户，以确保按最短路径扩展
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(a -> a[1]));

        // **距离表（HashMap<Integer, Integer>）：记录起点到每个用户的最短距离**
        // - 初始时，所有用户的距离设为无穷大（Integer.MAX_VALUE）
        // - 只有起点的距离设为 0
        Map<Integer, Integer> distances = new HashMap<>();

        // **前驱表（HashMap<Integer, Integer>）：记录路径信息**
        // - `previous.get(u) == v` 表示 `v` 是 `u` 在最短路径上的前驱
        // - 可用于回溯路径
        Map<Integer, Integer> previous = new HashMap<>();

        // **访问集合（HashSet<Integer>）：存储已经确定最短路径的用户**
        // - 访问过的用户不会再被重新处理，避免重复计算
        Set<Integer> visited = new HashSet<>();

        // **初始化距离表**
        for (Integer user : graph.keySet()) {
            distances.put(user, Integer.MAX_VALUE);
        }
        distances.put(startUser, 0); // 起点的距离为 0

        // **将起点加入优先队列**
        pq.offer(new int[]{startUser, 0});

        // **Dijkstra 主循环**
        while (!pq.isEmpty()) {
            // **取出当前距离最短的用户**
            int[] current = pq.poll();
            int user = current[0];  // 当前用户ID
            int dist = current[1];  // 当前用户的最短路径值

            // **如果该用户已经访问过，则跳过**
            if (visited.contains(user)) continue;
            visited.add(user);

            // **遍历当前用户的所有邻接节点**
            for (Map.Entry<Integer, Integer> neighbor : graph.get(user).entrySet()) {
                int neighborId = neighbor.getKey();   // 目标用户ID
                int weight = neighbor.getValue();    // 当前边的权重（消息数量）

                // **计算从起点到邻接节点的新路径长度**
                int newDist = dist + weight;

                // **如果找到更短的路径，则更新距离表**
                if (newDist < distances.get(neighborId)) {
                    distances.put(neighborId, newDist);
                    previous.put(neighborId, user); // 更新前驱信息

                    // **将新的路径信息加入优先队列**
                    pq.offer(new int[]{neighborId, newDist});
                }

        }

        // **最终，`distances` 里存储了从 `startUser` 到所有用户的最短路径**
        // **`previous` 记录了最短路径的回溯信息，可用于路径重构**
    }


    // 打印最短路径和社交距离
        if (distances.get(endUser) == Integer.MAX_VALUE) {
            System.out.println("无法找到用户 " + startUser + " 到用户 " + endUser + " 的路径。");
        } else {
            System.out.println("最短路径的社交距离为：" + distances.get(endUser));
            List<Integer> path = new ArrayList<>();
            for (Integer at = endUser; at != null; at = previous.get(at)) {
                path.add(at);
            }
            Collections.reverse(path);

            System.out.print("最短路径：");
            for (int i = 0; i < path.size(); i++) {
                System.out.print(path.get(i));
                if (i < path.size() - 1) {
                    System.out.print(" -> ");
                }
            }
            System.out.println();
        }
    }


    // **社交网络社区划分**
    // 目标：基于 **深度优先搜索（DFS）** 识别社交网络中的连通分量，即社区
    public void findCommunities() {
        // **访问集合（HashSet<Integer> visited）**
        // 作用：用于标记已访问的用户，避免重复遍历
        // 数据结构：`HashSet`，O(1) 时间复杂度的查询和插入
        Set<Integer> visited = new HashSet<>();

        // **社区列表（List<Set<Integer>> communities）**
        // 作用：存储所有识别出的社区，每个社区是一个用户集合
        // 数据结构：
        // - `ArrayList<Set<Integer>>`：存储多个社区
        // - 每个社区是 `HashSet<Integer>`，表示一个连通分量
        List<Set<Integer>> communities = new ArrayList<>();

        // **遍历所有用户，使用 DFS 识别连通分量**
        for (Integer user : graph.keySet()) {
            if (!visited.contains(user)) {  // 如果用户未访问，说明是一个新社区的起点
                Set<Integer> community = new HashSet<>(); // 存储当前社区的用户
                dfs(user, visited, community); // 使用 DFS 进行遍历
                communities.add(community); // 记录该社区
            }
        }

        // **输出社区信息**
        System.out.println("\n------ 社交网络的社区划分 ------");
        for (int i = 0; i < communities.size(); i++) {
            System.out.println("社区 " + (i + 1) + ": " + communities.get(i));
        }
    }

    // **深度优先搜索（DFS）：用于遍历一个社区内的所有用户**
    private void dfs(int user, Set<Integer> visited, Set<Integer> community) {
        visited.add(user); // 标记当前用户为已访问
        community.add(user); // 加入当前社区

        // **遍历当前用户的所有邻居**
        if (graph.containsKey(user)) {
            for (Integer neighbor : graph.get(user).keySet()) {
                if (!visited.contains(neighbor)) { // 仅访问未访问的用户
                    dfs(neighbor, visited, community); // 递归深入
                }
            }
        }
    }


    // 查询某个用户所在的社交社区
    public void findUserCommunity(int userId) {
        // 创建一个 HashSet 用于记录已访问的用户，避免重复访问
        Set<Integer> visited = new HashSet<>();

        // 遍历图中所有用户 (图的顶点)，graph 是一个邻接表 (Map<Integer, Set<Integer>>)
        // 其中 key 为用户 ID，value 为该用户的邻居用户 ID 集合
        for (Integer user : graph.keySet()) {
            // 如果当前用户还未被访问，则说明是一个新社区的起点
            if (!visited.contains(user)) {
                // 创建一个 HashSet 用于存储当前社区的所有用户
                Set<Integer> community = new HashSet<>();

                // 使用深度优先搜索 (DFS) 来遍历当前社区中的所有用户
                // 从当前用户开始，递归查找所有与该用户直接或间接相连的用户
                dfs(user, visited, community);

                // 检查当前社区是否包含用户 userId
                if (community.contains(userId)) {
                    // 如果包含，输出该社区的成员，并返回
                    System.out.println("用户 " + userId + " 所在的社区: " + community);
                    return;
                }
            }
        }

        // 如果遍历完所有社区后都未找到该用户，输出用户不在任何社区
        System.out.println("未找到用户 " + userId + " 所在的社区。");
    }}
