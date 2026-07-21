#!/usr/bin/env python3
"""
AC 自动机引擎：多模式字符串匹配 + 词边界 + 最长匹配优先。

核心特性：
- 大小写不敏感（匹配时统一 lower()）
- 字母边界（默认）：前后必须是分隔符（非字母）或行首行尾
- 完全边界（strict）：前后必须是非字母字符，即使 pattern 很长
- 最长匹配优先（RAV4 > RAV）
- 单次扫描完成所有规则匹配
- 从后往前替换，避免偏移量错乱

用法：
    rules = {'seat': '', 'amg': 'A.M.G', 'rav4': 'R.A.V.4'}
    strict_rules = {'amg'}  # 手动标记完全边界
    engine = ACEngine(rules, boundary_threshold=6, strict_rules=strict_rules)
    result = engine.replace("Seat Leon 55AMG")
    # result: " Leon 55A.M.G"  (AMG 前的 5 是数字，算边界)
"""

from collections import deque


class ACNode:
    """AC 自动机节点"""
    __slots__ = ('children', 'fail', 'outputs', 'depth')

    def __init__(self):
        self.children = {}   # char -> ACNode
        self.fail = None     # 失败指针
        self.outputs = []    # [(pattern, replacement, pattern_len, is_strict)]
        self.depth = 0       # 节点深度（用于计算匹配位置）


def _is_alpha(char):
    """判断字符是否是字母（包括 Unicode 字母）"""
    return char.isalpha()


class ACEngine:
    """
    AC 自动机引擎。

    Args:
        rules: {source_lower: replacement} 映射
        boundary_threshold: 词边界阈值，≤N 字符的规则启用边界检查
        strict_rules: set of str，手动标记需要完全边界的规则
    """

    def __init__(self, rules, boundary_threshold=6, strict_rules=None):
        self.rules = rules
        self.boundary_threshold = boundary_threshold
        self.strict_rules = strict_rules or set()
        self.root = ACNode()
        self._build()

    def _build(self):
        """构建 AC 自动机"""
        # Step 1: 构建 Trie
        for pattern, replacement in self.rules.items():
            is_strict = pattern in self.strict_rules
            node = self.root
            for char in pattern:
                if char not in node.children:
                    node.children[char] = ACNode()
                    node.children[char].depth = node.depth + 1
                node = node.children[char]
            node.outputs.append((pattern, replacement, len(pattern), is_strict))

        # Step 2: 构建失败指针 (BFS)
        queue = deque()

        # 根节点的直接子节点，fail 指向根
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        while queue:
            current = queue.popleft()

            for char, child in current.children.items():
                # 找 child 的 fail
                fail_node = current.fail
                while fail_node is not None and char not in fail_node.children:
                    fail_node = fail_node.fail

                if fail_node is None:
                    child.fail = self.root
                else:
                    child.fail = fail_node.children[char]

                # 继承 fail 节点的 outputs（关键：这让 AC 自动机能找到所有匹配）
                if child.fail.outputs:
                    child.outputs = child.outputs + child.fail.outputs

                queue.append(child)

    def _needs_boundary(self, pattern, is_strict):
        """判断一个 pattern 是否需要词边界检查"""
        if is_strict:
            return True  # strict 规则永远检查边界
        return len(pattern) <= self.boundary_threshold

    def _is_word_boundary(self, text, start, end):
        """
        字母边界检查：前后必须是分隔符（非字母）或行首行尾。

        分隔符 = 任何非字母字符（数字、空格、标点等）。
        只有字母-字母之间才算"词中"。

        Args:
            text: 完整文本（原始大小写）
            start: 匹配开始位置
            end: 匹配结束位置（exclusive）
        """
        # 左边界：行首或前一个字符不是字母
        left_ok = (start == 0) or (not _is_alpha(text[start - 1]))
        # 右边界：行尾或后一个字符不是字母
        right_ok = (end >= len(text)) or (not _is_alpha(text[end]))

        return left_ok and right_ok

    def find_matches(self, text):
        """
        在文本中查找所有匹配。

        Args:
            text: 输入文本（str）

        Returns:
            list of (start, end, pattern, replacement)
            已按 longest match 去重，按位置排序
        """
        if not text:
            return []

        text_lower = text.lower()
        all_matches = []  # (start, end, pattern, replacement, priority)

        state = self.root

        for i, char in enumerate(text_lower):
            # 沿 fail 指针跳转，直到找到匹配或回到根
            while state is not None and char not in state.children:
                state = state.fail

            if state is None:
                state = self.root
                continue

            state = state.children[char]

            # 收集当前节点的所有 outputs
            for pattern, replacement, pattern_len, is_strict in state.outputs:
                start = i - pattern_len + 1
                end = i + 1

                # 边界检查
                if self._needs_boundary(pattern, is_strict):
                    if not self._is_word_boundary(text, start, end):
                        continue

                # 优先级 = pattern 长度（越长越优先）
                all_matches.append((start, end, pattern, replacement, pattern_len))

        if not all_matches:
            return []

        # 去重：最长匹配优先，同长度取先出现的
        # 按 start 排序，然后按长度降序（保证最长优先）
        all_matches.sort(key=lambda m: (m[0], -m[4]))

        # 过滤重叠：贪心选择最长匹配
        selected = []
        last_end = -1

        for start, end, pattern, replacement, _ in all_matches:
            if start >= last_end:
                selected.append((start, end, pattern, replacement))
                last_end = end
            # 如果重叠但当前匹配更长，替换上一个
            elif selected and start < last_end:
                prev_start, prev_end, prev_pattern, prev_replacement = selected[-1]
                if (end - start) > (prev_end - prev_start):
                    selected[-1] = (start, end, pattern, replacement)
                    last_end = end

        return selected

    def replace(self, text):
        """
        执行替换。

        Args:
            text: 输入文本（str）

        Returns:
            str: 替换后的文本
        """
        matches = self.find_matches(text)

        if not matches:
            return text

        # 从后往前替换，避免偏移量错乱
        result = text
        for start, end, pattern, replacement in reversed(matches):
            result = result[:start] + replacement + result[end:]

        return result

    def match_and_replace(self, text):
        """
        查找匹配并返回详细信息 + 替换结果。

        Returns:
            dict: {
                'original': 原始文本,
                'replaced': 替换后文本,
                'matches': [(start, end, pattern, replacement), ...],
                'changed': 是否有替换发生
            }
        """
        matches = self.find_matches(text)
        replaced = self.replace(text)

        return {
            'original': text,
            'replaced': replaced,
            'matches': matches,
            'changed': replaced != text
        }


def create_engine(rules, boundary_threshold=6, strict_rules=None):
    """便捷函数：创建 AC 引擎"""
    return ACEngine(rules, boundary_threshold, strict_rules)


if __name__ == "__main__":
    # 测试：字母边界 + strict 完全边界
    test_rules = {
        'seat': '',
        'leon': 'L.e.o.n',
        'tsi': 'T.S.i',
        'mercedes-benz': '',
        'mercedes benz': '',
        'ge': 'G.E',
        'rav4': 'R.A.V.4',
        'rav': 'R.A.V',
        '4motion': '4.M.o.t.i.o.n',
        '4 motion': '4.M.o.t.i.o.n',
        'amg': 'A.M.G',
    }
    strict_rules = {'amg'}  # AMG 标记为完全边界

    engine = ACEngine(test_rules, boundary_threshold=6, strict_rules=strict_rules)

    test_cases = [
        ("Seat Leon 1.4 TSI", "Seat 删除, Leon 替换, TSI 替换"),
        ("Seattle", "短词在词中，不应匹配"),
        ("Affordable Seat", "Seat 有边界，应删除"),
        ("RAV4 Adventure", "RAV4 优先于 RAV"),
        ("Mercedes-Benz C200", "长词直接匹配删除"),
        ("4Motion AWD", "无空格变体"),
        ("4 Motion AWD", "有空格变体"),
        ("55AMG Kompressor", "AMG strict：数字算边界，应匹配"),
        ("SL55AMG", "AMG strict：前是字母，不应匹配"),
        ("AMG GT", "AMG strict：行首 + 空格，应匹配"),
    ]

    print("AC 引擎测试")
    print("=" * 60)
    for text, note in test_cases:
        result = engine.replace(text)
        matches = engine.find_matches(text)
        print(f"\n输入: \"{text}\"")
        print(f"输出: \"{result}\"")
        print(f"匹配: {[(m[2], m[0], m[1]) for m in matches]}")
        print(f"说明: {note}")
