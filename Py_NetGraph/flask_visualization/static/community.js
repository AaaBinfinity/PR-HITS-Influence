document.addEventListener("DOMContentLoaded", function () {
    // 初始化 echarts 图表
    let chart = echarts.init(document.getElementById("chart"));

    // 向服务器请求数据，获取用户社区划分数据
    fetch("/api/user_communities")
        .then(response => response.json())  // 将返回的响应转换为 JSON 格式
        .then(data => {
            // 获取前端展示的社区数据
            let communityMap = data.community_map;
            let nodes = data.nodes;
            let edges = data.edges;
            let colors = data.colors;  // 社区颜色

            console.log("Colors:", colors);  // Debugging log to check colors

            // 展示社区信息并添加复选框
            let communityList = document.getElementById("community-list");
            for (let communityId in communityMap) {
                let communityUsers = communityMap[communityId];

                // 创建复选框
                let checkbox = document.createElement("input");
                checkbox.type = "checkbox";
                checkbox.id = `community-${communityId}`;
                checkbox.checked = true;  // 默认选中所有社区
                checkbox.addEventListener("change", updateChart);  // 监听复选框的变化

                // 创建社区信息
                let communityItem = document.createElement("li");
                communityItem.innerHTML = `社区 ${communityId}：${communityUsers.map(userId => data.nodes.find(node => node.id === userId).username).join(", ")}`;
                communityItem.prepend(checkbox);  // 将复选框放在社区信息前面

                communityList.appendChild(communityItem);
            }

            // 更新图表的显示
            function updateChart() {
                // 获取选中的社区
                let selectedCommunities = Array.from(document.querySelectorAll("input[type='checkbox']"))
                    .filter(checkbox => checkbox.checked)
                    .map(checkbox => parseInt(checkbox.id.split("-")[1]));

                // 更新图例
                let legendData = [];
                selectedCommunities.forEach(i => {
                    legendData.push({
                        name: `社区 ${i + 1}`,  // 标注社区名称
                        icon: 'circle',  // 图例的样式
                        itemStyle: { color: colors[i] }  // 图例颜色
                    });
                });

                // 配置图表的选项
                let option = {
                    title: {
                        text: "用户社区划分网络",  // 图表的标题
                        left: "center",  // 标题位置居中
                        textStyle: { fontSize: 20 }  // 设置标题文字的大小
                    },
                    tooltip: {
                        trigger: "item",  // 鼠标悬停时触发提示框
                        formatter: function (params) {
                            if (params.dataType === "node") {
                                return `用户: <strong>${params.data.name}</strong><br>社区: ${params.data.community}`;
                            }
                            return `用户1: <strong>${params.data.source}</strong> → 用户2: <strong>${params.data.target}</strong>`;
                        }
                    },
                    legend: {
                        data: legendData,  // 添加社区图例
                        left: "center",  // 图例居中显示
                        top: "bottom",  // 图例放置在底部
                        orient: "horizontal",  // 水平排列
                        selectedMode: 'multiple',  // 可以选择显示多个社区
                        itemWidth: 10,  // 设置图例项宽度
                        itemHeight: 10,  // 设置图例项高度
                        textStyle: {
                            fontSize: 14  // 设置图例文字大小
                        },
                        zIndex: 10  // 确保图例在其他元素之上
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
                        label: {
                            show: true,  // 显示节点标签
                            position: "right",  // 标签显示在节点的右侧
                            formatter: "{b}"  // 标签显示节点的名称
                        },
                        // 设置节点数据
                        data: nodes.filter(n => selectedCommunities.includes(n.community)).map(n => {
                            return {
                                name: n.username,  // 用户名
                                id: n.id,  // 用户ID
                                symbolSize: 20,  // 固定大小的节点（你可以根据需要调整）
                                itemStyle: { color: colors[n.community] },  // 根据用户的社区分配颜色
                                community: n.community  // 社区ID
                            };
                        }),
                        // 设置边的数据
                        edges: edges.filter(e => selectedCommunities.includes(nodes.find(node => node.id === e.source).community) &&
                                                 selectedCommunities.includes(nodes.find(node => node.id === e.target).community))
                            .map(e => ({
                                source: e.source.toString(),  // 边的起点
                                target: e.target.toString()   // 边的终点
                            }))
                    }]
                };

                // 设置图表的配置并渲染
                chart.setOption(option);
            }

            // 初始化图表
            updateChart();
        })
        .catch(error => console.error("数据加载失败:", error));  // 错误处理
});
