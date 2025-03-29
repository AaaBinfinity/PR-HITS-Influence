document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/social_network")
        .then(response => response.json())
        .then(data => {
            let categories = [
                { name: "活跃用户" },
                { name: "普通用户" }
            ];

            // 📊 计算 Top 10 用户（按好友数降序排序）
            let top10Users = [...data.nodes]
                .sort((a, b) => b.degree - a.degree)  // 按好友数排序
                .slice(0, 10);  // 取前 10 名

            // 📝 更新排行榜
            let top10List = document.getElementById("top10-list");
            top10List.innerHTML = top10Users
                .map(user => `<li>${user.username} - 好友数: ${user.degree}</li>`)
                .join("");

            let option = {
                title: {
                    text: "社交关系网络",
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
                    left: "5%"
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
                    edgeSymbol: ["circle"],  // 只保留圆形，去掉箭头
                    edgeSymbolSize: [4],  // 设置边缘符号大小
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
        })
        .catch(error => console.error("数据加载失败:", error));
});
