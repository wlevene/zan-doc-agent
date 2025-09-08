#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dify Agent 系统测试运行器
统一的测试入口，可以运行所有测试或指定的测试模块
"""

import sys
import argparse
from typing import List, Optional

# 导入各个测试模块
import test_content_validator
import test_scenario_generator
import test_agent_manager


class TestRunner:
    """测试运行器类"""
    
    def __init__(self):
        self.test_modules = {
            'content_validator': test_content_validator,
            'scenario_generator': test_scenario_generator,
            'agent_manager': test_agent_manager
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("开始运行 Dify Agent 系统完整测试套件")
        print("=" * 60)
        
        failed_tests = []
        
        for module_name, module in self.test_modules.items():
            try:
                print(f"\n{'='*20} {module_name.upper()} 测试 {'='*20}")
                module.main()
                print(f"✅ {module_name} 测试完成")
            except Exception as e:
                print(f"❌ {module_name} 测试失败: {e}")
                failed_tests.append(module_name)
        
        # 测试总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total_tests = len(self.test_modules)
        passed_tests = total_tests - len(failed_tests)
        
        print(f"总测试模块数: {total_tests}")
        print(f"通过测试数: {passed_tests}")
        print(f"失败测试数: {len(failed_tests)}")
        
        if failed_tests:
            print(f"失败的测试模块: {', '.join(failed_tests)}")
            return False
        else:
            print("🎉 所有测试都通过了！")
            return True
    
    def run_specific_tests(self, test_names: List[str]):
        """运行指定的测试模块"""
        print("=" * 60)
        print(f"运行指定测试: {', '.join(test_names)}")
        print("=" * 60)
        
        failed_tests = []
        
        for test_name in test_names:
            if test_name not in self.test_modules:
                print(f"❌ 未找到测试模块: {test_name}")
                print(f"可用的测试模块: {', '.join(self.test_modules.keys())}")
                failed_tests.append(test_name)
                continue
            
            try:
                print(f"\n{'='*20} {test_name.upper()} 测试 {'='*20}")
                self.test_modules[test_name].main()
                print(f"✅ {test_name} 测试完成")
            except Exception as e:
                print(f"❌ {test_name} 测试失败: {e}")
                failed_tests.append(test_name)
        
        # 测试总结
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        
        total_tests = len(test_names)
        passed_tests = total_tests - len(failed_tests)
        
        print(f"运行测试数: {total_tests}")
        print(f"通过测试数: {passed_tests}")
        print(f"失败测试数: {len(failed_tests)}")
        
        if failed_tests:
            print(f"失败的测试: {', '.join(failed_tests)}")
            return False
        else:
            print("🎉 所有指定测试都通过了！")
            return True
    
    def list_available_tests(self):
        """列出可用的测试模块"""
        print("可用的测试模块:")
        for name, module in self.test_modules.items():
            doc = module.__doc__ or "无描述"
            print(f"  - {name}: {doc.strip()}")
    
    def run_interactive_mode(self):
        """交互式测试模式"""
        print("=== Dify Agent 交互式测试模式 ===")
        print("输入 'help' 查看可用命令")
        
        while True:
            try:
                command = input("\n测试> ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("退出测试模式")
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'list':
                    self.list_available_tests()
                elif command == 'all':
                    self.run_all_tests()
                elif command in self.test_modules:
                    self.run_specific_tests([command])
                else:
                    print(f"未知命令: {command}")
                    print("输入 'help' 查看可用命令")
            except KeyboardInterrupt:
                print("\n退出测试模式")
                break
            except Exception as e:
                print(f"执行错误: {e}")
    
    def _show_help(self):
        """显示帮助信息"""
        print("\n可用命令:")
        print("  help          - 显示此帮助信息")
        print("  list          - 列出所有可用测试模块")
        print("  all           - 运行所有测试")
        print("  <module_name> - 运行指定测试模块")
        print("  quit/exit/q   - 退出测试模式")
        print("\n可用测试模块:")
        for name in self.test_modules.keys():
            print(f"  {name}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Dify Agent 系统测试运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python test_runner.py                           # 运行所有测试
  python test_runner.py -t content_validator      # 运行指定测试
  python test_runner.py -t content_validator scenario_generator  # 运行多个测试
  python test_runner.py -i                        # 交互式模式
  python test_runner.py -l                        # 列出可用测试
        """
    )
    
    parser.add_argument(
        '-t', '--tests',
        nargs='*',
        help='指定要运行的测试模块名称'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='列出所有可用的测试模块'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='启动交互式测试模式'
    )
    
    args = parser.parse_args()
    runner = TestRunner()
    
    try:
        if args.list:
            runner.list_available_tests()
        elif args.interactive:
            runner.run_interactive_mode()
        elif args.tests:
            success = runner.run_specific_tests(args.tests)
            sys.exit(0 if success else 1)
        else:
            # 默认运行所有测试
            success = runner.run_all_tests()
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试运行器错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()