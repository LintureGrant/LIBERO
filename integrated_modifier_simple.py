#!/usr/bin/env python3
"""
整合修改器 - 纯Python版本
同时处理BDDL文件和init_state数组的修改（不依赖numpy）
"""

from typing import Dict, List, Tuple, Optional
import os
from bddl_modifier import BDDLModifier
from init_state_modifier_simple import InitStateModifierSimple, create_sample_init_state, save_list_to_json


class IntegratedModifierSimple:
    def __init__(self):
        self.bddl_modifier = BDDLModifier()
        self.init_state_modifier = InitStateModifierSimple()
    
    def process_bddl_and_init_state(self, 
                                   bddl_file: str, 
                                   init_state: List[List[float]],
                                   output_bddl: Optional[str] = None,
                                   output_init_state: Optional[str] = None,
                                   report_file: Optional[str] = None) -> Dict:
        """
        同时处理BDDL文件和init_state数组
        
        Args:
            bddl_file: 输入的BDDL文件路径
            init_state: 初始状态数组，形状为(50, n)的二维列表
            output_bddl: 输出BDDL文件路径（可选）
            output_init_state: 输出init_state文件路径（可选）
            report_file: 报告文件路径（可选）
        
        Returns:
            Dict: 包含所有修改结果的字典
        """
        print("=== 开始处理BDDL文件和init_state数组（纯Python版本）===\n")
        
        # 第一步：处理BDDL文件
        print("1. 处理BDDL文件...")
        bddl_result = self.bddl_modifier.modify_bddl_file(
            input_file=bddl_file,
            output_file=output_bddl,
            report_file=report_file
        )
        
        deleted_positions = bddl_result['deleted_objects_positions']
        print(f"   ✅ BDDL处理完成")
        print(f"   删除的objects位置: {deleted_positions}")
        print(f"   修改后文件: {bddl_result['modified_file']}")
        print()
        
        # 第二步：验证init_state结构
        print("2. 验证init_state结构...")
        validation = self.init_state_modifier.validate_init_state_structure(init_state)
        if not validation['valid']:
            raise ValueError(f"init_state结构无效: {validation['error']}")
        
        print(f"   ✅ 结构验证通过")
        print(f"   {validation['structure']}")
        print(f"   最大objects数量: {validation['max_objects_count']}")
        print()
        
        # 第三步：检查删除位置的有效性
        max_objects = validation['max_objects_count']
        invalid_positions = [pos for pos in deleted_positions if pos >= max_objects]
        if invalid_positions:
            raise ValueError(f"删除位置{invalid_positions}超出init_state中的有效范围[0, {max_objects-1}]")
        
        # 第四步：处理init_state数组
        print("3. 处理init_state数组...")
        modified_init_state, init_state_info = self.init_state_modifier.remove_deleted_objects_data(
            init_state, deleted_positions
        )
        
        print(f"   ✅ init_state处理完成")
        print(f"   原始形状: {init_state_info['original_shape']}")
        print(f"   修改后形状: {init_state_info['new_shape']}")
        print(f"   删除了 {init_state_info['total_deleted_columns']} 列数据")
        print()
        
        # 第五步：保存修改后的init_state
        if output_init_state:
            save_list_to_json(modified_init_state, output_init_state)
            print(f"4. 保存修改后的init_state到: {output_init_state}")
        else:
            # 默认保存路径
            base_name = os.path.splitext(bddl_file)[0]
            output_init_state = f"{base_name}_modified_init_state.json"
            save_list_to_json(modified_init_state, output_init_state)
            print(f"4. 保存修改后的init_state到: {output_init_state}")
        
        # 整合所有结果
        integrated_result = {
            # BDDL相关结果
            'bddl_result': bddl_result,
            'original_bddl_file': bddl_result['original_file'],
            'modified_bddl_file': bddl_result['modified_file'],
            'bddl_report_file': bddl_result['report_file'],
            
            # init_state相关结果
            'init_state_result': init_state_info,
            'original_init_state_shape': init_state_info['original_shape'],
            'modified_init_state_shape': init_state_info['new_shape'],
            'modified_init_state_file': os.path.abspath(output_init_state),
            'modified_init_state_array': modified_init_state,
            
            # 共同信息
            'deleted_objects_positions': deleted_positions,
            'obj_of_interest': bddl_result['obj_of_interest'],
            
            # 统计信息
            'summary': {
                'deleted_objects_count': len(deleted_positions),
                'deleted_fixtures_count': len(bddl_result['deleted_fixtures']),
                'deleted_init_statements_count': len(bddl_result['deleted_init_statements']),
                'deleted_init_state_columns': init_state_info['total_deleted_columns'],
                'init_state_size_reduction': f"{init_state_info['original_shape'][1]} -> {init_state_info['new_shape'][1]} 列"
            }
        }
        
        return integrated_result
    
    def generate_integrated_report(self, result: Dict, report_file: str = "integrated_report.md"):
        """生成整合报告"""
        report_content = f"""# 整合修改报告

## 概述
根据BDDL文件中的`:obj_of_interest`字段，同时修改了BDDL文件和对应的init_state数组。

## 目标对象
`{result['obj_of_interest']}`

## 修改统计
- 删除的objects数量: {result['summary']['deleted_objects_count']}
- 删除的fixtures数量: {result['summary']['deleted_fixtures_count']}
- 删除的init语句数量: {result['summary']['deleted_init_statements_count']}
- init_state删除的列数: {result['summary']['deleted_init_state_columns']}
- init_state尺寸变化: {result['summary']['init_state_size_reduction']}

## 文件路径
- 原始BDDL文件: `{result['original_bddl_file']}`
- 修改后BDDL文件: `{result['modified_bddl_file']}`
- BDDL详细报告: `{result['bddl_report_file']}`
- 修改后init_state文件: `{result['modified_init_state_file']}`

## 被删除的objects位置
{result['deleted_objects_positions']}

## 详细删除信息

### BDDL文件修改
#### 删除的fixtures:
"""
        
        for fixture in result['bddl_result']['deleted_fixtures']:
            report_content += f"- `{fixture}`\n"
        
        report_content += f"""
#### 删除的objects及其位置:
"""
        for pos, obj in result['bddl_result']['deleted_objects_details']:
            report_content += f"- 位置 {pos}: `{obj}`\n"
        
        report_content += f"""
#### 删除的init语句:
"""
        for stmt in result['bddl_result']['deleted_init_statements']:
            report_content += f"- `{stmt}`\n"
        
        report_content += f"""
### init_state数组修改
#### 原始形状: {result['original_init_state_shape']}
#### 修改后形状: {result['modified_init_state_shape']}

#### 删除的列范围:
"""
        
        for info in result['init_state_result']['deleted_ranges']:
            report_content += f"- 列 {info['range'][0]}-{info['range'][1]-1} (形状: {info['shape']})\n"
        
        report_content += f"""
## 使用说明
1. 加载修改后的BDDL文件: `{os.path.basename(result['modified_bddl_file'])}`
2. 加载修改后的init_state数组:
   ```python
   import json
   with open('{os.path.basename(result['modified_init_state_file'])}', 'r') as f:
       modified_init_state = json.load(f)
   ```

## 注意事项
- BDDL文件只修改了`:fixtures`、`:objects`和`:init`字段
- init_state数组保留了前10列的固定数据
- 删除的objects数据已从init_state中完全移除，后续数据已前移
- init_state数据以JSON格式保存
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 整合报告已保存到: {os.path.abspath(report_file)}")
        return os.path.abspath(report_file)


def example_integrated_usage():
    """整合使用示例"""
    print("=== 整合修改器使用示例（纯Python版本）===\n")
    
    # 1. 准备数据
    bddl_file = "problem.bddl"
    init_state = create_sample_init_state(num_objects=4)  # 创建有4个objects的init_state
    
    print(f"准备数据:")
    print(f"  BDDL文件: {bddl_file}")
    print(f"  init_state形状: {len(init_state)} x {len(init_state[0])}")
    print()
    
    # 2. 创建整合修改器并处理
    integrated_modifier = IntegratedModifierSimple()
    
    try:
        result = integrated_modifier.process_bddl_and_init_state(
            bddl_file=bddl_file,
            init_state=init_state,
            output_bddl="problem_integrated_simple_modified.bddl",
            output_init_state="init_state_integrated_simple_modified.json",
            report_file="bddl_integrated_simple_report.md"
        )
        
        print("\n" + "="*60)
        print("✅ 整合处理完成！")
        print("\n📊 处理结果统计:")
        for key, value in result['summary'].items():
            print(f"  {key}: {value}")
        
        print(f"\n📁 输出文件:")
        print(f"  修改后BDDL: {result['modified_bddl_file']}")
        print(f"  修改后init_state: {result['modified_init_state_file']}")
        print(f"  BDDL详细报告: {result['bddl_report_file']}")
        
        # 3. 生成整合报告
        integrated_report = integrated_modifier.generate_integrated_report(
            result, "complete_integrated_simple_report.md"
        )
        
        print(f"  整合报告: {integrated_report}")
        
        # 4. 验证结果
        print(f"\n🔍 结果验证:")
        print(f"  原始init_state形状: {len(init_state)} x {len(init_state[0])}")
        print(f"  修改后init_state形状: {result['modified_init_state_shape']}")
        print(f"  删除的objects位置: {result['deleted_objects_positions']}")
        print(f"  预期删除列数: {len(result['deleted_objects_positions']) * 7}")
        print(f"  实际删除列数: {result['summary']['deleted_init_state_columns']}")
        
        # 验证数据一致性
        expected_columns = len(init_state[0]) - len(result['deleted_objects_positions']) * 7
        actual_columns = result['modified_init_state_shape'][1]
        print(f"  列数验证: 预期{expected_columns} = 实际{actual_columns} ✅" if expected_columns == actual_columns else "❌")
        
        # 显示删除的具体列范围
        print(f"\n📋 删除的列范围详情:")
        for i, info in enumerate(result['init_state_result']['deleted_ranges']):
            print(f"  范围 {i+1}: 第{info['range'][0]}-{info['range'][1]-1}列 (Object {result['deleted_objects_positions'][len(result['deleted_objects_positions'])-1-i]})")
        
        return result
        
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")
        return None


def demonstrate_manual_usage():
    """演示手动使用方法"""
    print("\n=== 手动使用方法演示 ===\n")
    
    # 假设你有自己的init_state数据
    print("假设你有一个自己的init_state数据：")
    
    # 创建示例 - 你可以替换为你的实际数据
    your_init_state = create_sample_init_state(num_objects=4)
    print(f"你的init_state形状: {len(your_init_state)} x {len(your_init_state[0])}")
    
    # 从BDDL文件获取删除位置
    bddl_modifier = BDDLModifier()
    bddl_result = bddl_modifier.modify_bddl_file("problem.bddl")
    deleted_positions = bddl_result['deleted_objects_positions']
    
    print(f"从BDDL文件获取的删除位置: {deleted_positions}")
    
    # 修改init_state
    init_modifier = InitStateModifierSimple()
    modified_init_state, info = init_modifier.remove_deleted_objects_data(
        your_init_state, deleted_positions
    )
    
    print(f"修改后的init_state形状: {info['new_shape']}")
    print(f"删除了 {info['total_deleted_columns']} 列数据")
    
    # 保存结果
    save_list_to_json(modified_init_state, "your_modified_init_state.json")
    print(f"已保存到: your_modified_init_state.json")
    
    print("\n使用方法总结:")
    print("1. 用BDDLModifier处理BDDL文件，获取deleted_positions")
    print("2. 用InitStateModifierSimple.remove_deleted_objects_data()修改init_state")
    print("3. 保存结果到JSON文件")


if __name__ == "__main__":
    # 运行整合示例
    result = example_integrated_usage()
    
    if result:
        print(f"\n🎉 整合修改完成！所有文件已保存完毕。")
        # 演示手动使用方法
        demonstrate_manual_usage()
    else:
        print(f"\n💥 整合修改失败，请检查错误信息。")