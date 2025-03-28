import logging
from flask import Flask, jsonify, render_template, request
from analysis import analyze_friends, analyze_messages, analyze_friend_distribution, analyze_by_timestamp, analyze_Djs, \
    analyze_centrality

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

