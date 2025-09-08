#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify API 使用示例
演示如何使用 dify_client 模块进行文本生成
"""

from dify_client import DifyClient, DifyAPIError, FileInfo, FileType, TransferMethod


def demo_blocking_mode():
    """演示阻塞模式的使用"""
    print("=== 阻塞模式示例 ===")
    
    # 初始化客户端
    client = DifyClient(api_key="your-api-key-here")
    
    try:
        # 基础文本生成
        result = client.completion_messages_blocking(
            query="请帮我写一首关于春天的诗",
            user="test_user"
        )
        
        print(f"消息ID: {result.get('message_id')}")
        print(f"回答: {result.get('answer')}")
        print(f"用量: {result.get('usage')}")
        
        # 带变量的文本生成
        print("\n--- 带变量的调用 ---")
        result_with_inputs = client.completion_messages_blocking(
            query="请根据提供的信息生成内容",
            inputs={
                "topic": "人工智能",
                "style": "学术论文",
                "length": "500字"
            },
            user="test_user"
        )
        print(f"带变量的回答: {result_with_inputs.get('answer')[:100]}...")
        
    except DifyAPIError as e:
        print(f"API错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")


def demo_streaming_mode():
    """演示流式模式的使用"""
    print("\n=== 流式模式示例 ===")
    
    # 初始化客户端
    client = DifyClient(api_key="your-api-key-here")
    
    try:
        # 流式文本生成
        for chunk in client.completion_messages_streaming(
            query="请介绍一下人工智能的发展历程",
            user="test_user"
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
                print(f"\n流式错误: {chunk.get('message')}")
                break
                
    except DifyAPIError as e:
        print(f"API错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")


def demo_file_upload():
    """演示文件上传的使用"""
    print("\n=== 文件上传示例 ===")
    
    # 初始化客户端
    client = DifyClient(api_key="your-api-key-here")
    
    try:
        # 使用远程图片URL
        file_info = FileInfo(
            type=FileType.IMAGE.value,
            transfer_method=TransferMethod.REMOTE_URL.value,
            url="https://example.com/image.jpg"
        )
        
        result = client.completion_messages_blocking(
            query="请描述这张图片的内容",
            files=[file_info],
            user="test_user"
        )
        
        print(f"图片描述: {result.get('answer')}")
        
    except DifyAPIError as e:
        print(f"API错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")


def main():
    """主函数：运行所有示例"""
    print("Dify API 客户端使用示例")
    print("=" * 50)
    
    # 注意：在实际使用前，请将 'your-api-key-here' 替换为真实的API密钥
    print("⚠️  请先将API密钥替换为真实密钥后再运行示例")
    print()
    
    # 运行各种示例
    demo_blocking_mode()
    demo_streaming_mode()
    demo_file_upload()
    
    print("\n=" * 50)
    print("示例运行完成！")


if __name__ == "__main__":
    main()