#!/usr/bin/env python3
"""
规则清洗器：加载 Excel 规则表，合并链式依赖和大小写冲突。
输出干净的 {source_lower: replacement} 映射，供 AC 自动机使用。

用法：
    loader = RuleLoader("rules.xlsx")
    rules = loader.load()  # {source_lower: replacement}
    loader.report()        # 打印清洗报告
"""

import openpyxl
from collections import defaultdict


class RuleLoader:
    """加载并清洗替换规则"""

    def __init__(self, rules_path, sheet_name="Sheet1", src_col=1, dst_col=2, strict_col=3):
        """
        Args:
            rules_path: 规则 Excel 文件路径
            sheet_name: 工作表名
            src_col: 源词列号 (1-based)
            dst_col: 替换词列号 (1-based)
            strict_col: 完全边界标记列号 (1-based)，C 列写 "strict" 则启用完全边界
        """
        self.rules_path = rules_path
        self.sheet_name = sheet_name
        self.src_col = src_col
        self.dst_col = dst_col
        self.strict_col = strict_col

        # 原始规则
        self.raw_rules = []  # [{row, src, dst, is_delete, is_strict}]
        # 清洗后的规则
        self.clean_rules = {}  # {src_lower: replacement}
        # 完全边界规则集合
        self.strict_rules = set()  # {src_lower}
        # 清洗日志
        self.chain_merges = []  # 链式合并记录
        self.case_merges = []  # 大小写冲突合并记录
        self.manual_review = []  # 需要人工确认的

    def _read_excel(self):
        """读取 Excel 规则表"""
        wb = openpyxl.load_workbook(self.rules_path)
        ws = wb[self.sheet_name]

        for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            src = row[self.src_col - 1] if len(row) >= self.src_col else None
            dst = row[self.dst_col - 1] if len(row) >= self.dst_col else None
            strict = row[self.strict_col - 1] if len(row) >= self.strict_col else None

            if src is None:
                continue

            src = str(src).strip()
            if not src:
                continue

            is_strict = strict is not None and str(strict).strip().lower() == 'strict'

            self.raw_rules.append({
                'row': i,
                'src': src,
                'dst': str(dst).strip() if dst else '',
                'is_delete': dst is None or str(dst).strip() == '',
                'is_strict': is_strict
            })

        wb.close()

    def _build_chain_map(self):
        """
        构建链式映射：找到所有 A→B, B→C 形式的链。
        只有当规则 A 的替换目标恰好是另一条规则 B 的源词时，才构成链。

        Returns:
            dict: {链起点src_lower: 最终替换目标}
        """
        # src_lower -> rule (只保留第一条非删除规则用于查链)
        src_map = {}
        for r in self.raw_rules:
            key = r['src'].lower()
            if key not in src_map:
                src_map[key] = r

        # 替换图：src_lower -> dst (仅限非删除规则)
        replace_graph = {}
        for r in self.raw_rules:
            if not r['is_delete']:
                replace_graph[r['src'].lower()] = r['dst']

        # 追踪每条规则是否处于链中
        chain_end = {}  # {链起点src_lower: final_dst}

        for r in self.raw_rules:
            start = r['src'].lower()
            if start in chain_end:
                continue

            # 从这条规则开始追踪链
            path = [start]
            current = start
            visited = {start}

            # 只有当前节点的替换目标恰好是另一条规则的源词时，链才继续
            while current in replace_graph:
                next_dst = replace_graph[current]
                next_lower = next_dst.lower()

                # 链的下一跳必须是另一条规则的源词
                if next_lower not in src_map:
                    break
                if next_lower in visited:
                    break

                visited.add(next_lower)
                path.append(next_lower)
                current = next_lower

            # 如果路径长度 > 1，说明发现了链
            if len(path) > 1:
                # 链的终点是 path[-1]
                final_key = path[-1]
                final_rule = src_map.get(final_key)

                if final_rule and not final_rule['is_delete']:
                    final_dst = final_rule['dst']
                elif final_rule and final_rule['is_delete']:
                    final_dst = ''
                else:
                    # 终点不在规则表中，取链的最后一跳的替换值
                    final_dst = path[-1]

                # 只记录链的起点
                chain_end[start] = final_dst

        return chain_end

    def _resolve_case_conflicts(self, src_map):
        """
        处理大小写冲突：同一个 src_lower 对应多条规则。
        策略：删除让位于替换。
        """
        case_groups = defaultdict(list)
        for r in self.raw_rules:
            case_groups[r['src'].lower()].append(r)

        resolved = {}
        for src_lower, group in case_groups.items():
            if len(group) == 1:
                r = group[0]
                resolved[src_lower] = r['dst']
                continue

            # 多条规则冲突
            has_delete = any(r['is_delete'] for r in group)
            has_replace = any(not r['is_delete'] for r in group)
            replaces = [r for r in group if not r['is_delete']]

            if has_delete and has_replace:
                # 删除+替换 → 保留替换
                keep = replaces[0]
                resolved[src_lower] = keep['dst']
                self.case_merges.append({
                    'src_lower': src_lower,
                    'kept': f'"{keep["src"]}" → "{keep["dst"]}"',
                    'dropped': [f'"{r["src"]}" → "删除"' for r in group if r['is_delete']]
                })
            elif len(replaces) > 1:
                # 多个替换值不同 → 需要人工确认，暂用第一个
                dsts = set(r['dst'] for r in replaces)
                if len(dsts) == 1:
                    resolved[src_lower] = replaces[0]['dst']
                else:
                    resolved[src_lower] = replaces[0]['dst']
                    self.manual_review.append({
                        'src_lower': src_lower,
                        'variants': [(r['row'], r['src'], r['dst']) for r in replaces]
                    })
            else:
                # 全是删除 → 合并
                resolved[src_lower] = ''
                self.case_merges.append({
                    'src_lower': src_lower,
                    'kept': '删除',
                    'dropped': [f'"{r["src"]}" (行{r["row"]})' for r in group[1:]]
                })

        return resolved

    def load(self):
        """
        加载并清洗规则。

        Returns:
            dict: {source_lower: replacement}
                  replacement 为空字符串表示删除
        """
        self._read_excel()

        if not self.raw_rules:
            return {}

        # Step 1: 处理链式依赖
        chain_end = self._build_chain_map()

        # 记录链式合并日志
        for start, final_dst in chain_end.items():
            # 找到链的起点规则
            start_rule = None
            for r in self.raw_rules:
                if r['src'].lower() == start:
                    start_rule = r
                    break
            if start_rule:
                # 重建链路径用于日志
                path = [start]
                current = start
                visited = {start}
                src_map = {r['src'].lower(): r for r in self.raw_rules}
                replace_graph = {r['src'].lower(): r['dst'] for r in self.raw_rules if not r['is_delete']}

                while current in replace_graph:
                    next_dst = replace_graph[current]
                    next_lower = next_dst.lower()
                    if next_lower not in src_map or next_lower in visited:
                        break
                    visited.add(next_lower)
                    path.append(next_lower)
                    current = next_lower

                chain_str = ' → '.join([f'"{p}"' for p in path])
                self.chain_merges.append({
                    'original_chain': chain_str,
                    'merged': f'"{start_rule["src"]}" → "{final_dst}"',
                })

        # 用链的终点替换链起点的 dst
        for r in self.raw_rules:
            key = r['src'].lower()
            if key in chain_end:
                r['dst'] = chain_end[key]
                r['is_delete'] = (chain_end[key] == '')

        # Step 2: 处理大小写冲突
        self.clean_rules = self._resolve_case_conflicts(
            {r['src'].lower(): r for r in self.raw_rules}
        )

        # 收集 strict 规则
        self.strict_rules = {
            r['src'].lower()
            for r in self.raw_rules
            if r.get('is_strict', False) and r['src'].lower() in self.clean_rules
        }

        return self.clean_rules

    def report(self):
        """打印清洗报告"""
        print("=" * 60)
        print("规则清洗报告")
        print("=" * 60)
        print(f"原始规则数: {len(self.raw_rules)}")

        if self.chain_merges:
            print(f"\n链式合并 ({len(self.chain_merges)} 组):")
            seen = set()
            for m in self.chain_merges:
                key = m['merged']
                if key in seen:
                    continue
                seen.add(key)
                chain_str = ' → '.join(m['original_chain'])
                print(f"  {chain_str}")
                print(f"  合并为: {m['merged']}")
                print()

        if self.case_merges:
            print(f"大小写冲突合并 ({len(self.case_merges)} 组):")
            for m in self.case_merges:
                print(f"  \"{m['src_lower']}\"")
                print(f"    保留: {m['kept']}")
                for d in m['dropped']:
                    print(f"    丢弃: {d}")
                print()

        if self.manual_review:
            print(f"需要人工确认 ({len(self.manual_review)} 组):")
            for m in self.manual_review:
                print(f"  \"{m['src_lower']}\":")
                for row, src, dst in m['variants']:
                    print(f"    行{row}: \"{src}\" → \"{dst}\"")
                print()

        print(f"清洗后规则数: {len(self.clean_rules)}")
        print(f"其中删除规则: {sum(1 for v in self.clean_rules.values() if v == '')}")
        print(f"其中替换规则: {sum(1 for v in self.clean_rules.values() if v != '')}")
        if self.strict_rules:
            print(f"完全边界规则: {len(self.strict_rules)} 条")
            for s in sorted(self.strict_rules):
                print(f"  [strict] \"{s}\"")
        print("=" * 60)

    def get_rules_by_length(self):
        """按长度分组返回规则，用于调试"""
        if not self.clean_rules:
            self.load()

        short = {k: v for k, v in self.clean_rules.items() if len(k) <= 4}
        medium = {k: v for k, v in self.clean_rules.items() if 4 < len(k) <= 10}
        long_ = {k: v for k, v in self.clean_rules.items() if len(k) > 10}

        return {
            'short (<=4)': short,
            'medium (5-10)': medium,
            'long (>10)': long_,
        }


def load_rules(rules_path, sheet_name="Sheet1"):
    """便捷函数：加载并清洗规则"""
    loader = RuleLoader(rules_path, sheet_name)
    rules = loader.load()
    return rules, loader


if __name__ == "__main__":
    import sys

    rules_path = sys.argv[1] if len(sys.argv) > 1 else "examples/替换目标样例.xlsx"
    loader = RuleLoader(rules_path)
    rules = loader.load()
    loader.report()

    # 按长度分组展示
    groups = loader.get_rules_by_length()
    for name, group in groups.items():
        print(f"\n{name}: {len(group)} 条")
        for k, v in sorted(group.items()):
            action = "删除" if v == '' else f'→ "{v}"'
            print(f'  "{k}" {action}')
