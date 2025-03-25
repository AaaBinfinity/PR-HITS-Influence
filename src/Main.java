import java.util.*;
import java.io.*;

public class Main {
    // 显示菜单
    public static void showMenu() {

        System.out.println();
        System.out.println("●∞ ∞●∞ ∞●∞ ∞●  ●∞ ∞●∞ ∞●∞ ∞●  ●∞ ∞●∞ ∞●∞ ∞●  ");
        System.out.println("●∞ ∞●∞------ 社交网络影响力分析系统------∞●∞ ∞● ");
        System.out.println("●∞ ∞●∞ ∞●∞ ∞●  ●∞ ∞●∞ ∞●∞ ∞●  ●∞ ∞●∞ ∞●∞ ∞●  ");

        System.out.println("1. 查询用户的聊天记录");
        System.out.println("2. 录入新的聊天记录");
        System.out.println("3. 打印整个图");
        System.out.println("4. 获取用户数量");
        System.out.println("5. 最短路径和社交距离");
        System.out.println("6. 计算并显示 PageRank");
        System.out.println("7. 显示前 15 名用户的 PageRank");
        System.out.println("8. 输出所有社区");
        System.out.println("9. 查询某一用户所在的社区");
        System.out.println("10. 打印用户权威度（Authority） 和 枢纽度（Hub）");
        System.out.println("11. 退出");
        System.out.print("请选择操作: ");
    }

    // 获取有效的用户输入
    public static int getValidInput(Scanner scanner) {
        while (true) {
            if (scanner.hasNextInt()) {
                return scanner.nextInt();
            } else {
                System.out.println("无效输入，请输入一个数字！");
                scanner.next(); // 清除错误的输入
            }
        }
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        DirectedGraph dg =new DirectedGraph();
        String filePath = "./data/messages.csv";

        // 加载图数据
        dg.loadGraphFromCSV(filePath);
        boolean running = true;

        while (running) {
            showMenu();

            int choice = getValidInput(scanner);

            switch (choice) {
                case 1: {
                    System.out.print("请输入用户 ID 查询聊天记录：");
                    int userId = scanner.nextInt();
                    dg.queryUser(userId);
                    break;
                }
                case 2: {
                    // 录入新的聊天记录
                    System.out.print("请输入发送者 ID：");
                    int sender = getValidInput(scanner);

                    System.out.print("请输入接收者 ID：");
                    int receiver = getValidInput(scanner);

                    // 验证发送者和接收者是否相同
                    if (sender == receiver) {
                        System.out.println("错误：发送者和接收者不能相同！");
                        break;
                    }

                    System.out.print("请输入消息次数：");
                    int messageCount = getValidInput(scanner);

                    if (messageCount <= 0) {
                        System.out.println("错误：消息次数必须大于 0！");
                        break;
                    }

                    // 录入消息
                    dg.addMessage(sender, receiver, messageCount);
                    break;
                }
                case 3: {
                    // 打印图
                    dg.printGraph();
                    break;
                }
                case 4: {
                    //打印用户数量
                    System.out.println("当前用户数量：" + dg.getUserCount(filePath));
                    break;
                }
                case 5: {
                    System.out.println("请输入第一个用户：");
                    int id1 = getValidInput(scanner);
                    System.out.println("请输入第二个用户：");
                    int id12 = getValidInput(scanner);
                    dg.shortestPath(id1, id12);
                    break;
                }

                case 6: {
                    PageRank pr = new PageRank(dg.getGraph()); // 获取图数据
                    Map<Integer, Double> pagerank = pr.computePageRank();
                    pr.printPageRank(pagerank); // 直接打印不排序
                    break;
                }
                case 7: {
                    PageRank pr = new PageRank(dg.getGraph()); // 获取图数据
                    Map<Integer, Double> pagerank = pr.computePageRank();
                    pr.printTopNPageRank(pagerank, 15); // 打印前 15 名
                    break;
                }
                case 8: {
                    dg.findCommunities();  // 输出所有社区
                    break;
                }
                case 9: {
                    System.out.printf("输入要查询的用户：");
                    int users = getValidInput(scanner);
                    dg.findUserCommunity(users);
                    break;
                }

                case 10: {
                    // 创建一个 HashMap 来存储图的结构，键是节点的 ID，值是该节点的出边集合
                    Map<Integer, Set<Integer>> graph = new HashMap<>(); // 存储有向图

                    // 尝试读取 CSV 文件，并构建图结构
                    try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
                        String line;
                        br.readLine(); // 跳过文件的第一行（表头），假设表头是字段名或列说明

                        // 循环读取每一行数据
                        while ((line = br.readLine()) != null) {
                            // 用逗号分隔每一行的字段，假设 CSV 文件的每一行包含发送者和接收者的信息
                            String[] data = line.split(",");
                            int sender = Integer.parseInt(data[0].trim()); // 解析发送者的 ID
                            int receiver = Integer.parseInt(data[1].trim()); // 解析接收者的 ID

                            // 如果发送者的 ID 在图中不存在，则创建一个新的 HashSet
                            graph.putIfAbsent(sender, new HashSet<>());
                            // 如果接收者的 ID 在图中不存在，则创建一个新的 HashSet
                            graph.putIfAbsent(receiver, new HashSet<>());

                            // 将接收者添加到发送者的邻接集合中，表示发送者指向接收者
                            graph.get(sender).add(receiver);
                        }
                    } catch (IOException e) {
                        // 如果发生 I/O 异常（如文件读取错误），则打印错误堆栈
                        e.printStackTrace();
                    }

                    // 创建两个 HashMap 用于存储每个用户的权威度和枢纽度
                    Map<Integer, Double> authorityScores = new HashMap<>(); // 权威度
                    Map<Integer, Double> hubScores = new HashMap<>(); // 枢纽度

                    // 调用 HITS 算法来计算权威度和枢纽度
                    HITSAlgorithm.computeHITS(graph, authorityScores, hubScores);

                    // 提示用户选择排序方式
                    System.out.println("请选择排序方式：");
                    System.out.println("1. 按 Authority 排序");
                    System.out.println("2. 按 Hub 排序");

                    // 读取用户的输入选项
                    int choices = scanner.nextInt();

                    // 创建一个列表来存储图中的所有用户的权威度或枢纽度条目
                    List<Map.Entry<Integer, Double>> sortedList = new ArrayList<>();

                    // 根据用户选择排序
                    if (choices == 1) {
                        // 如果选择按权威度排序，获取所有权威度的条目并按值从大到小排序
                        sortedList = new ArrayList<>(authorityScores.entrySet());
                        sortedList.sort((a, b) -> Double.compare(b.getValue(), a.getValue())); // 按 Authority 排序
                    } else if (choices == 2) {
                        // 如果选择按枢纽度排序，获取所有枢纽度的条目并按值从大到小排序
                        sortedList = new ArrayList<>(hubScores.entrySet());
                        sortedList.sort((a, b) -> Double.compare(b.getValue(), a.getValue())); // 按 Hub 排序
                    } else {
                        // 如果用户输入了无效的选项，打印错误消息并退出
                        System.out.println("无效的选项！");
                        return;
                    }

                    // 输出排序后的结果，列出用户 ID、权威度和枢纽度
                    System.out.println("用户ID\tAuthority（权威）\tHub（枢纽）");
                    // 遍历排序后的列表，输出每个用户的 ID、权威度和枢纽度
                    for (Map.Entry<Integer, Double> entry : sortedList) {
                        int user = entry.getKey(); // 获取用户 ID
                        // 输出用户 ID、对应的权威度和枢纽度，格式化显示小数点后六位
                        System.out.printf("%d\t%.6f\t%.6f%n", user, authorityScores.get(user), hubScores.get(user));
                    }
                    break;
                }

                case 11: {
                    // 退出程序
                    System.out.println("程序已退出。");
                    running = false;
                    break;
                }
                default: {
                    System.out.println("无效选择，请重新输入！");
                    break;
                }
            }
        }

        scanner.close();
    }
}
