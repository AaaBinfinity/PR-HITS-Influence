from .centrality_analysis import analyze_centrality
from .friend_analysis import analyze_friends, analyze_friend_distribution
from .message_analysis import analyze_messages
from .pagerank_analysis import analyze_messages_pagerank
from .hits_analysis import analyze_messages_hits, get_messages_hits_data
from .community_analysis import analyze_community

# 调用相关函数
analyze_friends()
analyze_centrality()
analyze_messages()
analyze_messages_pagerank()
analyze_messages_hits()
analyze_community()
from .shortest_path import analyze_Djs
from .time_series_analysis import analyze_by_timestamp,analyze_user_behavior
