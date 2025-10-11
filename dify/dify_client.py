#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify API 封装类
用于文本生成型应用的API调用，支持阻塞和流式两种模式
"""

import json
import requests
from typing import Dict, Any, Optional, List, Iterator, Union
from dataclasses import dataclass
from enum import Enum


class ResponseMode(Enum):
    """响应模式枚举"""
    BLOCKING = "blocking"  # 阻塞模式
    STREAMING = "streaming"  # 流式模式


class FileType(Enum):
    """文件类型枚举"""
    IMAGE = "image"


class TransferMethod(Enum):
    """文件传递方式枚举"""
    REMOTE_URL = "remote_url"
    LOCAL_FILE = "local_file"


@dataclass
class FileInfo:
    """文件信息数据类"""
    type: str
    transfer_method: str
    url: Optional[str] = None
    upload_file_id: Optional[str] = None


@dataclass
class Usage:
    """模型用量信息"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class RetrieverResource:
    """引用和归属分段"""
    position: int
    dataset_id: str
    dataset_name: str
    document_id: str
    document_name: str
    data_source_type: str
    segment_id: str
    score: float
    content: str


class DifyAPIError(Exception):
    """Dify API 异常类"""
    def __init__(self, status_code: int, code: str, message: str, task_id: str = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.task_id = task_id
        super().__init__(f"[{status_code}] {code}: {message}")


class DifyClient:
    """Dify API 客户端"""
    
    def __init__(self, api_key: str, base_url: str = "http://119.45.130.88/v1"):
        """
        初始化Dify客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """处理错误响应"""
        try:
            error_data = response.json()
            raise DifyAPIError(
                status_code=response.status_code,
                code=error_data.get('code', 'unknown_error'),
                message=error_data.get('message', 'Unknown error occurred')
            )
        except json.JSONDecodeError:
            raise DifyAPIError(
                status_code=response.status_code,
                code='response_parse_error',
                message=f'Failed to parse error response: {response.text}'
            )
    
    def completion_messages_blocking(
        self,
        query: str = None,
        inputs: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        files: Optional[List[FileInfo]] = None
    ) -> Dict[str, Any]:
        """
        发送阻塞模式的文本生成请求
        
        Args:
            query: 用户输入的文本内容（会自动添加到 inputs["query"] 中）
            inputs: 应用定义的变量值
            user: 用户标识
            files: 上传的文件列表
            
        Returns:
            完整的响应结果
            
        Raises:
            DifyAPIError: API调用异常
        """
        # 处理 inputs，确保 query 正确传递
        final_inputs = inputs.copy() if inputs else {}
        if query is not None:
            final_inputs["query"] = query
            
        return self._completion_messages(
            inputs=final_inputs,
            response_mode=ResponseMode.BLOCKING,
            user=user,
            files=files
        )
    
    def completion_messages_streaming(
        self,
        query: str = None,
        inputs: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        files: Optional[List[FileInfo]] = None
    ) -> Iterator[Dict[str, Any]]:
        """
        发送流式模式的文本生成请求
        
        Args:
            query: 用户输入的文本内容（会自动添加到 inputs["query"] 中）
            inputs: 应用定义的变量值
            user: 用户标识
            files: 上传的文件列表
            
        Yields:
            流式响应块
            
        Raises:
            DifyAPIError: API调用异常
        """
        url = f"{self.base_url}/completion-messages"
        
        # 处理 inputs，确保 query 正确传递
        final_inputs = inputs.copy() if inputs else {}
        if query is not None:
            final_inputs["query"] = query
        
        # 构建请求数据
        data = {
            "inputs": final_inputs,
            "response_mode": ResponseMode.STREAMING.value,
            "user": user or "default_user"
        }
        
        if files:
            data["files"] = [self._file_info_to_dict(f) for f in files]
        
        try:
            response = self.session.post(url, json=data, stream=True)
            
            if not response.ok:
                self._handle_error_response(response)
            
            # 处理流式响应
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data_str = line[6:]  # 移除 'data: ' 前缀
                        if data_str.strip():
                            chunk_data = json.loads(data_str)
                            
                            # 检查是否有错误事件
                            if chunk_data.get('event') == 'error':
                                raise DifyAPIError(
                                    status_code=chunk_data.get('status', 500),
                                    code=chunk_data.get('code', 'stream_error'),
                                    message=chunk_data.get('message', 'Stream error occurred'),
                                    task_id=chunk_data.get('task_id')
                                )
                            
                            yield chunk_data
                    except json.JSONDecodeError:
                        continue  # 跳过无法解析的行
                        
        except requests.RequestException as e:
            raise DifyAPIError(
                status_code=0,
                code='request_error',
                message=f'Request failed: {str(e)}'
            )
    
    def _completion_messages(
        self,
        inputs: Dict[str, Any],
        response_mode: ResponseMode,
        user: Optional[str] = None,
        files: Optional[List[FileInfo]] = None
    ) -> Dict[str, Any]:
        """内部方法：发送文本生成请求"""
        url = f"{self.base_url}/completion-messages"
        
        # 构建请求数据
        data = {
            "inputs": inputs,
            "response_mode": response_mode.value,
            "user": user or "default_user"
        }
        
        if files:
            data["files"] = [self._file_info_to_dict(f) for f in files]
        
        print(f"## Request data: {data}")
        try:
            response = self.session.post(url, json=data)
            if not response.ok:
                self._handle_error_response(response)
            
            return response.json()
            
        except requests.RequestException as e:
            raise DifyAPIError(
                status_code=0,
                code='request_error',
                message=f'Request failed: {str(e)}'
            )
    
    def _file_info_to_dict(self, file_info: FileInfo) -> Dict[str, Any]:
        """将FileInfo对象转换为字典"""
        result = {
            "type": file_info.type,
            "transfer_method": file_info.transfer_method
        }
        
        if file_info.url:
            result["url"] = file_info.url
        if file_info.upload_file_id:
            result["upload_file_id"] = file_info.upload_file_id
            
        return result