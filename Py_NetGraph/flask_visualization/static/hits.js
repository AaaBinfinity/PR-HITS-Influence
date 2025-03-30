document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));  // 初始化图表
    const sortMethod = document.getElementById("sort-method");  // 获取排序方式选择元素
    const sizeMethod = document.getElementById("size-method");  // 获取大小方式选择元素
    const scaleFactor = 150;  // 缩放因子，用于调整节点的大小

    let cachedData = null;  // 缓存数据，用于避免重复请求

    // 根据 authority 和 hub 分数分类节点
    function categorizeNode(node) {
        if (node.authority > node.hub) {  // 如果 authority 分数大于 hub 分数
            return { name: "高 Authority", color: "#e74c3c" };  // 高 Authority 分类，颜色为红色
        } else if (node.hub > node.authority) {  // 如果 hub 分数大于 authority 分数
            return { name: "高 Hub", color: "#f39c12" };  // 高 Hub 分类，颜色为橙色
        } else {  // 如果 authority 和 hub 分数相等
            return { name: "其他", color: "#3498db" };  // 其他分类，颜色为蓝色
        }
    }

    // 更新 Top 10 排行榜
    function updateTop10(data, method) {
        const top10Users = [...data.nodes]
            .sort((a, b) => b[method] - a[method])  // 按照选择的排序方法排序
            .slice(0, 10);  // 取前 10 名用户

        const top10List = document.getElementById("top10-list");  // 获取排行榜列表元素
        top10List.innerHTML = top10Users
            .map(user => `<li>${user.username} - ${method.charAt(0).toUpperCase() + method.slice(1)}: ${user[method].toFixed(3)}</li>`)  // 格式化每个用户的排名
            .join("");  // 将所有用户的数据拼接成 HTML 列表项
    }

    // 更新图表
    function updateChart(data) {
        const selectedSizeMethod = sizeMethod.value;  // 获取选择的节点大小方法

        const option = {
            title: {
                text: "用户 HITS 影响力分析",  // 图表标题
                left: "center",  // 标题居中
                textStyle: { fontSize: 20 }  // 设置标题的字体大小
            },
            tooltip: {
                trigger: "item",  // 鼠标悬停触发
                formatter: function (params) {
                    if (params.dataType === "node") {  // 如果是节点
                        const authority = params.data.authority.toFixed(6);  // 将 authority 限制为 6 位小数
                        const hub = params.data.hub.toFixed(6);  // 将 hub 限制为 6 位小数
                        return `用户: <strong>${params.data.username}</strong><br>Authority: ${authority}<br>Hub: ${hub}`;  // 显示节点的详细信息
                    }
                    return `发送: <strong>${params.data.source}</strong> → 接收: <strong>${params.data.target}</strong><br>消息数: ${params.data.weight}`;  // 显示边的信息
                }
            },
            legend: {
                orient: "vertical",  // 图例垂直排列
                left: "left",  // 图例在左边
                data: ["高 Authority", "高 Hub", "其他"]  // 图例的分类数据
            },
            series: [{
                type: "graph",  // 图表类型为图形
                layout: "force",  // 使用力引导布局
                roam: true,  // 开启图表的缩放和拖动
                draggable: true,  // 开启节点拖动
                force: {
                    repulsion: 180,  // 排斥力
                    edgeLength: [60, 220]  // 边的长度范围
                },
                toolbox: {
                    show: true,  // 显示工具箱
                    feature: {
                        saveAsImage: { title: "保存图片" },  // 保存图片功能
                        dataZoom: { title: "缩放" },  // 缩放功能
                        restore: { title: "还原" }  // 还原功能
                    },
                    right: "5%"  // 工具箱右对齐
                },
                label: {
                    show: true,  // 显示标签
                    position: "right",  // 标签位置在节点右侧
                    formatter: "{b}"  // 标签显示节点名称
                },
                edgeSymbol: ["none", "arrow"],  // 边的符号，箭头表示边的方向
                edgeSymbolSize: [0, 8],  // 箭头的大小
                data: data.nodes.map(n => {
                    const category = categorizeNode(n);  // 获取节点的分类
                    return {
                        name: n.username,  // 节点名称
                        id: n.id,  // 节点ID
                        symbolSize: Math.max(n[selectedSizeMethod] * scaleFactor, 10),  // 节点大小，根据选定的大小方法进行计算
                        itemStyle: { color: category.color },  // 节点颜色
                        category: category.name,  // 节点分类
                        username: n.username,  // 用户名
                        authority: n.authority,  // Authority 值
                        hub: n.hub  // Hub 值
                    };
                }),
                edges: data.edges.map(e => ({
                    source: e.source.toString(),  // 边的起始节点
                    target: e.target.toString(),  // 边的目标节点
                    weight: e.weight,  // 边的权重
                    lineStyle: {
                        color: e.source === e.target ? '#BDC3C7' : (e.source > e.target ? '#adcffa' : '#ffd2a8'),  // 边的颜色，环形连接采用灰色，其他连接根据源节点和目标节点不同颜色
                        width: 2.0,  // 边的宽度
                        curveness: 0.05  // 边的曲率
                    }
                })),
                categories: [
                    { name: "高 Authority", color: "#e74c3c" },  // 高 Authority 类别，颜色为红色
                    { name: "高 Hub", color: "#f39c12" },  // 高 Hub 类别，颜色为橙色
                    { name: "其他", color: "#3498db" }  // 其他类别，颜色为蓝色
                ]
            }]
        };

        chart.setOption(option);  // 更新图表的配置项
    }

    // 如果缓存数据为空，则请求数据并缓存
    if (!cachedData) {
        fetch("/api/messages_hits")
            .then(response => response.json())
            .then(data => {
                cachedData = data;  // 存储获取的数据
                updateTop10(data, sortMethod.value);  // 更新排行榜
                updateChart(data);  // 更新图表

                // 添加排序和大小方法的事件监听器
                sortMethod.addEventListener("change", () => updateTop10(cachedData, sortMethod.value));  // 当排序方式变化时，更新排行榜
                sizeMethod.addEventListener("change", () => updateChart(cachedData));  // 当大小方式变化时，更新图表
            })
            .catch(error => console.error("数据加载失败:", error));  // 捕获并处理加载数据的错误
    } else {
        updateTop10(cachedData, sortMethod.value);  // 如果缓存数据存在，直接更新排行榜
        updateChart(cachedData);  // 直接更新图表
    }

    // 使图表在窗口大小变化时自适应
    window.addEventListener('resize', function() {
        chart.resize();  // 调整图表大小
    });
});
