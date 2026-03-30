import streamlit as st
import pandas as pd
import base64
import io
import libsql_experimental as libsql
from datetime import datetime

# ==================== 超级管理员配置 ====================
SUPER_ADMIN_PHONES = {"18820097665"}  # 超级管理员手机号集合

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="缘音乐",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ==================== 全局样式（可爱轻松风格） ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

    /* 全局背景 - 动态渐变 */
    .stApp {
        background: linear-gradient(135deg, #fff0f5 0%, #fce4ec 20%, #f3e5f5 40%, #e8eaf6 60%, #e1f5fe 80%, #e0f7fa 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 隐藏默认菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 标题样式 */
    h1 {
        color: #e91e63 !important;
        font-weight: 700 !important;
        text-align: center;
        text-shadow: 0 2px 10px rgba(233, 30, 99, 0.15);
    }
    h2, h3 {
        color: #ab47bc !important;
        font-weight: 600 !important;
    }

    /* 按钮美化 - 更小巧精致 */
    .stButton > button {
        background: linear-gradient(135deg, #f48fb1, #ce93d8) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.5px;
        padding: 6px 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(244, 143, 177, 0.3) !important;
        min-height: 38px !important;
        height: 38px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(240, 98, 146, 0.4) !important;
        background: linear-gradient(135deg, #f06292, #ab47bc) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* 输入框美化 */
    .stTextInput > div > div > input {
        border: 2px solid #f8bbd0 !important;
        border-radius: 16px !important;
        padding: 10px 16px !important;
        background: rgba(255,255,255,0.8) !important;
        transition: all 0.3s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #f06292 !important;
        box-shadow: 0 0 0 3px rgba(240, 98, 146, 0.12) !important;
        background: white !important;
    }
    .stSelectbox > div > div {
        border: 2px solid #f8bbd0 !important;
        border-radius: 16px !important;
    }
    .stNumberInput > div > div > input {
        border: 2px solid #f8bbd0 !important;
        border-radius: 16px !important;
    }

    /* 副标题 */
    .subtitle {
        color: #ce93d8;
        font-size: 0.85rem;
        letter-spacing: 4px;
        font-weight: 400;
        text-align: center;
        margin-top: -8px;
    }

    /* 欢迎横幅 */
    .welcome-banner {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(252,228,236,0.7));
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1.5px solid rgba(248, 187, 208, 0.3);
        padding: 20px 28px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(233, 150, 180, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .welcome-text {
        color: #5d4037;
        font-size: 1rem;
    }
    .welcome-text strong {
        color: #e91e63;
        font-size: 1.15rem;
    }
    .welcome-emoji {
        font-size: 2rem;
    }

    /* 统计信息 */
    .stat-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    .stat-item {
        flex: 1;
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1.5px solid rgba(248, 187, 208, 0.25);
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(233, 150, 180, 0.08);
    }
    .stat-num {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e91e63;
        display: block;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #a1887f;
        margin-top: 2px;
    }

    /* 空状态 */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #bcaaa4;
    }
    .empty-state .empty-icon {
        font-size: 4rem;
        margin-bottom: 16px;
        display: block;
    }
    .empty-state .empty-title {
        font-size: 1.1rem;
        color: #8d6e63;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .empty-state .empty-desc {
        font-size: 0.85rem;
        color: #bcaaa4;
    }

    /* 分隔线 */
    hr {
        border: none;
        border-top: 1.5px dashed rgba(248, 187, 208, 0.5);
        margin: 16px 0;
    }

    /* 浮动装饰 */
    .deco-float {
        position: fixed;
        pointer-events: none;
        z-index: 0;
        opacity: 0.15;
        font-size: 1.5rem;
        animation: floatUp 8s ease-in-out infinite;
    }
    @keyframes floatUp {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(10deg); }
    }

    /* 登录页装饰 */
    .login-deco {
        text-align: center;
        font-size: 3.5rem;
        margin-bottom: 8px;
        animation: bounce 2s ease-in-out infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    .login-subtitle-box {
        background: linear-gradient(135deg, rgba(252,228,236,0.6), rgba(243,229,245,0.6));
        border-radius: 30px;
        padding: 6px 24px;
        display: inline-block;
        margin: 4px auto 20px;
    }

    /* 页面标题区域 */
    .page-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.85), rgba(252,228,236,0.5));
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1.5px solid rgba(248, 187, 208, 0.25);
        padding: 16px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 15px rgba(233, 150, 180, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .page-header-title {
        color: #ab47bc;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
    }

    /* Expander 美化 */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.6) !important;
        border-radius: 14px !important;
        border: 1.5px solid rgba(248, 187, 208, 0.3) !important;
    }

    /* 表单美化 */
    [data-testid="stForm"] {
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1.5px solid rgba(248, 187, 208, 0.25);
        padding: 24px;
        box-shadow: 0 2px 15px rgba(233, 150, 180, 0.08);
    }

    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff0f5, #fce4ec, #f3e5f5) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.7) !important;
        color: #ab47bc !important;
        border: 1.5px solid rgba(248, 187, 208, 0.4) !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.95) !important;
        border-color: #f48fb1 !important;
        box-shadow: 0 2px 10px rgba(244, 143, 177, 0.2) !important;
    }

    /* 文件上传器美化 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #f8bbd0 !important;
        border-radius: 16px !important;
        padding: 8px !important;
    }

    /* 成功/警告/错误消息美化 */
    .stAlert {
        border-radius: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据库连接（Turso/libsql） ====================
@st.cache_resource
def get_connection():
    """获取 Turso 数据库连接（从 .streamlit/secrets.toml 读取配置）"""
    turso_url = st.secrets["turso"]["url"]
    turso_token = st.secrets["turso"]["auth_token"]
    return libsql.connect(turso_url, auth_token=turso_token)

conn = get_connection()

# ==================== 初始化数据库表 ====================
def init_db():
    """创建数据库表（如果不存在）- Turso/libsql"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE NOT NULL,
            nickname TEXT,
            gender TEXT,
            hobbies TEXT,
            age INTEGER,
            hometown TEXT
        )
    """)
    # 照片数据使用 Base64 文本存储
    conn.execute("""
        CREATE TABLE IF NOT EXISTS photo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            data_b64 TEXT NOT NULL,
            mime_type TEXT NOT NULL,
            original_name TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES user(id)
        )
    """)
    conn.commit()

init_db()

# ==================== 辅助函数 ====================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MIME_MAP = {
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'webp': 'image/webp',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _rows_to_dicts(cursor, columns):
    """将 cursor 结果转为字典列表"""
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

USER_COLUMNS = ['id', 'phone', 'nickname', 'gender', 'hobbies', 'age', 'hometown']

def get_user_by_phone(phone):
    """根据手机号查询用户"""
    cur = conn.execute("SELECT * FROM user WHERE phone = ?", (phone,))
    row = cur.fetchone()
    if row:
        return dict(zip(USER_COLUMNS, row))
    return None

def get_user_by_id(user_id):
    """根据 ID 查询用户"""
    cur = conn.execute("SELECT * FROM user WHERE id = ?", (int(user_id),))
    row = cur.fetchone()
    if row:
        return dict(zip(USER_COLUMNS, row))
    return None

def get_all_users():
    """获取所有用户（排除超级管理员）"""
    cur = conn.execute("SELECT * FROM user ORDER BY id")
    all_users = _rows_to_dicts(cur, USER_COLUMNS)
    return [u for u in all_users if u.get('phone') not in SUPER_ADMIN_PHONES]

def get_opposite_gender_users(gender):
    """获取异性用户（排除超级管理员）"""
    opposite = '女' if gender == '男' else '男'
    cur = conn.execute("SELECT * FROM user WHERE gender = ?", (opposite,))
    users = _rows_to_dicts(cur, USER_COLUMNS)
    return [u for u in users if u.get('phone') not in SUPER_ADMIN_PHONES]

PHOTO_LIST_COLUMNS = ['id', 'user_id', 'mime_type', 'original_name', 'created_at']

def get_user_photos(user_id):
    """获取用户的所有照片（返回 id, mime_type, original_name）"""
    cur = conn.execute(
        "SELECT id, user_id, mime_type, original_name, created_at FROM photo WHERE user_id = ?",
        (int(user_id),)
    )
    return _rows_to_dicts(cur, PHOTO_LIST_COLUMNS)

def get_photo_data(photo_id):
    """获取照片数据（Base64 文本 → 二进制）"""
    cur = conn.execute("SELECT data_b64, mime_type FROM photo WHERE id = ?", (int(photo_id),))
    row = cur.fetchone()
    if row:
        try:
            data = base64.b64decode(row[0])
        except Exception:
            data = row[0]  # 兜底
        return data, row[1]
    return None, None

def get_photo_count(user_id):
    """获取用户照片数量"""
    cur = conn.execute("SELECT COUNT(*) FROM photo WHERE user_id = ?", (int(user_id),))
    row = cur.fetchone()
    return int(row[0]) if row else 0

def photo_to_base64(photo_id):
    """将照片转为 base64 用于页面展示"""
    data, mime_type = get_photo_data(photo_id)
    if data:
        b64 = base64.b64encode(data).decode()
        return f"data:{mime_type};base64,{b64}"
    return None

def is_admin():
    """判断当前登录用户是否为超级管理员"""
    if not st.session_state.get('user_id'):
        return False
    login_phone = st.session_state.get('login_phone')
    if login_phone and login_phone in SUPER_ADMIN_PHONES:
        return True
    # 兜底：从数据库查询 phone 字段
    me = get_user_by_id(st.session_state.user_id)
    if me and me.get('phone') in SUPER_ADMIN_PHONES:
        st.session_state.login_phone = me.get('phone')
        return True
    return False

# ==================== 卡片渲染辅助函数 ====================
CARD_CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: transparent; }
    .cute-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(252,228,236,0.3));
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1.5px solid rgba(248, 187, 208, 0.3);
        padding: 20px 22px;
        margin: 0;
        box-shadow: 0 3px 15px rgba(233, 150, 180, 0.12);
        transition: all 0.3s ease;
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #5d4037;
        font-size: 14px;
        line-height: 1.5;
    }
    .cute-card:hover {
        border-color: #f8bbd0;
        box-shadow: 0 6px 25px rgba(233, 150, 180, 0.2);
        transform: translateY(-2px);
    }
    .user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #f8bbd0, #ce93d8);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        color: white;
        margin-right: 14px;
        flex-shrink: 0;
        box-shadow: 0 2px 8px rgba(244, 143, 177, 0.3);
    }
    .user-info-row {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    .user-name {
        font-weight: 700;
        font-size: 1.05rem;
        color: #5d4037;
    }
    .user-meta {
        color: #a1887f;
        font-size: 0.82rem;
        margin-top: 2px;
    }
    .hobby-tag {
        display: inline-block;
        background: linear-gradient(135deg, #fce4ec, #f3e5f5);
        border: 1px solid rgba(248, 187, 208, 0.6);
        color: #ad1457;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
    .match-high {
        display: inline-block;
        background: linear-gradient(135deg, #fce4ec, #f8bbd0);
        border: 2px solid #f06292;
        color: #c2185b;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: bold;
    }
    .match-medium {
        display: inline-block;
        background: linear-gradient(135deg, #f3e5f5, #e1bee7);
        border: 2px solid #ce93d8;
        color: #7b1fa2;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: bold;
    }
    .match-low {
        display: inline-block;
        background: #f5f5f5;
        border: 2px solid #e0e0e0;
        color: #9e9e9e;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: bold;
    }
    .photo-thumb {
        width: 72px;
        height: 72px;
        border-radius: 12px;
        object-fit: cover;
        border: 2px solid rgba(248, 187, 208, 0.5);
        margin-right: 6px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .photos-row {
        margin: 10px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .admin-photo-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(243,229,245,0.3));
        backdrop-filter: blur(10px);
        border: 1.5px solid rgba(248, 187, 208, 0.3);
        border-radius: 16px;
        padding: 14px 18px;
        margin: 0;
        box-shadow: 0 2px 10px rgba(233, 150, 180, 0.08);
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #5d4037;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .photo-count-tag {
        display: inline-block;
        background: linear-gradient(135deg, #fce4ec, #f3e5f5);
        border: 1px solid #f8bbd0;
        color: #e91e63;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
    }
</style>
"""

def render_card(html_body):
    """渲染带样式的 HTML 卡片（st.html 在 iframe 中，需要内嵌 CSS）"""
    st.html(CARD_CSS + html_body)

def simple_ai_match(user_hobbies, candidate_hobbies, user_age=None, candidate_age=None):
    """AI 匹配简易逻辑：计算兴趣爱好+年龄的匹配分数（百分制）"""
    if not user_hobbies or not candidate_hobbies:
        return 60
    u_set = set(h.strip() for h in str(user_hobbies).replace('，', ',').split(',') if h.strip())
    c_set = set(h.strip() for h in str(candidate_hobbies).replace('，', ',').split(',') if h.strip())
    if not u_set or not c_set:
        return 60
    # 爱好相似度（Jaccard），占 50% 权重
    intersection = len(u_set & c_set)
    union = len(u_set | c_set)
    hobby_score = intersection / union

    # 年龄差距得分，占 50% 权重
    if user_age and candidate_age:
        try:
            age_diff = abs(int(user_age) - int(candidate_age))
            age_score = max(0, 1 - age_diff / 10)
        except (ValueError, TypeError):
            age_score = 0.5
    else:
        age_score = 0.5

    raw = hobby_score * 0.5 + age_score * 0.5
    return round(60 + raw * 40)

# ==================== 初始化 session_state ====================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'login_phone' not in st.session_state:
    st.session_state.login_phone = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def navigate(page):
    st.session_state.page = page
    st.rerun()

def logout():
    st.session_state.user_id = None
    st.session_state.login_phone = None
    st.session_state.page = 'login'
    st.rerun()

# ==================== 页面：登录 ====================
def page_login():
    # 浮动装饰
    st.markdown("""
    <div style="text-align:center; padding-top: 40px;">
        <div class="login-deco">🎵</div>
        <h1 style="margin-bottom:0; font-size:2.5rem;">缘音乐</h1>
        <div style="text-align:center;">
            <div class="login-subtitle-box">
                <span class="subtitle" style="margin:0;">♪ YUAN MUSIC ♪</span>
            </div>
        </div>
        <p style="color:#a1887f; font-size:0.9rem; margin-top:4px;">用音乐连接有缘人 💕</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        phone = st.text_input("📱 输入手机号登录", placeholder="请输入手机号", label_visibility="collapsed")
        if st.button("🌸 进入广场", use_container_width=True):
            if phone:
                phone_stripped = phone.strip()
                user = get_user_by_phone(phone_stripped)
                # 超级管理员手机号：若数据库中不存在则自动创建
                if not user and phone_stripped in SUPER_ADMIN_PHONES:
                    conn.execute(
                        "INSERT INTO user (phone, nickname, gender, hobbies, age) VALUES (?, ?, ?, ?, ?)",
                        (phone_stripped, "超级管理员", "男", "管理", 0)
                    )
                    conn.commit()
                    user = get_user_by_phone(phone_stripped)
                if user:
                    st.session_state.user_id = user['id']
                    st.session_state.login_phone = phone_stripped
                    st.session_state.page = 'square'
                    st.rerun()
                else:
                    st.error("手机号不存在，请联系管理员导入")
            else:
                st.warning("请输入手机号")

        st.markdown("""
        <div style="text-align:center; margin-top:30px; color:#bcaaa4; font-size:0.78rem;">
            🌸 遇见美好，从这里开始 🌸
        </div>
        """, unsafe_allow_html=True)

# ==================== 页面：缘音乐广场 ====================
def page_square():
    me = get_user_by_id(st.session_state.user_id)
    if not me:
        logout()
        return

    # 导航栏 - 更紧凑的布局
    if is_admin():
        col1, col2, col3, col4, col5, col6 = st.columns([3, 1.2, 1.2, 1.2, 1.2, 0.8])
    else:
        col1, col2, col3, col4 = st.columns([4, 1.2, 1.2, 1])
    with col1:
        st.markdown("### 🌸 缘音乐广场")
    with col2:
        if st.button("✏️ 资料", key="nav_edit"):
            navigate('profile')
    with col3:
        if st.button("💘 配对", key="nav_match"):
            navigate('ai_match')
    if is_admin():
        with col4:
            if st.button("📷 照片", key="nav_admin_photos"):
                navigate('admin_photos')
        with col5:
            if st.button("📦 导入", key="nav_admin_import"):
                navigate('admin_import')
        with col6:
            if st.button("👋", key="nav_exit"):
                logout()
    else:
        with col4:
            if st.button("👋", key="nav_exit"):
                logout()

    # 欢迎横幅
    nickname = me.get('nickname', '')
    others_count = len(get_opposite_gender_users(me.get('gender', '')))
    st.markdown(f"""
    <div class="welcome-banner">
        <div class="welcome-text">
            你好呀，<strong>{nickname}</strong> ✨<br>
            <span style="font-size:0.82rem; color:#a1887f;">今天也要遇见美好的人哦~</span>
        </div>
        <div class="welcome-emoji">🎶</div>
    </div>
    """, unsafe_allow_html=True)

    # 统计信息
    all_users = get_all_users()
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item">
            <span class="stat-num">{len(all_users)}</span>
            <span class="stat-label">总用户数</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">{others_count}</span>
            <span class="stat-label">可匹配</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">💕</span>
            <span class="stat-label">等你发现</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 搜索筛选栏
    with st.expander("🔍 搜索筛选", expanded=False):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            search_nickname = st.text_input("搜索昵称", key="search_nick")
        with sc2:
            search_hobby = st.text_input("搜索爱好", key="search_hobby")
        with sc3:
            age_options = ["不限", "18-20岁", "21-23岁", "24-26岁", "27-29岁",
                           "30-32岁", "33-35岁", "36-38岁", "39-41岁", "42岁以上"]
            search_age = st.selectbox("🎂 年龄段", age_options, key="search_age")

    # 获取异性用户
    others = get_opposite_gender_users(me.get('gender', ''))

    # 应用搜索过滤
    if search_nickname:
        others = [u for u in others if search_nickname.lower() in (u.get('nickname', '') or '').lower()]
    if search_hobby:
        others = [u for u in others if search_hobby in (u.get('hobbies', '') or '')]
    if search_age != "不限":
        age_map = {
            "18-20岁": (18, 20), "21-23岁": (21, 23), "24-26岁": (24, 26),
            "27-29岁": (27, 29), "30-32岁": (30, 32), "33-35岁": (33, 35),
            "36-38岁": (36, 38), "39-41岁": (39, 41), "42岁以上": (42, 999),
        }
        lo, hi = age_map.get(search_age, (0, 999))
        others = [u for u in others if u.get('age') and lo <= int(u['age']) <= hi]

    if search_nickname or search_hobby or search_age != "不限":
        st.markdown(f"🔎 搜索结果：共找到 **{len(others)}** 人")

    # 展示用户卡片
    _render_user_cards(others)

# ==================== 页面：AI 配对 ====================
def page_ai_match():
    me = get_user_by_id(st.session_state.user_id)
    if not me:
        logout()
        return

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 💘 AI 智能配对")
    with col2:
        if st.button("🌸 返回"):
            navigate('square')

    st.markdown(f"""
    <div class="welcome-banner">
        <div class="welcome-text">
            根据兴趣爱好和年龄为 <strong>{me.get('nickname', '')}</strong> 匹配最佳对象 ✨
        </div>
        <div class="welcome-emoji">💘</div>
    </div>
    """, unsafe_allow_html=True)

    others = get_opposite_gender_users(me.get('gender', ''))

    # 计算匹配分数并排序
    match_list = []
    for u in others:
        score = simple_ai_match(me.get('hobbies'), u.get('hobbies'), me.get('age'), u.get('age'))
        match_list.append({'user': u, 'score': score})
    match_list.sort(key=lambda x: x['score'], reverse=True)

    # 展示配对结果
    for item in match_list:
        u = item['user']
        score = item['score']

        if score >= 85:
            score_html = f'<span class="match-high">💕 {score}分</span>'
        elif score >= 73:
            score_html = f'<span class="match-medium">💜 {score}分</span>'
        else:
            score_html = f'<span class="match-low">🤍 {score}分</span>'

        # 照片
        photos = get_user_photos(u['id'])
        photos_html = ""
        for p in photos:
            b64_url = photo_to_base64(p['id'])
            if b64_url:
                photos_html += f'<img src="{b64_url}" class="photo-thumb">'

        # 爱好标签
        hobbies_html = ""
        if u.get('hobbies'):
            for h in str(u['hobbies']).replace('，', ',').split(','):
                h = h.strip()
                if h:
                    hobbies_html += f'<span class="hobby-tag">{h}</span>'

        card_html = f"""
<div class="cute-card">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div class="user-info-row">
            <div class="user-avatar">{'👩' if u.get('gender') == '女' else '👨'}</div>
            <div>
                <div class="user-name">{u.get('nickname', '')}</div>
                <div class="user-meta">🎂 {u.get('age', '?')}岁 · 📍 {u.get('hometown', '未知') or '未知'}</div>
            </div>
        </div>
        {score_html}
    </div>
    {f'<div class="photos-row">{photos_html}</div>' if photos_html else ''}
    <div style="margin-top:8px;">{hobbies_html}</div>
</div>
"""
        render_card(card_html)

# ==================== 渲染用户卡片（广场用） ====================
def _render_user_cards(users):
    """渲染用户卡片列表"""
    if not users:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🌸</span>
            <div class="empty-title">暂时没有找到匹配的用户哦~</div>
            <div class="empty-desc">新的缘分正在路上，请耐心等待 💕</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for u in users:
        # 照片
        photos = get_user_photos(u['id'])
        photos_html = ""
        for p in photos:
            b64_url = photo_to_base64(p['id'])
            if b64_url:
                photos_html += f'<img src="{b64_url}" class="photo-thumb">'

        # 爱好标签
        hobbies_html = ""
        if u.get('hobbies'):
            for h in str(u['hobbies']).replace('，', ',').split(','):
                h = h.strip()
                if h:
                    hobbies_html += f'<span class="hobby-tag">{h}</span>'

        card_html = f"""
<div class="cute-card">
    <div class="user-info-row">
        <div class="user-avatar">{'👩' if u.get('gender') == '女' else '👨'}</div>
        <div>
            <div class="user-name">{u.get('nickname', '')}</div>
            <div class="user-meta">🎂 {u.get('age', '?')}岁 · 📍 {u.get('hometown', '未知') or '未知'}</div>
        </div>
    </div>
    {f'<div class="photos-row">{photos_html}</div>' if photos_html else ''}
    <div style="margin-top:8px;">{hobbies_html}</div>
</div>
"""
        render_card(card_html)

# ==================== 页面：编辑个人信息 ====================
def page_profile():
    me = get_user_by_id(st.session_state.user_id)
    if not me:
        logout()
        return

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### ✏️ 编辑个人信息")
    with col2:
        if st.button("🌸 返回"):
            navigate('square')

    st.markdown("---")

    # 个人信息表单
    with st.form("profile_form"):
        st.text_input("📱 手机号", value=me.get('phone', ''), disabled=True)
        nickname = st.text_input("✨ 昵称", value=me.get('nickname', '') or '')
        gender = st.radio("🌈 性别", ["男", "女"],
                          index=0 if me.get('gender') == '男' else 1,
                          horizontal=True)
        age = st.number_input("🎂 年龄", min_value=1, max_value=120,
                              value=int(me['age']) if me.get('age') else 25)
        hometown = st.text_input("🏠 家乡", value=me.get('hometown', '') or '')
        hobbies = st.text_input("🎯 兴趣爱好（多个用逗号分隔）",
                                value=me.get('hobbies', '') or '',
                                placeholder="如：音乐,旅游,跑步")

        if st.form_submit_button("💾 保存修改", use_container_width=True):
            conn.execute("""
                UPDATE user SET nickname=?, gender=?, age=?,
                hometown=?, hobbies=? WHERE id=?
""", (nickname.strip(), gender, age,
                  hometown.strip() or None, hobbies.strip() or None, me['id']))
            conn.commit()
            st.success("✅ 个人信息已更新！")
            st.rerun()

    # 照片管理区域
    st.markdown("---")
    st.markdown("#### 📷 我的照片（最多3张）")

    photos = get_user_photos(me['id'])
    photo_count = len(photos)

    # 展示已有照片
    if photos:
        cols = st.columns(3)
        for i, p in enumerate(photos):
            with cols[i]:
                b64_url = photo_to_base64(p['id'])
                if b64_url:
                    st.markdown(f'<img src="{b64_url}" style="width:100%;border-radius:14px;border:2px solid #f8bbd0;">', unsafe_allow_html=True)
                    if st.button(f"🗑️ 删除", key=f"del_photo_{p['id']}"):
                        conn.execute("DELETE FROM photo WHERE id = ?", (p['id'],))
                        conn.commit()
                        st.success("照片已删除")
                        st.rerun()

    # 上传新照片
    if photo_count < 3:
        uploaded = st.file_uploader(
            f"上传照片（还可上传 {3 - photo_count} 张）",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            key=f"photo_upload_{photo_count}"
        )
        if uploaded:
            # 防止 rerun 后重复插入：检查同名照片是否已存在
            existing = conn.execute(
                "SELECT id FROM photo WHERE user_id = ? AND original_name = ?",
                (me['id'], uploaded.name)
            ).fetchone()
            if not existing:
                file_data = uploaded.read()
                ext = uploaded.name.rsplit('.', 1)[1].lower() if '.' in uploaded.name else 'jpg'
                mime_type = MIME_MAP.get(ext, 'image/jpeg')

                # 将二进制数据编码为 Base64 文本存入 Turso
                data_b64 = base64.b64encode(file_data).decode('utf-8')
                conn.execute("""
                    INSERT INTO photo (user_id, data_b64, mime_type, original_name)
                    VALUES (?, ?, ?, ?)
""", (me['id'], data_b64, mime_type, uploaded.name))
                conn.commit()
                st.success("✅ 照片上传成功！")
                st.rerun()
    else:
        st.info("已达到最大照片数量（3张），如需更换请先删除已有照片")

    st.caption("支持 jpg/png/gif/webp 格式，单张不超过 5MB")

# ==================== 页面：管理员批量导入 ====================
def page_admin_import():
    col1, col2, col3 = st.columns([3, 1.2, 1.2])
    with col1:
        st.markdown("### 📦 批量导入用户")
    with col2:
        if st.button("📷 照片"):
            navigate('admin_photos')
    with col3:
        if st.button("🌸 广场"):
            navigate('square')

    st.markdown("---")

    # 下载模板
    sample_data = {
        'phone': ['13800000001', '13800000002'],
        'nickname': ['示例昵称1', '示例昵称2'],
        'gender': ['男', '女'],
        'hobbies': ['音乐,旅游,跑步', '绘画,美食,音乐'],
        'age': [25, 23],
        'hometown': ['北京', '上海']
    }
    df_template = pd.DataFrame(sample_data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='用户数据')
    output.seek(0)

    st.download_button(
        label="📥 下载 Excel 导入模板",
        data=output,
        file_name="用户导入模板.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")
    st.markdown("Excel 文件需包含以下列：`phone`, `nickname`, `gender`, `hobbies`, `age`, `hometown`（可选）")

    # 上传文件
    uploaded = st.file_uploader("选择 Excel/CSV 文件", type=['xlsx', 'xls', 'csv'])
    if uploaded:
        try:
            filename = uploaded.name.lower()
            if filename.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded, engine='openpyxl')
        except Exception as e:
            st.error(f"文件读取失败：{e}")
            return

        required_cols = ['phone', 'nickname', 'gender', 'hobbies', 'age']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(f"Excel 缺少必需列：{', '.join(missing)}")
            return

        st.dataframe(df, use_container_width=True)

        if st.button("🌟 确认导入", use_container_width=True):
            imported, skipped = 0, 0
            for _, row in df.iterrows():
                phone = str(row['phone']).strip()
                # 检查是否已存在
                existing = conn.execute(
                    "SELECT id FROM user WHERE phone = ?", (phone,)
                ).fetchone()
                if existing:
                    skipped += 1
                    continue
                conn.execute("""
                    INSERT INTO user (phone, nickname, gender, hobbies, age, hometown)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    phone,
                    str(row['nickname']).strip(),
                    str(row['gender']).strip(),
                    str(row.get('hobbies', '')).strip(),
                    int(row['age']) if pd.notna(row['age']) else None,
                    str(row.get('hometown', '')).strip() if pd.notna(row.get('hometown')) else None
                ))
                imported += 1
            conn.commit()
            st.success(f"✅ 导入完成！新增 **{imported}** 人，跳过已存在 **{skipped}** 人")
            st.balloons()

# ==================== 页面：管理员照片管理 ====================
def page_admin_photos():
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 📷 照片管理")
    with col2:
        if st.button("🔙 返回"):
            navigate('admin_import')

    st.markdown("🌟 为每位用户上传照片（每人最多3张），支持 jpg/png/gif/webp 格式")
    st.markdown("---")

    # 获取所有用户（包含超级管理员，但排除当前管理员自己）
    cur = conn.execute("SELECT * FROM user ORDER BY id")
    all_raw_users = _rows_to_dicts(cur, USER_COLUMNS)
    users = [u for u in all_raw_users if u.get('phone') not in SUPER_ADMIN_PHONES]

    for u in users:
        uid = u['id']
        photos = get_user_photos(uid)
        photo_count = len(photos)

        admin_card_html = f"""
<div class="admin-photo-card">
    <div style="display:flex; align-items:center; gap:10px;">
        <strong>{u.get('nickname', '')}</strong>
        <span style="color:#a1887f; font-size:0.82rem;">
            {u.get('phone', '')} · {u.get('gender', '')} · {u.get('age', '?')}岁
        </span>
    </div>
    <span class="photo-count-tag">{photo_count}/3</span>
</div>
"""
        render_card(admin_card_html)

        # 展示已有照片
        if photos:
            cols = st.columns(min(len(photos) + (1 if photo_count < 3 else 0), 4))
            for i, p in enumerate(photos):
                with cols[i]:
                    b64_url = photo_to_base64(p['id'])
                    if b64_url:
                        st.markdown(f'<img src="{b64_url}" style="width:90px;height:90px;border-radius:14px;object-fit:cover;border:2px solid #f8bbd0;">', unsafe_allow_html=True)
                        if st.button("✕", key=f"admin_del_{p['id']}"):
                            conn.execute("DELETE FROM photo WHERE id = ?", (p['id'],))
                            conn.commit()
                            st.rerun()

        # 上传按钮
        if photo_count < 3:
            uploaded = st.file_uploader(
                f"为 {u.get('nickname', '')} 上传照片",
                type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
                key=f"admin_upload_{uid}",
                label_visibility="collapsed"
            )
            if uploaded:
                # 防止 rerun 后重复插入：检查同名照片是否已存在
                existing = conn.execute(
                    "SELECT id FROM photo WHERE user_id = ? AND original_name = ?",
                    (uid, uploaded.name)
                ).fetchone()
                if not existing:
                    file_data = uploaded.read()
                    ext = uploaded.name.rsplit('.', 1)[1].lower() if '.' in uploaded.name else 'jpg'
                    mime_type = MIME_MAP.get(ext, 'image/jpeg')
                    # 将二进制数据编码为 Base64 文本存入 Turso
                    data_b64 = base64.b64encode(file_data).decode('utf-8')
                    conn.execute("""
                        INSERT INTO photo (user_id, data_b64, mime_type, original_name)
                        VALUES (?, ?, ?, ?)
""", (uid, data_b64, mime_type, uploaded.name))
                    conn.commit()
                    st.success(f"✅ 已为 {u.get('nickname', '')} 上传照片")
                    st.rerun()

        st.markdown("---")

# ==================== 路由分发 ====================
def main():
    # 未登录时，允许访问登录页和管理员页面
    page = st.session_state.page

    # 侧边栏导航（管理员入口）
    with st.sidebar:
        st.markdown("### 🎵 缘音乐")
        st.markdown("---")
        if st.session_state.user_id:
            me = get_user_by_id(st.session_state.user_id)
            if me:
                st.markdown(f"👤 **{me.get('nickname', '')}**")
            st.markdown("---")
            if st.button("🌸 缘音乐广场", use_container_width=True, key="nav_square"):
                navigate('square')
            if st.button("💘 AI 智能配对", use_container_width=True, key="nav_match_sidebar"):
                navigate('ai_match')
            if st.button("✏️ 编辑资料", use_container_width=True, key="nav_profile"):
                navigate('profile')
            st.markdown("---")
        if is_admin():
            st.markdown("##### 🔧 管理员")
            if st.button("📦 批量导入", use_container_width=True, key="nav_import"):
                navigate('admin_import')
            if st.button("📷 照片管理", use_container_width=True, key="nav_photos"):
                navigate('admin_photos')
        if st.session_state.user_id:
            st.markdown("---")
            if st.button("👋 退出登录", use_container_width=True, key="nav_logout"):
                logout()

    # 页面路由
    if page == 'login':
        page_login()
    elif page == 'square':
        if not st.session_state.user_id:
            navigate('login')
        else:
            page_square()
    elif page == 'ai_match':
        if not st.session_state.user_id:
            navigate('login')
        else:
            page_ai_match()
    elif page == 'profile':
        if not st.session_state.user_id:
            navigate('login')
        else:
            page_profile()
    elif page == 'admin_import':
        if is_admin():
            page_admin_import()
        else:
            st.error("⛔ 无权限访问，仅超级管理员可操作")
            navigate('login')
    elif page == 'admin_photos':
        if is_admin():
            page_admin_photos()
        else:
            st.error("⛔ 无权限访问，仅超级管理员可操作")
            navigate('login')
    else:
        page_login()

if __name__ == "__main__":
    main()
