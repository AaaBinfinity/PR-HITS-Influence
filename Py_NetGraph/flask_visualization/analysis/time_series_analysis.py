import pandas as pd
from database import fetch_data


def analyze_by_timestamp():
    """
    按时间戳分析消息数量，并将时间转换为北京时间（UTC+8）。

    1. 从数据库 `messages` 表中获取消息时间戳。
    2. 将 UTC 时间转换为北京时间（+8 时区）。
    3. 统计每个小时的消息数量，并按时间排序。
    4. 生成 JSON 格式的结果，返回时间序列数据。

    :return: 以 JSON 形式返回 {"time_series": [{"timestamp": str, "count": float}, ...]}
    """
    query = """
    SELECT
        DATE_FORMAT(CONVERT_TZ(timestamp, '+00:00', '+08:00'), '%Y-%m-%d %H:00:00') AS timestamp,
        COUNT(*) AS count
    FROM
        messages
    GROUP BY
        DATE_FORMAT(CONVERT_TZ(timestamp, '+00:00', '+08:00'), '%Y-%m-%d %H:00:00')
    ORDER BY
        timestamp;
    """

    # 从数据库获取数据
    df = fetch_data(query)

    # 检查数据是否为空
    if df is None or df.empty:
        return {"time_series": []}

    # 生成时间序列数据列表
    time_series = []
    for _, row in df.iterrows():
        time_series.append({
            "timestamp": row["timestamp"],  # 转换后的北京时间
            "count": float(row["count"])  # 确保 `count` 是浮点数格式
        })

    return {"time_series": time_series}


def analyze_user_behavior():
    """
    获取用户行为数据并生成分析报告。

    1. 查询 `messages` 表和 `users` 表，获取用户 ID、用户名、消息时间和消息内容。
    2. 处理时间格式，将 UTC 时间转换为北京时间。
    3. 统计每小时的用户活跃度，找出每个用户最活跃的时间段。
    4. 计算每个用户发送的总消息数量。
    5. 生成用户行为分析报告，并返回 JSON 结构。

    :return: 以 JSON 形式返回 {"user_behavior": [{"user_id": int, "username": str, "message_count": int, "active_period": str}, ...]}
    """
    query = """
        SELECT m.sender_id AS user_id, u.username, m.timestamp, m.content AS message 
        FROM messages m
        JOIN users u ON m.sender_id = u.id 
    """

    # 获取数据
    df = fetch_data(query)

    # 检查数据是否为空
    if df is None or df.empty:
        print("No data retrieved from the database.")
        return {"user_behavior": []}

    # 打印前几行数据，检查数据格式（调试用）
    print(df.head())

    # 将时间戳转换为 pandas 日期时间格式
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

    # 过滤掉转换失败的时间数据
    df = df.dropna(subset=["timestamp"])

    # 先 localize 为 UTC，然后转换为北京时间（Asia/Shanghai）
    df["beijing_time"] = df["timestamp"].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')

    # 统计每小时的用户活跃度
    df.set_index("beijing_time", inplace=True)
    user_activity = df.groupby([pd.Grouper(freq='H'), 'user_id']).size().unstack(fill_value=0)

    # 找出每个用户最活跃的时间段（发送消息最多的小时）
    user_active_period = user_activity.idxmax(axis=0)

    # 计算每个用户的消息总数
    user_message_count = df.groupby('user_id').size()

    # 获取用户 ID 到用户名的映射
    user_id_to_name = df.set_index("user_id")["username"].to_dict()

    # 生成用户行为分析报告
    user_behavior_report = []
    for user_id in user_message_count.index:
        user_behavior_report.append({
            "user_id": user_id,  # 用户 ID
            "username": user_id_to_name.get(user_id, "未知用户"),  # 获取用户名，若找不到则填充"未知用户"
            "message_count": int(user_message_count[user_id]),  # 确保消息计数是整数
            "active_period": str(user_active_period[user_id]) if not pd.isna(user_active_period[user_id]) else "无数据"
            # 若没有活跃时间则返回"无数据"
        })

    return {"user_behavior": user_behavior_report}
