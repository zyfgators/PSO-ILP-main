import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
from pulp import *
import numpy as np
import math
import uavAllocation112230211 as uavBp
from mpl_toolkits.mplot3d import Axes3D

def taskresCal(a,b,tc,tc_baseline,p):
    task_res = (a + (tc - tc_baseline)/(1-tc_baseline)) / (a+1) * math.exp(b*(p-1))
    return task_res

def tri_surface_3d():
    # 构建tc、p数据
    tc0 = 0.7
    tc = np.arange(0, 1, 0.01)
    p = np.arange(0, 1, 0.01)
    # 将数据网格化处理
    tc, p = np.meshgrid(tc, p)
    R = np.where(tc > tc0, (1 + ((tc - tc0) / (1 - tc0)) * np.exp(p - 1))/ 2, 0)
    # R =  (1 + (tc - 0.6) / 0.4) * np.exp(p)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(tc, p, R, cmap='GnBu', edgecolor='none')
    levels = np.arange(0, 1, 0.01)
    C = ax.contourf(tc, p, R, levels, cmap='GnBu')
    # ax.set_xlabel('Task Complete Rate', fontsize=13)
    # ax.set_ylabel('Attack Probability', fontsize=13)
    # ax.set_zlabel('UAV Resilience', fontsize=13)
    # ax.set_title('Surface plot')
    # plt.scatter()
    cax = fig.add_axes([0.85, 0.25, 0.03, 0.5])
    plt.colorbar(C, cax=cax)
    plt.show()



if __name__ == '__main__':
    tri_surface_3d()

