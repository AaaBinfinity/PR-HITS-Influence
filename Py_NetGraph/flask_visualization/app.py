from flask import Flask, jsonify, render_template
from analysis import analyze_friends, analyze_messages, analyze_friend_distribution, analyze_by_timestamp

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/show_social_network')
def show_social_network():
    """渲染前端页面"""
    return render_template('show_social_network.html')

@app.route('/show_messages')
def show_messages():
    """渲染前端页面"""
    return render_template('show_messages.html')

@app.route('/show_friend_distribution')
def show_friend_distribution():
    """渲染前端页面"""
    return render_template('show_friend_distribution.html')



@app.route('/api/social_network', methods=['GET'])
def get_social_network():
    """获取社交网络数据"""
    data = analyze_friends()
    return jsonify(data)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取社交网络数据"""
    data = analyze_messages()
    return jsonify(data)

@app.route('/api/friend_distribution', methods=['GET'])
def get_friend_distribution():
    """获取社交网络数据"""
    data = analyze_friend_distribution()
    return jsonify(data)

@app.route('/api/by_timestamp', methods=['GET'])
def get_by_timestamp():
    """获取社交网络数据"""
    data = analyze_by_timestamp()
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
