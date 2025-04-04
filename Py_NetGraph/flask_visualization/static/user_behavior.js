document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("user-chart"));

    let currentPage = 1;
    const itemsPerPage = 20;

    // Fetch user data and initialize table and chart
    fetch("/api/user_behavior")
        .then(response => response.json())
        .then(data => {
            let usernames = data.user_behavior.map(d => d.username);
            let messageCounts = data.user_behavior.map(d => d.message_count);
            let userBehavior = data.user_behavior;

            // Function to render the table based on the current page
            function renderTable(page) {
                let start = (page - 1) * itemsPerPage;
                let end = start + itemsPerPage;
                let pageData = userBehavior.slice(start, end);

                // 填充表格数据
                let tableBody = document.getElementById('user-table').getElementsByTagName('tbody')[0];
                tableBody.innerHTML = "";
                pageData.forEach(user => {
                    let row = document.createElement('tr');
                    row.innerHTML = `<td>${user.user_id}</td><td>${user.username}</td><td>${user.message_count}</td><td>${user.active_period}</td>`;
                    tableBody.appendChild(row);
                });

                // 更新分页信息
                document.getElementById("page-num").textContent = `第 ${currentPage} 页`;
            }

            // Initialize the table and chart
            renderTable(currentPage);

            // Configure ECharts chart
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
                                let colors = [
                                    "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
                                    "#FF8C00", "#FFD700", "#ADFF2F", "#00FFFF", "#8A2BE2",
                                    "#753252", "#00FA9A"
                                ];
                                return colors[params.dataIndex % colors.length];
                            },
                            barBorderRadius: [4, 4, 0, 0] // 圆角柱子
                        },
                        label: {
                            show: true,
                            position: "top",
                            color: "#333"
                        }
                    }
                ],
                dataZoom: [
                    {
                        type: "slider",
                        show: true,
                        xAxisIndex: [0],
                        start: 0,   // 默认从数据的第一个位置开始
                        end: 50,    // 默认显示30%的数据
                        handleSize: "8", // 滚动条滑块大小
                        textStyle: {
                            color: "#333"
                        },
                        bottom: 0 // 滚动条位置
                    }
                ]
            };
            chart.setOption(option);

            // Pagination buttons
            document.getElementById("prev-page").addEventListener("click", function () {
                if (currentPage > 1) {
                    currentPage--;
                    renderTable(currentPage);
                }
            });

            document.getElementById("next-page").addEventListener("click", function () {
                if (currentPage * itemsPerPage < userBehavior.length) {
                    currentPage++;
                    renderTable(currentPage);
                }
            });
        })
        .catch(error => console.error("数据加载失败:", error));
});