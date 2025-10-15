# wellnessmom配置文件

# 人物画像详情
PERSONA_DETAIL = """40岁养生妈妈，本科哲学+中医，165cm/65kg，上热下寒体质，易过敏手部脱皮，有14岁叛逆儿子(易湿疹流鼻血)，10岁挑食女儿(易上火牙龈肿痛)，46岁丈夫(三高肥胖)，70岁婆婆(高血压健康焦虑)，75岁公公(慢阻肺爱抽烟)，注重全家养生，懂中医经络，关注节气时事热点"""

# 产品K3代码
PRODUCT_K3_CODE = "03.11.01"

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