import java.util.*;

public class PageRank {
    private Map<Integer, Map<Integer, Integer>> graph; // 使用  邻接表  存储有向图，其中键是用户ID，值是一个映射，表示该用户指向的其他用户及对应的权重（消息次数）
    private final double d = 0.85; // 阻尼系数（Damping Factor），用于模拟用户随机跳转网页的概率，通常取值 0.85
    private final int maxIterations = 100; // PageRank 计算的最大迭代次数，防止无限循环
    private final double threshold = 0.0001; // 结果收敛的阈值，当所有节点的 PageRank 变化小于该值时停止迭代

    // 构造函数，接收一个图的邻接表表示，并初始化 PageRank 计算
    public PageRank(Map<Integer, Map<Integer, Integer>> graph) {
        this.graph = graph;
    }


    // 计算每个用户的 PageRank 值
    public Map<Integer, Double> computePageRank() {
        int N = graph.size(); // 图中节点的数量
        Map<Integer, Double> pagerank = new HashMap<>();
        Map<Integer, Double> newPagerank = new HashMap<>();

        // 初始化每个节点的 PageRank 值为 1 / N
        for (Integer userId : graph.keySet()) {
            pagerank.put(userId, 1.0 / N);
        }

        // 迭代更新 PageRank 值
        for (int iteration = 0; iteration < maxIterations; iteration++) {
            double diff = 0.0;

            // 对每个用户计算新的 PageRank 值
            for (Integer userId : graph.keySet()) {
                double rankSum = 0.0;

                // 计算指向该用户的所有用户的贡献
                for (Map.Entry<Integer, Map<Integer, Integer>> entry : graph.entrySet()) {
                    Integer sender = entry.getKey();
                    Map<Integer, Integer> edges = entry.getValue();

                    // 如果 sender -> userId 是一条边
                    if (edges.containsKey(userId)) {
                        int outDegree = edges.size(); // 发送者的出度
                        rankSum += pagerank.get(sender) / outDegree;
                    }
                }

                // 计算新 PageRank 值
                newPagerank.put(userId, (1 - d) / N + d * rankSum);

                // 计算 PageRank 值的变化量
                diff += Math.abs(newPagerank.get(userId) - pagerank.get(userId));
            }

            // 更新 pagerank
            pagerank = new HashMap<>(newPagerank);

            // 如果 PageRank 值变化小于阈值，表示收敛，退出迭代
            if (diff < threshold) {
                System.out.println("PageRank 收敛，迭代次数: " + iteration);
                break;
            }
        }

        // 归一化处理，确保所有 PageRank 值之和为 1
        double totalRank = pagerank.values().stream().mapToDouble(Double::doubleValue).sum();
        for (Map.Entry<Integer, Double> entry : pagerank.entrySet()) {
            entry.setValue(entry.getValue() / totalRank); // 每个 PageRank 值除以总和
        }

        return pagerank;
    }

    public void printPageRank(Map<Integer, Double> pagerank) {
        System.out.println("\n------ PageRank 结果 ------");
        List<Map.Entry<Integer, Double>> pageRankList = new ArrayList<>(pagerank.entrySet());
        for (Map.Entry<Integer, Double> entry : pageRankList) {
            System.out.println("用户 " + entry.getKey() + " 的 PageRank 值: " + entry.getValue());
        }
    }

    // 打印前 N 名用户的 PageRank 值（使用冒泡排序）
    public void printTopNPageRank(Map<Integer, Double> pagerank, int topN) {
        // 转换为列表
        List<Map.Entry<Integer, Double>> sortedList = new ArrayList<>(pagerank.entrySet());

        // 冒泡排序（降序）
        int n = sortedList.size();
        for (int i = 0; i < n - 1; i++) {
            for (int j = 0; j < n - 1 - i; j++) {
                if (sortedList.get(j).getValue() < sortedList.get(j + 1).getValue()) {
                    Collections.swap(sortedList, j, j + 1);
                }
            }
        }

        System.out.println("\n------ 前 " + topN + " 名用户的 PageRank ------");
        // 打印前 N 名用户的 PageRank 值
        for (int i = 0; i < topN && i < sortedList.size(); i++) {
            Map.Entry<Integer, Double> entry = sortedList.get(i);
            System.out.println("第 " + (i + 1) + " 名: 用户 " + entry.getKey() + " - PageRank 值: " + entry.getValue());
        }
    }

}
