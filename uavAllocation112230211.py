"""
@软件名称： UAVAllocation

@版 本 号： V1.12.230211
@更改说明： 基于1.11版程序，引入了无人机成本矩阵，将约束条件修改为无人机成本约束
@参考资料：2013.01.10无人机任务分配模型.docx
@author: ZengYiFan

"""
import random
from pulp import *
import numpy as np
import math

# 定义无人机UAV具有的载荷种类
loadList = ['load01', 'load02', 'load03', 'load04', 'load05']

# 定义单架无人机
class UAV:
    def __init__(self, name, loadCapacity, loadCostCoeff, uavCostCoeff):  #loadCostCoeff 表示不同种类的载荷单位价格系数 ；
                                                                          # uavCostCoeff 表示无人机装载量单位价格系数
        self.name = name
        self.loadCapacity = loadCapacity
        self.uavCostCoeff = uavCostCoeff
        self.loadCostCoeff = loadCostCoeff
        self.cost = 0

    def getLoadVal(self, loadName):
        return self.loadCapacity[loadName]

    def getLoadVal(self):
        xy = self.loadCapacity
        return xy

    def getCostVal(self):
        for i in range(len(loadList)):
            cost_temp = self.loadCapacity[i] * self.loadCostCoeff[i]
            self.cost = self.cost + cost_temp
        cost = self.cost + self.uavCostCoeff * sum(self.loadCapacity)
        return cost


# 定义无人机集群
class UavSwarm:
    def __init__(self, name):
        self.name = name
        self.uaves = list()  # uavSwarm开始为空列表

    def getUavNum(self):
        return len(self.uaves)

    def addUav(self, uavName, loadCapacity, uavCostCoeff, loadCostCoeff):
        uavN = UAV(uavName, loadCapacity, uavCostCoeff, loadCostCoeff)
        self.uaves.append(uavN)

    def delUav(self, uavName):
        for uav in self.uaves:
            if uav.name == uavName:
                self.uaves.remove(uav)  # 删除名称为uavName的UAV  ???
                break

    # 获取载荷能力矩阵值（已转换为np数组）
    def getLoadCapacity(self):
        loadCapacity = list()
        UavCost = list()
        for uav in self.uaves:
            loadCapacity.append(uav.getLoadVal())
            UavCost.append(uav.getCostVal())
        return np.array(loadCapacity),np.array(UavCost)



# 定义本案例所使用的军种
msList = ['MS01', 'MS02', 'MS03', 'MS04', 'MS05'];


# 作战区域及其军种配置
class BattleFieldClass:
    def __init__(self, name):
        self.name = name
        self.msInf = dict()  # 定义军种信息，开始为空字典，字典内容为军种名和军种数量
        self.msPro = dict()  # 定义军种打击概率，开始为空字典，字典内容为军种的打击概率

    # 增加军种信息，给定军种及其数量
    # def addMilitaryService(self,msName,msNum):
    #     self.msInf.setdefault(msName,[]).append(msNum)

    # 增加军种信息，按照本案例使用军种列表msList，一次性写入
    def addMilitaryService(self, msValues):
        self.msInf = dict(zip(msList, msValues))

    # 增加军种打击概率，给定不同军种的打击概率列表pList,一次性写入
    def addMilitaryAttackProbability(self, pValues):
        self.msPro = dict(zip(msList, pValues))


class MilitaryServiceSmashClass:
    def __init__(self, name, loadCapacity):
        self.name = name
        self.loadCapacity = loadCapacity


class SingleTaskClass:
    def __init__(self, name, msNum, smashPercent, reqMsSmash):
        self.name = name
        # self.battleFieldName = battleFieldName
        self.smashPercent = smashPercent
        self.msNum = msNum  # 本任务指定战域name的军种配置和数量msInf
        self.reqMsSmash = reqMsSmash  # 打击各军种所需载荷

    def getSmashLoad(self):
        reqTaskLoad = np.zeros(len(loadList))  # 创建指定行列数的矩阵, 一行对应一个军种，每列对应各种载荷
        for ms in self.msNum:
            temp = self.msNum[ms] * np.array(self.reqMsSmash[ms])  # ms为每个军种名称及数量信息
            reqTaskLoad += temp[0]
        return reqTaskLoad


def InitUavSwarm():
    uavSwarm = UavSwarm('UAV Swarm')
    # 添加UAV1对象
    uavSwarm.addUav('UAV1', [12, 2, 1, 1, 0], [10, 13, 17, 25, 50], 80)

    # 添加UAV2对象
    uavSwarm.addUav('UAV2', [2, 10, 1, 0, 1], [10, 13, 17, 25, 50], 70)

    # 添加UAV3对象
    uavSwarm.addUav('UAV3', [2, 2, 11, 1, 1], [10, 13, 17, 25, 50], 80)

    # 添加UAV4对象
    uavSwarm.addUav('UAV4', [4, 3, 2, 3, 2], [10, 13, 17, 25, 50], 100)

    # 添加UAV5对象
    uavSwarm.addUav('UAV5', [0, 1, 1, 1, 6], [10, 13, 17, 25, 50], 60)

    return uavSwarm


# 定义军种被击毁的载荷数量信息，即各军种击毁的载荷需求矩阵
def InitMsSmash():
    loadSmash = [[200, 160, 120, 80, 80],
                 [210, 150, 100, 75, 80],
                 [190, 165, 105, 80, 85],
                 [205, 155, 110, 85, 75],
                 [195, 170, 130, 90, 90]]
    msSmash = dict()
    i = 0
    for msName in msList:
        msSmash.setdefault(msName, []).append(loadSmash[i])
        i += 1
    return msSmash


battleFieldList = ['battlefield1', 'battlefield2', 'battlefield3']


def InitBattleField():
    battleField = list()
    # 定义战域1
    xx = BattleFieldClass(battleFieldList[0])
    # xx.addMilitaryService('军种1',2)
    # xx.addMilitaryService('军种2',1)
    # xx.addMilitaryService('军种3',1)
    # xx.addMilitaryService('军种4',3)
    # xx.addMilitaryService('军种5',2)
    xx.addMilitaryService([2, 1, 1, 3, 2])
    # level 1: [2, 1, 1, 3, 2]
    # level 2: [10, 5, 5, 15, 10]
    # level 3: [20, 10, 10, 30, 20]
    battleField.append(xx)

    # 定义战域2
    xx = BattleFieldClass(battleFieldList[1])
    xx.addMilitaryService([4, 2, 2, 1, 3])
    # level 1: [4, 2, 2, 1, 3]
    # level 2: [20, 10, 10, 5, 15]
    # level 3: [40, 20, 20, 10, 30]
    battleField.append(xx)

    # 定义战域3
    xx = BattleFieldClass(battleFieldList[2])
    xx.addMilitaryService([2, 1, 3, 3, 3])
    # level 1: [2, 1, 3, 3, 3]
    # level 2: [10, 5, 15, 15, 15]
    # level 3: [20, 10, 30, 30, 30]
    battleField.append(xx)

    # 定义军种被击毁的载荷数量信息，即各军种击毁的载荷需求矩阵
    reqMsSmash = InitMsSmash()

    return battleField, reqMsSmash


# def taskCompleteVal(attackProb,uavswarm):
# uavAllo: 它是[xij]表示的3*5,即第i个战域分配第j种无人机的数量
# xx:  表示某战域的军种数量矩阵
# battlefieldNum: 战域数量
# reqTaskLoad: 载荷需求矩阵
def taskCompleteVal(uavAllo, uavLoadMatrix, reqTaskLoad, iex, p, extraTaskLoad):
    tc = []
    newLoad = []
    resLoad = np.zeros((np.shape(extraTaskLoad)[0],np.shape(extraTaskLoad)[1]))
    enemyAtt = np.zeros((np.shape(extraTaskLoad)[0],np.shape(extraTaskLoad)[1]))
    enemyLoss = np.zeros((np.shape(extraTaskLoad)[0],np.shape(extraTaskLoad)[1]))
    # for i in range(np.shape(uavswarm)[0]):
    #     for j in range(np.shape(uavswarm)[1]):
    #         uavswarm[i][j] = uavswarm[i][j] * (1 - attackProb[i][j])
    # return uavswarm

    for i in range(np.shape(uavAllo)[0]):
        for j in range(np.shape(uavAllo)[1]):
            enemyAtt[i][j] = int(uavAllo[i][j] * p[i] * random.uniform(0, 1))
            enemyLoss[i][j] = enemyAtt[i][j] * 0.5

    for i in range(np.shape(uavAllo)[0]):
        for j in range(np.shape(uavAllo)[1]):
            uavAllo[i][j] = uavAllo[i][j] - enemyAtt[i][j]


    for i in range(np.shape(extraTaskLoad)[0]):
        for j in range(np.shape(extraTaskLoad)[1]):
            resLoad[i][j] = extraTaskLoad[i][j] + int(uavAllo[i][j] * p[i] * 2)

    # newLoad after attack
    for i in range(np.shape(uavAllo)[0]):
        temp = [0] * np.shape(uavAllo)[1]
        for j in range(np.shape(uavAllo)[1]):
            temp = temp + uavAllo[i][j] * uavLoadMatrix[j]
        newLoad.append(temp.tolist())



    # Task Complete Rate
    for i in range(np.shape(uavAllo)[0]):
        tc_temp = [0]
        for j in range(np.shape(uavAllo)[1]):
            if newLoad[i][j] >= reqTaskLoad[i][j] + iex[i][j]:
                tc_temp[0] = tc_temp[0] + 1
            else:
                tc_temp[0] = tc_temp[0] + newLoad[i][j] / (reqTaskLoad[i][j] + iex[i][j])
        tc_temp[0] = tc_temp[0] / 5
        tc.append(tc_temp[0])
    print('TC = ', tc)

    return newLoad, tc, resLoad, enemyLoss


# Resilience
def ResiVal(tc, tc_baseline, p, enemyLoss):
    tc_max = 1; a = 1 ; b = 1
    coff1 = 0.4; coff2 = 0.2; coff3 = 0.4
    f = [0,0,0]
    for i in range(len(tc)):
        if tc[i] > tc_baseline[i]:
            f[i] = (a + ((tc[i] - tc_baseline[i]) / (tc_max - tc_baseline[i]))) * (math.exp((p[i]-1)*b) / (a+1)) + sum(enemyLoss[i][:]) / np.shape(enemyLoss)[1] * 0.1
        else:
            f[i] = 0.001
    f_weighted = coff1 * f[0] + coff2 * f[1] + coff3 * f[2]
    print('Resilience = ', f_weighted)
    return f_weighted




def taskPSOCompleteVal(uavAllo, uavLoadMatrix, reqTaskLoad, iex, p):
    tc = []
    newLoad = []
    # for i in range(np.shape(uavswarm)[0]):
    #     for j in range(np.shape(uavswarm)[1]):
    #         uavswarm[i][j] = uavswarm[i][j] * (1 - attackProb[i][j])
    # return uavswarm

    for i in range(np.shape(uavAllo)[0]):
        for j in range(np.shape(uavAllo)[1]):
            uavAllo[i][j] = uavAllo[i][j] - int(uavAllo[i][j] * p[i] * random.uniform(0,1))

    # newLoad after attack
    for i in range(np.shape(uavAllo)[0]):
        temp = [0] * np.shape(uavAllo)[1]
        for j in range(np.shape(uavAllo)[1]):
            temp = temp + uavAllo[i][j] * uavLoadMatrix[j]
        newLoad.append(temp.tolist())


    # Task Complete Rate
    for i in range(np.shape(uavAllo)[0]):
        tc_temp = [0]
        for j in range(np.shape(uavAllo)[1]):
            if newLoad[i][j] >= reqTaskLoad[i][j] + iex[i][j]:
                tc_temp[0] = tc_temp[0] + 1
            else:
                tc_temp[0] = tc_temp[0] + newLoad[i][j] / (reqTaskLoad[i][j] + iex[i][j])
        tc_temp[0] = tc_temp[0] / 5
        tc.append(tc_temp[0])
    print('TC = ', tc)

    return newLoad, tc



def updateExTaskLoad(tc):
    updateEX = [[0] * len(loadList) for i in range(3)]
    for i in range(3):
        for j in range(5):
            updateEX[i][j] = (1 - tc[i]) * 80
    return updateEX


def getMsVal(battleFieldName, battleField):
    for xx in battleField:
        if xx.name == battleFieldName:
            return xx.msInf


# 定义打击任务, 并获取完成打击任务所需载荷
def InitSmashTask(battleField, reqMsSmash):
    taskList = list()
    taskList.append(SingleTaskClass('TASK01', getMsVal(battleFieldList[0], battleField), 100, reqMsSmash))
    taskList.append(SingleTaskClass('TASK02', getMsVal(battleFieldList[1], battleField), 100, reqMsSmash))
    taskList.append(SingleTaskClass('TASK03', getMsVal(battleFieldList[2], battleField), 100, reqMsSmash))

    # reqLoad = np.zeros((1, len(loadList)))  # 创建指定行列数的矩阵, 一行对应一个军种，每列对应各种载荷
    reqLoad = list()
    for task in taskList:
        reqLoad.append(task.getSmashLoad().tolist())
        # np.r_[reqLoad,task.getSmashLoad()]
    extraTaskLoad = [[0] * len(loadList) for i in range(len(taskList))]
    return reqLoad, extraTaskLoad


def BuildProblem(uavNum, battlefieldNum, uavLoadMatrix, reqTaskLoad, exMax, extraTaskLoad, uavCost):
    # Set up a problem
    prob = LpProblem('UAV task allocation', LpMinimize)

    # Set up parameters
    var_x = pulp.LpVariable.dicts("x", (range(battlefieldNum), range(uavNum)), lowBound=0, cat=LpInteger)
    row = len(reqTaskLoad[0])

    # Set up target function
    prob += lpSum((lpSum(var_x[k][i] * uavCost[i] for i in range(uavNum)) for k in range(battlefieldNum)))



    # Set up condition (total 3 conditions represent 3 battlefields)
    for i in range(row):
        for k in range(battlefieldNum):
            # prob += ((lpSum(uavLoadMatrix[i][j] * var_x[k][j] for j in range(uavNum))
            #           - lpSum(reqTaskLoad[k][i]) >= np.zeros(1, battlefieldNum) for k in range(battlefieldNum)))
            prob += (lpSum(uavLoadMatrix[j][i] * var_x[k][j] for j in range(uavNum)) - reqTaskLoad[k][i] -
                     exMax - extraTaskLoad[k][i] >= 0)

    return prob


def BuildResProblem(uavNum, battlefieldNum, uavLoadMatrix, reqTaskLoad, exMax, extraTaskLoad, uavCost, lamda, R, Rcon):
    # Set up a problem
    prob = LpProblem('UAV task allocation', LpMinimize)

    # Set up parameters
    var_x = pulp.LpVariable.dicts("x", (range(battlefieldNum), range(uavNum)), lowBound=0, cat=LpInteger)
    row = len(reqTaskLoad[0])

    # Set up target function
    prob += lpSum((lpSum(lamda * var_x[k][i] * uavCost[i] + (1 - lamda) * R * Rcon[i] * uavCost[i] for i in range(uavNum)) for k in range(battlefieldNum)))



    # Set up condition (total 3 conditions represent 3 battlefields)
    for i in range(row):
        for k in range(battlefieldNum):
            # prob += ((lpSum(uavLoadMatrix[i][j] * var_x[k][j] for j in range(uavNum))
            #           - lpSum(reqTaskLoad[k][i]) >= np.zeros(1, battlefieldNum) for k in range(battlefieldNum)))
            prob += (lpSum(uavLoadMatrix[j][i] * var_x[k][j] for j in range(uavNum)) - reqTaskLoad[k][i] - extraTaskLoad[k][i] -
                     exMax - reqTaskLoad[k][i] * (1 - lamda) * R >= 0)

    return prob

def probSolve(prob):
    uavswarm = []
    prob.solve(pulp.PULP_CBC_CMD(logPath=r'path.lp'))
    print('Status:', LpStatus[prob.status])
    for v in prob.variables():
        print(v.name, '=', v.varValue)
        uavswarm.append(v.varValue)
    uavswarm = (np.array(uavswarm).reshape((3, 5))).tolist()
    swarmCost = value(prob.objective)
    print('The total cost of UAV = ', swarmCost)
    return uavswarm


def uavAlly(lamda):
    uavSwarm = InitUavSwarm()
    battleField, reqMsSmash = InitBattleField()
    p = [0.2, 0.2, 0.2]  # 每个战域对应的打0.击概率 战域1打击概率0.2，战域2打击概率0.3，战域3打击概率0.2
    tc_baseline = [0.8,0.8,0.8]
    iex = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    exMax = 30  # 粒子群算法优化时为了使ex的范围保持在(-xmax,xmax),加入了一个exMax变量
    reqTaskLoad, extraTaskLoad = InitSmashTask(battleField, reqMsSmash)
    uavLoadMatrix, uavCostMatrix = uavSwarm.getLoadCapacity()
    uavNum = uavSwarm.getUavNum()
    battlefieldNum = len(battleFieldList)
    prob = BuildProblem(uavNum, battlefieldNum, uavLoadMatrix.tolist(), reqTaskLoad, exMax, extraTaskLoad,
                        uavCostMatrix)
    uavAllo = probSolve(prob)
    newLoad, tc, resLoad,enemyLoss = taskCompleteVal(uavAllo, uavLoadMatrix, reqTaskLoad, iex,p, extraTaskLoad)
    R = ResiVal(tc, tc_baseline, p, enemyLoss)
    if lamda != 1:
        Rcon = [100/R,100/R,100/R,300/R,100/R]  #韧性归一化系数
    else:
        Rcon = [100,100,100,300,100]
    prob_res = BuildResProblem(uavNum, battlefieldNum, uavLoadMatrix, reqTaskLoad, exMax, resLoad, uavCostMatrix, lamda, R, Rcon)
    uavAllo2 = probSolve(prob_res)
    uavTotal2 = sum(uavAllo2[0]) + sum(uavAllo2[1]) + sum(uavAllo2[2])
    print('Method 2: uavAllo = ', uavAllo2)
    print('Method 2: totalUav Number = ', uavTotal2)
    print('Method 2: Resilience = ',R)
    print('Method 2: Task Complete Rate = ',tc)
    print('The task is over.')


if __name__ == '__main__':
    lamda = float(input('Input a lamda: '))
    uavAlly(lamda)
    print("Task end.")
