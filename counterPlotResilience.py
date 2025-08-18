import numpy as np
import matplotlib.pyplot as plt

# 重新定义函数，使其能够处理数组形式的输入
def z_function(x, y):
    # 创建一个布尔数组，表示x是否小于0.4
    x_less_than_04 = x < 0.4
    # 创建一个布尔数组，表示x是否在0.4到1之间（不包括0.4和1）
    x_between_04_and_1 = (x >= 0.4) & (x < 1)

    # 根据条件计算z值
    z = np.where(x_less_than_04, 0,
                 np.where(x_between_04_and_1, (1 + (x - 0.7) / (1 - 0.7)) * np.exp(1 * (y - 1)) / 2, 0))
    return z

# 重新创建一个二维网格
x = np.linspace(0, 1, 400)
y = np.linspace(0, 1, 400)
X, Y = np.meshgrid(x, y)

# 重新生成高度数据
Z = z_function(X, Y)

# 创建等高线图，使用彩虹渐变色
plt.figure(figsize=(8, 6))
CS = plt.contourf(X, Y, Z, levels=np.arange(0, 1.01, 0.1), cmap='GnBu')
plt.colorbar(CS)

# 重新设置图表标题和坐标轴标签
# plt.title('Task Resilience')
plt.rcParams['font.family'] = 'Times New Roman'
plt.savefig("Task Resilience with baseline=0.4.png", dpi=200)

# 重新显示图表
plt.show()
