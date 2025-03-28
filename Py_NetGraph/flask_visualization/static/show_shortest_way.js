document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/social_network")
        .then(response => response.json())
        .then(data => {
            let categories = [
                { name: "活跃用户" },
                { name: "普通用户" }
            ];

            let option = {
                title: {
                    text: "社交关系网络",
                    left: "center",
                    textStyle: { fontSize: 20 }
                },
                tooltip: {
                    trigger: "item",
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            return `用户: <strong>${params.data.username}</strong><br>好友数: ${params.data.degree}`;
                        }
                        return `连接: ${params.data.source} ↔ ${params.data.target}`;
                    }
                },
                legend: {
                    data: categories.map(c => c.name),
                    left: "right"
                },
                series: [{
                    type: "graph",
                    layout: "force",
                    roam: true,
                    draggable: true,
                    force: {
                        repulsion: 150,
                        edgeLength: [50, 200]
                    },
                    label: {
                        show: true,
                        position: "right",
                        formatter: "{b}"
                    },
                    edgeSymbol: ["circle"],
                    edgeSymbolSize: [4, 10],
                    categories: categories,
                    data: data.nodes.map(n => ({
                        name: n.username,
                        id: n.id,
                        symbolSize: n.size / 100,
                        itemStyle: { color: n.color },
                        category: n.degree > 5 ? 0 : 1,  // 🎯 这里根据好友数区分类别
                        username: n.username,
                        degree: n.degree
                    })),
                    edges: data.edges.map(e => ({
                        source: e.source.toString(),
                        target: e.target.toString()
                    }))
                }]
            };

            chart.setOption(option);

            // 查询最短路径
            document.getElementById("find-path-btn").addEventListener("click", function() {
                let startUser = document.getElementById("start-user").value;
                let endUser = document.getElementById("end-user").value;

                // 请求后端获取路径
                fetch(`/api/shortest_path?start_user=${startUser}&end_user=${endUser}`)
                    .then(response => response.json())
                    .then(result => {
                        if (result.path) {
                            highlightPath(result.path);
                        } else {
                            alert(result.error || "未找到路径");
                        }
                    })
                    .catch(error => console.error("查询路径失败:", error));
            });

            // 高亮显示路径
            function highlightPath(path) {
                // 清空所有节点的高亮
                option.series[0].data.forEach(node => node.itemStyle = { color: node.color });

                // 高亮显示路径上的节点和边
                path.forEach((user, index) => {
                    let node = option.series[0].data.find(n => n.username === user.toString());
                    if (node) {
                        node.itemStyle = { color: "red" }; // 高亮显示节点
                    }

                    if (index < path.length - 1) {
                        let edge = option.series[0].edges.find(e =>
                            (e.source === path[index].toString() && e.target === path[index + 1].toString()) ||
                            (e.source === path[index + 1].toString() && e.target === path[index].toString())
                        );
                        if (edge) {
                            edge.lineStyle = { color: "red", width: 3 }; // 高亮显示边
                        }
                    }
                });

                // 更新图表显示
                chart.setOption(option);
            }

            // 刷新按钮功能
            document.getElementById("refresh-btn").addEventListener("click", function() {
                // 清空输入框
                document.getElementById("start-user").value = "";
                document.getElementById("end-user").value = "";

                // 清空图表
                chart.clear();
            });
        })
        .catch(error => console.error("数据加载失败:", error));
});
