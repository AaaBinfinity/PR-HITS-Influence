import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# 数据库配置
DB_CONFIG = {
    "user": "orlando",
    "password": "Anchor_Mar25",
    "host": "1.92.109.205",
    "port": "3306",
    "database": "chat_app"
}

# 创建 SQLAlchemy 引擎
DATABASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
engine = create_engine(DATABASE_URL, echo=True)

# 读取数据
def fetch_data(query):
    # 使用 SQLAlchemy 引擎执行查询
    df = pd.read_sql(query, engine)
    return df
# 查询用户表
query = "SELECT * FROM users"
# 创建基础类
Base = declarative_base()


# 用户表模型
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)


# 好友表模型
class Friend(Base):
    __tablename__ = "friends"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    friend_id = Column(Integer, ForeignKey("users.id"), primary_key=True)


# 消息表模型
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(String(50))



# 获取数据
df_users = fetch_data(query)

# 输出数据
print(df_users)
