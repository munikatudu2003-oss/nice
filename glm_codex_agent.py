"""GLM-5 + Codex 双模型集成最小可运行示例。

流程：
1. GLM-5 负责任务规划（是否需要代码 + 生成 Codex Prompt）
2. Codex（OpenAI 代码模型）负责产出代码
3. GLM-5 对结果做整理总结

使用方式：
    export OPENAI_API_KEY=...
    export GLM_API_KEY=...
    python glm_codex_agent.py "写一个 Python 批量重命名脚本"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass

from openai import OpenAI
from zhipuai import ZhipuAI


@dataclass
class OrchestratorConfig:
    """运行配置。"""

    glm_model: str = "glm-5"
    codex_model: str = "gpt-4.1-mini"
    max_output_tokens: int = 1800
    temperature: float = 0.1


class DualModelAgent:
    """GLM 规划 + Codex 写码的简易编排器。"""

    def __init__(self, config: OrchestratorConfig) -> None:
        self.config = config

        glm_key = os.environ.get("GLM_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")

        if not glm_key:
            raise RuntimeError("缺少环境变量 GLM_API_KEY")
        if not openai_key:
            raise RuntimeError("缺少环境变量 OPENAI_API_KEY")

        self.glm = ZhipuAI(api_key=glm_key)
        self.codex = OpenAI(api_key=openai_key)

    def plan(self, user_query: str) -> dict:
        """由 GLM 产出结构化计划。"""
        prompt = f"""
你是 AI 任务调度器，用户需求如下：
{user_query}

请仅返回 JSON（不要 markdown），格式如下：
{{
  "needs_code": true,
  "codex_prompt": "给代码模型的清晰指令",
  "notes": "你对任务的理解"
}}
""".strip()

        resp = self.glm.chat.completions.create(
            model=self.config.glm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = resp.choices[0].message.content
        return self._safe_json_parse(content)

    def write_code(self, codex_prompt: str) -> str:
        """调用 OpenAI 代码模型生成代码。"""
        response = self.codex.responses.create(
            model=self.config.codex_model,
            input=[
                {
                    "role": "system",
                    "content": "你是资深软件工程师。输出可直接运行的代码，必要时附简短注释。",
                },
                {"role": "user", "content": codex_prompt},
            ],
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
        )
        return response.output_text.strip()

    def summarize(self, user_query: str, code: str) -> str:
        """让 GLM 对代码做业务化总结。"""
        prompt = f"""
用户原始需求：{user_query}

下面是代码模型生成的结果：
{code}

请输出：
1) 代码实现了什么
2) 如何运行
3) 可扩展方向（3 点）
""".strip()

        resp = self.glm.chat.completions.create(
            model=self.config.glm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()

    @staticmethod
    def _safe_json_parse(content: str) -> dict:
        """容错解析 GLM 返回。"""
        text = content.strip()

        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"GLM 规划结果不是合法 JSON: {content}") from exc


def run(user_query: str, config: OrchestratorConfig) -> int:
    agent = DualModelAgent(config)

    plan = agent.plan(user_query)
    needs_code = bool(plan.get("needs_code"))

    print("=== GLM 规划 ===")
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    if not needs_code:
        print("\n无需生成代码。")
        return 0

    codex_prompt = str(plan.get("codex_prompt", "")).strip()
    if not codex_prompt:
        print("\n规划缺少 codex_prompt，无法继续。", file=sys.stderr)
        return 2

    code = agent.write_code(codex_prompt)
    print("\n=== Codex 代码结果 ===")
    print(code)

    summary = agent.summarize(user_query, code)
    print("\n=== GLM 业务总结 ===")
    print(summary)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GLM-5 + Codex 双模型编排示例")
    parser.add_argument("query", help="用户需求，例如：写一个批量重命名脚本")
    parser.add_argument("--glm-model", default="glm-5", help="GLM 模型名")
    parser.add_argument("--codex-model", default="gpt-4.1-mini", help="OpenAI 代码模型名")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    cfg = OrchestratorConfig(glm_model=args.glm_model, codex_model=args.codex_model)
    raise SystemExit(run(args.query, cfg))
