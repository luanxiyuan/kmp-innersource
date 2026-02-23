"""
轻量级 FAQ 问答服务器
依赖 AI 增强的 FAQ JSON，提供问答服务
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from jieba import cut as jieba_cut
from collections import defaultdict


@dataclass
class FAQMatch:
    """FAQ 匹配结果"""
    question: str
    answer: str
    title: str
    source_file: str
    score: float  # 匹配分数 0-1


class FAQServer:
    """FAQ 问答服务器"""
    
    def __init__(self, faq_file: str = "data/faq_enhanced.json"):
        """
        初始化 FAQ 服务器
        
        Args:
            faq_file: FAQ JSON 文件路径
        """
        self.faq_file = Path(faq_file)
        self.faq_data = None
        self.faqs = []
        self.keyword_index = defaultdict(list)
        
        # 尝试加载增强 FAQ，如果失败则加载基础 FAQ
        self._load_faq()
        
        # 构建索引
        self._build_index()
    
    def _load_faq(self):
        """加载 FAQ 数据"""
        if self.faq_file.exists():
            with open(self.faq_file, 'r', encoding='utf-8') as f:
                self.faq_data = json.load(f)
                self.faqs = self.faq_data.get('items', [])
                print(f"[OK] 加载增强型 FAQ 文件: {self.faq_file}")
                print(f"     共 {len(self.faqs)} 个 FAQ 条目")
        else:
            print(f"[ERROR] 未找到增强型 FAQ 文件")
            print(f"     请先运行 python scripts/build_faq_enhanced.py")
            self.faqs = []
    
    def _build_index(self):
        """构建关键词索引"""
        for i, faq in enumerate(self.faqs):
            # 使用问题标题的关键词
            question = faq.get('question', '')
            keywords = faq.get('keywords', [])
            
            # 将问题分词
            for word in jieba_cut(question):
                if len(word) > 1:  # 忽略单字
                    self.keyword_index[word].append(i)
            
            # 添加预定义关键词
            for keyword in keywords:
                if keyword and len(keyword) > 1:
                    self.keyword_index[keyword].append(i)
        
        print(f"[OK] 构建关键词索引完成")
    
    def _calculate_similarity(self, query: str, faq: Dict) -> float:
        """
        计算查询与 FAQ 的相似度
        
        Args:
            query: 用户查询
            faq: FAQ 条目
            
        Returns:
            相似度分数 0-1
        """
        question = faq.get('question', '')
        answer = faq.get('answer', '')
        
        # 简单的关键词匹配
        query_words = set(jieba_cut(query))
        question_words = set(jieba_cut(question))
        
        if not query_words or not question_words:
            return 0.0
        
        # 计算交集比例
        intersection = query_words & question_words
        score = len(intersection) / max(len(query_words), len(question_words))
        
        return score
    
    def query(self, question: str, top_k: int = 3) -> List[FAQMatch]:
        """
        查询 FAQ
        
        Args:
            question: 用户问题
            top_k: 返回前 K 个结果
            
        Returns:
            匹配结果列表
        """
        if not self.faqs:
            return []
        
        # 计算每个 FAQ 的相似度
        matches = []
        for faq in self.faqs:
            score = self._calculate_similarity(question, faq)
            if score > 0:
                matches.append(FAQMatch(
                    question=faq.get('question', ''),
                    answer=faq.get('answer', ''),
                    title=faq.get('title', ''),
                    source_file=faq.get('source_file', ''),
                    score=score
                ))
        
        # 按分数排序
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # 返回前 K 个结果
        return matches[:top_k]
    
    def get_all_faqs(self) -> List[Dict]:
        """获取所有 FAQ"""
        return self.faqs


def main():
    """测试 FAQ 服务器"""
    print("=" * 60)
    print("FAQ 问答服务器测试")
    print("=" * 60)
    
    # 初始化服务器
    server = FAQServer()
    
    if not server.faqs:
        print("\n[ERROR] 没有可用的 FAQ 数据")
        return
    
    # 测试查询
    print("\n测试查询:")
    test_queries = [
        "Confluence 是什么",
        "NotebookLM 怎么用",
        "如何部署服务"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        matches = server.query(query, top_k=2)
        
        if matches:
            for i, match in enumerate(matches, 1):
                print(f"  [{i}] 分数: {match.score:.2f}")
                print(f"      问题: {match.question}")
                print(f"      答案: {match.answer[:100]}...")
        else:
            print("  未找到匹配结果")


if __name__ == "__main__":
    main()
