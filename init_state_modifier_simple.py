#!/usr/bin/env python3
"""
Init State修改器 - 纯Python版本
根据被删除的objects位置修改init_state数组（不依赖numpy）
"""

from typing import List, Tuple, Union, Dict
import json


class InitStateModifierSimple:
    def __init__(self):
        self.objects_per_data_count = 7  # 每个object对应7个数据
        self.objects_start_index = 10    # objects数据从第10列开始
    
    def remove_deleted_objects_data(self, init_state: List[List[float]], deleted_positions: List[int]) -> Tuple[List[List[float]], Dict]:
        """
        根据被删除的objects位置删除init_state中对应的数据
        
        Args:
            init_state: 形状为(50, n)的二维列表
            deleted_positions: 被删除objects的位置列表，例如[0, 1, 2, 3]
        
        Returns:
            Tuple[List[List[float]], Dict]: (修改后的数组, 删除信息)
        """
        if len(init_state) != 50:
            raise ValueError(f"init_state必须有50行，当前行数为{len(init_state)}")
        
        if not init_state or len(init_state[0]) < self.objects_start_index:
            raise ValueError(f"init_state列数至少需要{self.objects_start_index}，当前为{len(init_state[0]) if init_state else 0}")
        
        original_shape = (len(init_state), len(init_state[0]))
        
        if not deleted_positions:
            return [row[:] for row in init_state], {
                "deleted_ranges": [], 
                "original_shape": original_shape, 
                "new_shape": original_shape
            }
        
        # 验证删除位置的有效性
        max_objects = (len(init_state[0]) - self.objects_start_index) // self.objects_per_data_count
        for pos in deleted_positions:
            if pos < 0 or pos >= max_objects:
                raise ValueError(f"删除位置{pos}超出有效范围[0, {max_objects-1}]")
        
        # 计算需要删除的列索引范围
        deletion_ranges = []
        for pos in deleted_positions:
            start_col = self.objects_start_index + pos * self.objects_per_data_count
            end_col = start_col + self.objects_per_data_count
            deletion_ranges.append((start_col, end_col))
        
        # 按删除位置从大到小排序，避免索引变化问题
        deletion_ranges.sort(key=lambda x: x[0], reverse=True)
        
        # 执行删除操作
        modified_state = [row[:] for row in init_state]  # 深拷贝
        deleted_info = []
        
        for start_col, end_col in deletion_ranges:
            # 记录删除信息
            deleted_data = [row[start_col:end_col] for row in modified_state]
            deleted_info.append({
                "range": (start_col, end_col),
                "shape": (len(deleted_data), len(deleted_data[0]) if deleted_data else 0),
                "data_sample": deleted_data[0] if deleted_data else []  # 保存第一行作为样本
            })
            
            # 删除对应列
            for row in modified_state:
                del row[start_col:end_col]
        
        new_shape = (len(modified_state), len(modified_state[0]) if modified_state else 0)
        
        # 构建返回信息
        result_info = {
            "deleted_ranges": deleted_info,
            "original_shape": original_shape,
            "new_shape": new_shape,
            "deleted_positions": sorted(deleted_positions),
            "total_deleted_columns": len(deleted_positions) * self.objects_per_data_count
        }
        
        return modified_state, result_info
    
    def validate_init_state_structure(self, init_state: List[List[float]]) -> Dict:
        """验证init_state数组的结构"""
        if not init_state:
            return {"valid": False, "error": "数组为空"}
        
        if len(init_state) != 50:
            return {"valid": False, "error": f"数组必须有50行，当前行数: {len(init_state)}"}
        
        row_length = len(init_state[0])
        if row_length < self.objects_start_index:
            return {"valid": False, "error": f"数组列数至少需要{self.objects_start_index}，当前为: {row_length}"}
        
        # 检查所有行长度是否一致
        for i, row in enumerate(init_state):
            if len(row) != row_length:
                return {"valid": False, "error": f"第{i}行长度不一致: 预期{row_length}，实际{len(row)}"}
        
        objects_columns = row_length - self.objects_start_index
        if objects_columns % self.objects_per_data_count != 0:
            return {
                "valid": False, 
                "error": f"objects数据列数({objects_columns})必须是{self.objects_per_data_count}的倍数"
            }
        
        max_objects = objects_columns // self.objects_per_data_count
        
        return {
            "valid": True,
            "total_columns": row_length,
            "objects_columns": objects_columns,
            "max_objects_count": max_objects,
            "structure": f"前{self.objects_start_index}列为固定数据，后{objects_columns}列为{max_objects}个objects数据"
        }
    
    def get_object_data_range(self, object_position: int) -> Tuple[int, int]:
        """获取指定object在init_state中对应的列范围"""
        start_col = self.objects_start_index + object_position * self.objects_per_data_count
        end_col = start_col + self.objects_per_data_count
        return start_col, end_col
    
    def preview_deletion(self, init_state: List[List[float]], deleted_positions: List[int]) -> Dict:
        """预览删除操作，不实际执行删除"""
        validation = self.validate_init_state_structure(init_state)
        if not validation["valid"]:
            return {"error": validation["error"]}
        
        max_objects = validation["max_objects_count"]
        
        # 验证删除位置
        invalid_positions = [pos for pos in deleted_positions if pos < 0 or pos >= max_objects]
        if invalid_positions:
            return {"error": f"无效的删除位置: {invalid_positions}，有效范围: [0, {max_objects-1}]"}
        
        # 计算删除信息
        deletion_info = []
        for pos in sorted(deleted_positions):
            start_col, end_col = self.get_object_data_range(pos)
            deletion_info.append({
                "object_position": pos,
                "column_range": (start_col, end_col),
                "columns_to_delete": list(range(start_col, end_col))
            })
        
        total_deleted_columns = len(deleted_positions) * self.objects_per_data_count
        original_shape = (len(init_state), len(init_state[0]))
        new_shape = (original_shape[0], original_shape[1] - total_deleted_columns)
        
        return {
            "original_shape": original_shape,
            "new_shape": new_shape,
            "deletion_info": deletion_info,
            "total_deleted_columns": total_deleted_columns,
            "deleted_positions": sorted(deleted_positions)
        }


def create_sample_init_state(num_objects: int = 4) -> List[List[float]]:
    """创建一个示例的init_state数组用于测试"""
    import random
    
    total_columns = 10 + num_objects * 7  # 前10列固定 + objects数据
    init_state = []
    
    for row in range(50):
        row_data = []
        # 前10列固定数据
        for col in range(10):
            row_data.append(random.random())
        
        # objects数据
        for obj_idx in range(num_objects):
            for col in range(7):
                # 为了便于识别，给不同的object数据设置不同的值范围
                value = (obj_idx + 1) * 10 + random.random()
                row_data.append(value)
        
        init_state.append(row_data)
    
    return init_state


def save_list_to_json(data: List[List[float]], filename: str):
    """保存二维列表到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_list_from_json(filename: str) -> List[List[float]]:
    """从JSON文件加载二维列表"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def demonstrate_usage():
    """演示使用方法"""
    print("=== Init State修改器演示（纯Python版本）===\n")
    
    # 创建示例数据
    modifier = InitStateModifierSimple()
    init_state = create_sample_init_state(num_objects=4)
    
    print(f"原始init_state形状: {len(init_state)} x {len(init_state[0])}")
    print(f"前10列为固定数据，后28列为4个objects数据(每个7列)")
    print()
    
    # 验证结构
    validation = modifier.validate_init_state_structure(init_state)
    print("结构验证:")
    print(f"  有效: {validation['valid']}")
    if validation['valid']:
        print(f"  {validation['structure']}")
        print(f"  最大objects数量: {validation['max_objects_count']}")
    print()
    
    # 预览删除操作
    deleted_positions = [0, 1, 2, 3]  # 删除所有objects
    preview = modifier.preview_deletion(init_state, deleted_positions)
    print("删除预览:")
    print(f"  删除positions: {preview['deleted_positions']}")
    print(f"  原始形状: {preview['original_shape']}")
    print(f"  删除后形状: {preview['new_shape']}")
    print(f"  总删除列数: {preview['total_deleted_columns']}")
    print()
    
    for info in preview['deletion_info']:
        print(f"  Object {info['object_position']}: 删除列 {info['column_range'][0]}-{info['column_range'][1]-1}")
    print()
    
    # 执行删除
    modified_state, result_info = modifier.remove_deleted_objects_data(init_state, deleted_positions)
    
    print("删除结果:")
    print(f"  修改后形状: {result_info['new_shape']}")
    print(f"  删除的positions: {result_info['deleted_positions']}")
    print(f"  总删除列数: {result_info['total_deleted_columns']}")
    print()
    
    # 显示删除的详细信息
    print("删除详情:")
    for i, info in enumerate(result_info['deleted_ranges']):
        print(f"  删除范围 {i+1}: 列{info['range'][0]}-{info['range'][1]-1}")
        print(f"    形状: {info['shape']}")
        print(f"    样本数据: {info['data_sample'][:3]}...")  # 只显示前3个数据
    print()
    
    # 保存结果
    save_list_to_json(init_state, "original_init_state.json")
    save_list_to_json(modified_state, "modified_init_state.json")
    
    with open("init_state_modification_info.json", 'w', encoding='utf-8') as f:
        json.dump(result_info, f, indent=2, ensure_ascii=False)
    
    print("文件已保存:")
    print("  original_init_state.json - 原始数组")
    print("  modified_init_state.json - 修改后数组")
    print("  init_state_modification_info.json - 修改信息")
    
    return modified_state, result_info


if __name__ == "__main__":
    # 演示基本用法
    modified_array, info = demonstrate_usage()
    
    print("\n" + "="*50)
    print(f"最终结果：")
    print(f"原始数组形状: {info['original_shape']}")
    print(f"修改后数组形状: {info['new_shape']}")
    print(f"删除了 {info['total_deleted_columns']} 列数据")