# BDDL文件修改器

一个用于根据`obj_of_interest`字段自动修改BDDL文件的Python工具。该工具可以保留与目标对象相关的项目，删除无关项目，并生成详细的删除报告。

## 功能特性

- ✅ 自动解析BDDL文件结构
- ✅ 根据`obj_of_interest`确定相关项目
- ✅ 智能过滤`:fixtures`、`:objects`和`:init`字段
- ✅ 保留`main_table`（始终保留）
- ✅ 记录被删除项目的详细位置信息
- ✅ 生成修改后的BDDL文件
- ✅ 生成详细的删除报告
- ✅ 支持命令行和编程接口

## 文件结构

```
.
├── bddl_modifier.py          # 主要的修改器类
├── example_usage.py          # 使用示例
├── problem.bddl              # 示例输入文件
├── problem_fixed.bddl        # 修改后的文件
├── fixed_report.md           # 删除报告
└── README_bddl_modifier.md   # 本文档
```

## 安装要求

- Python 3.6+
- 标准库（无需额外依赖）

## 使用方法

### 1. 命令行使用

```bash
# 基本使用
python3 bddl_modifier.py input_file.bddl

# 指定输出文件
python3 bddl_modifier.py input_file.bddl -o output_file.bddl

# 指定报告文件
python3 bddl_modifier.py input_file.bddl -r report.md

# 完整参数
python3 bddl_modifier.py input_file.bddl -o output_file.bddl -r report.md
```

### 2. 编程接口使用

```python
from bddl_modifier import BDDLModifier

# 创建修改器实例
modifier = BDDLModifier()

# 修改文件
result = modifier.modify_bddl_file(
    input_file="problem.bddl",
    output_file="modified.bddl",  # 可选
    report_file="report.md"       # 可选
)

# 查看结果
print(f"修改后文件: {result['modified_file']}")
print(f"被删除的objects位置: {result['deleted_objects_positions']}")
```

### 3. 批量处理

```python
from bddl_modifier import BDDLModifier
import os

modifier = BDDLModifier()
bddl_files = ["file1.bddl", "file2.bddl", "file3.bddl"]

for file_path in bddl_files:
    if os.path.exists(file_path):
        result = modifier.modify_bddl_file(file_path)
        print(f"处理完成: {result['modified_file']}")
```

## 工作原理

### 1. 解析阶段
- 读取BDDL文件内容
- 提取`obj_of_interest`字段值
- 解析`:fixtures`、`:objects`、`:init`字段

### 2. 过滤阶段
- 根据`obj_of_interest`确定相关项目
- 始终保留`main_table`
- 过滤出需要保留和删除的项目

### 3. 生成阶段
- 生成修改后的BDDL文件
- 记录删除项目的位置信息
- 创建详细的删除报告

## 示例

### 输入文件 (problem.bddl)
```lisp
(:obj_of_interest
  wooden_cabinet_1_middle_region
)

(:fixtures
  main_table - table
  wooden_cabinet_1 - wooden_cabinet
  flat_stove_1 - flat_stove
  wine_rack_1 - wine_rack
)

(:objects
  akita_black_bowl_1 - akita_black_bowl
  cream_cheese_1 - cream_cheese
  wine_bottle_1 - wine_bottle
  plate_1 - plate
)
```

### 输出结果

**修改后的文件:**
```lisp
(:fixtures
  main_table - table
  wooden_cabinet_1 - wooden_cabinet
)

(:objects
  
)

(:init
  (On wooden_cabinet_1 main_table_cabinet_region)
)
```

**删除的objects位置:**
- 位置 0: `akita_black_bowl_1 - akita_black_bowl`
- 位置 1: `cream_cheese_1 - cream_cheese`
- 位置 2: `wine_bottle_1 - wine_bottle`
- 位置 3: `plate_1 - plate`

## API参考

### BDDLModifier类

#### 主要方法

- `modify_bddl_file(input_file, output_file=None, report_file=None)`: 修改BDDL文件的主函数
- `read_bddl_file(file_path)`: 读取BDDL文件
- `extract_obj_of_interest(content)`: 提取obj_of_interest字段
- `determine_related_items(obj_of_interest)`: 确定相关项目

#### 返回值结构

```python
{
    'original_file': '/path/to/original.bddl',
    'modified_file': '/path/to/modified.bddl',
    'report_file': '/path/to/report.md',
    'obj_of_interest': 'wooden_cabinet_1_middle_region',
    'deleted_objects_positions': [0, 1, 2, 3],
    'deleted_objects_details': [(0, 'akita_black_bowl_1 - akita_black_bowl'), ...],
    'deleted_fixtures': ['flat_stove_1 - flat_stove', ...],
    'deleted_init_statements': ['(On wine_bottle_1 main_table_wine_bottle_region)', ...]
}
```

## 注意事项

1. **保留规则**: 始终保留`main_table`和与`obj_of_interest`相关的项目
2. **字段范围**: 只修改`:fixtures`、`:objects`和`:init`字段，其他字段保持不变
3. **位置记录**: 准确记录被删除项目在原始`:objects`字段中的位置（从0开始）
4. **文件编码**: 使用UTF-8编码读写文件

## 错误处理

- 文件不存在: 抛出`FileNotFoundError`
- 缺少`obj_of_interest`字段: 抛出`ValueError`
- 文件读写错误: 抛出相应的IO异常

## 运行示例

```bash
# 运行示例程序
python3 example_usage.py
```

这将展示三种不同的使用方式：
1. 基本使用示例
2. 批量处理示例
3. 编程式使用示例

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。