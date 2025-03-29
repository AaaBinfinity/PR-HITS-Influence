document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/friend_distribution")
        .then(response => response.json())
        .then(data => {
            let mean_friends = data.stats.mean_friends;
            let median_friends = data.stats.median_friends;

            let option = {
                toolbox: {
                    show: true,
                    feature: {
                        saveAsImage: { title: "保存图片" },
                        dataZoom: { title: "缩放" },
                        restore: { title: "还原" }
                    },
                    right: "5%"
                },
                title: {
                    text: "好友数量分布",
                    left: "center",
                    textStyle: { fontSize: 18 }
                },
                tooltip: {
                    trigger: "item",
                    formatter: function (params) {
                        return `用户 ID: <strong>${params.data.user_id}</strong><br>好友数: <strong>${params.data.value}</strong>`;
                    }
                },
                legend: {
                    data: ["好友数", "均值", "中位数"],
                    bottom: "5%",
                    left: "center"
                },
                grid: {
                    left: "10%",
                    right: "10%",
                    bottom: "20%",
                    containLabel: true
                },
                xAxis: {
                    type: "category",
                    name: "用户ID",
                    data: data.friend_data.map(d => d.user_id),
                    axisLabel: { interval: 0, rotate: 45 }
                },
                yAxis: {
                    type: "value",
                    name: "好友数量"
                },
                series: [
                    {
                        name: "好友数",
                        type: "bar",
                        data: data.friend_data.map(d => ({
                            value: d.friend_count,
                            itemStyle: { color: d.color },
                            user_id: d.user_id
                        })),
                        label: {
                            show: true,
                            position: "top"
                        }
                    },
                    {
                        name: "均值",
                        type: "line",
                        markLine: {
                            symbol: "none",
                            data: [
                                {
                                    name: "均值",
                                    yAxis: mean_friends,
                                    label: { formatter: `均值: ${mean_friends.toFixed(1)}` },
                                    lineStyle: { color: "red", type: "dashed" }
                                }
                            ]
                        }
                    },
                    {
                        name: "中位数",
                        type: "line",
                        markLine: {
                            symbol: "none",
                            data: [
                                {
                                    name: "中位数",
                                    yAxis: median_friends,
                                    label: { formatter: `中位数: ${median_friends.toFixed(1)}` },
                                    lineStyle: { color: "blue", type: "dashed" }
                                }
                            ]
                        }
                    }
                ]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));
});
