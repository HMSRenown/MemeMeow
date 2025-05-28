import sys
import types
import streamlit as st
import random
import os
import yaml
import streamlit_authenticator as stauth
from services.image_search import ImageSearch
from config.settings import Config
from base import *
from loguru import logger

logger.remove(handler_id=None)
logger.add(os.path.join(Config().base_dir, 'Logs', "{time:YYYY-MM-DD}/{time:YYYY-MM-DD}.log"), level="TRACE", backtrace=True)
if TRACE_MODE:
    logger.add(sys.stdout, level="TRACE", backtrace=True)
elif DEBUG_MODE:
    logger.add(sys.stdout, level="DEBUG", backtrace=True)
else:
    logger.add(sys.stdout, level="INFO", backtrace=True)

def delete_all_files_in_folder(folder_path):
    try:
        # 遍历文件夹中的所有文件和子文件夹
        for root, dirs, files in os.walk(folder_path, topdown=False):
            # 删除所有文件
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            # 删除所有空文件夹
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
    except Exception as e:
        print(f"删除过程中出现错误: {e}")

verify_folder(os.path.join(Config().temp_dir))
delete_all_files_in_folder(os.path.join(Config().temp_dir))

# 加载认证配置
config_file = os.path.join(Config().base_dir, 'config', 'auth_config.yaml')
enable_auth = True
if not os.path.exists(config_file):
    enable_auth = False
else:
    with open(config_file, 'r', encoding='utf-8') as f:
        auth_config = yaml.safe_load(f)
    enable_auth = auth_config.get('auth_enabled', False)

# 检查是否启用身份验证
if enable_auth:
    # 创建认证器
    authenticator = stauth.Authenticate(
        auth_config['credentials'],
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days'],
        auth_config['preauthorized']
    )

    # 登录界面
    name, authentication_status, username = authenticator.login('登录', 'main')

    if authentication_status == False:
        st.error('用户名或密码错误')
    elif authentication_status == None:
        st.warning('请输入用户名和密码')
    elif authentication_status:
        # 添加登出按钮
        # authenticator.logout('登出', 'sidebar')
        # st.sidebar.write(f'欢迎 *{name}*')
        
        # 只有登录成功后才显示页面导航
        pg = st.navigation([
            st.Page("stpages/Mememeow.py", title="MemeMeow"),
            st.Page("stpages/label_images.py", title="标注图片"),
            st.Page("stpages/upload_images.py", title="上传图片"),
            st.Page("stpages/resource_pack.py", title="资源包管理"),
        ])
        pg.run()
    else:
        st.error('身份验证失败，请重试')
else:
    # 未启用身份验证，直接显示页面导航
    pg = st.navigation([
        st.Page("stpages/Mememeow.py", title="MemeMeow"),
        st.Page("stpages/label_images.py", title="标注图片"),
        st.Page("stpages/upload_images.py", title="上传图片"),
        st.Page("stpages/resource_pack.py", title="资源包管理"),
    ])
    pg.run()