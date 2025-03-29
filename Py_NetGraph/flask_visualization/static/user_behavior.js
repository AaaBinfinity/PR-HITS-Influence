document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("user-chart"));

    fetch("/api/user_behavior")
        .then(response => response.json())
        .then(data => {
            let usernames = data.user_behavior.map(d => d.username);
            let messageCounts = data.user_behavior.map(d => d.message_count);

            // 填充表格数据
            let tableBody = document.getElementById('user-table');
            tableBody.innerHTML = "";
            data.user_behavior.forEach(user => {
                let row = document.createElement('tr');
                row.innerHTML = `<td>${user.user_id}</td><td>${user.username}</td><td>${user.message_count}</td><td>${user.active_period}</td>`;
                tableBody.appendChild(row);
            });

            // 配置 ECharts 图表
            let option = {
                title: {
                    text: "用户行为分析",
                    left: "center",
                    textStyle: { fontSize: 18 }
                },
                legend: {
                    data: ["消息数"], // 图例
                    top: "5%",
                    left: "center"
                },
                tooltip: {
                    trigger: "axis",
                    axisPointer: {
                        type: "shadow"
                    },
                    backgroundColor: "rgba(50,50,50,0.8)",
                    textStyle: {
                        color: "#fff"
                    },
                    formatter: function (params) {
                        let username = params[0].axisValue;
                        let value = params[0].data;
                        return `👤 用户名: <strong>${username}</strong><br>💬 消息数: <strong>${value}</strong>`;
                    }
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
                xAxis: {
                    type: "category",
                    name: "用户名",
                    data: usernames,
                    axisLabel: {
                        rotate: 30,
                        interval: 0,
                        color: "#333"
                    }
                },
                yAxis: {
                    type: "value",
                    name: "消息数",
                    splitLine: {
                        show: true,
                        lineStyle: {
                            type: "dashed"
                        }
                    }
                },
                series: [
                    {
                        name: "消息数",
                        type: "bar",
                        data: messageCounts,
                        itemStyle: {
                            color: function (params) {
                                let colors = ["#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF"];
                                return colors[params.dataIndex % colors.length]; // 五彩颜色交替
                            },
                            barBorderRadius: [4, 4, 0, 0] // 圆角柱子
                        },
                        label: {
                            show: true,
                            position: "top",
                            color: "#333"
                        }
                    }
                ]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));
});
