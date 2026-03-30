import streamlit as st
import pandas as pd
import base64
import io
import requests
import json
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

# ==================== 全局样式（AI 科技风格） ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Orbitron:wght@400;700;900&display=swap');

    /* 全局背景 - 深色科技渐变 */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1137 25%, #141852 50%, #0d1137 75%, #0a0e27 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 网格背景装饰 */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 60px 60px;
        pointer-events: none;
        z-index: 0;
    }

    /* 隐藏默认菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 标题样式 - 霓虹发光 */
    h1 {
        background: linear-gradient(135deg, #00f5ff, #7c4dff, #ff4081) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 700 !important;
        text-align: center;
        filter: drop-shadow(0 0 20px rgba(0, 245, 255, 0.3));
    }
    h2, h3 {
        color: #00e5ff !important;
        font-weight: 600 !important;
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
    }

    /* 全局文字颜色 */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #c8d6e5;
    }
    .stApp .stMarkdown p {
        color: #c8d6e5;
    }

    /* 按钮美化 - 科技霓虹 */
    .stButton > button {
        background: linear-gradient(135deg, #0d47a1, #1565c0, #00bcd4) !important;
        color: #e0f7fa !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
        padding: 6px 18px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(0, 188, 212, 0.2), inset 0 0 15px rgba(0, 188, 212, 0.05) !important;
        min-height: 38px !important;
        height: 38px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.4), 0 0 50px rgba(0, 188, 212, 0.15) !important;
        background: linear-gradient(135deg, #1565c0, #00bcd4, #00e5ff) !important;
        border-color: rgba(0, 229, 255, 0.6) !important;
    }
    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* 输入框美化 - 科技毛玻璃风 */
    .stTextInput > div > div > input {
        border: 1.5px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.65), rgba(20, 24, 82, 0.55)) !important;
        backdrop-filter: blur(12px) !important;
        color: #e0f7fa !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15), 0 0 8px rgba(0, 229, 255, 0.04) !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(0, 229, 255, 0.5) !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.12), 0 0 24px rgba(0, 229, 255, 0.04), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.8), rgba(20, 24, 82, 0.7)) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(200, 214, 229, 0.35) !important;
    }

    /* 下拉框美化 - 科技毛玻璃风 */
    .stSelectbox > div > div {
        border: 1.5px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.65), rgba(20, 24, 82, 0.55)) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15), 0 0 8px rgba(0, 229, 255, 0.04) !important;
    }
    .stSelectbox > div > div:hover {
        border-color: rgba(0, 229, 255, 0.35) !important;
        box-shadow: 0 0 10px rgba(0, 229, 255, 0.08), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }
    /* 下拉框选项列表 - 全面覆盖 */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="select"] [data-baseweb="menu"],
    [data-baseweb="menu"],
    [role="listbox"],
    [data-baseweb="popover"] [data-baseweb="menu"],
    div[data-baseweb="popover"] > div > ul,
    div[data-baseweb="popover"] > div {
        background: #0d1137 !important;
        background-color: #0d1137 !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 229, 255, 0.06) !important;
    }
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [role="listbox"] li,
    [role="option"],
    [data-baseweb="menu"] [role="option"] {
        color: #c8d6e5 !important;
        background: transparent !important;
        background-color: transparent !important;
        transition: all 0.2s ease !important;
    }
    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover,
    [role="listbox"] li:hover,
    [role="option"]:hover,
    [data-baseweb="menu"] [role="option"]:hover {
        background: rgba(0, 229, 255, 0.1) !important;
        background-color: rgba(0, 229, 255, 0.1) !important;
        color: #e0f7fa !important;
    }
    [data-baseweb="popover"] li[aria-selected="true"],
    [data-baseweb="menu"] li[aria-selected="true"],
    [role="option"][aria-selected="true"],
    [data-baseweb="menu"] [role="option"][aria-selected="true"] {
        background: rgba(0, 229, 255, 0.15) !important;
        background-color: rgba(0, 229, 255, 0.15) !important;
        color: #00e5ff !important;
    }
    /* 下拉框滚动条 */
    [data-baseweb="popover"] ::-webkit-scrollbar,
    [data-baseweb="menu"] ::-webkit-scrollbar {
        width: 6px;
    }
    [data-baseweb="popover"] ::-webkit-scrollbar-track,
    [data-baseweb="menu"] ::-webkit-scrollbar-track {
        background: rgba(13, 17, 55, 0.5);
        border-radius: 3px;
    }
    [data-baseweb="popover"] ::-webkit-scrollbar-thumb,
    [data-baseweb="menu"] ::-webkit-scrollbar-thumb {
        background: rgba(0, 229, 255, 0.2);
        border-radius: 3px;
    }
    [data-baseweb="popover"] ::-webkit-scrollbar-thumb:hover,
    [data-baseweb="menu"] ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 229, 255, 0.35);
    }

    /* 数字输入框 */
    .stNumberInput > div > div > input {
        border: 1.5px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.65), rgba(20, 24, 82, 0.55)) !important;
        backdrop-filter: blur(12px) !important;
        color: #e0f7fa !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15), 0 0 8px rgba(0, 229, 255, 0.04) !important;
    }
    .stNumberInput > div > div > input:focus {
        border-color: rgba(0, 229, 255, 0.5) !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.12), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.8), rgba(20, 24, 82, 0.7)) !important;
    }

    /* 多选框美化 */
    .stMultiSelect > div > div {
        border: 1.5px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.65), rgba(20, 24, 82, 0.55)) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15), 0 0 8px rgba(0, 229, 255, 0.04) !important;
    }
    .stMultiSelect > div > div:hover {
        border-color: rgba(0, 229, 255, 0.35) !important;
    }

    /* 文本域美化 */
    .stTextArea > div > div > textarea {
        border: 1.5px solid rgba(0, 229, 255, 0.2) !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.65), rgba(20, 24, 82, 0.55)) !important;
        backdrop-filter: blur(12px) !important;
        color: #e0f7fa !important;
        transition: all 0.3s ease !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15), 0 0 8px rgba(0, 229, 255, 0.04) !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(0, 229, 255, 0.5) !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.12), inset 0 1px 2px rgba(0, 0, 0, 0.1) !important;
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.8), rgba(20, 24, 82, 0.7)) !important;
    }

    /* 副标题 */
    .subtitle {
        color: #00e5ff;
        font-size: 0.85rem;
        letter-spacing: 6px;
        font-weight: 400;
        text-align: center;
        margin-top: -8px;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
    }

    /* 欢迎横幅 - 科技毛玻璃 */
    .welcome-banner {
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.85), rgba(20, 24, 82, 0.7));
        backdrop-filter: blur(20px);
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, 0.15);
        padding: 20px 28px;
        margin-bottom: 20px;
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.05), inset 0 0 30px rgba(0, 229, 255, 0.02);
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }
    .welcome-banner::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 200%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.05), transparent);
        animation: scanLine 4s linear infinite;
    }
    @keyframes scanLine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    .welcome-text {
        color: #c8d6e5;
        font-size: 1rem;
        z-index: 1;
    }
    .welcome-text strong {
        color: #00e5ff;
        font-size: 1.15rem;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
    }
    .welcome-emoji {
        font-size: 2rem;
        z-index: 1;
        filter: drop-shadow(0 0 8px rgba(0, 229, 255, 0.5));
    }

    /* 统计信息 - 科技面板 */
    .stat-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    .stat-item {
        flex: 1;
        background: rgba(13, 17, 55, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 14px;
        border: 1px solid rgba(0, 229, 255, 0.12);
        padding: 14px 16px;
        text-align: center;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.04);
        position: relative;
        overflow: hidden;
    }
    .stat-item::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00e5ff, transparent);
        opacity: 0.5;
    }
    .stat-num {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00e5ff;
        display: block;
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.5);
        font-family: 'Orbitron', sans-serif;
    }
    .stat-label {
        font-size: 0.75rem;
        color: rgba(200, 214, 229, 0.6);
        margin-top: 2px;
        letter-spacing: 1px;
    }

    /* 空状态 */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: rgba(200, 214, 229, 0.5);
    }
    .empty-state .empty-icon {
        font-size: 4rem;
        margin-bottom: 16px;
        display: block;
        filter: drop-shadow(0 0 15px rgba(0, 229, 255, 0.3));
    }
    .empty-state .empty-title {
        font-size: 1.1rem;
        color: #00e5ff;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .empty-state .empty-desc {
        font-size: 0.85rem;
        color: rgba(200, 214, 229, 0.4);
    }

    /* 分隔线 - 科技线条 */
    hr {
        border: none;
        border-top: 1px solid rgba(0, 229, 255, 0.12);
        margin: 16px 0;
        box-shadow: 0 0 8px rgba(0, 229, 255, 0.05);
    }

    /* 脉冲动画 */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* 数据流动画 */
    @keyframes dataFlow {
        0% { transform: translateY(0) scale(1); opacity: 0.6; }
        50% { transform: translateY(-15px) scale(1.1); opacity: 1; }
        100% { transform: translateY(0) scale(1); opacity: 0.6; }
    }

    /* 登录页装饰 - AI 风格 */
    .login-deco {
        text-align: center;
        font-size: 3.5rem;
        margin-bottom: 8px;
        animation: dataFlow 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(0, 229, 255, 0.5));
    }
    .login-subtitle-box {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.08), rgba(124, 77, 255, 0.08));
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 30px;
        padding: 6px 24px;
        display: inline-block;
        margin: 4px auto 20px;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.05);
    }

    /* 页面标题区域 */
    .page-header {
        background: rgba(13, 17, 55, 0.8);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, 0.12);
        padding: 16px 24px;
        margin-bottom: 16px;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .page-header-title {
        color: #00e5ff;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
    }

    /* Expander 美化 */
    .streamlit-expanderHeader {
        background: rgba(13, 17, 55, 0.6) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 229, 255, 0.12) !important;
        color: #c8d6e5 !important;
    }
    /* Expander 内容区域 */
    [data-testid="stExpander"] {
        background: rgba(13, 17, 55, 0.6) !important;
        border: 1px solid rgba(0, 229, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] > div {
        background: transparent !important;
    }
    [data-testid="stExpander"] details {
        background: rgba(13, 17, 55, 0.6) !important;
        border: 1px solid rgba(0, 229, 255, 0.12) !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] summary {
        background: rgba(13, 17, 55, 0.7) !important;
        color: #c8d6e5 !important;
    }
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: rgba(10, 14, 39, 0.8) !important;
    }

    /* 表单美化 */
    [data-testid="stForm"] {
        background: rgba(13, 17, 55, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, 0.12);
        padding: 24px;
        box-shadow: 0 0 25px rgba(0, 229, 255, 0.04);
    }

    /* 侧边栏美化 - 深色科技 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #080b20, #0d1137, #141852) !important;
        border-right: 1px solid rgba(0, 229, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(0, 229, 255, 0.06) !important;
        color: #00e5ff !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0, 229, 255, 0.12) !important;
        border-color: rgba(0, 229, 255, 0.4) !important;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h5 {
        color: #00e5ff !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div {
        color: #c8d6e5 !important;
    }

    /* 文件上传器美化 */
    [data-testid="stFileUploader"] {
        border: 1.5px dashed rgba(0, 229, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 8px !important;
        background: rgba(10, 14, 39, 0.5) !important;
    }

    /* 成功/警告/错误消息美化 */
    .stAlert {
        border-radius: 12px !important;
        background: rgba(13, 17, 55, 0.8) !important;
        border: 1px solid rgba(0, 229, 255, 0.15) !important;
    }

    /* Radio 按钮颜色 */
    .stRadio > div {
        color: #c8d6e5 !important;
    }

    /* DataFrame / 表格样式 */
    .stDataFrame {
        border: 1px solid rgba(0, 229, 255, 0.12) !important;
        border-radius: 12px !important;
    }

    /* 下载按钮 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1a237e, #283593) !important;
        color: #00e5ff !important;
        border: 1px solid rgba(0, 229, 255, 0.2) !important;
    }

    /* Caption 文字 */
    .stCaption, small {
        color: rgba(200, 214, 229, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Turso HTTP API 封装 ====================
class TursoConnection:
    """通过 Turso HTTP API 操作数据库（纯 Python，无需编译原生库）"""

    def __init__(self, url, auth_token):
        # 将 libsql:// 转为 https://
        self.base_url = url.replace("libsql://", "https://")
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

    def _post(self, statements):
        """发送请求到 Turso HTTP API（Pipeline 模式）"""
        payload = {"requests": []}
        for stmt in statements:
            if isinstance(stmt, str):
                payload["requests"].append({"type": "execute", "stmt": {"sql": stmt}})
            else:
                sql, args = stmt
                named_args = []
                for i, arg in enumerate(args):
                    if arg is None:
                        named_args.append({"type": "null"})
                    elif isinstance(arg, int):
                        named_args.append({"type": "integer", "value": str(arg)})
                    elif isinstance(arg, float):
                        named_args.append({"type": "float", "value": arg})
                    else:
                        named_args.append({"type": "text", "value": str(arg)})
                payload["requests"].append({
                    "type": "execute",
                    "stmt": {"sql": sql, "args": named_args}
                })
        payload["requests"].append({"type": "close"})
        resp = requests.post(
            f"{self.base_url}/v2/pipeline",
            headers=self.headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def execute(self, sql, params=None):
        """执行单条 SQL，返回 TursoCursor 对象"""
        if params:
            result = self._post([(sql, params)])
        else:
            result = self._post([sql])
        # 解析结果
        results = result.get("results", [])
        if results and results[0].get("type") == "ok":
            response = results[0]["response"]
            res = response.get("result", {})
            cols = [c["name"] for c in res.get("cols", [])]
            rows = []
            for row in res.get("rows", []):
                parsed_row = []
                for cell in row:
                    if cell.get("type") == "null":
                        parsed_row.append(None)
                    elif cell.get("type") == "integer":
                        parsed_row.append(int(cell["value"]))
                    elif cell.get("type") == "float":
                        parsed_row.append(float(cell["value"]))
                    else:
                        parsed_row.append(cell.get("value"))
                rows.append(tuple(parsed_row))
            return TursoCursor(cols, rows)
        # 检查是否有错误
        if results and results[0].get("type") == "error":
            err = results[0].get("error", {})
            raise Exception(f"Turso error: {err.get('message', str(err))}")
        return TursoCursor([], [])

    def commit(self):
        """Turso HTTP API 自动提交，此方法为兼容性保留"""
        pass


class TursoCursor:
    """模拟 DB-API cursor 对象"""

    def __init__(self, columns, rows):
        self.columns = columns
        self._rows = rows
        self._index = 0

    def fetchone(self):
        if self._index < len(self._rows):
            row = self._rows[self._index]
            self._index += 1
            return row
        return None

    def fetchall(self):
        remaining = self._rows[self._index:]
        self._index = len(self._rows)
        return remaining


@st.cache_resource
def get_connection():
    """获取 Turso 数据库连接（HTTP API 方式，无需编译原生库）"""
    turso_url = st.secrets["turso"]["url"]
    turso_token = st.secrets["turso"]["auth_token"]
    return TursoConnection(turso_url, turso_token)

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
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.9), rgba(20, 24, 82, 0.7));
        backdrop-filter: blur(15px);
        border-radius: 16px;
        border: 1px solid rgba(0, 229, 255, 0.12);
        padding: 20px 22px;
        margin: 0;
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.05), inset 0 0 20px rgba(0, 229, 255, 0.02);
        transition: all 0.3s ease;
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #c8d6e5;
        font-size: 14px;
        line-height: 1.5;
        position: relative;
        overflow: hidden;
    }
    .cute-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.3), transparent);
    }
    .cute-card:hover {
        border-color: rgba(0, 229, 255, 0.3);
        box-shadow: 0 0 30px rgba(0, 229, 255, 0.1), inset 0 0 30px rgba(0, 229, 255, 0.03);
        transform: translateY(-2px);
    }
    .user-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0d47a1, #00bcd4);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        color: white;
        margin-right: 14px;
        flex-shrink: 0;
        box-shadow: 0 0 15px rgba(0, 188, 212, 0.3);
        border: 1px solid rgba(0, 229, 255, 0.2);
    }
    .user-info-row {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    .user-name {
        font-weight: 700;
        font-size: 1.05rem;
        color: #e0f7fa;
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.2);
    }
    .user-meta {
        color: rgba(200, 214, 229, 0.6);
        font-size: 0.82rem;
        margin-top: 2px;
    }
    .hobby-tag {
        display: inline-block;
        background: rgba(0, 229, 255, 0.06);
        border: 1px solid rgba(0, 229, 255, 0.2);
        color: #00e5ff;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
        font-weight: 500;
        text-shadow: 0 0 5px rgba(0, 229, 255, 0.3);
    }
    .match-high {
        display: inline-block;
        background: rgba(0, 229, 255, 0.1);
        border: 1.5px solid #00e5ff;
        color: #00e5ff;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: bold;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.2);
        text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
    }
    .match-medium {
        display: inline-block;
        background: rgba(124, 77, 255, 0.1);
        border: 1.5px solid #7c4dff;
        color: #b388ff;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: bold;
        box-shadow: 0 0 12px rgba(124, 77, 255, 0.15);
    }
    .match-low {
        display: inline-block;
        background: rgba(200, 214, 229, 0.05);
        border: 1.5px solid rgba(200, 214, 229, 0.2);
        color: rgba(200, 214, 229, 0.5);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: bold;
    }
    .photo-thumb {
        width: 72px;
        height: 72px;
        border-radius: 10px;
        object-fit: cover;
        border: 1.5px solid rgba(0, 229, 255, 0.2);
        margin-right: 6px;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.08);
    }
    .photos-row {
        margin: 10px 0 6px 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .admin-photo-card {
        background: linear-gradient(135deg, rgba(13, 17, 55, 0.85), rgba(20, 24, 82, 0.6));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 229, 255, 0.12);
        border-radius: 14px;
        padding: 14px 18px;
        margin: 0;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.04);
        font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #c8d6e5;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .photo-count-tag {
        display: inline-block;
        background: rgba(0, 229, 255, 0.08);
        border: 1px solid rgba(0, 229, 255, 0.25);
        color: #00e5ff;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(0, 229, 255, 0.3);
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
        <p style="color:rgba(200,214,229,0.6); font-size:0.9rem; margin-top:4px;">AI 驱动 · 用音乐连接有缘人 🤖💕</p>
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
        <div style="text-align:center; margin-top:30px; color:rgba(200,214,229,0.4); font-size:0.78rem; letter-spacing:2px;">
            ⚡ AI 智能匹配 · 遇见美好，从这里开始 ⚡
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
        st.markdown("### ⚡ 缘音乐广场")
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
            你好，<strong>{nickname}</strong> ⚡<br>
            <span style="font-size:0.82rem; color:rgba(200,214,229,0.5);">AI 正在为你寻找最佳匹配...</span>
        </div>
        <div class="welcome-emoji">🤖</div>
    </div>
    """, unsafe_allow_html=True)

    # 统计信息
    all_users = get_all_users()
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-item">
            <span class="stat-num">{len(all_users)}</span>
            <span class="stat-label">USERS</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">{others_count}</span>
            <span class="stat-label">MATCHES</span>
        </div>
        <div class="stat-item">
            <span class="stat-num">⚡</span>
            <span class="stat-label">AI READY</span>
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
            AI 正在分析兴趣与年龄数据，为 <strong>{me.get('nickname', '')}</strong> 计算最佳匹配 ⚡
        </div>
        <div class="welcome-emoji">🧠</div>
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
            <span class="empty-icon">🔍</span>
            <div class="empty-title">AI 暂未检索到匹配用户</div>
            <div class="empty-desc">系统持续扫描中，新的连接即将建立 ⚡</div>
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
                    st.markdown(f'<img src="{b64_url}" style="width:100%;border-radius:12px;border:1.5px solid rgba(0,229,255,0.2);box-shadow:0 0 12px rgba(0,229,255,0.08);">', unsafe_allow_html=True)
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
<span style="color:rgba(200,214,229,0.5); font-size:0.82rem;">
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
                        st.markdown(f'<img src="{b64_url}" style="width:90px;height:90px;border-radius:10px;object-fit:cover;border:1.5px solid rgba(0,229,255,0.2);box-shadow:0 0 10px rgba(0,229,255,0.08);">', unsafe_allow_html=True)
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
        st.markdown("### 🤖 缘音乐 AI")
        st.markdown("---")
        if st.session_state.user_id:
            me = get_user_by_id(st.session_state.user_id)
            if me:
                st.markdown(f"👤 **{me.get('nickname', '')}**")
            st.markdown("---")
            if st.button("⚡ 缘音乐广场", use_container_width=True, key="nav_square"):
                navigate('square')
            if st.button("🧠 AI 智能配对", use_container_width=True, key="nav_match_sidebar"):
                navigate('ai_match')
            if st.button("✏️ 编辑资料", use_container_width=True, key="nav_profile"):
                navigate('profile')
            st.markdown("---")
        if is_admin():
            st.markdown("##### 🛡️ 管理员")
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
