import logging
from flask import Flask, render_template, request, jsonify
from analysis import *

# 设置日志配置
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 文件处理器，将日志记录到文件
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 控制台处理器，将日志输出到终端
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(file_formatter)

# 将处理器添加到日志器中
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 初始化 Flask 应用
app = Flask(__name__)

# 首页路由
@app.route('/')
def index():
    logger.info('访问首页')
    return render_template('index.html')

# 获取消息 HITS 数据的 API
@app.route('/api/messages_hits', methods=['GET'])
def get_messages_hits():
    logger.info('正在获取消息 HITS 数据')
    data = get_messages_hits_data()
    logger.info('消息 HITS 数据获取成功')
    return jsonify(data)

# 展示消息 HITS 页面
@app.route('/show_messages_hits')
def show_messages_hits():
    logger.info('访问社交网络 HITS 页面')
    return render_template('show_messages_hits.html')

# 获取时间序列数据的 API
@app.route('/api/by_timestamp', methods=['GET'])
def get_analyze_by_timestamp():
    logger.info('正在获取时间序列数据')
    data = analyze_by_timestamp()
    logger.info('时间序列数据获取成功')
    return jsonify(data)

# 展示时间序列分析页面
@app.route('/show_by_timestamp')
def show_by_timestamp():
    logger.info('访问时间戳分析页面')
    return render_template('timestamp_analysis.html')

# 获取消息 PageRank 数据的 API
@app.route('/api/messages_pagerank', methods=['GET'])
def get_messages_pagerank():
    logger.info('正在获取消息 PageRank 数据')
    data = analyze_messages_pagerank()
    logger.info('消息 PageRank 数据获取成功')
    return jsonify(data)

# 展示消息 PageRank 页面
@app.route('/show_messages_pagerank')
def show_messages_pagerank():
    logger.info('访问社交网络 PageRank 页面')
    return render_template('show_messages_pagerank.html')

# 获取用户社区划分数据的 API
@app.route('/api/user_communities', methods=['GET'])
def get_user_communities():
    logger.info('正在获取用户社区数据')
    data = analyze_community()
    logger.info('用户社区数据获取成功')
    return jsonify(data)

# 展示用户社区页面
@app.route('/show_user_communities')
def show_user_communities():
    logger.info('访问用户社区页面')
    return render_template('show_user_communities.html')

# 展示社交网络页面
@app.route('/show_social_network')
def show_social_network():
    logger.info('访问社交网络页面')
    return render_template('show_social_network.html')

# 展示好友分布页面
@app.route('/show_friend_distribution')
def show_friend_distribution():
    logger.info('访问好友分布页面')
    return render_template('show_friend_distribution.html')

# 展示最短路径页面
@app.route('/show_shortest_way')
def show_shortest_way():
    logger.info('访问最短路径页面')
    return render_template('show_shortest_way.html')

# 获取用户行为数据的 API
@app.route('/api/user_behavior', methods=['GET'])
def get_user_behavior():
    logger.info('正在获取用户行为数据')
    data = analyze_user_behavior()
    logger.info('用户行为数据获取成功')
    return jsonify(data)

# 展示用户行为分析页面
@app.route('/show_user_behavior')
def show_user_behavior():
    logger.info('访问用户行为分析页面')
    return render_template('user_behavior.html')

# 获取最短路径的 API
@app.route('/api/shortest_path', methods=['GET'])
def shortest_path():
    start_user = request.args.get('start_user')
    end_user = request.args.get('end_user')
    logger.info(f'请求计算从 {start_user} 到 {end_user} 的最短路径')
    result = analyze_Djs(start_user, end_user)
    logger.info(f'最短路径结果: {result}')
    return jsonify(result)

# 获取社交网络数据的 API
@app.route('/api/social_network', methods=['GET'])
def get_social_network():
    logger.info('正在获取社交网络数据')
    data = analyze_friends()
    logger.info('社交网络数据获取成功')
    return jsonify(data)

# 展示中心性页面
@app.route('/show_centrality')
def show_centrality():
    logger.info('访问中心性页面')
    return render_template('show_messages_Centrality.html')

# 获取中心性数据的 API
@app.route('/api/centrality', methods=['GET'])
def get_centrality():
    logger.info('正在获取中心性数据')
    data = analyze_centrality()
    logger.info('中心性数据获取成功')
    return jsonify(data)

# 展示消息传播页面
@app.route('/show_messages')
def show_messages():
    logger.info('访问消息传播页面')
    return render_template('show_messages_Diffusion.html')

# 获取消息数据的 API
@app.route('/api/messages', methods=['GET'])
def get_messages():
    logger.info('正在获取消息数据')
    data = analyze_messages()
    logger.info('消息数据获取成功')
    return jsonify(data)

# 获取好友分布数据的 API
@app.route('/api/friend_distribution', methods=['GET'])
def get_friend_distribution():
    logger.info('正在获取好友分布数据')
    data = analyze_friend_distribution()
    logger.info('好友分布数据获取成功')
    return jsonify(data)

# 启动 Flask 应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    logger.info('Flask 应用启动')
