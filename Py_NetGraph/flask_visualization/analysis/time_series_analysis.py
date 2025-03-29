import pandas as pd
from database import fetch_data
import pytz

def analyze_by_timestamp():
    """获取消息互动数据并计算时间序列属性"""
    # 查询消息的时间戳数据，确保获取到原始时间戳
    query = "SELECT timestamp FROM messages;"
    df_time = fetch_data(query)

    # 检查数据是否为空
    if df_time.empty:
        print("No data retrieved from the database.")
        return {"time_series": []}

    # 将时间戳转换为datetime类型
    df_time["timestamp"] = pd.to_datetime(df_time["timestamp"], errors='coerce')

    # 如果时间数据中存在无效值，去除它们
    df_time = df_time.dropna(subset=["timestamp"])

    # 将时间戳转换为北京时间
    df_time["beijing_time"] = df_time["timestamp"].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')

    # 获取当前时间，确保 `now` 是带时区的
    now = pd.Timestamp.now(tz="Asia/Shanghai")
    print("Current time (now):", now)

    # 过滤最近 24 小时数据
    df_time = df_time[df_time["beijing_time"] >= now - pd.Timedelta(hours=24)]

    print("Filtered data:\n", df_time.head())

    # 按小时进行重采样（或者按天进行重采样，依据需求调整）
    df_time.set_index("beijing_time", inplace=True)
    msg_count = df_time.resample('H').size()  # 'H' 表示按小时分组

    # 平滑处理：使用滚动平均
    window_size = 10  # 设置窗口大小
    msg_count_smoothed = msg_count.rolling(window=window_size, min_periods=1).mean().round(0)

    # 归一化时间戳，用于 JSON 输出
    timestamps = msg_count.index.astype(str).tolist()
    smoothed_values = msg_count_smoothed.tolist()

    # 构造 JSON 格式的时间序列数据
    time_series = [{"timestamp": timestamps[i], "count": smoothed_values[i]} for i in range(len(timestamps))]

    return {"time_series": time_series}
