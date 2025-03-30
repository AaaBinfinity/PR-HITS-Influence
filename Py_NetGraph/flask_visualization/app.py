import logging
from flask import Flask, render_template, request, jsonify

from analysis.network_analysis import *
from analysis.shortest_path import *
from analysis.time_series_analysis import *
# Set up logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create file handler that logs to a file
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Create console handler that logs to the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(file_formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = Flask(__name__)

@app.route('/')
def index():
    logger.info('Index page accessed')
    return render_template('index.html')


@app.route('/api/messages_hits', methods=['GET'])
def get_messages_hits():
    logger.info('Fetching messages HITS data')

    data = get_messages_hits_data()
    logger.info('Messages HITS data fetched successfully')
    return jsonify(data)

@app.route('/show_messages_hits')
def show_messages_hits():
    logger.info('Social network HITS page accessed')
    return render_template('show_messages_hits.html')


@app.route('/api/by_timestamp', methods=['GET'])
def get_analyze_by_timestamp():
    """处理 /api/by 请求并返回时间序列数据"""
    data = analyze_by_timestamp()
    return jsonify(data)
@app.route('/show_by_timestamp')
def show_by_timestamp():
    logger.info('Social network page accessed')
    return render_template('timestamp_analysis.html')
@app.route('/api/messages_pagerank', methods=['GET'])
def get_messages_pagerank():
    logger.info('Fetching messages PageRank data')
    data = analyze_messages_pagerank()
    logger.info('Messages PageRank data fetched successfully')
    return jsonify(data)


@app.route('/show_messages_pagerank')
def show_messages_pagerank():
    logger.info('Social network page accessed')
    return render_template('show_messages_pagerank.html')


@app.route('/api/user_communities', methods=['GET'])
def get_user_communities():
    """获取用户社区划分数据"""
    data = analyze_community()
    return jsonify(data)

@app.route('/show_user_communities')
def show_user_communities():
    """渲染用户社区页面"""
    return render_template('show_user_communities.html')
@app.route('/show_social_network')
def show_social_network():
    logger.info('Social network page accessed')
    return render_template('show_social_network.html')


@app.route('/show_friend_distribution')
def show_friend_distribution():
    logger.info('Friend distribution page accessed')
    return render_template('show_friend_distribution.html')

@app.route('/show_shortest_way')
def show_shortest_way():
    logger.info('Shortest way page accessed')
    return render_template("show_shortest_way.html")

@app.route('/api/user_behavior', methods=['GET'])
def get_user_behavior():
    """处理 /api/user_behavior 请求并返回用户行为数据"""
    data = analyze_user_behavior()
    return jsonify(data)

@app.route('/show_user_behavior')
def show_user_behavior():
    """渲染用户行为分析页面"""
    logger.info('User behavior analysis page accessed')
    return render_template('user_behavior.html')
@app.route('/api/shortest_path', methods=['GET'])
def shortest_path():
    start_user = request.args.get('start_user')
    end_user = request.args.get('end_user')
    logger.info(f'Shortest path requested from {start_user} to {end_user}')
    result = analyze_Djs(start_user, end_user)
    logger.info(f'Shortest path result: {result}')
    return jsonify(result)

@app.route('/api/social_network', methods=['GET'])
def get_social_network():
    logger.info('Fetching social network data')
    data = analyze_friends()
    logger.info('Social network data fetched successfully')
    return jsonify(data)

@app.route('/show_centrality')
def show_centrality():
    return render_template('show_messages_Centrality.html')

@app.route('/api/centrality', methods=['GET'])
def get_centrality():
    data = analyze_centrality()
    return jsonify(data)

@app.route('/show_messages')
def show_messages():
    logger.info('Messages page accessed')
    return render_template('show_messages_Diffusion.html')
@app.route('/api/messages', methods=['GET'])
def get_messages():
    logger.info('Fetching messages data')
    data = analyze_messages()
    logger.info('Messages data fetched successfully')
    return jsonify(data)

@app.route('/api/friend_distribution', methods=['GET'])
def get_friend_distribution():
    logger.info('Fetching friend distribution data')
    data = analyze_friend_distribution()
    logger.info('Friend distribution data fetched successfully')
    return jsonify(data)

@app.route('/api/by_timestamp', methods=['GET'])
def get_by_timestamp():
    logger.info('Fetching message count by timestamp')
    data = analyze_by_timestamp()
    logger.info('Message count by timestamp fetched successfully')
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    logger.info('Flask app started')

