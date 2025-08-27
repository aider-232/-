import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import requests
from io import BytesIO
import json  # 新增：用于处理类别名称的保存和加载
import os

# 加载训练好的模型和类别名称
def load_model_and_classes(model_path, classes_path=r'产品图像分类_通用_类别.json'):
    """加载模型和对应的类别名称"""
    # 加载模型
    model = tf.keras.models.load_model(model_path)
    
    # 加载类别名称
    if os.path.exists(classes_path):
        with open(classes_path, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
        return model, class_names
    
    else:
        raise FileNotFoundError(f"类别名称文件 {classes_path} 不存在")

# 定义图片预处理函数
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
def predict_from_file(image_path, model, class_names):
    # 加载本地图片
    img = load_img(image_path)
    # 预处理
    processed_img = preprocess_image(img)
    # 预测
    return _predict(processed_img, model, class_names)

# 从网络URL加载图片并预测
def predict_from_url(image_url, model, class_names):
    try:
        # 发送请求下载图片
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 将图片数据转换为PIL对象
        img = load_img(BytesIO(response.content))
        
        # 预处理并预测
        processed_img = preprocess_image(img)
        return _predict(processed_img, model, class_names)
    
    except Exception as e:
        return f"下载或处理图片失败：{str(e)}", 0.0

# 内部预测函数
def _predict(processed_img, model, class_names):
    # 模型预测
    prediction_prob = model.predict(processed_img)
    predicted_class_idx = np.argmax(prediction_prob)
    
    predicted_class = class_names[predicted_class_idx]
    confidence = prediction_prob[0][predicted_class_idx] * 100  # 转换为百分比
    
    return predicted_class, confidence

# 训练时保存类别名称的辅助函数（训练脚本中使用）
def save_class_names(class_names, save_path='class_names.json'):
    """保存类别名称到JSON文件"""
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(class_names, f, ensure_ascii=False, indent=2)
    print(f"类别名称已保存到 {save_path}")

# 测试入口
if __name__ == "__main__":
    # 加载模型和类别名称
    model, class_names = load_model_and_classes(r"kk.h5")
    print(f"加载的类别名称: {class_names}")
    
    # 测试本地图片
    print("\n=== 本地图片测试 ===")
    try:
        file_result, file_confidence = predict_from_file("测试图片.png", model, class_names)
        print(f"预测类别：{file_result}")
        print(f"置信度：{file_confidence:.2f}%")
    except Exception as e:
        print(f"本地图片预测失败：{str(e)}")
    
    # 测试网络图片
    print("\n=== 网络图片测试 ===")
    url = "https://m.media-amazon.com/images/I/41CJq0ogaoL._AC_US600_.jpg"  # 替换为实际图片URL
    url_result, url_confidence = predict_from_url(url, model, class_names)
    print(f"预测类别：{url_result}")
    print(f"置信度：{url_confidence:.2f}%")

