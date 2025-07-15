#!/usr/bin/env python3
"""
BDDL文件修改器 - 简单字符串匹配版
通过检查obj_of_interest中是否包含物体名称来决定保留或删除
"""

import re
import os
from typing import Dict, List, Tuple, Set
from datetime import datetime


class BDDLModifierSimpleMatch:
    def __init__(self):
        self.original_content = ""
        self.modified_content = ""
        self.deleted_objects_positions = []
        self.deleted_fixtures = []
        self.deleted_init_statements = []
        
    def read_bddl_file(self, file_path: str) -> str:
        """读取BDDL文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.original_content = content
            return content
        except FileNotFoundError:
            raise FileNotFoundError(f"找不到文件: {file_path}")
        except Exception as e:
            raise Exception(f"读取文件时出错: {e}")
    
    def extract_obj_of_interest(self, content: str) -> str:
        """提取obj_of_interest字段的值"""
        pattern = r'\(:obj_of_interest\s+([^\)]+)\)'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_section(self, content: str, section_name: str) -> str:
        """提取指定section的内容"""
        pattern = rf'\({section_name}\s+(.*?)\n\s*\)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def extract_item_name(self, item_line: str) -> str:
        """从一行中提取短横线前的物体名称"""
        # 例如: "flat_stove_1 - flat_stove" -> "flat_stove_1"
        if ' - ' in item_line:
            return item_line.split(' - ')[0].strip()
        return item_line.strip()
    
    def parse_fixtures(self, fixtures_content: str) -> List[Tuple[str, str]]:
        """解析fixtures字段，返回(name, type)列表"""
        fixtures = []
        lines = fixtures_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('('):
                parts = line.split(' - ')
                if len(parts) == 2:
                    fixtures.append((parts[0].strip(), parts[1].strip()))
        return fixtures
    
    def parse_objects(self, objects_content: str) -> List[Tuple[str, str]]:
        """解析objects字段，返回(name, type)列表"""
        objects = []
        lines = objects_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('('):
                parts = line.split(' - ')
                if len(parts) == 2:
                    objects.append((parts[0].strip(), parts[1].strip()))
        return objects
    
    def parse_init_statements(self, init_content: str) -> List[str]:
        """解析init字段，返回语句列表"""
        statements = []
        # 匹配 (On ...) 格式的语句
        pattern = r'\(On\s+[^)]+\)'
        matches = re.findall(pattern, init_content)
        return matches
    
    def should_keep_item(self, item_name: str, obj_of_interest: str) -> bool:
        """判断是否应该保留某个项目"""
        # main_table总是保留
        if item_name == 'main_table':
            return True
        
        # 检查obj_of_interest中是否包含item_name
        return item_name in obj_of_interest
    
    def filter_fixtures(self, fixtures: List[Tuple[str, str]], obj_of_interest: str) -> Tuple[List[Tuple[str, str]], List[str]]:
        """过滤fixtures，返回保留的和删除的"""
        kept_fixtures = []
        deleted_fixtures = []
        
        print(f"过滤fixtures，obj_of_interest: {obj_of_interest}")
        
        for name, obj_type in fixtures:
            if self.should_keep_item(name, obj_of_interest):
                kept_fixtures.append((name, obj_type))
                print(f"  保留fixture: {name} (匹配)")
            else:
                deleted_fixtures.append(f"{name} - {obj_type}")
                print(f"  删除fixture: {name} (不匹配)")
        
        return kept_fixtures, deleted_fixtures
    
    def filter_objects(self, objects: List[Tuple[str, str]], obj_of_interest: str) -> Tuple[List[Tuple[str, str]], List[Tuple[int, str]]]:
        """过滤objects，返回保留的和删除的（带位置信息）"""
        kept_objects = []
        deleted_objects = []
        
        print(f"过滤objects，obj_of_interest: {obj_of_interest}")
        
        for i, (name, obj_type) in enumerate(objects):
            if self.should_keep_item(name, obj_of_interest):
                kept_objects.append((name, obj_type))
                print(f"  保留object: {name} (位置{i}, 匹配)")
            else:
                deleted_objects.append((i, f"{name} - {obj_type}"))
                print(f"  删除object: {name} (位置{i}, 不匹配)")
        
        return kept_objects, deleted_objects
    
    def filter_init_statements(self, statements: List[str], obj_of_interest: str) -> Tuple[List[str], List[str]]:
        """过滤init语句，返回保留的和删除的"""
        kept_statements = []
        deleted_statements = []
        
        print(f"过滤init语句，obj_of_interest: {obj_of_interest}")
        
        for statement in statements:
            # 提取语句中的物体名称
            # 例如: "(On wine_bottle_1 main_table_wine_bottle_region)" -> wine_bottle_1
            pattern = r'\(On\s+(\w+)\s+'
            match = re.match(pattern, statement)
            
            should_keep = False
            if match:
                item_name = match.group(1)
                if self.should_keep_item(item_name, obj_of_interest):
                    should_keep = True
                    print(f"  保留语句: {statement} (包含{item_name})")
                else:
                    print(f"  删除语句: {statement} (包含{item_name}, 不匹配)")
            else:
                # 如果无法解析，默认保留
                should_keep = True
                print(f"  保留语句: {statement} (无法解析，默认保留)")
            
            if should_keep:
                kept_statements.append(statement)
            else:
                deleted_statements.append(statement)
        
        return kept_statements, deleted_statements
    
    def generate_modified_content(self, content: str, kept_fixtures: List[Tuple[str, str]], 
                                kept_objects: List[Tuple[str, str]], kept_init: List[str]) -> str:
        """生成修改后的BDDL文件内容"""
        # 替换fixtures字段
        fixtures_text = "\n    ".join([f"{name} - {obj_type}" for name, obj_type in kept_fixtures])
        fixtures_pattern = r'(\(:fixtures\s+)(.*?)(\n\s*\))'
        content = re.sub(fixtures_pattern, rf'\1{fixtures_text}\3', content, flags=re.DOTALL)
        
        # 替换objects字段
        if kept_objects:
            objects_text = "\n    ".join([f"{name} - {obj_type}" for name, obj_type in kept_objects])
        else:
            objects_text = ""
        objects_pattern = r'(\(:objects\s+)(.*?)(\n\s*\))'
        content = re.sub(objects_pattern, rf'\1{objects_text}\3', content, flags=re.DOTALL)
        
        # 替换init字段
        init_text = "\n    ".join(kept_init)
        init_pattern = r'(\(:init\s+)(.*?)(\n\s*\))'
        content = re.sub(init_pattern, rf'\1{init_text}\3', content, flags=re.DOTALL)
        
        return content
    
    def generate_report(self, original_file: str, modified_file: str, obj_of_interest: str) -> str:
        """生成删除报告"""
        report = f"""# BDDL文件修改报告（简单字符串匹配版）

## 修改概述
根据`:obj_of_interest`字段中的`{obj_of_interest}`，通过简单字符串匹配保留相关项目，删除无关项目。

## 匹配规则
- 检查物体名称（短横线前部分）是否包含在`:obj_of_interest`中
- `main_table`总是保留
- 对`:fixtures`、`:objects`和`:init`字段应用相同规则

## 修改时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文件路径
- 原始文件: `{os.path.abspath(original_file)}`
- 修改后文件: `{os.path.abspath(modified_file)}`

## 被删除项详细记录

### :fixtures字段中被删除的项目
"""
        if self.deleted_fixtures:
            for fixture in self.deleted_fixtures:
                report += f"- `{fixture}`\n"
        else:
            report += "- 无\n"
        
        report += f"""
### :objects字段中被删除的项目及其位置
"""
        if self.deleted_objects_positions:
            for pos, obj in self.deleted_objects_positions:
                report += f"- 位置 {pos}: `{obj}`\n"
        else:
            report += "- 无\n"
        
        report += f"""
### :init字段中被删除的语句
"""
        if self.deleted_init_statements:
            for stmt in self.deleted_init_statements:
                report += f"- `{stmt}`\n"
        else:
            report += "- 无\n"
        
        report += """
## 注意事项
- 所有修改仅涉及:fixtures、:objects和:init字段
- 其他字段(:domain、:language、:regions、:obj_of_interest、:goal)保持不变
- main_table始终被保留
- 使用简单字符串包含匹配，不分析语义关系
"""
        
        return report
    
    def modify_bddl_file(self, input_file: str, output_file: str = None, report_file: str = None) -> Dict[str, str]:
        """修改BDDL文件的主函数"""
        # 设置默认输出文件名
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_simple_match_modified.bddl"
        
        if report_file is None:
            base_name = os.path.splitext(input_file)[0]
            report_file = f"{base_name}_simple_match_report.md"
        
        # 读取文件
        content = self.read_bddl_file(input_file)
        
        # 提取obj_of_interest
        obj_of_interest = self.extract_obj_of_interest(content)
        if not obj_of_interest:
            raise ValueError("未找到obj_of_interest字段")
        
        print(f"目标对象: {obj_of_interest}")
        
        # 解析各个字段
        fixtures_content = self.extract_section(content, ':fixtures')
        objects_content = self.extract_section(content, ':objects')
        init_content = self.extract_section(content, ':init')
        
        fixtures = self.parse_fixtures(fixtures_content)
        objects = self.parse_objects(objects_content)
        init_statements = self.parse_init_statements(init_content)
        
        print(f"发现 {len(fixtures)} 个fixtures，{len(objects)} 个objects，{len(init_statements)} 个init语句")
        
        # 过滤各个字段
        kept_fixtures, self.deleted_fixtures = self.filter_fixtures(fixtures, obj_of_interest)
        kept_objects, self.deleted_objects_positions = self.filter_objects(objects, obj_of_interest)
        kept_init, self.deleted_init_statements = self.filter_init_statements(init_statements, obj_of_interest)
        
        print(f"\n结果统计:")
        print(f"保留: {len(kept_fixtures)} fixtures, {len(kept_objects)} objects, {len(kept_init)} init语句")
        print(f"删除: {len(self.deleted_fixtures)} fixtures, {len(self.deleted_objects_positions)} objects, {len(self.deleted_init_statements)} init语句")
        
        # 生成修改后的内容
        self.modified_content = self.generate_modified_content(content, kept_fixtures, kept_objects, kept_init)
        
        # 保存修改后的文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.modified_content)
        
        # 生成并保存报告
        report = self.generate_report(input_file, output_file, obj_of_interest)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 返回结果信息
        result = {
            'original_file': os.path.abspath(input_file),
            'modified_file': os.path.abspath(output_file),
            'report_file': os.path.abspath(report_file),
            'obj_of_interest': obj_of_interest,
            'deleted_objects_positions': [pos for pos, _ in self.deleted_objects_positions],
            'deleted_objects_details': self.deleted_objects_positions,
            'deleted_fixtures': self.deleted_fixtures,
            'deleted_init_statements': self.deleted_init_statements
        }
        
        return result


def test_different_scenarios():
    """测试不同场景"""
    modifier = BDDLModifierSimpleMatch()
    
    # 测试场景1: flat_stove相关
    print("="*60)
    print("测试场景1: flat_stove_1_cook_region")
    print("="*60)
    try:
        result1 = modifier.modify_bddl_file("problem_flat_stove.bddl")
        print(f"✅ 场景1完成，删除的objects位置: {result1['deleted_objects_positions']}")
    except Exception as e:
        print(f"❌ 场景1失败: {e}")
    
    # 测试场景2: wooden_cabinet相关
    print("\n" + "="*60)
    print("测试场景2: wooden_cabinet_1_middle_region") 
    print("="*60)
    try:
        result2 = modifier.modify_bddl_file("problem.bddl")
        print(f"✅ 场景2完成，删除的objects位置: {result2['deleted_objects_positions']}")
    except Exception as e:
        print(f"❌ 场景2失败: {e}")


if __name__ == "__main__":
    test_different_scenarios()