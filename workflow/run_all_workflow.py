#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有工作流脚本

这个脚本依次执行三个工作流：
1. sunian-girl/sunian.py - 素年养生工作流
2. wellnessmom/wellness_workflow.py - 养生妈妈工作流  
3. workmen/workmen.py - 职场生存优化师工作流

作者: SOLO Coding
创建时间: 2024-01-15
"""

import sys
import os
import subprocess
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'workflow_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class WorkflowRunner:
    """工作流运行器"""
    
    def __init__(self):
        self.workflow_dir = Path(__file__).parent
        self.workflows = [
            {
                'name': '素年养生工作流',
                'script_path': self.workflow_dir / 'sunian-girl' / 'sunian.py',
                'description': '生成素年养生相关的内容和产品推荐'
            },
            {
                'name': '养生妈妈工作流',
                'script_path': self.workflow_dir / 'wellnessmom' / 'wellness_workflow.py',
                'description': '生成养生妈妈相关的内容和产品推荐'
            },
            {
                'name': '职场生存优化师工作流',
                'script_path': self.workflow_dir / 'workmen' / 'workmen.py',
                'description': '生成职场生存优化师相关的内容和产品推荐'
            }
        ]
        self.results = []
    
    def run_single_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个工作流"""
        name = workflow['name']
        script_path = workflow['script_path']
        description = workflow['description']
        
        logger.info(f"开始运行工作流: {name}")
        logger.info(f"描述: {description}")
        logger.info(f"脚本路径: {script_path}")
        
        start_time = time.time()
        
        try:
            # 检查脚本文件是否存在
            if not script_path.exists():
                raise FileNotFoundError(f"脚本文件不存在: {script_path}")
            
            # 运行脚本
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(script_path.parent),
                capture_output=True,
                text=True,
                timeout=1200  # 10分钟超时
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                logger.info(f"✅ {name} 执行成功 (耗时: {duration:.2f}秒)")
                if result.stdout:
                    logger.info(f"输出: {result.stdout}")
                
                return {
                    'name': name,
                    'success': True,
                    'duration': duration,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
            else:
                logger.error(f"❌ {name} 执行失败 (返回码: {result.returncode})")
                if result.stderr:
                    logger.error(f"错误信息: {result.stderr}")
                if result.stdout:
                    logger.info(f"输出: {result.stdout}")
                
                return {
                    'name': name,
                    'success': False,
                    'duration': duration,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ {name} 执行超时 (超过10分钟)")
            return {
                'name': name,
                'success': False,
                'duration': 600,
                'stdout': '',
                'stderr': '执行超时',
                'returncode': -1
            }
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"❌ {name} 执行异常: {str(e)}")
            return {
                'name': name,
                'success': False,
                'duration': duration,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def run_all_workflows(self) -> List[Dict[str, Any]]:
        """运行所有工作流"""
        logger.info("=" * 60)
        logger.info("开始运行所有工作流")
        logger.info("=" * 60)
        
        total_start_time = time.time()
        
        for i, workflow in enumerate(self.workflows, 1):
            logger.info(f"\n[{i}/{len(self.workflows)}] 准备运行: {workflow['name']}")
            logger.info("-" * 40)
            
            result = self.run_single_workflow(workflow)
            self.results.append(result)
            
            # 在工作流之间添加短暂延迟
            if i < len(self.workflows):
                logger.info("等待3秒后继续下一个工作流...")
                time.sleep(3)
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # 输出总结报告
        self.print_summary_report(total_duration)
        
        return self.results
    
    def print_summary_report(self, total_duration: float):
        """打印总结报告"""
        logger.info("\n" + "=" * 60)
        logger.info("工作流执行总结报告")
        logger.info("=" * 60)
        
        successful_count = sum(1 for result in self.results if result['success'])
        failed_count = len(self.results) - successful_count
        
        logger.info(f"总执行时间: {total_duration:.2f}秒")
        logger.info(f"成功工作流: {successful_count}/{len(self.results)}")
        logger.info(f"失败工作流: {failed_count}/{len(self.results)}")
        
        logger.info("\n详细结果:")
        for result in self.results:
            status = "✅ 成功" if result['success'] else "❌ 失败"
            logger.info(f"  {result['name']}: {status} (耗时: {result['duration']:.2f}秒)")
            if not result['success'] and result['stderr']:
                logger.info(f"    错误: {result['stderr']}")
        
        if successful_count == len(self.results):
            logger.info("\n🎉 所有工作流都执行成功！")
        else:
            logger.info(f"\n⚠️  有 {failed_count} 个工作流执行失败，请检查日志")


def main():
    """主函数"""
    try:
        runner = WorkflowRunner()
        results = runner.run_all_workflows()
        
        # 根据执行结果设置退出码
        failed_count = sum(1 for result in results if not result['success'])
        if failed_count > 0:
            sys.exit(1)  # 有失败的工作流
        else:
            sys.exit(0)  # 所有工作流都成功
            
    except KeyboardInterrupt:
        logger.info("\n用户中断执行")
        sys.exit(130)
    except Exception as e:
        logger.error(f"运行器异常: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()