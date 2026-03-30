import os
import uuid
import warnings
import datetime
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify, Response
from werkzeug.utils import secure_filename
import pandas as pd
from io import BytesIO
from flask_sqlalchemy import SQLAlchemy

# 读取 Streamlit 官方数据库配置（.streamlit/secrets.toml）
try:
    import tomllib
except ImportError:
    import tomli as tomllib  # Python < 3.11

app = Flask(__name__)
app.secret_key = 'yuan_music_secret_key'

basedir = os.path.abspath(os.path.dirname(__file__))

# --- 从 .streamlit/secrets.toml 读取数据库配置（Streamlit 官方方式） ---
SECRETS_FILE = os.path.join(basedir, '.streamlit', 'secrets.toml')

def load_db_url():
    """从 .streamlit/secrets.toml 读取数据库连接 URL"""
    try:
        with open(SECRETS_FILE, 'rb') as f:
            secrets = tomllib.load(f)
        db_url = secrets.get('connections', {}).get('sql', {}).get('url', '')
        if db_url:
            # 如果是相对路径的 SQLite，转为绝对路径
            if db_url.startswith('sqlite:///') and not db_url.startswith('sqlite:////'):
                db_path = db_url.replace('sqlite:///', '')
                db_url = 'sqlite:///' + os.path.join(basedir, db_path)
            return db_url
    except FileNotFoundError:
        print(f"⚠️ 配置文件不存在: {SECRETS_FILE}")
    except Exception as e:
        print(f"⚠️ 读取配置文件失败: {e}")
    
    # 默认使用 SQLite
    default_url = 'sqlite:///' + os.path.join(basedir, 'yuan_music.db')
    print(f"ℹ️ 使用默认数据库: {default_url}")
    return default_url

app.config['SQLALCHEMY_DATABASE_URI'] = load_db_url()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 照片上传配置（照片二进制数据存入数据库，不再保存到本地文件）
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 单次请求最大 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# MIME 类型映射
MIME_MAP = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'webp': 'image/webp',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# --- 1. 数据模型（与 Streamlit st.connection("sql") 兼容的 SQLAlchemy 模型） ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    nickname = db.Column(db.String(50))
    gender = db.Column(db.String(10))  # "男" 或 "女"
    hobbies = db.Column(db.Text)      # 兴趣爱好
    age = db.Column(db.Integer)
    hometown = db.Column(db.String(100))
    photos = db.relationship('Photo', backref='user', lazy=True, cascade='all, delete-orphan')

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)  # 照片二进制数据（存入数据库）
    mime_type = db.Column(db.String(50), nullable=False)  # MIME 类型，如 image/jpeg
    original_name = db.Column(db.String(200))  # 原始文件名
    created_at = db.Column(db.DateTime, default=db.func.now())

# 初始化数据库
with app.app_context():
    db.create_all()
    print(f"✅ 数据库初始化成功（配置来自 .streamlit/secrets.toml）")
    print(f"   连接地址: {app.config['SQLALCHEMY_DATABASE_URI']}")

# --- 2. 核心功能逻辑 ---

# AI 匹配简易逻辑：计算兴趣爱好的匹配分数（百分制）
def simple_ai_match(user_hobbies, candidate_hobbies, user_age=None, candidate_age=None):
    if not user_hobbies or not candidate_hobbies:
        return 60
    u_set = set(h.strip() for h in user_hobbies.replace('，', ',').split(',') if h.strip())
    c_set = set(h.strip() for h in candidate_hobbies.replace('，', ',').split(',') if h.strip())
    if not u_set or not c_set:
        return 60
    # 爱好相似度（Jaccard），占 50% 权重
    intersection = len(u_set & c_set)
    union = len(u_set | c_set)
    hobby_score = intersection / union  # 0~1

    # 年龄差距得分，占 50% 权重
    # 年龄差 0 岁 → 1.0，差 3 岁 → 0.7，差 5 岁 → 0.5，差 10 岁 → 0，差 >10 岁 → 0
    if user_age and candidate_age:
        age_diff = abs(user_age - candidate_age)
        age_score = max(0, 1 - age_diff / 10)  # 0~1
    else:
        age_score = 0.5  # 缺少年龄信息时给中间分

    # 综合得分：爱好 50% + 年龄 50%，映射到 60~100
    raw = hobby_score * 0.5 + age_score * 0.5
    return round(60 + raw * 40)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('square'))
    return render_template('login.html')

# 登录功能（演示版：手机号即登录）
@app.route('/login', methods=['POST'])
def login():
    phone = request.form.get('phone')
    user = User.query.filter_by(phone=phone).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('square'))
    flash('手机号不存在，请联系管理员导入')
    return redirect(url_for('index'))

# 缘音乐广场
@app.route('/square')
def square():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))
    
    me = User.query.get(user_id)
    # 基础查询：异性
    query = User.query.filter(User.gender != me.gender)

    # 获取搜索参数
    nickname = request.args.get('nickname', '').strip()
    hobby = request.args.get('hobby', '').strip()
    age_range = request.args.get('age_range', '').strip()

    # 按昵称模糊搜索
    if nickname:
        query = query.filter(User.nickname.contains(nickname))
    # 按爱好模糊搜索
    if hobby:
        query = query.filter(User.hobbies.contains(hobby))
    # 按年龄段筛选（3岁间隔）
    if age_range:
        if age_range == '18-20':
            query = query.filter(User.age >= 18, User.age <= 20)
        elif age_range == '21-23':
            query = query.filter(User.age >= 21, User.age <= 23)
        elif age_range == '24-26':
            query = query.filter(User.age >= 24, User.age <= 26)
        elif age_range == '27-29':
            query = query.filter(User.age >= 27, User.age <= 29)
        elif age_range == '30-32':
            query = query.filter(User.age >= 30, User.age <= 32)
        elif age_range == '33-35':
            query = query.filter(User.age >= 33, User.age <= 35)
        elif age_range == '36-38':
            query = query.filter(User.age >= 36, User.age <= 38)
        elif age_range == '39-41':
            query = query.filter(User.age >= 39, User.age <= 41)
        elif age_range == '42+':
            query = query.filter(User.age > 41)

    others = query.all()
    return render_template('square.html', users=others, me=me,
                           search_nickname=nickname, search_hobby=hobby, search_age_range=age_range)

# AI 配对
@app.route('/ai_match')
def match():
    user_id = session.get('user_id')
    if not user_id: return redirect(url_for('index'))
    me = User.query.get(user_id)
    others = User.query.filter(User.gender != me.gender).all()
    
    # 计算每个候选人的匹配分数并按分数降序排序
    match_list = []
    for u in others:
        score = simple_ai_match(me.hobbies, u.hobbies, me.age, u.age)
        match_list.append({'user': u, 'score': score})
    match_list.sort(key=lambda x: x['score'], reverse=True)
    return render_template('square.html', match_list=match_list, is_match=True, me=me)

# 编辑个人信息
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))
    me = User.query.get(user_id)
    if not me:
        session.clear()
        return redirect(url_for('index'))

    if request.method == 'POST':
        me.nickname = request.form.get('nickname', '').strip()
        me.gender = request.form.get('gender', '').strip()
        age_str = request.form.get('age', '').strip()
        me.age = int(age_str) if age_str else None
        me.hometown = request.form.get('hometown', '').strip() or None
        me.hobbies = request.form.get('hobbies', '').strip() or None
        db.session.commit()
        flash('✅ 个人信息已更新')
        return redirect(url_for('profile'))

    return render_template('profile.html', me=me)

# 上传照片（个人）
@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '请先登录'}), 401
    me = User.query.get(user_id)
    if not me:
        return jsonify({'error': '用户不存在'}), 404

    # 检查当前照片数量
    current_count = Photo.query.filter_by(user_id=me.id).count()
    if current_count >= 3:
        return jsonify({'error': '最多只能上传3张照片'}), 400

    file = request.files.get('photo')
    if not file or file.filename == '':
        return jsonify({'error': '请选择照片'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，请上传 jpg/png/gif/webp'}), 400

    # 读取文件二进制数据，存入数据库
    ext = file.filename.rsplit('.', 1)[1].lower()
    mime_type = MIME_MAP.get(ext, 'image/jpeg')
    file_data = file.read()

    photo = Photo(user_id=me.id, data=file_data, mime_type=mime_type, original_name=file.filename)
    db.session.add(photo)
    db.session.commit()
    return jsonify({'success': True, 'photo_id': photo.id, 'url': f'/photo/{photo.id}'})

# 从数据库读取照片并返回（替代本地文件读取）
@app.route('/photo/<int:photo_id>')
def serve_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return 'Not Found', 404
    return Response(photo.data, mimetype=photo.mime_type,
                    headers={'Cache-Control': 'public, max-age=86400'})

# 删除照片（个人）
@app.route('/delete_photo/<int:photo_id>', methods=['POST'])
def delete_photo(photo_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '请先登录'}), 401
    photo = Photo.query.get(photo_id)
    if not photo or photo.user_id != user_id:
        return jsonify({'error': '照片不存在'}), 404
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'success': True})

# 管理员：照片管理页面
@app.route('/admin_photos')
def admin_photos():
    users = User.query.order_by(User.id).all()
    return render_template('admin_photos.html', users=users)

# 管理员：为指定用户上传照片
@app.route('/admin_upload_photo/<int:uid>', methods=['POST'])
def admin_upload_photo(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    current_count = Photo.query.filter_by(user_id=uid).count()
    if current_count >= 3:
        return jsonify({'error': f'{user.nickname} 已有3张照片，请先删除再上传'}), 400

    file = request.files.get('photo')
    if not file or file.filename == '':
        return jsonify({'error': '请选择照片'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 读取文件二进制数据，存入数据库
    ext = file.filename.rsplit('.', 1)[1].lower()
    mime_type = MIME_MAP.get(ext, 'image/jpeg')
    file_data = file.read()

    photo = Photo(user_id=uid, data=file_data, mime_type=mime_type, original_name=file.filename)
    db.session.add(photo)
    db.session.commit()
    return jsonify({'success': True, 'photo_id': photo.id, 'url': f'/photo/{photo.id}'})

# 管理员：删除指定照片
@app.route('/admin_delete_photo/<int:photo_id>', methods=['POST'])
def admin_delete_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({'error': '照片不存在'}), 404
    db.session.delete(photo)
    db.session.commit()
    return jsonify({'success': True})

# 后台批量导入 Excel（访问 /admin_import 触发）
@app.route('/admin_import', methods=['GET', 'POST'])
def admin_import():
    if request.method == 'GET':
        # 展示上传表单页面（可爱轻松风格）
        return '''
        <!DOCTYPE html>
        <html lang="zh">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>批量导入 - 缘音乐</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
            <style>
                body { background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 30%, #e8eaf6 60%, #e0f7fa 100%);
                    color: #5d4037; font-family: 'Noto Sans SC', sans-serif; min-height: 100vh; }
                .navbar-cute { background: rgba(255,255,255,0.8)!important; backdrop-filter: blur(15px);
                    border-bottom: 2px solid #f8bbd0; box-shadow: 0 2px 12px rgba(233,150,180,0.15); }
                .navbar-cute .navbar-brand { color: #e91e63!important; font-weight: 700; letter-spacing: 1px; font-size: 1.1rem; }
                .import-card { position: relative; z-index: 1; max-width: 550px; margin: 40px auto;
                    background: rgba(255,255,255,0.85); backdrop-filter: blur(10px);
                    border: 2px solid rgba(248,187,208,0.5); border-radius: 24px;
                    padding: 35px; box-shadow: 0 4px 20px rgba(233,150,180,0.15); }
                .import-card h2 { color: #e91e63; font-weight: 700; font-size: 1.4rem; margin-bottom: 15px; }
                .import-card p { color: #8d6e63; font-size: 0.9rem; }
                .import-card a { color: #e91e63; text-decoration: none; font-weight: 500; transition: all 0.3s; }
                .import-card a:hover { color: #ab47bc; }
                .file-input { background: rgba(243,229,245,0.3); border: 2px dashed #e1bee7;
                    border-radius: 16px; padding: 20px; text-align: center; cursor: pointer; transition: all 0.3s; color: #a1887f; }
                .file-input:hover { border-color: #f06292; background: rgba(252,228,236,0.3); }
                input[type="file"] { color: #8d6e63; }
                input[type="file"]::file-selector-button { background: linear-gradient(135deg, #fce4ec, #f3e5f5); border: 2px solid #f8bbd0;
                    color: #e91e63; border-radius: 10px; padding: 6px 16px; cursor: pointer; transition: all 0.3s; margin-right: 10px; font-weight: 500; }
                input[type="file"]::file-selector-button:hover { background: #f8bbd0; color: #c2185b; }
                .btn-upload { background: linear-gradient(135deg, #f06292, #ab47bc); border: none; color: #fff;
                    border-radius: 16px; padding: 12px 40px; font-weight: 700; letter-spacing: 2px; font-size: 1rem;
                    transition: all 0.3s; box-shadow: 0 4px 15px rgba(240,98,146,0.3); }
                .btn-upload:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(240,98,146,0.4); color: #fff; }
            </style>
        </head>
        <body>
            <nav class="navbar navbar-cute sticky-top">
                <div class="container-fluid">
                    <span class="navbar-brand">📦 数据导入</span>
                </div>
            </nav>
            <div class="import-card">
                <h2>🌸 批量导入用户（Excel）</h2>
                <p>Excel 文件需包含以下列：phone, nickname, gender, hobbies, age, hometown（可选）</p>
                <p style="margin-bottom: 15px;"><a href="/admin_import/template">📥 下载 Excel 导入模板</a></p>
                <p style="margin-bottom: 25px;"><a href="/admin_photos">📷 管理用户照片</a></p>
                <form method="post" enctype="multipart/form-data">
                    <div class="file-input mb-4">
                        <input type="file" name="file" accept=".xlsx,.xls,.csv" required>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-upload">🌟 上传并导入</button>
                    </div>
                </form>
            </div>
        </body>
        </html>
        '''

    # POST：处理上传的文件
    file = request.files.get('file')
    if not file or file.filename == '':
        flash('请选择要上传的文件')
        return redirect(url_for('admin_import'))

    filename = file.filename.lower()
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file, engine='openpyxl')
        else:
            flash('不支持的文件格式，请上传 .xlsx / .xls / .csv 文件')
            return redirect(url_for('admin_import'))
    except Exception as e:
        flash(f'文件读取失败：{e}')
        return redirect(url_for('admin_import'))

    # 校验必需列
    required_cols = ['phone', 'nickname', 'gender', 'hobbies', 'age']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        flash(f'Excel 缺少必需列：{", ".join(missing)}')
        return redirect(url_for('admin_import'))

    # 逐行导入
    imported, skipped = 0, 0
    for _, row in df.iterrows():
        phone = str(row['phone']).strip()
        if User.query.filter_by(phone=phone).first():
            skipped += 1
            continue
        u = User(
            phone=phone,
            nickname=str(row['nickname']).strip(),
            gender=str(row['gender']).strip(),
            hobbies=str(row.get('hobbies', '')).strip(),
            age=int(row['age']) if pd.notna(row['age']) else None,
            hometown=str(row.get('hometown', '')).strip() if pd.notna(row.get('hometown')) else None
        )
        db.session.add(u)
        imported += 1
    db.session.commit()
    return f'导入完成！新增 {imported} 人，跳过已存在 {skipped} 人。<br><a href="/admin_import">继续导入</a> | <a href="/square">进入广场</a>'

# 下载 Excel 导入模板
@app.route('/admin_import/template')
def admin_import_template():
    # 创建包含示例数据的模板
    sample_data = {
        'phone': ['13800000001', '13800000002'],
        'nickname': ['示例昵称1', '示例昵称2'],
        'gender': ['男', '女'],
        'hobbies': ['音乐,旅游,跑步', '绘画,美食,音乐'],
        'age': [25, 23],
        'hometown': ['北京', '上海']
    }
    df = pd.DataFrame(sample_data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='用户数据')
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='用户导入模板.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5002)