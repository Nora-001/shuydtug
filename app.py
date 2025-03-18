from flask import Flask, request, redirect, url_for, render_template, session, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import random
import string
from io import BytesIO

# 初始化 Flask 应用
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# 生成随机验证码
def generate_captcha():
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    session['captcha'] = captcha  # 将验证码存储到 session
    return captcha

# 生成图像验证码
@app.route('/captcha')
def captcha_image():
    captcha_text = generate_captcha()  # 生成验证码
    print(f"生成的验证码：{captcha_text}")  # 调试输出

    # 创建验证码图片
    img = Image.new('RGB', (100, 40), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 尝试加载更合适的字体
    try:
        font = ImageFont.truetype("arial.ttf", 24)  # 使用 Arial 字体（Windows 常见字体）
    except:
        font = ImageFont.load_default()  # 如果 `arial.ttf` 不存在，使用默认字体
    
    draw.text((10, 5), captcha_text, fill=(0, 0, 0), font=font)

    # 转换图像为字节流
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # 禁用缓存，确保每次刷新都会生成新验证码
    response = send_file(img_io, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-cache'
    return response

# 首页路由
@app.route('/')
def index():
    return render_template('feedback.html', show_success_message=False)
    

# 提交反馈路由
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    # 处理反馈数据
    description = request.form.get('description')
    contact = request.form.get('contact', '匿名')
    image = request.files.get('image')
    user_captcha = request.form.get('captcha')

    # 验证验证码
    if user_captcha != session.get('captcha'):
        return '验证码错误！'

    # 图片处理（如果上传了图片）
    image_url = ''
    if image and image.filename != '':
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # 确保上传文件夹存在
        image.save(image_path)
        image_url = f"/{app.config['UPLOAD_FOLDER']}/{image.filename}"

    # 将反馈数据写入 feedback.txt
    with open('feedback.txt', 'a', encoding='utf-8') as f:
        f.write(f"问题描述：{description}\n")
        f.write(f"联系方式：{contact}\n")
        if image_url:
            f.write(f"图片链接：{image_url}\n")
        f.write("\n" + "="*30 + "\n\n")

    # 渲染模板并传递 show_success_message 变量
    return render_template('feedback.html', show_success_message=True)


if __name__ == '__main__':
    app.run(debug=True)
