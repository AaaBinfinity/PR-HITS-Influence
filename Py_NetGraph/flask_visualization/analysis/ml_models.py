import torch
import torch.nn as nn
import dgl
from dgl.nn import SAGEConv
import networkx as nx
import numpy as np

# 定义 GraphSAGE 模型
class GraphSAGE(nn.Module):
    def __init__(self, in_feats, hidden_feats, out_feats):
        super(GraphSAGE, self).__init__()
        self.conv1 = SAGEConv(in_feats, hidden_feats, "mean")
        self.conv2 = SAGEConv(hidden_feats, out_feats, "mean")

    def forward(self, g, features):
        h = self.conv1(g, features)
        h = torch.relu(h)
        h = self.conv2(g, h)
        return h

# 生成社交网络数据（假设100个用户）
G = nx.erdos_renyi_graph(n=100, p=0.05)  # 100个节点，5%概率连接
edges = list(G.edges)
src, dst = zip(*edges)
g = dgl.graph((torch.tensor(src), torch.tensor(dst)))

# 随机生成节点特征（活跃度、影响力等）
features = torch.rand((g.num_nodes(), 5))

# 创建训练数据（1表示该用户转发了消息，0表示未转发）
labels = torch.randint(0, 2, (g.num_nodes(), 1)).float()

# 初始化模型
model = GraphSAGE(in_feats=5, hidden_feats=16, out_feats=1)
criterion = nn.BCEWithLogitsLoss()  # 二分类损失
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# 训练模型
epochs = 100
for epoch in range(epochs):
    optimizer.zero_grad()
    output = model(g, features)  # 预测传播概率
    loss = criterion(output, labels)
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# 保存训练好的模型
torch.save(model.state_dict(), "message_spread_model.pth")
print("模型已保存！")
