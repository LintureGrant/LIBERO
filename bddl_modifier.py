#!/usr/bin/env python3
"""
BDDL文件修改器
根据obj_of_interest字段自动修改BDDL文件，保留相关项目并删除无关项目
"""

import re
import os
from typing import Dict, List, Tuple, Set
from datetime import datetime


class BDDLModifier:
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
    
    def determine_related_items(self, obj_of_interest: str) -> Set[str]:
        """根据obj_of_interest确定相关的项目"""
        related_items = set()
        
        # 总是保留main_table
        related_items.add('main_table')
        
        # 如果obj_of_interest包含某个对象的引用，则保留该对象
        # 例如: wooden_cabinet_1_middle_region -> wooden_cabinet_1
        if '_' in obj_of_interest:
            parts = obj_of_interest.split('_')
            # 尝试不同的组合来找到可能的对象名
            for i in range(1, len(parts)):
                potential_object = '_'.join(parts[:i+1])
                related_items.add(potential_object)
        
        return related_items
    
    def filter_fixtures(self, fixtures: List[Tuple[str, str]], related_items: Set[str]) -> Tuple[List[Tuple[str, str]], List[str]]:
        """过滤fixtures，返回保留的和删除的"""
        kept_fixtures = []
        deleted_fixtures = []
        
        for name, obj_type in fixtures:
            if name in related_items:
                kept_fixtures.append((name, obj_type))
            else:
                deleted_fixtures.append(f"{name} - {obj_type}")
        
        return kept_fixtures, deleted_fixtures
    
    def filter_objects(self, objects: List[Tuple[str, str]], related_items: Set[str]) -> Tuple[List[Tuple[str, str]], List[Tuple[int, str]]]:
        """过滤objects，返回保留的和删除的（带位置信息）"""
        kept_objects = []
        deleted_objects = []
        
        for i, (name, obj_type) in enumerate(objects):
            if name in related_items:
                kept_objects.append((name, obj_type))
            else:
                deleted_objects.append((i, f"{name} - {obj_type}"))
        
        return kept_objects, deleted_objects
    
    def filter_init_statements(self, statements: List[str], related_items: Set[str], deleted_fixtures: List[str], deleted_objects: List[Tuple[int, str]]) -> Tuple[List[str], List[str]]:
        """过滤init语句，返回保留的和删除的"""
        kept_statements = []
        deleted_statements = []
        
        # 提取被删除的对象和fixtures的名称
        deleted_names = set()
        for fixture in deleted_fixtures:
            name = fixture.split(' - ')[0].strip()
            deleted_names.add(name)
        for _, obj in deleted_objects:
            name = obj.split(' - ')[0].strip()
            deleted_names.add(name)
        
        for statement in statements:
            # 检查语句中是否包含被删除的对象或fixtures
            contains_deleted = False
            for deleted_name in deleted_names:
                if deleted_name in statement:
                    contains_deleted = True
                    break
            
            if contains_deleted:
                deleted_statements.append(statement)
            else:
                kept_statements.append(statement)
        
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
        report = f"""# BDDL文件修改报告

## 修改概述
根据`:obj_of_interest`字段中的`{obj_of_interest}`，保留了相关项目，删除了其他无关项目。

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
"""
        
        return report
    
    def modify_bddl_file(self, input_file: str, output_file: str = None, report_file: str = None) -> Dict[str, str]:
        """修改BDDL文件的主函数"""
        # 设置默认输出文件名
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_modified.bddl"
        
        if report_file is None:
            base_name = os.path.splitext(input_file)[0]
            report_file = f"{base_name}_deletion_report.md"
        
        # 读取文件
        content = self.read_bddl_file(input_file)
        
        # 提取obj_of_interest
        obj_of_interest = self.extract_obj_of_interest(content)
        if not obj_of_interest:
            raise ValueError("未找到obj_of_interest字段")
        
        # 确定相关项目
        related_items = self.determine_related_items(obj_of_interest)
        
        # 解析各个字段
        fixtures_content = self.extract_section(content, ':fixtures')
        objects_content = self.extract_section(content, ':objects')
        init_content = self.extract_section(content, ':init')
        
        fixtures = self.parse_fixtures(fixtures_content)
        objects = self.parse_objects(objects_content)
        init_statements = self.parse_init_statements(init_content)
        
        # 过滤各个字段
        kept_fixtures, self.deleted_fixtures = self.filter_fixtures(fixtures, related_items)
        kept_objects, self.deleted_objects_positions = self.filter_objects(objects, related_items)
        kept_init, self.deleted_init_statements = self.filter_init_statements(init_statements, related_items, self.deleted_fixtures, self.deleted_objects_positions)
        
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


def main():
    """主函数，提供命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BDDL文件修改器')
    parser.add_argument('input_file', help='输入的BDDL文件路径')
    parser.add_argument('-o', '--output', help='输出的BDDL文件路径')
    parser.add_argument('-r', '--report', help='删除报告文件路径')
    
    args = parser.parse_args()
    
    try:
        modifier = BDDLModifier()
        result = modifier.modify_bddl_file(args.input_file, args.output, args.report)
        
        print("BDDL文件修改完成！")
        print(f"原始文件: {result['original_file']}")
        print(f"修改后文件: {result['modified_file']}")
        print(f"删除报告: {result['report_file']}")
        print(f"目标对象: {result['obj_of_interest']}")
        print(f"被删除的objects位置: {result['deleted_objects_positions']}")
        
    except Exception as e:
        print(f"错误: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())