# Dify API 封装

这是一个用于 Dify 文本生成型应用的 Python API 封装库，支持阻塞和流式两种调用模式。

## 项目结构

```
zan-doc-agent/
├── dify_client.py      # Dify API 封装核心模块
├── agents.py           # Agent 系统核心模块
├── main.py             # 基础使用示例
├── agent_examples.py   # Agent 系统使用示例
├── requirements.txt    # 项目依赖
└── README.md          # 项目文档
```

## 功能特性

### 🔧 核心功能
- 🚀 **简单易用**：提供简洁的 API 接口，快速集成
- 🔄 **双模式支持**：支持阻塞和流式两种调用模式
- 📁 **文件支持**：支持图片等文件的上传和处理
- 🛡️ **错误处理**：完善的错误处理和异常管理
- 📝 **类型提示**：完整的类型注解，提供更好的开发体验
- 🔧 **可配置**：支持自定义 API 地址和参数配置

### 🤖 Agent 系统
- 🎯 **业务场景封装**：基于 DifyClient 封装特定业务场景的 Agent
- 🏭 **工厂模式**：统一的 Agent 创建和管理机制
- 🔄 **可扩展架构**：支持自定义 Agent 类型，满足不同业务需求
- 📋 **内置 Agent**：
  - **文案场景验收器**：专业的文案内容验收工具
  - **场景生成器**：智能场景内容生成工具
- 🔗 **统一接口**：所有 Agent 都实现统一的处理接口

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 初始化客户端

```python
from dify_client import DifyClient

# 使用你的API密钥初始化客户端
client = DifyClient(api_key="your-api-key-here")
```

### 2. 阻塞模式调用

```python
try:
    result = client.completion_messages_blocking(
        query="请帮我写一首关于春天的诗",
        user="user_123"
    )
    
    print(f"消息ID: {result['message_id']}")
    print(f"回答: {result['answer']}")
    print(f"用量: {result['usage']}")
    
except DifyAPIError as e:
    print(f"API错误: {e}")
```

### 3. 流式模式调用

```python
try:
    for chunk in client.completion_messages_streaming(
        query="请介绍一下人工智能的发展历程",
        user="user_123"
    ):
        event = chunk.get('event')
        
        if event == 'message':
            # 实时输出文本块
            print(chunk.get('answer', ''), end='', flush=True)
        elif event == 'message_end':
            # 消息结束
            print(f"\n\n消息ID: {chunk.get('message_id')}")
            print(f"用量: {chunk.get('usage')}")
            break
        elif event == 'error':
            print(f"流式错误: {chunk.get('message')}")
            break
            
except DifyAPIError as e:
    print(f"API错误: {e}")
```

### 4. 带文件的调用

```python
from dify_client import FileInfo, FileType, TransferMethod

# 使用远程图片URL
file_info = FileInfo(
    type=FileType.IMAGE.value,
    transfer_method=TransferMethod.REMOTE_URL.value,
    url="https://example.com/image.jpg"
)

result = client.completion_messages_blocking(
    query="请描述这张图片的内容",
    files=[file_info],
    user="user123"
)

print(result['answer'])
```

## Agent 系统使用

### 快速开始

```python
from dify_client import DifyClient
from agents import AgentFactory, AgentType

# 初始化客户端和工厂
client = DifyClient(api_key="your-api-key-here")
factory = AgentFactory(client)

# 创建文案验收器
validator = factory.create_agent(AgentType.CONTENT_VALIDATOR)

# 验收文案
result = validator.process(
    query="请验收这个营销文案",
    content_to_validate="AI助手让工作更高效！"
)

print(result.content)
```

### 文案场景验收器

```python
from agents import ContentValidatorAgent

# 创建验收器
validator = ContentValidatorAgent(
    dify_client=client,
    validation_criteria=["语法正确性", "品牌一致性", "用户体验"]
)

# 单个文案验收
result = validator.process(
    query="验收这个产品描述",
    content_to_validate="我们的AI产品功能强大，操作简单",
    inputs={"target_audience": "企业用户"}
)

# 批量验收
batch_results = validator.validate_batch([
    "文案1：产品特色介绍",
    "文案2：用户使用指南",
    "文案3：技术优势说明"
])
```

### 场景生成器

```python
from agents import ScenarioGeneratorAgent

# 创建生成器
generator = ScenarioGeneratorAgent(
    dify_client=client,
    scenario_types=["营销场景", "用户故事", "产品演示"]
)

# 生成营销场景
result = generator.process(
    query="为AI办公助手生成营销场景",
    scenario_type="营销场景",
    target_audience="中小企业"
)

# 生成多个场景变体
scenarios = generator.generate_multiple_scenarios(
    base_query="客户服务场景",
    count=3,
    scenario_type="客户服务场景"
)
```

### 自定义 Agent

```python
from agents import BaseAgent, AgentConfig, AgentResponse, AgentType

class CustomAgent(BaseAgent):
    def __init__(self, dify_client):
        config = AgentConfig(
            name="自定义Agent",
            description="处理特定业务逻辑",
            agent_type=AgentType.CUSTOM,
            system_prompt="你是一个专业的业务助手"
        )
        super().__init__(dify_client, config)
    
    def process(self, query, inputs=None, **kwargs):
        # 实现自定义处理逻辑
        try:
            raw_response = self.client.completion_messages_blocking(
                query=self._build_query(query),
                inputs=self._prepare_inputs(inputs)
            )
            return self._handle_response(raw_response)
        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                error_message=str(e)
            )
    
    def process_streaming(self, query, inputs=None, **kwargs):
        # 实现流式处理逻辑
        for chunk in self.client.completion_messages_streaming(
            query=self._build_query(query),
            inputs=self._prepare_inputs(inputs)
        ):
            yield self._handle_response(chunk)
```

### 5. 带应用变量的调用

```python
result = client.completion_messages_blocking(
    query="请根据提供的信息生成内容",
    inputs={
        "topic": "人工智能",
        "style": "学术论文",
        "length": "1000字"
    },
    user="user_123"
)
```

## API 参考

### DifyClient

#### 初始化参数

- `api_key` (str): Dify API 密钥
- `base_url` (str, 可选): API 基础URL，默认为 "http://119.45.130.88/v1"

#### 方法

##### completion_messages_blocking

阻塞模式的文本生成请求。

**参数:**
- `query` (str): 用户输入的文本内容
- `inputs` (Dict[str, Any], 可选): 应用定义的变量值
- `user` (str, 可选): 用户标识
- `files` (List[FileInfo], 可选): 上传的文件列表

**返回:** Dict[str, Any] - 完整的响应结果

##### completion_messages_streaming

流式模式的文本生成请求。

**参数:** 同 `completion_messages_blocking`

**返回:** Iterator[Dict[str, Any]] - 流式响应块迭代器

### 数据类

#### FileInfo

文件信息数据类。

```python
@dataclass
class FileInfo:
    type: str                    # 文件类型，如 "image"
    transfer_method: str         # 传递方式，"remote_url" 或 "local_file"
    url: Optional[str] = None    # 远程URL（当transfer_method为remote_url时）
    upload_file_id: Optional[str] = None  # 上传文件ID（当transfer_method为local_file时）
```

### 异常处理

#### DifyAPIError

Dify API 异常类，包含以下属性：

- `status_code` (int): HTTP状态码
- `code` (str): 错误码
- `message` (str): 错误消息
- `task_id` (str, 可选): 任务ID

## 流式响应事件类型

- `message`: LLM返回文本块事件
- `message_end`: 消息结束事件
- `tts_message`: TTS音频流事件
- `tts_message_end`: TTS音频流结束事件
- `message_replace`: 消息内容替换事件
- `error`: 错误事件
- `ping`: 保持连接的ping事件

## 错误码说明

- `404`: 对话不存在
- `400 invalid_param`: 传入参数异常
- `400 app_unavailable`: App配置不可用
- `400 provider_not_initialize`: 无可用模型凭据配置
- `400 provider_quota_exceeded`: 模型调用额度不足
- `400 model_currently_not_support`: 当前模型不可用
- `400 completion_request_error`: 文本生成失败
- `500`: 服务内部异常

## 注意事项

1. **API密钥安全**: 请将API密钥存储在后端，避免在客户端暴露
2. **流式模式**: 推荐使用流式模式以获得更好的用户体验
3. **错误处理**: 建议在生产环境中添加重试机制和完善的错误处理
4. **用户标识**: 建议为每个用户设置唯一的用户标识以便统计和管理

## 许可证

MIT License