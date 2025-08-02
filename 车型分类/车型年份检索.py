# %%
import pandas as pd
import re
import string
import numpy as np
from typing import Dict, List, Optional

# 定义有效年份范围
MIN_VALID_YEAR = 1980
MAX_VALID_YEAR = 2100

# --------------------------
# 1. 预统计位置规律
# --------------------------
def 统计位置规律(标注数据路径: str) -> Dict[str, Dict]:
    数据 = pd.read_excel(标注数据路径)
    规律 = {}
    
    for _, 行 in 数据.iterrows():
        文本 = str(行['文本'])
        型号列表 = [i.strip().lower() for i in str(行['型号']).split(',')]
        年份列表 = [i.strip() for i in str(行['年份范围']).split(',')]
        
        for 型号, 年份 in zip(型号列表, 年份列表):
            型号位置 = 文本.lower().find(型号)
            年份位置 = 文本.find(年份)
            if 型号位置 == -1 or 年份位置 == -1:
                continue
            
            距离 = 年份位置 - 型号位置
            方向 = "前置" if 距离 < 0 else "后置"
            
            if 型号 not in 规律:
                规律[型号] = {"距离列表": [], "前置次数": 0, "总次数": 0}
            
            规律[型号]["距离列表"].append(abs(距离))
            规律[型号]["总次数"] += 1
            if 方向 == "前置":
                规律[型号]["前置次数"] += 1
    
    for 型号 in 规律:
        距离列表 = 规律[型号]["距离列表"]
        总次数 = 规律[型号]["总次数"]
        前置概率 = 规律[型号]["前置次数"] / 总次数 if 总次数 > 0 else 0.5
        分位数 = int(np.percentile(距离列表, 90)) + 5 if 距离列表 else 50
        规律[型号] = {
            "前置概率": 前置概率,
            "搜索范围": 分位数,
            "主要格式": "范围" if "-" in 年份 else "单独"  # 简化版格式判断
        }
    
    return 规律

# --------------------------
# 2. 年份解析与范围过滤
# --------------------------
def 解析年份(年份文本: str) -> List[int]:
    """解析年份并过滤1980-2100以外的无效值"""
    年份列表 = []
    年份项 = re.split(r'[,\s]+', 年份文本.strip())
    
    for 项 in 年份项:
        项 = 项.strip()
        if not 项:
            continue
        
        # 处理范围格式
        if "-" in 项:
            起止 = 项.split("-", 1)
            if len(起止) == 2:
                开始 = 补全年份(起止[0].strip())
                结束 = 补全年份(起止[1].strip())
                if 开始 and 结束 and 开始 <= 结束:
                    # 过滤范围外年份
                    有效开始 = max(开始, MIN_VALID_YEAR)
                    有效结束 = min(结束, MAX_VALID_YEAR)
                    if 有效开始 <= 有效结束:
                        年份列表.extend([有效开始, 有效结束])
        
        # 处理单独年份
        elif 项.isdigit():
            单独年份 = 补全年份(项)
            if 单独年份 and MIN_VALID_YEAR <= 单独年份 <= MAX_VALID_YEAR:
                年份列表.append(单独年份)
    
    return 年份列表

def 补全年份(简写: str) -> Optional[int]:
    """补全年份并初步过滤"""
    try:
        数值 = int(简写)
        长度 = len(简写)
        
        if 长度 == 4:
            return 数值 if MIN_VALID_YEAR <= 数值 <= MAX_VALID_YEAR else None
        elif 长度 == 2:
            完整年份 = 2000 + 数值 if 数值 <= 50 else 1900 + 数值
            return 完整年份 if MIN_VALID_YEAR <= 完整年份 <= MAX_VALID_YEAR else None
        elif 1 <= 长度 <= 3:
            完整年份 = 2000 + 数值 if 数值 <= 50 else None
            return 完整年份 if 完整年份 and MIN_VALID_YEAR <= 完整年份 <= MAX_VALID_YEAR else None
        return None
    except:
        return None

# --------------------------
# 3. 核心提取函数
# --------------------------
def 提取指定型号的年份(
    文本: str,
    目标型号: str,
    位置规律: Dict[str, Dict],
    默认搜索范围: int = 60
) -> Optional[str]:
    目标型号标准化 = 目标型号.translate(
        str.maketrans("", "", string.punctuation)
    ).lower().strip()
    文本标准化 = 文本.lower()
    原始文本 = 文本
    型号长度 = len(目标型号标准化)
    文本总长度 = len(文本标准化)
    型号位置列表 = []

    # 定位型号
    for i in range(文本总长度 - 型号长度 + 1):
        if 文本标准化[i:i+型号长度] == 目标型号标准化:
            型号位置列表.append((i, i + 型号长度))
    if not 型号位置列表:
        print(f"未找到型号：{目标型号}")
        return None

    # 获取搜索参数
    型号规律 = 位置规律.get(目标型号标准化, {
        "前置概率": 0.5,
        "搜索范围": 默认搜索范围,
        "主要格式": "范围"
    })
    搜索范围 = 型号规律["搜索范围"]

    # 收集并解析年份
    所有年份 = []
    for (型号起始, 型号结束) in 型号位置列表:
        # 调整搜索方向权重
        前置权重 = 1.5 if 型号规律["前置概率"] > 0.6 else 1.0
        后置权重 = 1.5 if 型号规律["前置概率"] < 0.4 else 1.0
        
        范围起始 = max(0, 型号起始 - int(搜索范围 * 前置权重))
        范围结束 = min(len(原始文本), 型号结束 + int(搜索范围 * 后置权重))
        搜索区域 = 原始文本[范围起始:范围结束]

        # 提取年份碎片
        if 型号规律["主要格式"] == "范围":
            年份匹配 = re.findall(r'\b\d{1,4}[-\s]\d{1,4}\b', 搜索区域)
        else:
            年份匹配 = re.findall(r'\b\d{1,4}\b', 搜索区域)
        
        # 解析并过滤
        for 匹配 in 年份匹配:
            解析结果 = 解析年份(匹配)
            所有年份.extend(解析结果)

    # 处理有效年份
    if not 所有年份:
        print(f"未找到{目标型号}在{MIN_VALID_YEAR}-{MAX_VALID_YEAR}之间的年份")
        return None

    所有年份 = sorted(list(set(所有年份)))
    最小年份 = 所有年份[0]
    最大年份 = 所有年份[-1]
    
    return f"{最小年份}-{最大年份}" if 最小年份 != 最大年份 else f"{最小年份}"

# --------------------------
# 测试年份范围限制
# --------------------------
if __name__ == "__main__":
    # 1. 预统计规律（实际使用时只需运行一次，可保存为文件复用）
    标注数据路径 = "C:/Users/Administrator/Desktop/车型标注数据.xlsx"  # 按之前的格式准备
    位置规律 = 统计位置规律(标注数据路径)

    temp = []
    df = pd.read_excel("C:/Users/Administrator/Desktop/车型标注数据.xlsx" )
    for i,j in zip(df['文本'],df['型号']):
        年份 = 提取指定型号的年份(i, j, 位置规律)
        temp.append(年份)
    a = 0
    for i in range(len(df['年份范围'].to_list())):
        if df['年份范围'].to_list()[i] == temp[i]:
            a = a + 1
        else:
            print(df['年份范围'].to_list()[i],temp[i])
    print(df.shape[0])
    print(a/df.shape[0])

    
    

# %%



