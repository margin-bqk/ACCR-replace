目标是做一个**高性能文本匹配库**，支持「AC 自动机 + 正则表达式 + 流式（streaming）输入」，并通过 Cython 加速。

## 🧠 一、项目定位概述

这是一个**面向大规模文本扫描与实时流检测**的 Python 库，支持：

- 多模式匹配（AC 自动机）

- 正则匹配（兼容 `re` 语法）

- 流式增量输入（支持日志流、文件流等）

- Python 封装友好，可直接 import 使用

- 性能目标：接近 C 实现的速度（>10x Python）

#### ⚙️ 二、整体技术栈

| 模块          | 技术栈                                              | 用途                                                  |
| ----------- | ------------------------------------------------ | --------------------------------------------------- |
| **算法层**     | Cython（或 C/C++ + Cython 接口）                      | 实现 AC 自动机、正则引擎整合、高性能匹配逻辑                            |
| **流式输入层**   | Python generator + ring buffer（或 memoryview）     | 支持 streaming 输入，增量匹配                                |
| **正则支持层**   | PCRE2 或 Python 内置 `re` 封装                        | 将正则编译成状态机，与 AC 输出协同                                 |
| **封装层**     | Python class（带 context 管理）                       | 提供易用的 API，如 `matcher.feed(chunk)`、`matcher.match()` |
| **构建工具**    | `setuptools` + `pyproject.toml` + `Cython.Build` | 自动编译并打包                                             |
| **测试与性能验证** | `pytest` + `timeit` + 对照 pure Python 实现          | 验证正确性与性能提升                                          |
| **可选扩展**    | `mmap` / `asyncio` / `uvloop`                    | 支持大文件扫描与异步流                                         |

## 🧩 三、输入输出设计（API 视角）

### 核心类：`Matcher`

```python
from fastmatcher import Matcher

# 初始化
matcher = Matcher(
    patterns=["apple", "banana", "orange"],
    regex=[r"\d{4}-\d{2}-\d{2}"],
    streaming=True
)

# 流式输入
for chunk in read_file_stream("log.txt"):
    for match in matcher.feed(chunk):
        print(match)
```

### 输入

- **AC 模式表**：`patterns: list[str]`

- **正则表达式**：`regex: list[str]`

- **流模式控制**：`streaming: bool`（True 则保留状态）

### 输出

- `feed(chunk)` 返回一个匹配结果列表

每个结果是一个结构体（或 namedtuple）：

```python
Match(
    type="ac" | "regex",
    pattern="apple",
    start=1024,
    end=1029,
    context="...附近文本..."
)
```

## 🧮 四、Cython 实现层结构（概念级）

fastmatcher/
 ├── __init__.py
 ├── matcher.pyx         # 主逻辑封装
 ├── ac_automaton.pxd    # AC 自动机定义（结构体与方法）
 ├── ac_automaton.pyx    # AC 自动机实现（构建、转移、匹配）
 ├── regex_engine.pyx    # 正则编译与匹配（可能用 C 接口调用 PCRE）
 ├── buffer.pxd/.pyx     # 环形缓冲区与流状态管理
 ├── utils.pxd/.pyx      # 辅助函数
 ├── setup.py            # 编译入口
 └── tests/
      └── test_matcher.py

核心逻辑大致如下：

```cpp
cdef class ACAutomaton:
    cdef dict goto
    cdef dict output
    cdef dict fail
    def build(self, patterns): ...
    def search(self, text): ...

cdef class Matcher:
    cdef ACAutomaton ac
    cdef list regex_engines
    cdef bytes buffer
    def feed(self, bytes chunk): ...

```

## 🚀 五、可扩展方向

| 功能           | 说明                                         |
| ------------ | ------------------------------------------ |
| **多线程/异步流**  | 使用 Python 的 `asyncio` 或者 Cython 的 nogil 模式 |
| **GPU/多核并行** | 基于 text chunk 分割后并行匹配                      |
| **语义层过滤**    | 匹配后使用 LLM 或 embedding 判断上下文                |
| **增量字典**     | 运行时追加/删除 pattern，不必重建整个 AC 树               |
| **多语言绑定**    | 未来支持 Rust 或 Node.js 的 binding              |