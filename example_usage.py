#!/usr/bin/env python3
"""
BDDL修改器使用示例
演示如何使用BDDLModifier类来修改BDDL文件
"""

from bddl_modifier import BDDLModifier
import os


def example_usage():
    """使用示例"""
    print("=== BDDL文件修改器使用示例 ===\n")
    
    # 创建修改器实例
    modifier = BDDLModifier()
    
    # 输入文件路径
    input_file = "problem.bddl"
    
    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件 {input_file}")
        return
    
    try:
        # 修改BDDL文件
        print(f"正在处理文件: {input_file}")
        result = modifier.modify_bddl_file(
            input_file=input_file,
            output_file="problem_auto_modified.bddl",
            report_file="auto_deletion_report.md"
        )
        
        # 打印结果
        print("✅ 修改完成！")
        print("\n📁 文件信息:")
        print(f"  原始文件: {result['original_file']}")
        print(f"  修改后文件: {result['modified_file']}")
        print(f"  删除报告: {result['report_file']}")
        
        print(f"\n🎯 目标对象: {result['obj_of_interest']}")
        
        print(f"\n📊 删除统计:")
        print(f"  删除的fixtures数量: {len(result['deleted_fixtures'])}")
        print(f"  删除的objects数量: {len(result['deleted_objects_positions'])}")
        print(f"  删除的init语句数量: {len(result['deleted_init_statements'])}")
        
        if result['deleted_objects_positions']:
            print(f"\n🗑️ 被删除的objects位置: {result['deleted_objects_positions']}")
            print("📝 被删除的objects详情:")
            for pos, obj in result['deleted_objects_details']:
                print(f"    位置 {pos}: {obj}")
        
        print(f"\n📄 详细删除报告已保存到: {result['report_file']}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


def batch_processing_example():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===\n")
    
    # 假设有多个BDDL文件需要处理
    bddl_files = ["problem.bddl"]  # 可以添加更多文件
    
    modifier = BDDLModifier()
    
    for file_path in bddl_files:
        if os.path.exists(file_path):
            try:
                print(f"处理文件: {file_path}")
                result = modifier.modify_bddl_file(file_path)
                print(f"✅ {file_path} 处理完成")
                print(f"   输出: {result['modified_file']}")
                print(f"   删除的objects位置: {result['deleted_objects_positions']}")
                print()
            except Exception as e:
                print(f"❌ 处理 {file_path} 时出错: {e}\n")
        else:
            print(f"⚠️  文件不存在: {file_path}\n")


def programmatic_usage_example():
    """编程式使用示例"""
    print("\n=== 编程式使用示例 ===\n")
    
    modifier = BDDLModifier()
    
    try:
        # 读取文件
        content = modifier.read_bddl_file("problem.bddl")
        print("✅ 文件读取成功")
        
        # 提取关键信息
        obj_of_interest = modifier.extract_obj_of_interest(content)
        print(f"🎯 obj_of_interest: {obj_of_interest}")
        
        # 确定相关项目
        related_items = modifier.determine_related_items(obj_of_interest)
        print(f"🔗 相关项目: {related_items}")
        
        # 解析各个字段
        fixtures_content = modifier.extract_section(content, ':fixtures')
        objects_content = modifier.extract_section(content, ':objects')
        
        fixtures = modifier.parse_fixtures(fixtures_content)
        objects = modifier.parse_objects(objects_content)
        
        print(f"🏗️  原始fixtures: {len(fixtures)}个")
        print(f"📦 原始objects: {len(objects)}个")
        
        # 过滤
        kept_fixtures, deleted_fixtures = modifier.filter_fixtures(fixtures, related_items)
        kept_objects, deleted_objects = modifier.filter_objects(objects, related_items)
        
        print(f"✅ 保留fixtures: {len(kept_fixtures)}个")
        print(f"❌ 删除fixtures: {len(deleted_fixtures)}个")
        print(f"✅ 保留objects: {len(kept_objects)}个")
        print(f"❌ 删除objects: {len(deleted_objects)}个")
        
        # 显示删除的objects位置
        if deleted_objects:
            print("🗑️ 删除的objects位置信息:")
            for pos, obj in deleted_objects:
                print(f"    位置 {pos}: {obj}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    example_usage()
    batch_processing_example()
    programmatic_usage_example()