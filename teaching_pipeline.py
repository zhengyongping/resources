# -*- coding: utf-8 -*-
# @file: teaching_pipeline.py
import os
import re
import json
import requests
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import traceback
import time

class Pipeline:
    class Valves(BaseModel):
        # 定义管道参数
        name: str = "教学内容生成器"
        description: str = "根据知识点、教学方法和难度级别生成详细的教学设计"
        help_text: str = "请提供知识点、教学方法和难度级别。例如：'请生成关于牛顿第二定律的教学内容，使用探究式教学法，难度级别为4'"
        enabled: bool = True

    def __init__(self):
        self.name = "教学内容生成器"
        self.api_url = "http://host.docker.internal:7234/generate_teaching_content"
        self.valves = self.Valves()
        
    async def on_startup(self):
        print(f"教学内容生成器 Pipeline 已启动")
        return True

    async def on_shutdown(self):
        print(f"教学内容生成器 Pipeline 已关闭")
        return True

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"处理用户消息: {user_message}")
        
        try:
            # 从用户消息中提取参数
            knowledge_point = self._extract_knowledge_point(user_message)
            teaching_method = self._extract_teaching_method(user_message)
            difficulty = self._extract_difficulty(user_message)
            api_type = "openai" if "openai" in user_message.lower() else "ollama"
            use_advanced_rag = "高级RAG" in user_message or "高级检索" in user_message
            use_web_search = "网络搜索" in user_message or "联网" in user_message
            
            # 验证必要参数
            if not knowledge_point or not teaching_method:
                return "请提供完整的信息，包括知识点和教学方法。例如：'请生成关于牛顿第二定律的教学内容，使用探究式教学法，难度级别为4'"
            
            # 调用API生成教学内容
            payload = {
                "knowledge_point": knowledge_point,
                "teaching_method": teaching_method,
                "difficulty": difficulty,
                "api_type": api_type,
                "use_advanced_rag": use_advanced_rag,
                "use_web_search": use_web_search
            }
            
            # 检查是否请求流式输出
            stream_mode = "stream" in user_message.lower() or "流式" in user_message
            
            if stream_mode:
                # 返回生成器函数进行流式输出
                return self._stream_response(knowledge_point, teaching_method, difficulty, payload)
            else:
                # 非流式输出，一次性返回结果
                response = requests.post(self.api_url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    teaching_note = result.get("teaching_note", {})
                    
                    # 格式化输出为Markdown文本
                    formatted_result = f"""# {knowledge_point} 教学设计 ({difficulty}级)

## 教学大纲
{teaching_note.get('教学大纲', '未生成')}

## 教学重点
{teaching_note.get('教学重点', '未生成')}

## 教学难点
{teaching_note.get('教学难点', '未生成')}

## 教学引入设计
{teaching_note.get('教学引入设计', '未生成')}

## 教学重点讲解设计
{teaching_note.get('教学重点讲解设计', '未生成')}

## 教学难点突破设计
{teaching_note.get('教学难点突破设计', '未生成')}

## 参考资料
{teaching_note.get('参考资料', '未提供参考资料')}
"""
                    return formatted_result
                else:
                    return f"生成教学内容失败: {response.text}"
                    
        except Exception as e:
            error_trace = traceback.format_exc()
            return f"处理请求时出错: {str(e)}\n\n详细错误信息: {error_trace}"
    
    def _stream_response(self, knowledge_point, teaching_method, difficulty, payload):
        """流式输出响应"""
        try:
            # 首先输出标题和正在处理的提示
            yield f"# {knowledge_point} 教学设计 ({difficulty}级)\n\n"
            yield f"正在生成教学内容，请稍候...\n\n"
            
            # 模拟知识检索过程
            yield f"🔍 正在检索与「{knowledge_point}」相关的知识...\n"
            time.sleep(1)
            
            # 调用API生成教学内容
            response = requests.post(self.api_url, json=payload)
            
            if response.status_code != 200:
                yield f"❌ 生成教学内容失败: {response.text}"
                return
                
            result = response.json()
            teaching_note = result.get("teaching_note", {})
            
            # 流式输出各个部分
            yield "✅ 知识检索完成！正在生成教学设计...\n\n"
            time.sleep(0.5)
            
            # 教学大纲
            yield "## 教学大纲\n"
            content = teaching_note.get('教学大纲', '未生成')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.1)
            yield "\n"
            
            # 教学重点
            yield "## 教学重点\n"
            content = teaching_note.get('教学重点', '未生成')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.1)
            yield "\n"
            
            # 教学难点
            yield "## 教学难点\n"
            content = teaching_note.get('教学难点', '未生成')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.1)
            yield "\n"
            
            # 教学引入设计
            yield "## 教学引入设计\n"
            content = teaching_note.get('教学引入设计', '未生成')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.05)
            yield "\n"
            
            # 教学重点讲解设计
            yield "## 教学重点讲解设计\n"
            content = teaching_note.get('教学重点讲解设计', '未生成')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.05)
            yield "\n"
            
            # 教学难点突破设计
            yield "## 教学难点突破设计\n"
            content = teaching_note.get('教学难点突破设计', '未生成')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.05)
            yield "\n"
            
            # 参考资料
            yield "## 参考资料\n"
            content = teaching_note.get('参考资料', '未提供参考资料')
            for line in content.split('\n'):
                yield line + "\n"
                time.sleep(0.1)
            
            # 完成提示
            yield "\n✨ 教学内容生成完成！"
            
        except Exception as e:
            error_trace = traceback.format_exc()
            yield f"❌ 流式输出过程中出错: {str(e)}\n\n详细错误信息: {error_trace}"
    
    def _extract_knowledge_point(self, message):
        """从用户消息中提取知识点"""
        patterns = [
            r'关于["\']?(.*?)[\'"]?的教学',
            r'知识点[：:]\s*[\"\'"]?(.*?)[\"\'"]?',
            r'生成(.*?)的教学'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_teaching_method(self, message):
        """从用户消息中提取教学方法"""
        patterns = [
            r'使用[\"\'"]?(.*?教学法)[\"\'"]?',
            r'教学方法[：:]\s*[\"\'"]?(.*?)[\"\'"]?',
            r'采用[\"\'"]?(.*?教学法)[\"\'"]?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_difficulty(self, message):
        """从用户消息中提取难度级别"""
        match = re.search(r'难度[级别]?[为是:：]?\s*(\d+)', message)
        return match.group(1) if match else "3"
