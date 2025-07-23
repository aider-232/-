import tkinter as tk
from tkinter import ttk, messagebox
import requests

class FBACalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FBA费用计算器")
        self.root.geometry("500x450")
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TEntry", font=("SimHei", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建输入框架
        self.input_frame = ttk.LabelFrame(self.main_frame, text="商品信息", padding="10")
        self.input_frame.pack(fill=tk.X, pady=10)
        
        # 长度输入
        ttk.Label(self.input_frame, text="长度 (cm):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.length_var = tk.DoubleVar(value=15)
        ttk.Entry(self.input_frame, textvariable=self.length_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 宽度输入
        ttk.Label(self.input_frame, text="宽度 (cm):").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.width_var = tk.DoubleVar(value=15)
        ttk.Entry(self.input_frame, textvariable=self.width_var, width=10).grid(row=0, column=3, sticky=tk.W, pady=5)
        
        # 高度输入
        ttk.Label(self.input_frame, text="高度 (cm):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.height_var = tk.DoubleVar(value=15)
        ttk.Entry(self.input_frame, textvariable=self.height_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 重量输入
        ttk.Label(self.input_frame, text="重量 (g):").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.weight_var = tk.DoubleVar(value=15)
        ttk.Entry(self.input_frame, textvariable=self.weight_var, width=10).grid(row=1, column=3, sticky=tk.W, pady=5)
        
        # 国家选择
        ttk.Label(self.input_frame, text="目标国家:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.country_var = tk.StringVar(value="US")
        ttk.Combobox(self.input_frame, textvariable=self.country_var, values=["US", "MX", "CA", "UK", "DE", "FR", "IT", "ES"], width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 计算按钮
        self.calculate_btn = ttk.Button(self.main_frame, text="计算FBA费用", command=self.calculate_fba)
        self.calculate_btn.pack(pady=10)
        
        # 结果框架
        self.result_frame = ttk.LabelFrame(self.main_frame, text="计算结果", padding="10")
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 结果文本框
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, height=10, font=("SimHei", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(self.result_text, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

    def calculate_volume_weight(self):
        """计算体积重量"""
        length = self.length_var.get()
        width = self.width_var.get()
        height = self.height_var.get()
        return length * width * height / 6000 * 1000

    def calculate_fba(self):
        """计算FBA费用"""
        try:
            # 获取输入值
            length = self.length_var.get()
            width = self.width_var.get()
            height = self.height_var.get()
            weight = self.weight_var.get()
            country = self.country_var.get()
            
            # 计算体积重
            volume_weight = self.calculate_volume_weight()
            
            # 确定计费重量
            billing_weight = volume_weight if volume_weight > weight else weight
            
            # 清空结果文本框
            self.result_text.delete(1.0, tk.END)
            
            # 显示计算信息
            self.result_text.insert(tk.END, f"商品尺寸: {length} x {width} x {height} cm\n")
            self.result_text.insert(tk.END, f"商品重量: {weight} g\n")
            self.result_text.insert(tk.END, f"体积重量: {volume_weight:.2f} g\n")
            self.result_text.insert(tk.END, f"计费重量: {billing_weight:.2f} g\n\n")
            self.result_text.insert(tk.END, f"目标国家: {country}\n\n")
            self.result_text.insert(tk.END, "正在获取FBA费用信息...\n")
            self.root.update()
            
            # 调用API
            url = f"https://www.sellersprite.com/v2/tools/fba-calculator/calculate/{country}"
            data = {
                "marketplace": country,
                "length": length,
                "width": width,
                "height": height,
                "lengthUnit": "cm",
                "weights": billing_weight,
                "weightUnit": "g",
                "isSmallAndLight": False,
                "param": {
                    "isClothes": False,
                    "withBattery": False,
                    "isTV": False
                }
            }
            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0"
            }
            
            # 发送请求
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                json_data = "FBA费用:" + str(response.json()["data"])
                # 直接显示API返回的结果
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, json_data)
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"请求失败，状态码: {response.status_code}\n")
                self.result_text.insert(tk.END, f"错误信息: {response.text}")
                
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"发生错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FBACalculatorApp(root)
    root.mainloop()    