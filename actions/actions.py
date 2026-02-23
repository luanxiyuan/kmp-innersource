"""
Rasa 自定义动作
支持同义词匹配、模糊提问理解和对话引导
"""

import sys
import json
from pathlib import Path
from typing import Any, Text, Dict, List
from collections import defaultdict

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ActionSearchFAQ(Action):
    """增强型 FAQ 搜索 - 支持同义词和模糊匹配"""
    
    name = "action_search_faq"
    
    def __init__(self):
        """初始化 FAQ 数据"""
        self.faq_items = []
        self.keyword_index = defaultdict(list)
        self.faq_loaded = False
    
    def _load_faq_data(self):
        """加载 FAQ 数据（懒加载）"""
        if self.faq_loaded:
            return True

        # 加载增强型 FAQ
        faq_file = project_root / "data" / "faq_enhanced.json"
        index_file = project_root / "data" / "keyword_index_enhanced.json"
        
        for index_file in index_files:
            if index_file.exists():
                break
        
        try:
            # 加载 FAQ 数据
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
            
            self.faq_items = faq_data.get('items', [])

        # 检查是否是增强型 FAQ
        self.is_enhanced = faq_data.get('enhanced', False)

        print(f"✓ 加载增强型 FAQ: {len(self.faq_items)} 条")
            
            # 加载关键词索引
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.keyword_index = defaultdict(list, json.load(f))
            
            self.faq_loaded = True
            return True
            
        except FileNotFoundError as e:
            print(f"警告: FAQ 数据文件未找到: {e}")
            print(f"请先运行 build_faq_enhanced.py 脚本")
            return False
        except Exception as e:
            print(f"加载 FAQ 数据时出错: {e}")
            return False
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        执行 FAQ 搜索动作
        
        Args:
            dispatcher: 消息分发器
            tracker: 对话跟踪器
            domain: 领域配置
            
        Returns:
            事件列表
        """
        # 加载 FAQ 数据
        if not self._load_faq_data():
            dispatcher.utter_message(
                text="抱歉，知识库尚未初始化。\n"
                "请联系管理员运行 FAQ 构建脚本。"
            )
            return []
        
        # 获取用户消息
        user_message = tracker.latest_message.get('text', '').strip()
        
        if not user_message:
            dispatcher.utter_message(text="请告诉我你想了解什么？")
            return []
        
        # 搜索 FAQ
        result = self._search_faq(user_message)
        
        if result:
            # 发送答案
            response = self._build_response(user_message, result)
            dispatcher.utter_message(text=response)
            
            # 如果有对话引导，添加追问提示
            if result.get('conversation_starters'):
                starters = result.get('conversation_starters', [])
                if starters:
                    followup = "\n\n💡 **可能还想知道：**\n"
                    followup += "\n".join([f"• {s}" for s in starters[:3]])
                    dispatcher.utter_message(text=followup)
        else:
            # 未找到匹配结果
            dispatcher.utter_message(text="utter_no_results")
        
        return []
    
    def _search_faq(self, query: str) -> Dict:
        """
        搜索 FAQ（增强型匹配，支持同义词和模糊查询）
        
        Args:
            query: 用户查询
            
        Returns:
            匹配的 FAQ 条目或 None
        """
        query_lower = query.lower()
        
        # 方法 1: 关键词/同义词匹配
        matched_indices = set()
        scores = defaultdict(int)
        
        # 检查每个关键词（包括同义词）
        for keyword, indices in self.keyword_index.items():
            if keyword.lower() in query_lower:
                matched_indices.update(indices)
                # 根据匹配位置给分（完整匹配优先）
                if keyword.lower() == query_lower:
                    for idx in indices:
                        scores[idx] += 3  # 完整匹配高分
                else:
                    for idx in indices:
                        scores[idx] += 1  # 部分匹配
        
        # 如果找到匹配，选择得分最高的
        if scores:
            best_idx = max(scores.items(), key=lambda x: x[1])[0]
            return self.faq_items[best_idx]
        
        # 方法 2: 语义相似度（模糊提问理解）
        # 例如："怎么上线代码？" → "如何部署服务"
        result = self._semantic_match(query_lower)
        if result:
            return result
        
        # 方法 3: 标题模糊匹配
        for item in self.faq_items:
            title = item.get('title', '').lower()
            question = item.get('question', '').lower()
            
            # 检查查询是否在标题或问题中
            if query_lower in title or query_lower in question:
                return item
            
            # 检查查询词汇在标题中的覆盖率
            query_words = query_lower.split()
            matched_words = sum(1 for word in query_words if word in title)
            if matched_words >= len(query_words) * 0.4:  # 至少 40% 的词匹配
                return item
        
        # 方法 4: 字符串相似度检查
        for item in self.faq_items:
            title = item.get('title', '')
            question = item.get('question', '')
            
            # 简单的字符串包含检查
            if any(word in title or word in question for word in query.split()):
                return item
        
        return None
    
    def _semantic_match(self, query: str) -> Dict:
        """
        语义相似度匹配（支持模糊提问理解）
        
        Args:
            query: 用户查询
            
        Returns:
            匹配的 FAQ 条目或 None
        """
        # 定义语义映射（可以扩展或由 LLM 生成）
        semantic_mappings = {
            "上线": ["部署", "发布", "交付"],
            "发布": ["部署", "上线", "交付"],
            "交付": ["部署", "上线", "发布"],
            "配置": ["设置", "安装", "初始化"],
            "设置": ["配置", "安装", "调整"],
            "安装": ["部署", "配置", "设置"],
            "调试": ["测试", "排错", "排查"],
            "排错": ["调试", "修复", "排查"],
            "排查": ["调试", "排错", "诊断"],
            "测试": ["验证", "检查", "调试"],
            "查看": ["阅读", "获取", "访问"],
            "访问": ["查看", "打开", "进入"],
        }
        
        # 检查查询中的关键词是否可以语义映射
        for keyword, synonyms in semantic_mappings.items():
            if keyword in query:
                # 在标题中查找同义词
                for item in self.faq_items:
                    title = item.get('title', '').lower()
                    for synonym in synonyms:
                        if synonym in title:
                            return item
        
        return None
    
    def _build_response(self, query: str, result: Dict) -> str:
        """
        构建响应文本
        
        Args:
            query: 用户查询
            result: FAQ 条目
            
        Returns:
            格式化的响应文本
        """
        # 获取问题（增强型 FAQ 的 question 已经是优化后的）
        original_question = result.get('question', query)
        answer = result.get('answer', '')
        title = result.get('title', '')
        source_file = result.get('source_file', '')
        
        # 构建答案
        response = f"📄 **{original_question}**\n\n"
        response += f"{answer}\n\n"
        
        # 添加来源信息
        response += f"🔗 **文档**: {title}\n"
        response += f"📁 **文件**: {source_file}"
        
        # 如果答案被截断，提示查看原文
        if answer.endswith('...'):
            response += f"\n\n💡 以上为内容摘要，完整内容请查看原文档"
        
        return response


class ActionGetFAQDetails(Action):
    """获取 FAQ 详细信息（支持多结果展示）"""
    
    name = "action_get_faq_details"
    
    def __init__(self):
        """初始化 FAQ 数据"""
        self.faq_items = []
        self.faq_loaded = False
    
    def _load_faq_data(self):
        """加载 FAQ 数据（懒加载）"""
        if self.faq_loaded:
            return True

        # 加载增强型 FAQ
        faq_file = project_root / "data" / "faq_enhanced.json"
        
        try:
            with open(faq_file, 'r', encoding='utf-8') as f:
                faq_data = json.load(f)
            
            self.faq_items = faq_data.get('items', [])
            self.faq_loaded = True
            return True
            
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"加载 FAQ 数据时出错: {e}")
            return False
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        执行获取详细信息动作
        
        Args:
            dispatcher: 消息分发器
            tracker: 对话跟踪器
            domain: 领域配置
            
        Returns:
            事件列表
        """
        # 获取用户消息
        user_message = tracker.latest_message.get('text', '').strip()
        
        if not user_message:
            dispatcher.utter_message(text="请告诉我你想了解什么？")
            return []
        
        # 加载 FAQ 数据
        if not self._load_faq_data():
            dispatcher.utter_message(text="抱歉，知识库尚未初始化。")
            return []
        
        # 搜索所有可能相关的 FAQ
        results = []
        user_message_lower = user_message.lower()
        
        for item in self.faq_items:
            title = item.get('title', '').lower()
            question = item.get('question', '').lower()
            
            if user_message_lower in title or user_message_lower in question:
                results.append(item)
        
        if results:
            # 构建响应
            response = f"📋 找到 {len(results)} 个相关文档：\n\n"
            
            for i, result in enumerate(results[:5], 1):
                response += f"\n**{i}. {result.get('question')}**\n"
                response += f"   {result.get('answer', '')[:200]}...\n"
                response += f"   📁 {result.get('source_file')}\n"
            
            dispatcher.utter_message(text=response)
        else:
            dispatcher.utter_message(text="没有找到更多相关内容。")
        
        return []


class ActionResetConversation(Action):
    """重置对话动作"""
    
    name = "action_reset_conversation"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        执行重置对话动作
        
        Args:
            dispatcher: 消息分发器
            tracker: 对话跟踪器
            domain: 领域配置
            
        Returns:
            事件列表
        """
        dispatcher.utter_message(
            text="对话已重置。请问有什么可以帮助你的？"
        )
        
        return []


if __name__ == "__main__":
    # 测试代码
    print("Rasa Actions Module Loaded")
    print("Available actions:")
    print("  - action_search_faq (支持同义词、模糊匹配和对话引导)")
    print("  - action_get_faq_details")
    print("  - action_reset_conversation")
