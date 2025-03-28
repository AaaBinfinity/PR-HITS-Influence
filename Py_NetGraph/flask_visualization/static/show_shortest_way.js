document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/social_network")
        .then(response => response.json())
        .then(data => {
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
                    data: data.nodes.map(n => ({
                        name: n.username,
                        id: n.id,
                        symbolSize: n.size / 100,
                        itemStyle: { color: n.color },
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

            document.getElementById("find-path-btn").addEventListener("click", function() {
                let startUser = document.getElementById("start-user").value;
                let endUser = document.getElementById("end-user").value;

                fetch(`/api/shortest_path?start_user=${startUser}&end_user=${endUser}`)
                    .then(response => response.json())
                    .then(result => {
                        if (result.path) {
                            highlightPath(result.path);
                            document.getElementById("result").innerHTML = `
                                <p>路径: ${result.path.join(" -> ")}</p>
                                <p>步骤数: ${result.steps} 步</p>
                            `;
                        } else {
                            alert(result.error || "未找到路径");
                        }
                    })
                    .catch(error => console.error("查询路径失败:", error));
            });

            // 高亮显示路径
            function highlightPath(path) {
                // 克隆原始数据
                let newNodes = JSON.parse(JSON.stringify(option.series[0].data));
                let newEdges = JSON.parse(JSON.stringify(option.series[0].edges));

                // 1️⃣ **高亮路径上的节点**
                path.forEach(user => {
                    let nodeIndex = newNodes.findIndex(n => n.username === user.toString());
                    if (nodeIndex !== -1) {
                        newNodes[nodeIndex] = {
                            ...newNodes[nodeIndex],
                            symbolSize: 20, // 增大节点
                            itemStyle: { color: "purple" }, // 高亮节点为红色
                            emphasis: { itemStyle: { color: "purple" } } // 鼠标悬浮时高亮
                        };
                    }
                });

                // 2️⃣ **高亮路径上的边**
                for (let i = 0; i < path.length - 1; i++) {
                    let edgeIndex = newEdges.findIndex(e =>
                        (e.source === path[i].toString() && e.target === path[i + 1].toString()) ||
                        (e.source === path[i + 1].toString() && e.target === path[i].toString())
                    );
                    if (edgeIndex !== -1) {
                        newEdges[edgeIndex] = {
                            ...newEdges[edgeIndex],
                            lineStyle: { color: "red", width: 5 } // 更粗的红色边
                        };
                    }
                }

                // 3️⃣ **强制更新图表**
                chart.setOption({
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
                        data: newNodes, // 更新节点
                        edges: newEdges  // 更新边
                    }]
                });
            }

            document.getElementById("refresh-btn").addEventListener("click", function() {
                document.getElementById("start-user").value = "";
                document.getElementById("end-user").value = "";
                chart.clear();
            });
        })
        .catch(error => console.error("数据加载失败:", error));
});
