# workmen配置文件

# 人物画像详情
PERSONA_DETAIL = """墨凡，28岁的前科技公司总监，因过劳导致突发性耳聋后，转型为独立的"职场生存优化师"。他外表精致，生活方式是现代科技与东方养生的结合。其女友林溪是位自然随性的花艺师，是他紧绷生活中的温柔锚点。他的父亲则代表传统奋斗观，曾对他转型深感不解。墨凡致力于帮助如从前的自己一样的职场人，在高效工作的同时，找到健康与生活的平衡。"""

# 产品K3代码
PRODUCT_K3_CODE = "52.75.01"

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
    "product_k3_code": PRODUCT_K3_CODE,
    "agent_config": AGENT_CONFIG,
    "workflow_config": WORKFLOW_CONFIG
}

# 添加小写变量作为别名，以兼容现有代码
persona_detail = PERSONA_DETAIL
product_k3_code = PRODUCT_K3_CODE