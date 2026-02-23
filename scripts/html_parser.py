"""
HTML 解析模块
从 Confluence 导出的 HTML 文件中提取纯文本内容和元数据
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class FAQItem:
    """FAQ 条目数据结构"""
    question: str          # 问题（从标题生成）
    answer: str            # 答案（页面摘要）
    title: str            # 页面标题
    source_file: str      # 源文件名
    relative_path: str    # 相对路径
    keywords: List[str]   # 关键词列表
    metadata: Dict        # 额外元数据


class HTMLParser:
    """HTML 解析器"""
    
    # 需要移除的标签
    REMOVE_TAGS = [
        'script', 'style', 'nav', 'footer', 'header', 
        'aside', 'iframe', 'noscript', 'link', 'meta'
    ]
    
    def __init__(self, html_dir: str):
        """
        初始化 HTML 解析器
        
        Args:
            html_dir: HTML 文件目录
        """
        self.html_dir = Path(html_dir)
        if not self.html_dir.exists():
            raise FileNotFoundError(f"HTML 目录不存在: {html_dir}")
    
    def find_html_files(self) -> List[Path]:
        """
        查找所有 HTML 文件
        
        Returns:
            HTML 文件路径列表
        """
        html_files = []
        for ext in ['*.html', '*.htm']:
            html_files.extend(self.html_dir.glob(f"**/{ext}"))
        return sorted(html_files)
    
    def parse_file(self, file_path: Path) -> Dict:
        """
        解析单个 HTML 文件
        
        Args:
            file_path: HTML 文件路径
            
        Returns:
            解析结果字典
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            return None
        
        # 解析 HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 移除不需要的标签
        for tag in self.REMOVE_TAGS:
            for element in soup.find_all(tag):
                element.decompose()
        
        # 提取标题
        title = self._extract_title(soup, file_path)
        
        # 提取纯文本内容
        content = self._extract_main_content(soup)
        
        # 提取关键词
        keywords = self._extract_keywords(title, content)
        
        # 提取元数据
        metadata = self._extract_metadata(soup)
        
        # 获取相对路径
        relative_path = file_path.relative_to(self.html_dir)
        
        return {
            'title': title,
            'content': content,
            'source_file': file_path.name,
            'relative_path': str(relative_path),
            'keywords': keywords,
            'metadata': metadata,
            'full_path': str(file_path)
        }
    
    def _extract_title(self, soup: BeautifulSoup, file_path: Path) -> str:
        """提取页面标题"""
        # 尝试从 title 标签获取
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text(strip=True):
            return title_tag.get_text(strip=True)
        
        # 尝试从 h1 标签获取
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text(strip=True):
            return h1_tag.get_text(strip=True)
        
        # 使用文件名
        return file_path.stem.replace('_', ' ').replace('-', ' ')
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """提取纯文本内容"""
        # 尝试找到主要内容区域
        main_tag = soup.find('main')
        if main_tag:
            content = main_tag.get_text(separator='\n', strip=True)
        elif soup.find('article'):
            content = soup.find('article').get_text(separator='\n', strip=True)
        elif soup.find('body'):
            content = soup.find('body').get_text(separator='\n', strip=True)
        else:
            content = soup.get_text(separator='\n', strip=True)
        
        # 清理空白
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content
    
    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """
        从标题和内容中提取关键词
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            关键词列表
        """
        keywords = []
        
        # 常见技术关键词
        common_keywords = [
            '部署', '配置', '安装', '调试', '测试',
            '数据库', 'API', '接口', '服务', '服务器',
            '错误', '问题', '解决', '方法', '步骤',
            '权限', '环境', '依赖', '版本', '发布',
            '备份', '恢复', '监控', '告警', '日志',
            '优化', '性能', '缓存', '加密', '安全',
            'Docker', 'Kubernetes', 'MySQL', 'Redis',
            'Git', 'CI/CD', 'Jenkins', 'Nginx'
        ]
        
        # 从标题中查找关键词
        for keyword in common_keywords:
            if keyword in title:
                keywords.append(keyword)
        
        # 如果没有找到关键词，使用标题的第一部分作为关键词
        if not keywords:
            # 将标题按空格和标点分割
            parts = re.split(r'[\s,，、。.!?！?]', title)
            keywords = [p for p in parts if p]
        
        return keywords[:10]  # 最多返回 10 个关键词
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """提取页面元数据"""
        metadata = {}
        
        # 提取作者
        author = soup.find('meta', attrs={'name': 'author'})
        if author:
            metadata['author'] = author.get('content', '')
        
        # 提取日期
        date = soup.find('meta', attrs={'name': 'date'})
        if date:
            metadata['date'] = date.get('content', '')
        
        # 提取描述
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            metadata['description'] = description.get('content', '')
        
        return metadata
    
    def parse_directory(self) -> List[FAQItem]:
        """
        解析目录中的所有 HTML 文件并生成 FAQ 条目
        
        Returns:
            FAQ 条目列表
        """
        faq_items = []
        html_files = self.find_html_files()
        
        print(f"找到 {len(html_files)} 个 HTML 文件")
        
        for html_file in html_files:
            print(f"正在解析: {html_file.relative_to(self.html_dir)}")
            
            parsed_data = self.parse_file(html_file)
            if parsed_data:
                # 生成问题（将标题转换为问题形式）
                question = self._generate_question(parsed_data['title'])
                
                # 生成答案（页面摘要）
                answer = self._generate_answer(parsed_data['content'])
                
                faq_item = FAQItem(
                    question=question,
                    answer=answer,
                    title=parsed_data['title'],
                    source_file=parsed_data['source_file'],
                    relative_path=parsed_data['relative_path'],
                    keywords=parsed_data['keywords'],
                    metadata=parsed_data['metadata']
                )
                
                faq_items.append(faq_item)
        
        print(f"共生成 {len(faq_items)} 个 FAQ 条目")
        return faq_items
    
    def _generate_question(self, title: str) -> str:
        """
        从标题生成问题
        
        Args:
            title: 页面标题
            
        Returns:
            问题文本
        """
        # 如果标题已经是问句形式，直接返回
        if title.endswith('?') or title.endswith('？'):
            return title
        
        # 添加疑问词
        question_prefixes = ['如何', '怎么', '如何进行', '如何完成', '如何操作']
        
        # 检查标题是否以动宾结构开头
        for prefix in question_prefixes:
            if title.startswith(prefix):
                return title
        
        # 默认添加"如何"
        return f"如何{title}"
    
    def _generate_answer(self, content: str) -> str:
        """
        生成答案（取内容前 500 字作为摘要）
        
        Args:
            content: 页面内容
            
        Returns:
            答案摘要
        """
        # 清理内容
        content = content.strip()
        
        # 如果内容少于 500 字，直接返回
        if len(content) <= 500:
            return content
        
        # 取前 500 字
        answer = content[:500]
        
        # 在句子边界截断
        last_period = max(
            answer.rfind('。'),
            answer.rfind('！'),
            answer.rfind('？'),
            answer.rfind('.'),
            answer.rfind('!'),
            answer.rfind('?')
        )
        
        if last_period > 200:
            answer = answer[:last_period + 1]
        
        return answer


if __name__ == "__main__":
    # 测试代码
    parser = HTMLParser("../confluence_html")
    faq_items = parser.parse_directory()
    
    for i, item in enumerate(faq_items[:3]):
        print(f"\n--- FAQ {i+1} ---")
        print(f"问题: {item.question}")
        print(f"标题: {item.title}")
        print(f"关键词: {', '.join(item.keywords)}")
        print(f"答案: {item.answer[:200]}...")
