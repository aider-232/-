# %%
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import requests  # 用于下载网络图片
from io import BytesIO  # 用于处理内存中的图片数据
import os  # 用于处理临时文件（可选）

# 加载训练好的模型
model = tf.keras.models.load_model('floor_mat_classifier.h5')

# 定义图片预处理函数（支持PIL图片对象）
def preprocess_image(img):
    img_size = (224, 224)  # 需与训练时一致
    
    # 调整图片尺寸
    img = img.resize(img_size)
    
    # 转换为数组并增加维度
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    
    # 预处理（需与训练时使用的模型对应）
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    
    return img_array

# 从本地文件加载图片并预测
def predict_from_file(image_path):
    # 加载本地图片
    img = load_img(image_path)
    # 预处理
    processed_img = preprocess_image(img)
    # 预测
    return _predict(processed_img)

# 从网络URL加载图片并预测
def predict_from_url(image_url):
    try:
        # 发送请求下载图片
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 将图片数据转换为PIL对象
        img = load_img(BytesIO(response.content))
        
        # 预处理并预测
        processed_img = preprocess_image(img)
        return _predict(processed_img)
    
    except Exception as e:
        return f"下载或处理图片失败：{str(e)}", 0.0

# 内部预测函数（复用逻辑）
def _predict(processed_img):
    # 模型预测
    prediction_prob = model.predict(processed_img)
    predicted_class_idx = np.argmax(prediction_prob)
    
    # 类别名称（需与训练时一致）
    class_names = ['cargo linear', 'floor mat', 'floor mat cargo linear']
    
    predicted_class = class_names[predicted_class_idx]
    confidence = prediction_prob[0][predicted_class_idx] * 100  # 转换为百分比
    
    return predicted_class, confidence

# 测试入口
if __name__ == "__main__":
    # 测试本地图片（替换为你的图片路径）
    print("=== 本地图片测试 ===")
    file_result, file_confidence = predict_from_file("测试图片_脚尾垫.jpeg")
    print(f"预测类别：{file_result}")
    print(f"置信度：{file_confidence:.2f}%")
    
    # 测试网络图片（替换为有效的图片URL）
    print("\n=== 网络图片测试 ===")
    url = "https://example.com/floor_mat.jpg"  # 替换为实际图片URL
    url_result, url_confidence = predict_from_url(url)
    print(f"预测类别：{url_result}")
    print(f"置信度：{url_confidence:.2f}%")


