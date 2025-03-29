document.addEventListener("DOMContentLoaded", function() {
    fetch("/api/messages_hits")
        .then(response => response.json())
        .then(data => {
            let chart = echarts.init(document.getElementById("chart"));
            let option = {
                title: { text: "用户 HITS 影响力分析", left: "center" },
                tooltip: {},
                series: [{
                    type: "graph",
                    layout: "force",
                    data: data.nodes.map(node => ({
                        name: node.username,
                        value: node.authority + node.hub,
                        symbolSize: node.size,
                        id: node.id
                    })),
                    links: data.edges.map(edge => ({
                        source: edge.source,
                        target: edge.target,
                        value: edge.weight
                    })),
                    roam: true,
                    label: { show: true, position: "right" },
                    force: { repulsion: 100 }
                }]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败", error));
});
