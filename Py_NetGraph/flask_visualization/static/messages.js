document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/messages")
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
                .map(user => `<li>${user.username} - 活跃度: ${user.activity}</li>`)
                .join("");

            let option = {
                title: {
                    text: "消息互动网络",
                    left: "center",
                    textStyle: { fontSize: 20 }
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
                tooltip: {
                    trigger: "item",
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            return `用户: <strong>${params.data.username}</strong><br>活跃度: ${params.data.activity}`;
                        }
                        return `发送: <strong>${params.data.source}</strong> → 接收: <strong>${params.data.target}</strong><br>消息数: ${params.data.weight}`;
                    }
                },
                legend: {
                    orient: "vertical",
                    left: "left",
                    data: categories.map(c => c.name),
                    textStyle: {
                        color: "#333"  // 图例文字颜色
                    },
                    itemWidth: 12,  // 图例图标宽度
                    itemHeight: 12, // 图例图标高度
                    formatter: function (name) {
                        // 将图例颜色自定义为每个活跃度类别的颜色
                        const category = categories.find(c => c.name === name);
                        return `{${name}|${name}}`;
                    },
                    textStyle: {
                        rich: {
                            "高活跃": { color: "#e74c3c" },
                            "中活跃": { color: "#f39c12" },
                            "低活跃": { color: "#3498db" }
                        }
                    }
                },
                series: [{
                    type: "graph",
                    layout: "force",
                    roam: true,
                    draggable: true,
                    force: {
                        repulsion: 230,
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
                            activity: n.activity
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
                    categories: categories.map(c => ({ name: c.name, itemStyle: { color: c.color } }))
                }]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));
});
