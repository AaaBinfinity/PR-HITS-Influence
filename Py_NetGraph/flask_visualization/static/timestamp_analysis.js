document.addEventListener("DOMContentLoaded", function () {
    let chart = echarts.init(document.getElementById("chart"));

    fetch("/api/by_timestamp")
        .then(response => response.json())
        .then(data => {
            let timestamps = data.time_series.map(d => d.timestamp);
            let counts = data.time_series.map(d => d.count);

            let option = {
                title: {
                    text: "消息互动趋势",
                    left: "center",
                    textStyle: { fontSize: 18 }
                },
                tooltip: {
                    trigger: "axis",
                    formatter: function (params) {
                        let date = params[0].axisValue;
                        let value = params[0].data;
                        return `时间: <strong>${date}</strong><br>消息数: <strong>${value.toFixed(1)}</strong>`;
                    }
                },
                xAxis: {
                    type: "category",
                    name: "时间",
                    data: timestamps,
                    axisLabel: { rotate: 45 }
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
                yAxis: {
                    type: "value",
                    name: "消息数"
                },
                dataZoom: [
                    {
                        type: "slider", // 添加滚动条
                        show: true,
                        start: 50, // 默认显示后半部分
                        end: 100,
                        height: 10, // 改变滚动条的高度
                        bottom: 10,
                        handleStyle: {
                            color: '#007bff', // 滑块颜色
                            borderColor: '#0056b3', // 滑块边框颜色
                            borderWidth: 2, // 滑块边框宽度
                            shadowBlur: 4, // 滑块阴影效果
                            shadowColor: 'rgba(0, 123, 255, 0.5)', // 滑块阴影颜色
                        },
                        fillerColor: 'rgba(0, 123, 255, 0.2)', // 填充颜色
                        borderColor: '#0056b3', // 滑动条边框颜色
                        backgroundColor: '#e0e0e0' // 背景颜色
                    }
                ],
                series: [
                    {
                        name: "消息数",
                        type: "line",
                        data: counts,
                        smooth: true,
                        lineStyle: { color: "blue" },
                        itemStyle: { color: "blue" },
                        label: {
                            show: true,
                            position: "top"
                        }
                    }
                ]
            };
            chart.setOption(option);
        })
        .catch(error => console.error("数据加载失败:", error));
});
