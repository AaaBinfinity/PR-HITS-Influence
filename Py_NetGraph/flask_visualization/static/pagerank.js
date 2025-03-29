document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/messages_pagerank")
        .then(response => response.json())
        .then(data => {
            // 计算 PageRank Top 10 用户
            let top10Users = [...data.nodes]
                .sort((a, b) => b.pagerank - a.pagerank)  // 按 PageRank 值降序排列
                .slice(0, 10);  // 取前 10 名

            // 更新排行榜
            let top10List = document.getElementById("top10-list");
            top10List.innerHTML = top10Users
                .map(user => `<li>${user.username} - PageRank: ${user.pagerank.toFixed(4)}</li>`)
                .join("");

            let option = {
                title: {
                    text: "用户 PageRank 传播性网络",
                    left: "center",
                    textStyle: { fontSize: 20 }
                },
                tooltip: {
                    trigger: "item",
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            return `用户: <strong>${params.data.username}</strong><br>PageRank: ${params.data.pagerank.toFixed(4)}`;
                        }
                        return `发送: <strong>${params.data.source}</strong> → 接收: <strong>${params.data.target}</strong><br>消息数: ${params.data.weight}`;
                    }
                },
                legend: {
                    orient: "vertical",
                    left: "left",
                    data: ["高影响力", "中影响力", "低影响力"]
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
                toolbox: {
                    show: true,
                    feature: {
                        saveAsImage: { title: "保存图片" },
                        dataZoom: { title: "缩放" },
                        restore: { title: "还原" }
                    },
                    right: "5%"
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
                        if (n.pagerank > 0.05) {
                            category = { name: "高影响力", color: "#e74c3c" };
                        } else if (n.pagerank > 0.005) {
                            category = { name: "中影响力", color: "#f39c12" };
                        } else {
                            category = { name: "低影响力", color: "#3498db" };
                        }
                        return {
                            name: n.username,
                            id: n.id,
                            symbolSize: n.size / 100,
                            itemStyle: { color: category.color },
                            category: category.name,
                            username: n.username,
                            pagerank: n.pagerank
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
                    categories: [
                        { name: "高影响力", color: "#e74c3c" },
                        { name: "中影响力", color: "#f39c12" },
                        { name: "低影响力", color: "#3498db" }
                    ]
                }]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));
});
