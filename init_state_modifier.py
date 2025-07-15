#!/usr/bin/env python3
"""
Init State修改器
根据被删除的objects位置修改init_state数组
"""

import numpy as np
from typing import List, Tuple, Union
import json


class InitStateModifier:
    def __init__(self):
        self.objects_per_data_count = 7  # 每个object对应7个数据
        self.objects_start_index = 10    # objects数据从第10列开始
    
    def remove_deleted_objects_data(self, init_state: np.ndarray, deleted_positions: List[int]) -> Tuple[np.ndarray, dict]:
        """
        根据被删除的objects位置删除init_state中对应的数据
        
        Args:
            init_state: 形状为(50, n)的numpy数组
            deleted_positions: 被删除objects的位置列表，例如[0, 1, 2, 3]
        
        Returns:
            Tuple[np.ndarray, dict]: (修改后的数组, 删除信息)
        """
        if init_state.ndim != 2 or init_state.shape[0] != 50:
            raise ValueError(f"init_state必须是形状为(50, n)的数组，当前形状为{init_state.shape}")
        
        if not deleted_positions:
            return init_state.copy(), {"deleted_ranges": [], "original_shape": init_state.shape, "new_shape": init_state.shape}
        
        # 验证删除位置的有效性
        max_objects = (init_state.shape[1] - self.objects_start_index) // self.objects_per_data_count
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
        modified_state = init_state.copy()
        deleted_info = []
        
        for start_col, end_col in deletion_ranges:
            # 记录删除信息
            deleted_data = modified_state[:, start_col:end_col].copy()
            deleted_info.append({
                "range": (start_col, end_col),
                "shape": deleted_data.shape,
                "data_sample": deleted_data[0, :].tolist()  # 保存第一行作为样本
            })
            
            # 删除对应列
            modified_state = np.delete(modified_state, range(start_col, end_col), axis=1)
        
        # 构建返回信息
        result_info = {
            "deleted_ranges": deleted_info,
            "original_shape": init_state.shape,
            "new_shape": modified_state.shape,
            "deleted_positions": sorted(deleted_positions),
            "total_deleted_columns": len(deleted_positions) * self.objects_per_data_count
        }
        
        return modified_state, result_info
    
    def validate_init_state_structure(self, init_state: np.ndarray) -> dict:
        """验证init_state数组的结构"""
        if init_state.ndim != 2:
            return {"valid": False, "error": f"数组必须是2维的，当前维度: {init_state.ndim}"}
        
        if init_state.shape[0] != 50:
            return {"valid": False, "error": f"数组第一维必须是50，当前为: {init_state.shape[0]}"}
        
        if init_state.shape[1] < self.objects_start_index:
            return {"valid": False, "error": f"数组第二维至少需要{self.objects_start_index}列，当前为: {init_state.shape[1]}"}
        
        objects_columns = init_state.shape[1] - self.objects_start_index
        if objects_columns % self.objects_per_data_count != 0:
            return {
                "valid": False, 
                "error": f"objects数据列数({objects_columns})必须是{self.objects_per_data_count}的倍数"
            }
        
        max_objects = objects_columns // self.objects_per_data_count
        
        return {
            "valid": True,
            "total_columns": init_state.shape[1],
            "objects_columns": objects_columns,
            "max_objects_count": max_objects,
            "structure": f"前{self.objects_start_index}列为固定数据，后{objects_columns}列为{max_objects}个objects数据"
        }
    
    def get_object_data_range(self, object_position: int) -> Tuple[int, int]:
        """获取指定object在init_state中对应的列范围"""
        start_col = self.objects_start_index + object_position * self.objects_per_data_count
        end_col = start_col + self.objects_per_data_count
        return start_col, end_col
    
    def preview_deletion(self, init_state: np.ndarray, deleted_positions: List[int]) -> dict:
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
        new_shape = (init_state.shape[0], init_state.shape[1] - total_deleted_columns)
        
        return {
            "original_shape": init_state.shape,
            "new_shape": new_shape,
            "deletion_info": deletion_info,
            "total_deleted_columns": total_deleted_columns,
            "deleted_positions": sorted(deleted_positions)
        }


def create_sample_init_state(num_objects: int = 4) -> np.ndarray:
    """创建一个示例的init_state数组用于测试"""
    total_columns = 10 + num_objects * 7  # 前10列固定 + objects数据
    init_state = np.random.rand(50, total_columns)
    
    # 为了便于识别，给不同的object数据设置不同的值范围
    for i in range(num_objects):
        start_col = 10 + i * 7
        end_col = start_col + 7
        init_state[:, start_col:end_col] = (i + 1) * 10 + np.random.rand(50, 7)
    
    return init_state


def demonstrate_usage():
    """演示使用方法"""
    print("=== Init State修改器演示 ===\n")
    
    # 创建示例数据
    modifier = InitStateModifier()
    init_state = create_sample_init_state(num_objects=4)
    
    print(f"原始init_state形状: {init_state.shape}")
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
    
    return modified_state, result_info


def save_arrays_to_files(original: np.ndarray, modified: np.ndarray, 
                        result_info: dict, prefix: str = "init_state"):
    """保存数组到文件"""
    # 保存numpy数组
    np.save(f"{prefix}_original.npy", original)
    np.save(f"{prefix}_modified.npy", modified)
    
    # 保存结果信息到JSON
    # 将numpy类型转换为Python原生类型以便JSON序列化
    json_info = {}
    for key, value in result_info.items():
        if isinstance(value, np.ndarray):
            json_info[key] = value.tolist()
        elif isinstance(value, tuple):
            json_info[key] = list(value)
        else:
            json_info[key] = value
    
    with open(f"{prefix}_modification_info.json", 'w', encoding='utf-8') as f:
        json.dump(json_info, f, indent=2, ensure_ascii=False)
    
    print(f"文件已保存:")
    print(f"  {prefix}_original.npy - 原始数组")
    print(f"  {prefix}_modified.npy - 修改后数组")
    print(f"  {prefix}_modification_info.json - 修改信息")


if __name__ == "__main__":
    # 演示基本用法
    modified_array, info = demonstrate_usage()
    
    print("\n" + "="*50)
    
    # 保存结果到文件
    original_array = create_sample_init_state(num_objects=4)
    save_arrays_to_files(original_array, modified_array, info)
    
    print(f"\n最终结果：")
    print(f"原始数组形状: {original_array.shape}")
    print(f"修改后数组形状: {modified_array.shape}")
    print(f"删除了 {info['total_deleted_columns']} 列数据")