#!/usr/bin/env python3
"""
整合修改器 - 增强版
使用增强版的BDDL修改器，能够通过init语句分析objects与fixtures的关联关系
"""

from typing import Dict, List, Tuple, Optional
import os
from bddl_modifier_enhanced import BDDLModifierEnhanced
from init_state_modifier_simple import InitStateModifierSimple, create_sample_init_state, save_list_to_json


class IntegratedModifierEnhanced:
    def __init__(self):
        self.bddl_modifier = BDDLModifierEnhanced()
        self.init_state_modifier = InitStateModifierSimple()
    
    def process_bddl_and_init_state(self, 
                                   bddl_file: str, 
                                   init_state: List[List[float]],
                                   output_bddl: Optional[str] = None,
                                   output_init_state: Optional[str] = None,
                                   report_file: Optional[str] = None) -> Dict:
        """
        同时处理BDDL文件和init_state数组（使用增强版BDDL修改器）
        
        Args:
            bddl_file: 输入的BDDL文件路径
            init_state: 初始状态数组，形状为(50, n)的二维列表
            output_bddl: 输出BDDL文件路径（可选）
            output_init_state: 输出init_state文件路径（可选）
            report_file: 报告文件路径（可选）
        
        Returns:
            Dict: 包含所有修改结果的字典
        """
        print("=== 开始处理BDDL文件和init_state数组（增强版）===\n")
        
        # 第一步：处理BDDL文件
        print("1. 处理BDDL文件...")
        bddl_result = self.bddl_modifier.modify_bddl_file(
            input_file=bddl_file,
            output_file=output_bddl,
            report_file=report_file
        )
        
        deleted_positions = bddl_result['deleted_objects_positions']
        print(f"   ✅ BDDL处理完成")
        print(f"   目标对象: {bddl_result['obj_of_interest']}")
        print(f"   相关项目: {bddl_result['related_items']}")
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
            output_init_state = f"{base_name}_enhanced_modified_init_state.json"
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
            'related_items': bddl_result['related_items'],
            
            # 统计信息
            'summary': {
                'deleted_objects_count': len(deleted_positions),
                'deleted_fixtures_count': len(bddl_result['deleted_fixtures']),
                'deleted_init_statements_count': len(bddl_result['deleted_init_statements']),
                'deleted_init_state_columns': init_state_info['total_deleted_columns'],
                'init_state_size_reduction': f"{init_state_info['original_shape'][1]} -> {init_state_info['new_shape'][1]} 列",
                'related_items_summary': f"保留了 {len(bddl_result['related_items'])} 个相关项目"
            }
        }
        
        return integrated_result
    
    def generate_integrated_report(self, result: Dict, report_file: str = "integrated_enhanced_report.md"):
        """生成增强版整合报告"""
        report_content = f"""# 整合修改报告（增强版）

## 概述
根据BDDL文件中的`:obj_of_interest`字段，通过分析`:init`语句确定相关项目，同时修改了BDDL文件和对应的init_state数组。

## 目标对象
`{result['obj_of_interest']}`

## 识别的相关项目
{result['related_items']}

## 修改统计
- 删除的objects数量: {result['summary']['deleted_objects_count']}
- 删除的fixtures数量: {result['summary']['deleted_fixtures_count']}
- 删除的init语句数量: {result['summary']['deleted_init_statements_count']}
- init_state删除的列数: {result['summary']['deleted_init_state_columns']}
- init_state尺寸变化: {result['summary']['init_state_size_reduction']}
- {result['summary']['related_items_summary']}

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
## 增强功能说明
- **智能关联分析**: 通过分析`:init`语句自动识别objects与fixtures的关联关系
- **精确保留**: 只保留与`:obj_of_interest`相关的fixtures和objects
- **数据一致性**: 确保BDDL文件和init_state数组的修改保持一致

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
- 增强版能够通过init语句自动识别相关性，避免误删除相关objects
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 增强版整合报告已保存到: {os.path.abspath(report_file)}")
        return os.path.abspath(report_file)


def example_enhanced_usage():
    """增强版整合使用示例"""
    print("=== 增强版整合修改器使用示例 ===\n")
    
    # 1. 准备数据
    bddl_file = "problem_flat_stove.bddl"
    init_state = create_sample_init_state(num_objects=6)  # 创建有6个objects的init_state
    
    print(f"准备数据:")
    print(f"  BDDL文件: {bddl_file}")
    print(f"  init_state形状: {len(init_state)} x {len(init_state[0])}")
    print()
    
    # 2. 创建增强版整合修改器并处理
    integrated_modifier = IntegratedModifierEnhanced()
    
    try:
        result = integrated_modifier.process_bddl_and_init_state(
            bddl_file=bddl_file,
            init_state=init_state,
            output_bddl="problem_flat_stove_enhanced_integrated_modified.bddl",
            output_init_state="init_state_flat_stove_enhanced_modified.json",
            report_file="bddl_flat_stove_enhanced_report.md"
        )
        
        print("\n" + "="*60)
        print("✅ 增强版整合处理完成！")
        print("\n📊 处理结果统计:")
        for key, value in result['summary'].items():
            print(f"  {key}: {value}")
        
        print(f"\n🎯 关键信息:")
        print(f"  目标对象: {result['obj_of_interest']}")
        print(f"  相关项目: {result['related_items']}")
        print(f"  删除的objects位置: {result['deleted_objects_positions']}")
        
        print(f"\n📁 输出文件:")
        print(f"  修改后BDDL: {result['modified_bddl_file']}")
        print(f"  修改后init_state: {result['modified_init_state_file']}")
        print(f"  BDDL详细报告: {result['bddl_report_file']}")
        
        # 3. 生成增强版整合报告
        integrated_report = integrated_modifier.generate_integrated_report(
            result, "complete_enhanced_integrated_report.md"
        )
        
        print(f"  增强版整合报告: {integrated_report}")
        
        # 4. 验证结果
        print(f"\n🔍 结果验证:")
        print(f"  原始init_state形状: {len(init_state)} x {len(init_state[0])}")
        print(f"  修改后init_state形状: {result['modified_init_state_shape']}")
        print(f"  预期删除列数: {len(result['deleted_objects_positions']) * 7}")
        print(f"  实际删除列数: {result['summary']['deleted_init_state_columns']}")
        
        # 验证数据一致性
        expected_columns = len(init_state[0]) - len(result['deleted_objects_positions']) * 7
        actual_columns = result['modified_init_state_shape'][1]
        print(f"  列数验证: 预期{expected_columns} = 实际{actual_columns} ✅" if expected_columns == actual_columns else "❌")
        
        # 显示详细的删除和保留信息
        print(f"\n📋 详细修改信息:")
        print(f"  保留的相关项目数量: {len(result['related_items'])}")
        print(f"  删除的objects位置: {result['deleted_objects_positions']}")
        
        return result
        
    except Exception as e:
        print(f"❌ 处理过程中出错: {e}")
        return None


if __name__ == "__main__":
    # 运行增强版整合示例
    result = example_enhanced_usage()
    
    if result:
        print(f"\n🎉 增强版整合修改完成！")
        print(f"✅ 问题已解决：现在能够正确保留与:obj_of_interest相关的fixture和objects")
    else:
        print(f"\n💥 增强版整合修改失败，请检查错误信息。")