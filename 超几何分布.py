import math

def hypergeometric_probability(N, K, n, k):
    """
    计算超几何分布的概率 P(X=k)
    
    参数:
    N -- 总体数量
    K -- 总体中具有目标特征的元素数量
    n -- 样本量（抽取的元素数量）
    k -- 样本中具有目标特征的元素数量
    
    返回:
    概率值 P(X=k)
    """
    # 检查输入是否有效
    if k < 0 or k > min(n, K) or (n - k) > (N - K):
        return 0.0
    
    # 计算组合数 C(a, b) = a!/(b!(a-b)!)
    def combination(a, b):
        if b < 0 or b > a:
            return 0
        # 使用math.comb（Python 3.10+支持）
        return math.comb(a, b)
    
    # 计算超几何分布概率
    numerator = combination(K, k) * combination(N - K, n - k)
    denominator = combination(N, n)
    
    return numerator / denominator if denominator != 0 else 0.0

def hypergeometric_cdf(N, K, n, max_k):
    """计算累积分布函数 P(X ≤ max_k)"""
    prob = 0.0
    for k in range(0, max_k + 1):
        prob += hypergeometric_probability(N, K, n, k)
    return prob

if __name__ == "__main__":
    # 示例1：产品质量抽检
    print("示例1：产品质量抽检")
    N, K, n = 50, 3, 5  # 50件产品，3件不合格，抽5件
    k = 1  # 恰好1件不合格
    prob = hypergeometric_probability(N, K, n, k)
    print(f"从50件产品（含3件不合格品）中抽5件，恰好抽到1件不合格品的概率：{prob:.4f} ({prob*100:.2f}%)")

