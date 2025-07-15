# BDDL文件和Init State数组修改器

根据您的需求，我已经开发了一套完整的工具来处理BDDL文件和init_state数组的修改。

## 🎯 核心功能

✅ **BDDL文件修改**：根据`:obj_of_interest`字段自动过滤相关项目  
✅ **Init State修改**：根据删除的objects位置删除对应的数组数据  
✅ **位置记录**：准确记录被删除项在`:objects`字段中的位置  
✅ **数据一致性**：确保BDDL文件和init_state数组的修改保持一致  
✅ **详细报告**：生成完整的修改报告和统计信息  

## 📦 文件结构

```
.
├── bddl_modifier.py                    # BDDL文件修改器
├── init_state_modifier_simple.py      # Init State修改器（纯Python版本）
├── integrated_modifier_simple.py      # 整合修改器（推荐使用）
├── problem.bddl                        # 示例BDDL文件
├── README_final.md                     # 本文档
└── example_usage.py                    # 使用示例
```

## 🚀 快速开始

### 方法一：一键整合处理（推荐）

```python
from integrated_modifier_simple import IntegratedModifierSimple
from init_state_modifier_simple import create_sample_init_state

# 1. 准备数据
bddl_file = "your_file.bddl"  # 你的BDDL文件
init_state = your_init_state_data  # 你的init_state数据 (50×n的二维列表)

# 2. 一键处理
modifier = IntegratedModifierSimple()
result = modifier.process_bddl_and_init_state(
    bddl_file=bddl_file,
    init_state=init_state,
    output_bddl="modified_file.bddl",
    output_init_state="modified_init_state.json"
)

# 3. 查看结果
print(f"删除的objects位置: {result['deleted_objects_positions']}")
print(f"修改后的文件: {result['modified_bddl_file']}")
print(f"修改后的init_state: {result['modified_init_state_file']}")
```

### 方法二：分步处理

```python
from bddl_modifier import BDDLModifier
from init_state_modifier_simple import InitStateModifierSimple

# 1. 处理BDDL文件
bddl_modifier = BDDLModifier()
bddl_result = bddl_modifier.modify_bddl_file("your_file.bddl")
deleted_positions = bddl_result['deleted_objects_positions']

# 2. 处理init_state数组
init_modifier = InitStateModifierSimple()
modified_init_state, info = init_modifier.remove_deleted_objects_data(
    your_init_state, deleted_positions
)

# 3. 保存结果
from init_state_modifier_simple import save_list_to_json
save_list_to_json(modified_init_state, "modified_init_state.json")
```

## 📋 详细说明

### Init State数组结构要求

您的init_state数组必须满足以下结构：

- **形状**：`(50, n)` - 50行，n列
- **前10列**：固定数据（始终保留）
- **第10列开始**：objects数据，每个object占7列
- **对应关系**：init_state[:, 10:]与BDDL文件中的`:objects`字段顺序对应

### 删除规则

当删除BDDL文件中第i个object时：
- **删除列范围**：`init_state[:, 10+i*7:10+(i+1)*7]`
- **后续数据前移**：删除后的数据会自动前移，保持连续性

### 示例说明

**原始数据：**
```
:objects字段: [obj0, obj1, obj2, obj3]
init_state形状: (50, 38)  # 前10列固定 + 4个object×7列 = 38列
```

**删除obj0, obj1, obj2, obj3后：**
```
:objects字段: []
init_state形状: (50, 10)  # 只保留前10列固定数据
删除的位置: [0, 1, 2, 3]
删除的列范围: 
  - obj0: 第10-16列
  - obj1: 第17-23列  
  - obj2: 第24-30列
  - obj3: 第31-37列
```

## 🧪 运行测试

```bash
# 测试init_state修改器
python3 init_state_modifier_simple.py

# 测试整合修改器
python3 integrated_modifier_simple.py

# 测试BDDL修改器
python3 example_usage.py
```

## 📊 输出文件

运行完成后，您将得到以下文件：

1. **修改后的BDDL文件** (`*_modified.bddl`)
2. **修改后的init_state** (`*_modified.json`)
3. **BDDL修改报告** (`*_report.md`)
4. **整合修改报告** (`*_integrated_report.md`)

## 💾 数据加载

### 加载修改后的init_state

```python
import json

# 从JSON文件加载
with open('modified_init_state.json', 'r') as f:
    modified_init_state = json.load(f)

print(f"修改后形状: {len(modified_init_state)} x {len(modified_init_state[0])}")
```

### 如果您有numpy数组

```python
# 如果您的原始数据是numpy数组
import numpy as np

# 转换为列表格式
your_numpy_array = np.random.rand(50, 38)
init_state_list = your_numpy_array.tolist()

# 处理后转换回numpy数组
modified_array = np.array(modified_init_state)
```

## 🔧 自定义配置

您可以修改以下参数来适应不同的需求：

```python
class InitStateModifierSimple:
    def __init__(self):
        self.objects_per_data_count = 7  # 每个object对应的数据列数
        self.objects_start_index = 10    # objects数据开始的列索引
```

## ⚠️ 注意事项

1. **数据格式**：init_state必须是50×n的二维列表
2. **对应关系**：确保init_state的objects数据与BDDL文件中的`:objects`字段顺序一致
3. **备份数据**：建议在处理前备份原始数据
4. **依赖要求**：本工具使用纯Python实现，无需额外依赖

## 🐛 错误处理

常见错误及解决方案：

- **"init_state必须有50行"**：检查您的数组行数
- **"删除位置超出有效范围"**：init_state中的objects数量少于BDDL中的数量
- **"数组列数不一致"**：确保init_state的每一行长度相同

## 📝 完整示例

以下是一个完整的使用示例：

```python
#!/usr/bin/env python3

from integrated_modifier_simple import IntegratedModifierSimple
from init_state_modifier_simple import create_sample_init_state

def main():
    # 创建示例数据（替换为您的实际数据）
    bddl_file = "problem.bddl"
    init_state = create_sample_init_state(num_objects=4)
    
    print(f"原始init_state形状: {len(init_state)} x {len(init_state[0])}")
    
    # 处理数据
    modifier = IntegratedModifierSimple()
    result = modifier.process_bddl_and_init_state(
        bddl_file=bddl_file,
        init_state=init_state
    )
    
    # 显示结果
    print("\n处理结果:")
    print(f"删除的objects位置: {result['deleted_objects_positions']}")
    print(f"原始形状: {result['original_init_state_shape']}")
    print(f"修改后形状: {result['modified_init_state_shape']}")
    print(f"删除了 {result['summary']['deleted_init_state_columns']} 列数据")
    
    return result

if __name__ == "__main__":
    result = main()
```

## 📞 支持

如果您在使用过程中遇到问题，请检查：

1. 输入数据是否符合格式要求
2. BDDL文件是否包含`:obj_of_interest`字段
3. init_state数组的结构是否正确

工具已经过充分测试，能够正确处理您的需求：根据`:objects`字段中被删除项的位置，删除init_state数组中对应的数据，并保持数据的连续性。