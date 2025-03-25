import java.util.*;

public class HITSAlgorithm {
    private static final int MAX_ITERATIONS = 100;  // 迭代次数
    private static final double TOLERANCE = 1e-6;  // 收敛阈值

    // 计算 HITS 权威度和枢纽度
    public static void computeHITS(Map<Integer, Set<Integer>> graph,
                                   Map<Integer, Double> authorityScores,
                                   Map<Integer, Double> hubScores) {
        // 初始化所有用户的 Hub 和 Authority 值为 1
        for (Integer node : graph.keySet()) {
            authorityScores.put(node, 1.0);
            hubScores.put(node, 1.0);
        }

        for (int iter = 0; iter < MAX_ITERATIONS; iter++) {
            Map<Integer, Double> newAuthorityScores = new HashMap<>();
            Map<Integer, Double> newHubScores = new HashMap<>();

            // 计算 Authority 值：被 Hub 连接的权重总和
            for (Integer node : graph.keySet()) {
                double authoritySum = 0;
                for (Integer inbound : graph.keySet()) {
                    if (graph.get(inbound).contains(node)) {
                        authoritySum += hubScores.get(inbound);
                    }
                }
                newAuthorityScores.put(node, authoritySum);
            }

            // 计算 Hub 值：指向 Authority 的总和
            for (Integer node : graph.keySet()) {
                double hubSum = 0;
                for (Integer outbound : graph.get(node)) {
                    hubSum += authorityScores.get(outbound);
                }
                newHubScores.put(node, hubSum);
            }

            // 归一化（Normalization）
            normalize(newAuthorityScores);
            normalize(newHubScores);

            // 判断是否收敛
            if (hasConverged(authorityScores, newAuthorityScores) &&
                    hasConverged(hubScores, newHubScores)) {
                break;
            }

            authorityScores.putAll(newAuthorityScores);
            hubScores.putAll(newHubScores);
        }
    }

    // 归一化函数
    private static void normalize(Map<Integer, Double> scores) {
        double sum = Math.sqrt(scores.values().stream().mapToDouble(x -> x * x).sum());
        for (Integer node : scores.keySet()) {
            scores.put(node, scores.get(node) / (sum == 0 ? 1 : sum));
        }
    }

    // 判断收敛
    private static boolean hasConverged(Map<Integer, Double> oldScores, Map<Integer, Double> newScores) {
        for (Integer node : oldScores.keySet()) {
            if (Math.abs(oldScores.get(node) - newScores.get(node)) > TOLERANCE) {
                return false;
            }
        }
        return true;
    }
}
