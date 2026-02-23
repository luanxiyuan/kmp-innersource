"""
构建增强型 FAQ 知识库脚本
从 HTML 文件解析 → 大模型优化 → 生成 FAQ JSON
"""

import argparse
import sys
import asyncio
import json
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from html_parser import HTMLParser
from faq_enhancer import FAQEnhancer


async def build_enhanced_faq(
    html_dir: str = "confluence_html",
    output_file: str = "data/faq_enhanced.json",
    model_type: str = None
):
    """
    构建增强型 FAQ 知识库

    Args:
        html_dir: HTML 文件目录
        output_file: 输出 FAQ JSON 文件路径
        model_type: 大模型类型（None 则从环境变量读取）
    """
    print("=" * 60)
    print("开始构建增强型 FAQ 知识库")
    print("=" * 60)
    
    # ==================== 步骤 1: 解析 HTML 文件 ====================
    print(f"\n步骤 1: 解析 HTML 文件")
    print(f"目录: {html_dir}")
    
    try:
        parser = HTMLParser(html_dir)
        faq_items = parser.parse_directory()
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print(f"\n请确保目录 '{html_dir}' 存在并包含 HTML 文件")
        return False
    except Exception as e:
        print(f"解析 HTML 时出错: {e}")
        return False
    
    if not faq_items:
        print("错误: 未找到任何 FAQ 条目")
        print("请检查 HTML 文件内容")
        return False
    
    # 转换为字典格式
    raw_faq_items = [
        {
            'question': item.question,
            'answer': item.answer,
            'title': item.title,
            'source_file': item.source_file,
            'relative_path': item.relative_path,
            'keywords': item.keywords,
            'metadata': item.metadata
        }
        for item in faq_items
    ]
    
    # 保存原始 FAQ（用于对比）
    raw_faq_file = Path("data/faq_raw.json")
    raw_faq_data = {
        "version": "1.0",
        "enhanced": False,
        "count": len(raw_faq_items),
        "items": raw_faq_items
    }
    
    with open(raw_faq_file, 'w', encoding='utf-8') as f:
        json.dump(raw_faq_data, f, ensure_ascii=False, indent=2)
    print(f"原始 FAQ 已保存到: {raw_faq_file}")
    
    # ==================== 步骤 2: 大模型优化 ====================
    print(f"\n步骤 2: 使用大模型优化 FAQ")

    try:
        # 初始化增强器
        enhancer = FAQEnhancer(model_type=model_type)

        # 批量优化
        enhanced_items = await enhancer.enhance_faq_batch(raw_faq_items)

    except Exception as e:
        print(f"[ERROR] 大模型优化失败: {e}")
        print("请检查 API 配置或网络连接")
        return False
    
    # ==================== 步骤 3: 保存增强型 FAQ ====================
    print(f"\n步骤 3: 保存增强型 FAQ JSON")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    faq_data = {
        "version": "2.0",
        "enhanced": True,
        "model_type": model_type,
        "count": len(enhanced_items),
        "items": enhanced_items
    }
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(faq_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] 增强型 FAQ 已保存到: {output_path}")
    except Exception as e:
        print(f"保存 FAQ 时出错: {e}")
        return False
    
    # ==================== 步骤 4: 生成关键词索引（包含同义词）====================
    print(f"\n步骤 4: 生成增强关键词索引")
    keyword_index = generate_enhanced_keyword_index(enhanced_items)
    index_path = Path("data/keyword_index_enhanced.json")
    
    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(keyword_index, f, ensure_ascii=False, indent=2)
        print(f"[OK] 增强关键词索引已保存到: {index_path}")
    except Exception as e:
        print(f"保存关键词索引时出错: {e}")
        return False
    
    # ==================== 步骤 5: 生成对话引导数据 ====================
    print(f"\n步骤 5: 生成对话引导数据")
    conversation_guides = generate_conversation_guides(enhanced_items)
    guides_path = Path("data/conversation_guides.json")
    
    try:
        with open(guides_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_guides, f, ensure_ascii=False, indent=2)
        print(f"[OK] 对话引导数据已保存到: {guides_path}")
    except Exception as e:
        print(f"保存对话引导数据时出错: {e}")
        return False
    
    # ==================== 完成 ====================
    print("\n" + "=" * 60)
    print("增强型 FAQ 知识库构建完成!")
    print("=" * 60)
    print(f"\n统计信息:")
    print(f"  - HTML 文件: {len(parser.find_html_files())}")
    print(f"  - FAQ 条目: {len(enhanced_items)}")
    print(f"  - 使用模型: {model_type}")
    print(f"  - FAQ 文件: {output_path}")
    print(f"  - 关键词索引: {index_path}")
    print(f"  - 对话引导: {guides_path}")
    print(f"\n接下来可以运行:")
    print(f"  rasa train          # 训练 Rasa 模型")
    print(f"  rasa run --enable-api --cors \"*\"")
    print(f"  rasa run actions")
    
    return True


def generate_enhanced_keyword_index(faq_items: list) -> dict:
    """
    生成增强关键词索引（包含同义词）
    
    Args:
        faq_items: FAQ 条目列表
        
    Returns:
        关键词索引字典
    """
    index = {}
    
    for i, item in enumerate(faq_items):
        # 获取关键词
        keywords = item.get('keywords', [])
        synonyms = item.get('synonyms', {})
        
        # 添加主关键词
        for keyword in keywords:
            if keyword not in index:
                index[keyword] = []
            index[keyword].append(i)
            
            # 添加同义词
            if keyword in synonyms:
                for synonym in synonyms[keyword]:
                    if synonym not in index:
                        index[synonym] = []
                    index[synonym].append(i)
    
    return index


def generate_conversation_guides(faq_items: list) -> dict:
    """
    生成对话引导数据
    
    Args:
        faq_items: FAQ 条目列表
        
    Returns:
        对话引导字典
    """
    guides = {}
    
    for i, item in enumerate(faq_items):
        question = item.get('question', '')
        starters = item.get('conversation_starters', [])
        
        if starters:
            guides[str(i)] = {
                'question': question,
                'title': item.get('title', ''),
                'follow_up_questions': starters
            }
    
    return guides


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="构建增强型 FAQ 知识库")
    parser.add_argument(
        "--html-dir",
        default="confluence_html",
        help="HTML 文件目录 (默认: confluence_html)"
    )
    parser.add_argument(
        "--output",
        default="data/faq_enhanced.json",
        help="输出 FAQ JSON 文件路径 (默认: data/faq_enhanced.json)"
    )
    parser.add_argument(
        "--model-type",
        choices=['openai', 'anthropic', 'qwen', 'deepseek', 'local'],
        help="大模型类型 (默认从环境变量 LLM_TYPE 读取)"
    )

    args = parser.parse_args()

    success = asyncio.run(
        build_enhanced_faq(
            html_dir=args.html_dir,
            output_file=args.output,
            model_type=args.model_type
        )
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
