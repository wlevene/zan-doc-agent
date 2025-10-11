# 配置包初始化文件

from .workmen_config import CONFIG as WORKMEN_CONFIG
from .sunian_config import CONFIG as SUNIAN_CONFIG
from .wellnessmom_config import CONFIG as WELLNESSMOM_CONFIG

# 配置映射，用于根据类型名获取对应的配置
CONFIG_MAP = {
    "workmen": WORKMEN_CONFIG,
    "sunian": SUNIAN_CONFIG,
    "wellnessmom": WELLNESSMOM_CONFIG
}

__all__ = ["WORKMEN_CONFIG", "SUNIAN_CONFIG", "WELLNESSMOM_CONFIG", "CONFIG_MAP"]