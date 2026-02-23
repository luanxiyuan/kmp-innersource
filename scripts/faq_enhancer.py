"""
FAQ 增强模块
使用大模型 API 优化 FAQ 内容，提升问答质量
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class FAQEnhancer:
    """FAQ 增强器 - 使用大模型 API 优化 FAQ"""
    
    def __init__(self, model_type: str = None):
        """
        初始化 FAQ 增强器
        
        Args:
            model_type: 大模型类型 (openai, anthropic, qwen, local)
                      如果不指定，从环境变量 LLM_TYPE 读取，默认为 openai
        """
        self.model_type = model_type or os.getenv('LLM_TYPE', 'openai')
        
        # 检查 API 密钥
        self._check_api_keys()
        
        # 初始化客户端
        self._init_client()
        
        print(f"✓ FAQ 增强器已初始化，使用模型: {self.model_type}")
    
    def _check_api_keys(self):
        """检查 API 密钥配置"""
        if self.model_type == 'openai':
            if not os.getenv('OPENAI_API_KEY'):
                raise ValueError(
                    "未找到 OPENAI_API_KEY 环境变量\n"
                    "请在 .env 文件中配置: OPENAI_API_KEY=sk-xxx"
                )
        elif self.model_type == 'anthropic':
            if not os.getenv('ANTHROPIC_API_KEY'):
                raise ValueError(
                    "未找到 ANTHROPIC_API_KEY 环境变量\n"
                    "请在 .env 文件中配置: ANTHROPIC_API_KEY=sk-ant-xxx"
                )
        elif self.model_type == 'qwen':
            if not os.getenv('DASHSCOPE_API_KEY'):
                raise ValueError(
                    "未找到 DASHSCOPE_API_KEY 环境变量\n"
                    "请在 .env 文件中配置: DASHSCOPE_API_KEY=sk-xxx"
                )
        elif self.model_type == 'deepseek':
            if not os.getenv('DEEPSEEK_API_KEY'):
                raise ValueError(
                    "未找到 DEEPSEEK_API_KEY 环境变量\n"
                    "请在 .env 文件中配置: DEEPSEEK_API_KEY=sk-xxx"
                )
        elif self.model_type == 'local':
            # 本地模型无需 API Key
            pass
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    def _init_client(self):
        """初始化大模型客户端"""
        if self.model_type == 'openai':
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(
                    api_key=os.getenv('OPENAI_API_KEY'),
                    base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
                )
                self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            except ImportError:
                raise ImportError(
                    "请安装 openai 库: pip install openai>=1.0.0"
                )
        
        elif self.model_type == 'anthropic':
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                )
                self.model = os.getenv('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
            except ImportError:
                raise ImportError(
                    "请安装 anthropic 库: pip install anthropic>=0.18.0"
                )
        
        elif self.model_type == 'qwen':
            try:
                import dashscope
                dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
                self.model = os.getenv('DASHSCOPE_MODEL', 'qwen-turbo')
            except ImportError:
                raise ImportError(
                    "请安装 dashscope 库: pip install dashscope"
                )
        
        elif self.model_type == 'deepseek':
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(
                    api_key=os.getenv('DEEPSEEK_API_KEY'),
                    base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
                )
                self.model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            except ImportError:
                raise ImportError(
                    "请安装 openai 库: pip install openai>=1.0.0"
                )
        
        elif self.model_type == 'local':
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                import torch
                
                model_name = os.getenv('LOCAL_MODEL', 'Qwen/Qwen2.5-7B-Instruct')
                device_map = os.getenv('LOCAL_DEVICE', 'auto')
                torch_dtype = getattr(torch, os.getenv('LOCAL_DTYPE', 'float16'))
                
                print(f"正在加载本地模型: {model_name}")
                print("首次运行会自动下载模型文件，请耐心等待...")
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch_dtype,
                    device_map=device_map,
                    trust_remote_code=True
                )
                
                print("✓ 本地模型加载完成")
                
            except ImportError:
                raise ImportError(
                    "请安装 transformers 和 torch: pip install transformers torch"
                )
    
    async def enhance_faq_batch(self, faq_items: List[Dict]) -> List[Dict]:
        """
        批量优化 FAQ 列表
        
        Args:
            faq_items: 原始 FAQ 条目列表
            
        Returns:
            优化后的 FAQ 条目列表
        """
        print(f"开始批量优化 {len(faq_items)} 条 FAQ...")
        
        # 构建批量优化提示
        enhanced_items = []
        
        # 分批处理（每批 20 条，避免超时）
        batch_size = 20
        for i in range(0, len(faq_items), batch_size):
            batch = faq_items[i:i + batch_size]
            print(f"正在处理第 {i//batch_size + 1} 批（{len(batch)} 条）...")
            
            # 批量优化
            enhanced_batch = await self._enhance_batch(batch)
            enhanced_items.extend(enhanced_batch)
        
        print(f"✓ 批量优化完成，共处理 {len(enhanced_items)} 条 FAQ")
        
        return enhanced_items
    
    async def _enhance_batch(self, faq_items: List[Dict]) -> List[Dict]:
        """
        优化一批 FAQ 条目
        
        Args:
            faq_items: FAQ 条目列表
            
        Returns:
            优化后的 FAQ 条目列表
        """
        # 将 FAQ 批量转换为提示
        faq_context = self._format_faq_batch(faq_items)
        
        prompt = f"""你是一个专业的技术文档优化助手。请将以下技术文档内容优化为简洁、自然的问答对。

优化要求：
1. **问题优化**：将标题转换为更自然的问题形式，支持模糊提问（如"怎么上线代码？"能匹配）
2. **答案优化**：将原始 HTML 文本提炼为简洁、专业的回答语言（200-300字）
3. **关键词提取**：提取 5-10 个核心关键词，用于模糊匹配
4. **同义词扩展**：为每个关键词添加同义词，提高匹配率

输出格式（必须是有效的 JSON 数组）：
[
  {{
    "question": "优化后的问题（自然口语化）",
    "answer": "优化后的答案（简洁专业，200-300字）",
    "keywords": ["关键词1", "关键词2", ...],
    "synonyms": {{"关键词1": ["同义词1", "同义词2"], ...}},
    "conversation_starter": ["追问1", "追问2", ...]
  }},
  ...
]

原始 FAQ 内容：
{faq_context}

请严格按照 JSON 格式输出，不要添加任何其他文字："""
        
        # 调用大模型 API
        response = await self._call_llm(prompt)
        
        # 解析响应
        try:
            enhanced_data = json.loads(response)
            
            # 合并原始数据和优化数据
            enhanced_items = []
            for original, enhanced in zip(faq_items, enhanced_data):
                enhanced_item = original.copy()
                enhanced_item.update({
                    'question': enhanced.get('question', original.get('question')),
                    'answer': enhanced.get('answer', original.get('answer')),
                    'keywords': enhanced.get('keywords', original.get('keywords', [])),
                    'synonyms': enhanced.get('synonyms', {}),
                    'conversation_starters': enhanced.get('conversation_starter', [])
                })
                enhanced_items.append(enhanced_item)
            
            return enhanced_items
            
        except json.JSONDecodeError as e:
            print(f"警告: 解析 LLM 响应失败: {e}")
            print(f"原始响应: {response[:500]}...")
            # 返回原始数据
            return faq_items
    
    def _format_faq_batch(self, faq_items: List[Dict]) -> str:
        """
        将 FAQ 批量格式化为文本
        
        Args:
            faq_items: FAQ 条目列表
            
        Returns:
            格式化的文本
        """
        formatted = ""
        for i, item in enumerate(faq_items, 1):
            formatted += f"""
条目 {i}:
标题: {item.get('title')}
原始问题: {item.get('question')}
原始答案: {item.get('answer')}
源文件: {item.get('source_file')}
---
"""
        return formatted
    
    async def _call_llm(self, prompt: str) -> str:
        """
        调用大模型 API
        
        Args:
            prompt: 提示词
            
        Returns:
            响应文本
        """
        if self.model_type == 'openai':
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的技术文档优化助手，擅长将技术文档转换为简洁的问答对。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            return response.choices[0].message.content
        
        elif self.model_type == 'anthropic':
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content[0].text
        
        elif self.model_type == 'qwen':
            import dashscope
            response = await asyncio.to_thread(
                dashscope.Generation.call,
                model=self.model,
                prompt=prompt,
                max_tokens=4096,
                temperature=0.3
            )
            return response['output']['text']
        
        elif self.model_type == 'deepseek':
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的技术文档优化助手，擅长将技术文档转换为简洁的问答对。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4096
            )
            return response.choices[0].message.content
        
        elif self.model_type == 'local':
            # 本地模型调用
            text = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True
            )
            
            model_inputs = self.tokenizer(
                [text],
                return_tensors="pt"
            ).to(self.model.device)
            
            generated_ids = self.model.generate(
                model_inputs.input_ids,
                max_new_tokens=2048,
                temperature=0.3,
                do_sample=True
            )
            
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            return response


async def main():
    """主函数：演示 FAQ 增强功能"""
    import argparse
    
    parser = argparse.ArgumentParser(description="增强 FAQ 知识库")
    parser.add_argument(
        "--input",
        default="data/faq.json",
        help="原始 FAQ 文件路径"
    )
    parser.add_argument(
        "--output",
        default="data/faq_enhanced.json",
        help="增强后的 FAQ 文件路径"
    )
    parser.add_argument(
        "--model-type",
        choices=['openai', 'anthropic', 'qwen', 'local'],
        help="大模型类型（默认从环境变量读取）"
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 找不到文件 {args.input}")
        print("请先运行 build_faq.py 生成原始 FAQ")
        return 1
    
    # 加载原始 FAQ
    print(f"加载原始 FAQ: {args.input}")
    with open(input_path, 'r', encoding='utf-8') as f:
        faq_data = json.load(f)
    
    faq_items = faq_data.get('items', [])
    print(f"共加载 {len(faq_items)} 条 FAQ")
    
    # 初始化增强器
    model_type = args.model_type or os.getenv('LLM_TYPE', 'openai')
    enhancer = FAQEnhancer(model_type=model_type)
    
    # 批量优化
    enhanced_items = await enhancer.enhance_faq_batch(faq_items)
    
    # 保存增强后的 FAQ
    output_path = Path(args.output)
    output_data = {
        "version": "2.0",
        "enhanced": True,
        "model_type": model_type,
        "count": len(enhanced_items),
        "items": enhanced_items
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 增强后的 FAQ 已保存到: {args.output}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
