from typing import Dict, Any, Optional, List, Union, Literal
import requests
from pydantic import BaseModel, Field
import json


# ===== 文件相关模型 =====
class FileInput(BaseModel):
    """文件输入模型"""
    type: Literal["document", "image", "audio", "video", "custom"] = Field(
        ..., description="文件类型"
    )
    transfer_method: Literal["remote_url", "local_file"] = Field(
        ..., description="传递方式"
    )
    url: Optional[str] = Field(
        None, description="图片地址（仅当传递方式为 remote_url 时）"
    )
    upload_file_id: Optional[str] = Field(
        None, description="上传文件 ID（仅当传递方式为 local_file 时）"
    )


# ===== 请求模型 =====
class WorkflowInput(BaseModel):
    """工作流输入模型"""
    inputs: Dict[str, Any] = Field(
        default_factory=dict, 
        description="允许传入 App 定义的各变量值，可包含文件列表"
    )
    response_mode: Literal["streaming", "blocking"] = Field(
        default="blocking", description="返回响应模式"
    )
    user: str = Field(..., description="用户标识，用于定义终端用户的身份")
    files: Optional[List[FileInput]] = Field(
        default=None, description="文件列表，可选"
    )
    trace_id: Optional[str] = Field(
        default=None, description="链路追踪ID，可选"
    )


# ===== 响应数据模型 =====
class ExecutionMetadata(BaseModel):
    """执行元数据"""
    total_tokens: Optional[int] = Field(None, description="总使用 tokens")
    total_price: Optional[float] = Field(None, description="总费用")
    currency: Optional[str] = Field(None, description="货币，如 USD / RMB")


class WorkflowRunData(BaseModel):
    """工作流运行数据"""
    id: str = Field(..., description="workflow 执行 ID")
    workflow_id: str = Field(..., description="关联 Workflow ID")
    status: Literal["running", "succeeded", "failed", "stopped"] = Field(
        ..., description="执行状态"
    )
    outputs: Optional[Dict[str, Any]] = Field(None, description="输出内容")
    error: Optional[str] = Field(None, description="错误原因")
    elapsed_time: Optional[float] = Field(None, description="耗时(s)")
    total_tokens: Optional[int] = Field(None, description="总使用 tokens")
    total_steps: int = Field(default=0, description="总步数")
    created_at: int = Field(..., description="开始时间戳")
    finished_at: int = Field(..., description="结束时间戳")


# ===== Blocking 模式响应 =====
class CompletionResponse(BaseModel):
    """完整的 App 结果（blocking 模式）"""
    workflow_run_id: str = Field(..., description="workflow 执行 ID")
    task_id: str = Field(..., description="任务 ID")
    data: WorkflowRunData = Field(..., description="详细内容")


# ===== Streaming 模式事件数据模型 =====
class WorkflowStartedData(BaseModel):
    """workflow 开始执行数据"""
    id: str = Field(..., description="workflow 执行 ID")
    workflow_id: str = Field(..., description="关联 Workflow ID")
    created_at: int = Field(..., description="开始时间戳")


class NodeStartedData(BaseModel):
    """node 开始执行数据"""
    id: str = Field(..., description="workflow 执行 ID")
    node_id: str = Field(..., description="节点 ID")
    node_type: str = Field(..., description="节点类型")
    title: str = Field(..., description="节点名称")
    index: int = Field(..., description="执行序号")
    predecessor_node_id: str = Field(..., description="前置节点 ID")
    inputs: Dict[str, Any] = Field(..., description="节点中所有使用到的前置节点变量内容")
    created_at: int = Field(..., description="开始时间戳")


class TextChunkData(BaseModel):
    """文本片段数据"""
    text: str = Field(..., description="文本内容")
    from_variable_selector: List[str] = Field(
        ..., description="文本来源路径，帮助开发者了解文本是由哪个节点的哪个变量生成的"
    )


class NodeFinishedData(BaseModel):
    """node 执行结束数据"""
    id: str = Field(..., description="node 执行 ID")
    node_id: str = Field(..., description="节点 ID")
    index: int = Field(..., description="执行序号")
    predecessor_node_id: Optional[str] = Field(None, description="前置节点 ID")
    inputs: Dict[str, Any] = Field(..., description="节点中所有使用到的前置节点变量内容")
    process_data: Optional[Dict[str, Any]] = Field(None, description="节点过程数据")
    outputs: Optional[Dict[str, Any]] = Field(None, description="输出内容")
    status: Literal["running", "succeeded", "failed", "stopped"] = Field(
        ..., description="执行状态"
    )
    error: Optional[str] = Field(None, description="错误原因")
    elapsed_time: Optional[float] = Field(None, description="耗时(s)")
    execution_metadata: ExecutionMetadata = Field(..., description="元数据")
    total_tokens: Optional[int] = Field(None, description="总使用 tokens")
    total_price: Optional[float] = Field(None, description="总费用")
    currency: Optional[str] = Field(None, description="货币")
    created_at: int = Field(..., description="开始时间戳")


class WorkflowFinishedData(BaseModel):
    """workflow 执行结束数据"""
    id: str = Field(..., description="workflow 执行 ID")
    workflow_id: str = Field(..., description="关联 Workflow ID")
    status: Literal["running", "succeeded", "failed", "stopped"] = Field(
        ..., description="执行状态"
    )
    outputs: Optional[Dict[str, Any]] = Field(None, description="输出内容")
    error: Optional[str] = Field(None, description="错误原因")
    elapsed_time: Optional[float] = Field(None, description="耗时(s)")
    total_tokens: Optional[int] = Field(None, description="总使用 tokens")
    total_steps: int = Field(default=0, description="总步数")
    created_at: int = Field(..., description="开始时间戳")
    finished_at: int = Field(..., description="结束时间戳")


class TTSMessageData(BaseModel):
    """TTS 音频流数据"""
    task_id: str = Field(..., description="任务 ID")
    message_id: str = Field(..., description="消息唯一 ID")
    audio: str = Field(..., description="语音合成之后的音频块使用 Base64 编码之后的文本内容")
    created_at: int = Field(..., description="创建时间戳")


# ===== Streaming 模式事件模型 =====
class WorkflowStartedEvent(BaseModel):
    """workflow 开始执行事件"""
    task_id: str = Field(..., description="任务 ID")
    workflow_run_id: str = Field(..., description="workflow 执行 ID")
    event: Literal["workflow_started"] = Field(..., description="事件类型")
    data: WorkflowStartedData = Field(..., description="详细内容")


class NodeStartedEvent(BaseModel):
    """node 开始执行事件"""
    task_id: str = Field(..., description="任务 ID")
    workflow_run_id: str = Field(..., description="workflow 执行 ID")
    event: Literal["node_started"] = Field(..., description="事件类型")
    data: NodeStartedData = Field(..., description="详细内容")


class TextChunkEvent(BaseModel):
    """文本片段事件"""
    task_id: str = Field(..., description="任务 ID")
    workflow_run_id: str = Field(..., description="workflow 执行 ID")
    event: Literal["text_chunk"] = Field(..., description="事件类型")
    data: TextChunkData = Field(..., description="详细内容")


class NodeFinishedEvent(BaseModel):
    """node 执行结束事件"""
    task_id: str = Field(..., description="任务 ID")
    workflow_run_id: str = Field(..., description="workflow 执行 ID")
    event: Literal["node_finished"] = Field(..., description="事件类型")
    data: NodeFinishedData = Field(..., description="详细内容")


class WorkflowFinishedEvent(BaseModel):
    """workflow 执行结束事件"""
    task_id: str = Field(..., description="任务 ID")
    workflow_run_id: str = Field(..., description="workflow 执行 ID")
    event: Literal["workflow_finished"] = Field(..., description="事件类型")
    data: WorkflowFinishedData = Field(..., description="详细内容")


class TTSMessageEvent(BaseModel):
    """TTS 音频流事件"""
    event: Literal["tts_message"] = Field(..., description="事件类型")
    task_id: str = Field(..., description="任务 ID")
    message_id: str = Field(..., description="消息唯一 ID")
    audio: str = Field(..., description="Base64编码的音频内容")
    created_at: int = Field(..., description="创建时间戳")


class TTSMessageEndEvent(BaseModel):
    """TTS 音频流结束事件"""
    event: Literal["tts_message_end"] = Field(..., description="事件类型")
    task_id: str = Field(..., description="任务 ID")
    message_id: str = Field(..., description="消息唯一 ID")
    audio: str = Field(..., description="结束事件音频为空字符串")
    created_at: int = Field(..., description="创建时间戳")


class PingEvent(BaseModel):
    """保持连接存活的 ping 事件"""
    event: Literal["ping"] = Field(..., description="事件类型")


# 联合类型用于所有可能的流式事件
StreamEvent = Union[
    WorkflowStartedEvent,
    NodeStartedEvent,
    TextChunkEvent,
    NodeFinishedEvent,
    WorkflowFinishedEvent,
    TTSMessageEvent,
    TTSMessageEndEvent,
    PingEvent
]


# ===== 错误响应模型 =====
class ErrorResponse(BaseModel):
    """错误响应模型"""
    status_code: int = Field(..., description="HTTP 状态码")
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")


# ===== 文件上传相关模型 =====
class FileUploadInput(BaseModel):
    """文件上传输入模型"""
    user: str = Field(..., description="用户标识")
    type: str = Field(..., description="文件类型，如 TXT")


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    id: str = Field(..., description="文件 ID")
    name: str = Field(..., description="文件名")
    size: int = Field(..., description="文件大小（字节）")
    extension: str = Field(..., description="文件后缀")
    mime_type: str = Field(..., description="文件 MIME 类型")
    created_by: int = Field(..., description="上传人 ID")
    created_at: int = Field(..., description="上传时间戳")


# ===== 工作流状态查询模型 =====
class WorkflowRunStatusResponse(BaseModel):
    """工作流执行状态查询响应"""
    id: str = Field(..., description="workflow 执行 ID")
    workflow_id: str = Field(..., description="关联的 Workflow ID")
    status: Literal["running", "succeeded", "failed", "stopped"] = Field(
        ..., description="执行状态"
    )
    inputs: str = Field(..., description="任务输入内容（JSON字符串）")
    outputs: Optional[Dict[str, Any]] = Field(None, description="任务输出内容")
    error: Optional[str] = Field(None, description="错误原因")
    total_steps: int = Field(..., description="任务执行总步数")
    total_tokens: int = Field(..., description="任务执行总 tokens")
    created_at: int = Field(..., description="任务开始时间戳")
    finished_at: int = Field(..., description="任务结束时间戳")
    elapsed_time: float = Field(..., description="耗时 (秒)")


# ===== 停止响应模型 =====
class StopTaskInput(BaseModel):
    """停止任务输入模型"""
    user: str = Field(..., description="用户标识")


class StopTaskResponse(BaseModel):
    """停止任务响应模型"""
    result: Literal["success"] = Field(..., description="固定返回 success")


# ===== 应用信息相关模型 =====
class AppInfoResponse(BaseModel):
    """应用基本信息响应"""
    name: str = Field(..., description="应用名称")
    description: str = Field(..., description="应用描述")
    tags: List[str] = Field(..., description="应用标签")
    mode: str = Field(..., description="应用模式")
    author_name: str = Field(..., description="作者名称")


class UserInputFormField(BaseModel):
    """用户输入表单字段基类"""
    label: str = Field(..., description="控件展示标签名")
    variable: str = Field(..., description="控件 ID")
    required: bool = Field(..., description="是否必填")
    default: str = Field(..., description="默认值")


class TextInputField(UserInputFormField):
    """文本输入控件"""
    pass


class ParagraphField(UserInputFormField):
    """段落文本输入控件"""
    pass


class SelectField(UserInputFormField):
    """下拉控件"""
    options: List[str] = Field(..., description="选项值")


class FileUploadSettings(BaseModel):
    """文件上传设置"""
    enabled: bool = Field(..., description="是否启用")
    number_limits: int = Field(default=3, description="文件数量限制")
    transfer_methods: List[Literal["remote_url", "local_file"]] = Field(
        ..., description="传输方式列表"
    )
    detail: Optional[str] = Field(None, description="详细设置（仅图片）")


class SystemParameters(BaseModel):
    """系统参数"""
    file_size_limit: int = Field(..., description="文档上传大小限制 (MB)")
    image_file_size_limit: int = Field(..., description="图片文件上传大小限制（MB）")
    audio_file_size_limit: int = Field(..., description="音频文件上传大小限制 (MB)")
    video_file_size_limit: int = Field(..., description="视频文件上传大小限制 (MB)")


class AppParametersResponse(BaseModel):
    """应用参数响应"""
    user_input_form: List[Dict[str, Any]] = Field(..., description="用户输入表单配置")
    file_upload: Dict[str, FileUploadSettings] = Field(..., description="文件上传配置")
    system_parameters: SystemParameters = Field(..., description="系统参数")


class AppSiteResponse(BaseModel):
    """应用 WebApp 设置响应"""
    title: str = Field(..., description="WebApp 名称")
    icon_type: str = Field(..., description="图标类型")
    icon: str = Field(..., description="图标")
    icon_background: str = Field(..., description="背景色")
    icon_url: Optional[str] = Field(None, description="图标 URL")
    description: str = Field(..., description="描述")
    copyright: str = Field(..., description="版权信息")
    privacy_policy: str = Field(..., description="隐私政策链接")
    custom_disclaimer: str = Field(..., description="自定义免责声明")
    default_language: str = Field(..., description="默认语言")
    show_workflow_steps: bool = Field(..., description="是否显示工作流详情")


class DifyClient:
    """Dify API 客户端"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        初始化 Dify 客户端
        
        Args:
            base_url: API 服务器地址，如 http://119.45.130.88:8080/v1
            api_key: API 密钥
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def run_workflow(
        self, workflow_input: WorkflowInput
    ) -> Union[CompletionResponse, List[StreamEvent]]:
        """
        执行 workflow
        
        Args:
            workflow_input: 工作流输入参数
            
        Returns:
            CompletionResponse: blocking 模式的工作流执行结果
            List[StreamEvent]: streaming 模式的事件流列表
            
        Raises:
            requests.exceptions.RequestException: 网络请求异常
            ValueError: 响应数据格式错误
        """
        url = f"{self.base_url}/workflows/run"
        
        try:
            if workflow_input.response_mode == "streaming":
                # 流式模式
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=workflow_input.model_dump(),
                    timeout=300,
                    stream=True
                )
                response.raise_for_status()
                
                events = []
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            try:
                                event_data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                                # 根据 event 类型解析不同的事件
                                event_type = event_data.get('event')
                                if event_type == 'workflow_started':
                                    events.append(WorkflowStartedEvent(**event_data))
                                elif event_type == 'node_started':
                                    events.append(NodeStartedEvent(**event_data))
                                elif event_type == 'text_chunk':
                                    events.append(TextChunkEvent(**event_data))
                                elif event_type == 'node_finished':
                                    events.append(NodeFinishedEvent(**event_data))
                                elif event_type == 'workflow_finished':
                                    events.append(WorkflowFinishedEvent(**event_data))
                                elif event_type == 'tts_message':
                                    events.append(TTSMessageEvent(**event_data))
                                elif event_type == 'tts_message_end':
                                    events.append(TTSMessageEndEvent(**event_data))
                                elif event_type == 'ping':
                                    events.append(PingEvent(**event_data))
                            except (json.JSONDecodeError, KeyError) as e:
                                print(f"Failed to parse event: {line_str}, error: {e}")
                                continue
                return events
            else:
                # 阻塞模式
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=workflow_input.model_dump(),
                    timeout=300
                )
                response.raise_for_status()
                
                result_data = response.json()
                return CompletionResponse(**result_data)
                
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"请求失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")
    
    def get_workflow_status(self, workflow_run_id: str) -> WorkflowRunStatusResponse:
        """
        获取 workflow 执行情况
        
        Args:
            workflow_run_id: workflow 执行 ID
            
        Returns:
            WorkflowRunStatusResponse: 工作流状态信息
        """
        url = f"{self.base_url}/workflows/run/{workflow_run_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            return WorkflowRunStatusResponse(**result_data)
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"请求失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")
    
    def stop_task(self, task_id: str, user: str) -> StopTaskResponse:
        """
        停止响应（仅支持流式模式）
        
        Args:
            task_id: 任务 ID
            user: 用户标识
            
        Returns:
            StopTaskResponse: 停止任务响应
        """
        url = f"{self.base_url}/workflows/tasks/{task_id}/stop"
        stop_input = StopTaskInput(user=user)
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=stop_input.model_dump(),
                timeout=30
            )
            response.raise_for_status()
            
            result_data = response.json()
            return StopTaskResponse(**result_data)
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"请求失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")
    
    def upload_file(self, file_path: str, user: str, file_type: str = "TXT") -> FileUploadResponse:
        """
        上传文件
        
        Args:
            file_path: 文件路径
            user: 用户标识
            file_type: 文件类型
            
        Returns:
            FileUploadResponse: 文件上传响应
        """
        url = f"{self.base_url}/files/upload"
        
        # 移除 Content-Type header，让 requests 自动设置 multipart/form-data
        upload_headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (file_path, file, 'text/plain')}
                data = {"user": user, "type": file_type}
                
                response = requests.post(
                    url,
                    headers=upload_headers,
                    files=files,
                    data=data,
                    timeout=300
                )
                response.raise_for_status()
                
                result_data = response.json()
                return FileUploadResponse(**result_data)
                
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"文件上传失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")
    
    def get_app_info(self) -> AppInfoResponse:
        """
        获取应用基本信息
        
        Returns:
            AppInfoResponse: 应用信息
        """
        url = f"{self.base_url}/info"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            return AppInfoResponse(**result_data)
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"请求失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")
    
    def get_app_parameters(self) -> AppParametersResponse:
        """
        获取应用参数
        
        Returns:
            AppParametersResponse: 应用参数
        """
        url = f"{self.base_url}/parameters"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            return AppParametersResponse(**result_data)
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"请求失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")
    
    def get_app_site_settings(self) -> AppSiteResponse:
        """
        获取应用 WebApp 设置
        
        Returns:
            AppSiteResponse: WebApp 设置
        """
        url = f"{self.base_url}/site"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result_data = response.json()
            return AppSiteResponse(**result_data)
            
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(f"请求失败: {e}")
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"响应数据格式错误: {e}")