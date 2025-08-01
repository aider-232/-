import math
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HypergeometricCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("超几何分布计算器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置字体，确保中文显示正常
        plt.rcParams["font.family"] = ["SimHei"]
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入面板
        self.create_input_panel()
        
        # 创建结果面板
        self.create_result_panel()
        
        # 创建图表面板
        self.create_chart_panel()
        
    def create_input_panel(self):
        input_frame = ttk.LabelFrame(self.main_frame, text="参数设置", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 总体数量 N
        ttk.Label(input_frame, text="总体数量 (N):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.N_var = tk.IntVar(value=50)
        ttk.Entry(input_frame, textvariable=self.N_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        # 总体中不合格品数量 K
        ttk.Label(input_frame, text="总体中不合格品数量 (K):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.K_var = tk.IntVar(value=3)
        ttk.Entry(input_frame, textvariable=self.K_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        # 样本量 n
        ttk.Label(input_frame, text="样本量 (n):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.n_var = tk.IntVar(value=5)
        ttk.Entry(input_frame, textvariable=self.n_var, width=15).grid(row=2, column=1, padx=5, pady=5)
        
        # 样本中不合格品数量 k
        ttk.Label(input_frame, text="样本中不合格品数量 (k):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.k_var = tk.IntVar(value=1)
        ttk.Entry(input_frame, textvariable=self.k_var, width=15).grid(row=3, column=1, padx=5, pady=5)
        
        # 计算按钮
        calculate_btn = ttk.Button(input_frame, text="计算概率", command=self.calculate_probabilities)
        calculate_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
    def create_result_panel(self):
        result_frame = ttk.LabelFrame(self.main_frame, text="计算结果", padding="10")
        result_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 单个概率结果
        ttk.Label(result_frame, text="P(X = k):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.single_prob_var = tk.StringVar(value="0.0000")
        ttk.Label(result_frame, textvariable=self.single_prob_var, font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 累积概率结果 (≤k)
        ttk.Label(result_frame, text="P(X ≤ k):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.cdf_leq_var = tk.StringVar(value="0.0000")
        ttk.Label(result_frame, textvariable=self.cdf_leq_var, font=("Arial", 10, "bold")).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 累积概率结果 (≥k)
        ttk.Label(result_frame, text="P(X ≥ k):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.cdf_geq_var = tk.StringVar(value="0.0000")
        ttk.Label(result_frame, textvariable=self.cdf_geq_var, font=("Arial", 10, "bold")).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
    def create_chart_panel(self):
        chart_frame = ttk.LabelFrame(self.main_frame, text="超几何分布图表", padding="10")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建图表
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def combination(self, a, b):
        """计算组合数 C(a, b)"""
        if b < 0 or b > a:
            return 0
        return math.comb(a, b)
    
    def hypergeometric_probability(self, N, K, n, k):
        """计算超几何分布的概率 P(X=k)"""
        # 检查输入是否有效
        if k < 0 or k > min(n, K) or (n - k) > (N - K):
            return 0.0
        
        numerator = self.combination(K, k) * self.combination(N - K, n - k)
        denominator = self.combination(N, n)
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def hypergeometric_cdf(self, N, K, n, max_k):
        """计算累积分布函数 P(X ≤ max_k)"""
        prob = 0.0
        for k in range(0, max_k + 1):
            prob += self.hypergeometric_probability(N, K, n, k)
        return prob
    
    def calculate_probabilities(self):
        try:
            # 获取输入值
            N = self.N_var.get()
            K = self.K_var.get()
            n = self.n_var.get()
            k = self.k_var.get()
            
            # 验证输入
            if N <= 0:
                messagebox.showerror("输入错误", "总体数量 N 必须大于 0")
                return
            
            if K < 0 or K > N:
                messagebox.showerror("输入错误", "不合格品数量 K 必须在 0 到 N 之间")
                return
                
            if n < 1 or n > N:
                messagebox.showerror("输入错误", "样本量 n 必须在 1 到 N 之间")
                return
                
            if k < 0 or k > min(n, K):
                messagebox.showerror("输入错误", f"样本中不合格品数量 k 必须在 0 到 {min(n, K)} 之间")
                return
            
            # 计算概率
            single_prob = self.hypergeometric_probability(N, K, n, k)
            cdf_leq = self.hypergeometric_cdf(N, K, n, k)
            cdf_geq = 1 - self.hypergeometric_cdf(N, K, n, k - 1) if k > 0 else 1.0
            
            # 更新结果显示
            self.single_prob_var.set(f"{single_prob:.6f} ({single_prob*100:.2f}%)")
            self.cdf_leq_var.set(f"{cdf_leq:.6f} ({cdf_leq*100:.2f}%)")
            self.cdf_geq_var.set(f"{cdf_geq:.6f} ({cdf_geq*100:.2f}%)")
            
            # 更新图表
            self.update_chart(N, K, n, k)
            
        except Exception as e:
            messagebox.showerror("计算错误", f"计算过程中发生错误: {str(e)}")
    
    def update_chart(self, N, K, n, k):
        """更新超几何分布图表"""
        # 清除现有图表
        self.ax.clear()
        
        # 计算所有可能的k值及其概率
        max_possible_k = min(n, K)
        k_values = list(range(0, max_possible_k + 1))
        probabilities = [self.hypergeometric_probability(N, K, n, k_val) for k_val in k_values]
        
        # 绘制柱状图
        bars = self.ax.bar(k_values, probabilities, color='skyblue', edgecolor='black')
        
        # 高亮显示当前k值的柱子
        if k in k_values:
            idx = k_values.index(k)
            bars[idx].set_color('orange')
        
        # 设置图表属性
        self.ax.set_title(f'超几何分布 (N={N}, K={K}, n={n})')
        self.ax.set_xlabel('样本中的不合格品数量 (k)')
        self.ax.set_ylabel('概率')
        self.ax.set_xticks(k_values)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.4f}',
                    ha='center', va='bottom')
        
        # 调整布局并更新画布
        self.fig.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = HypergeometricCalculator(root)
    root.mainloop()
    