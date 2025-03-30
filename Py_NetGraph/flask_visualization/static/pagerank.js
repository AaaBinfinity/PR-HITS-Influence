document.addEventListener("DOMContentLoaded", function () {
    // 初始化 echarts 图表
    let chart = echarts.init(document.getElementById("chart"));

    // 向服务器请求数据，获取 PageRank 相关数据
    fetch("/api/messages_pagerank")
        .then(response => response.json())  // 将返回的响应转换为 JSON 格式
        .then(data => {
            // 计算 PageRank 排行前 10 名用户
            let top10Users = [...data.nodes]
                .sort((a, b) => b.pagerank - a.pagerank)  // 根据 PageRank 值降序排列
                .slice(0, 10);  // 取前 10 名用户

            // 更新页面上的前 10 名用户排行榜
            let top10List = document.getElementById("top10-list");
            top10List.innerHTML = top10Users
                .map(user => `<li>${user.username} - PageRank: ${user.pagerank.toFixed(4)}</li>`)
                .join("");  // 将每个用户的名称和 PageRank 值以列表的形式显示

            // 配置图表的选项
            let option = {
                title: {
                    text: "用户 PageRank 传播性网络",  // 图表的标题
                    left: "center",  // 标题位置居中
                    textStyle: { fontSize: 20 }  // 设置标题文字的大小
                },
                tooltip: {
                    trigger: "item",  // 鼠标悬停时触发提示框
                    formatter: function (params) {
                        if (params.dataType === "node") {
                            // 如果悬停的是节点，显示用户的名称和 PageRank 值
                            return `用户: <strong>${params.data.username}</strong><br>PageRank: ${params.data.pagerank.toFixed(4)}`;
                        }
                        // 如果悬停的是边，显示消息发送和接收者的信息
                        return `发送: <strong>${params.data.source}</strong> → 接收: <strong>${params.data.target}</strong><br>消息数: ${params.data.weight}`;
                    }
                },
                legend: {
                    orient: "vertical",  // 设置图例的方向为纵向
                    left: "left",  // 图例位置在左侧
                    data: ["高影响力", "中影响力", "低影响力"]  // 图例的项
                },
                series: [{
                    type: "graph",  // 图表类型为图形（即网络图）
                    layout: "force",  // 使用力导向布局
                    roam: true,  // 允许图表自由拖动
                    draggable: true,  // 允许节点拖动
                    force: {
                        repulsion: 230,  // 节点之间的排斥力
                        edgeLength: [60, 220]  // 边的长度范围
                    },
                    toolbox: {
                        show: true,  // 显示工具箱
                        feature: {
                            saveAsImage: { title: "保存图片" },  // 允许保存图片
                            dataZoom: { title: "缩放" },  // 允许缩放
                            restore: { title: "还原" }  // 允许恢复到初始状态
                        },
                        right: "5%"  // 工具箱位置
                    },
                    label: {
                        show: true,  // 显示节点标签
                        position: "right",  // 标签显示在节点的右侧
                        formatter: "{b}"  // 标签显示节点的名称
                    },
                    edgeSymbol: ["none", "arrow"],  // 边的样式，箭头表示有方向
                    edgeSymbolSize: [0, 8],  // 设置箭头的大小
                    // 设置节点数据
                    data: data.nodes.map(n => {
                        let category;
                        // 根据 PageRank 值来划分影响力分类
                        if (n.pagerank > 0.05) {
                            category = { name: "高影响力", color: "#e74c3c" };  // 高影响力用户
                        } else if (n.pagerank > 0.005) {
                            category = { name: "中影响力", color: "#f39c12" };  // 中影响力用户
                        } else {
                            category = { name: "低影响力", color: "#3498db" };  // 低影响力用户
                        }
                        return {
                            name: n.username,  // 用户名
                            id: n.id,  // 用户ID
                            symbolSize: n.size / 100,  // 节点大小（根据用户大小进行调整）
                            itemStyle: { color: category.color },  // 根据影响力类别设置颜色
                            category: category.name,  // 分类名称
                            username: n.username,  // 用户名
                            pagerank: n.pagerank  // PageRank 值
                        };
                    }),
                    // 设置边的数据
                    edges: data.edges.map(e => ({
                        source: e.source.toString(),  // 边的起点
                        target: e.target.toString(),  // 边的终点
                        weight: e.weight,  // 边的权重（消息数）
                        lineStyle: {
                            color: e.source === e.target ? '#BDC3C7' : (e.source > e.target ? '#adcffa' : '#ffd2a8'),  // 设置边的颜色
                            width: 2.0,  // 设置边的宽度
                            curveness: 0.05  // 设置边的弯曲度
                        }
                    })),
                    categories: [
                        { name: "高影响力", color: "#e74c3c" },
                        { name: "中影响力", color: "#f39c12" },
                        { name: "低影响力", color: "#3498db" }
                    ]  // 定义影响力分类的颜色
                }]
            };

            // 设置图表的配置并渲染
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));  // 错误处理
});
