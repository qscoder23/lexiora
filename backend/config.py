"""复用 src/config.py，路径指向项目根目录"""
from pathlib import Path
import sys

# 将项目根目录加入 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import load_config

__all__ = ["load_config"]