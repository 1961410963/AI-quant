"""Token管理模块"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, set_key
import tushare as ts
from config.settings import LOCAL_ENV_FILE, USER_ENV_FILE

def get_env_file():
    """获取环境变量文件路径，优先使用项目本地的 .env"""
    if LOCAL_ENV_FILE.exists():
        return LOCAL_ENV_FILE
    return USER_ENV_FILE

def init_env_file():
    """初始化环境变量文件，只使用项目本地的 .env"""
    # 确保项目本地 .env 文件存在
    if not LOCAL_ENV_FILE.exists():
        LOCAL_ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_ENV_FILE.touch()
    
    # 加载项目本地的 .env
    load_dotenv(LOCAL_ENV_FILE, override=True)

def get_tushare_token() -> Optional[str]:
    """获取Tushare token，从项目本地 .env 读取"""
    init_env_file()
    token = os.getenv("TUSHARE_TOKEN")
    return token

def set_tushare_token(token: str, use_local: bool = True):
    """
    设置Tushare token
    
    参数:
        token: Tushare API token
        use_local: 是否保存到项目本地 .env 文件（默认 True）
    """
    init_env_file()
    
    env_file = LOCAL_ENV_FILE
    
    if not env_file.exists():
        env_file.touch()
    
    set_key(env_file, "TUSHARE_TOKEN", token)
    ts.set_token(token)

