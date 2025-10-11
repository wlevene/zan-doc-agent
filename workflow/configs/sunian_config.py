# sunian-girl配置文件

# 人物画像详情
PERSONA_DETAIL = """苏念，25岁的都市时尚博主，同时也是中医养生文化的年轻推广者。她身材纤细，气质清新，善于将传统养生智慧与现代都市生活方式相结合。苏念的父母都是中医从业者，从小耳濡目染让她对中医养生有着深入的理解。她热衷于通过社交媒体分享实用的养生小技巧，帮助都市年轻人在快节奏的生活中找到平衡。"""

# 代理配置
AGENT_CONFIG = {
    "wellness_agent": {
        "model": "default",
        "temperature": 0.7
    },
    "scenario_generator": {
        "model": "default",
        "temperature": 0.8
    },
    "content_generator": {
        "model": "default",
        "temperature": 0.9
    }
}

# 工作流配置
WORKFLOW_CONFIG = {
    "max_retries": 3,
    "output_dir": None  # 使用默认输出目录
}

# 导出配置
CONFIG = {
    "persona_detail": PERSONA_DETAIL,
    "agent_config": AGENT_CONFIG,
    "workflow_config": WORKFLOW_CONFIG
}

# 添加小写变量作为别名，以兼容现有代码
persona_detail = PERSONA_DETAIL