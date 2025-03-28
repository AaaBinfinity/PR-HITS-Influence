document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/centrality")
        .then(response => response.json())
        .then(data => {
            // 定义中心性类别
            const categories = [
                { name: "高中心性", color: "#e74c3c" },
                { name: "中中心性", color: "#f39c12" },
                { name: "低中心性", color: "#3498db" }
            ];

            // 计算 Top 10 用户
            let top10Users = [...data.nodes]
                .sort((a, b) => b.centrality - a.centrality)  // 按中心性降序排列
                .slice(0, 10);

            // 更新排行榜
            let top10List = document.getElementById("top10-list");
            top10List.innerHTML = top10Users
                .map(user => `<li>${user.username} - 中心性: ${user.centrality}</li>`)
                .join("");

            let option = {
                title: {
                    text: "用户中心性分析",
                    left: "center",
                    textStyle: { fontSize: 20 }
                },
                tooltip: {
                    trigger: "item",
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            return `用户: <strong>${params.data.username}</strong><br>中心性: ${params.data.centrality}`;
                        }
                        return `发送: <strong>${params.data.source}</strong> → 接收: <strong>${params.data.target}</strong><br>消息数: ${params.data.weight}`;
                    }
                },
                legend: {
                    orient: "vertical",
                    left: "left",
                    data: categories.map(c => c.name)
                },
                series: [{
                    type: "graph",
                    layout: "force",
                    roam: true,
                    draggable: true,
                    force: {
                        repulsion: 180,
                        edgeLength: [60, 220]
                    },
                    label: {
                        show: true,
                        position: "right",
                        formatter: "{b}"
                    },
                    edgeSymbol: ["none", "arrow"],
                    edgeSymbolSize: [0, 8],
                    data: data.nodes.map(n => {
                        let category;
                        if (n.centrality > 1800) {
                            category = categories[0];
                        } else if (n.centrality > 300) {
                            category = categories[1];
                        } else {
                            category = categories[2];
                        }
                        return {
                            name: n.username,
                            id: n.id,
                            symbolSize: n.size / 100,
                            itemStyle: { color: category.color },
                            category: category.name,
                            username: n.username,
                            centrality: n.centrality
                        };
                    }),
                    edges: data.edges.map(e => ({
                        source: e.source.toString(),
                        target: e.target.toString(),
                        weight: e.weight,
                        lineStyle: {
                            color: e.source === e.target ? '#BDC3C7' : (e.source > e.target ? '#adcffa' : '#ffd2a8'),
                            width: 2.0,
                            curveness: 0.05
                        }
                    })),
                    categories: categories
                }]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));
});
