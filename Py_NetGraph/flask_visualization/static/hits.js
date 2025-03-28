document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/hits")
        .then(response => response.json())
        .then(data => {
            // 定义活跃度类别
            const categories = [
                { name: "高活跃", color: "#e74c3c" },
                { name: "中活跃", color: "#f39c12" },
                { name: "低活跃", color: "#3498db" }
            ];

            // 计算 Top 10 用户
            let top10Users = [...data.nodes]
                .sort((a, b) => b.activity - a.activity)  // 按活跃度降序排列
                .slice(0, 10);  // 取前 10 名

            // 更新排行榜
            let top10List = document.getElementById("top10-list");
            top10List.innerHTML = top10Users
                .map(user => `<li>${user.username} - 活跃度: ${user.activity} - Hub: ${user.hub} - Authority: ${user.authority}</li>`)
                .join("");

            let option = {
                title: {
                    text: "消息互动网络",
                    left: "center",
                    textStyle: { fontSize: 20 }
                },
                tooltip: {
                    trigger: "item",
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            return `用户: <strong>${params.data.username}</strong><br>活跃度: ${params.data.activity}<br>Hub: ${params.data.hub}<br>Authority: ${params.data.authority}`;
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
                        if (n.activity > 1800) {
                            category = categories[0];
                        } else if (n.activity > 300) {
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
                            activity: n.activity,
                            hub: n.hub,
                            authority: n.authority
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
