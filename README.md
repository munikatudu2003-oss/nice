# GLM-5 + Codex 双模型集成（可直接运行）

这是一个最小可运行的「双模型编排」示例：

- **GLM-5**：做任务理解、拆解、调度。
- **Codex/OpenAI 代码模型**：专注生成可运行代码。
- **GLM-5 再总结**：把代码结果转成可读的执行说明和扩展建议。

## 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置密钥

```bash
export OPENAI_API_KEY="你的 OpenAI Key"
export GLM_API_KEY="你的 GLM Key"
```

## 3. 运行

```bash
python glm_codex_agent.py "写一个Python批量重命名文件的脚本"
```

你将看到 3 段输出：

1. `GLM 规划 JSON`
2. `Codex 代码结果`
3. `GLM 业务总结`

## 4. 扩展建议

- 接入执行沙箱（例如 Docker）来自动运行和验证生成代码。
- 增加“报错修复循环”：运行失败后，把错误堆栈回传给 Codex 修复。
- 增加模型路由器：按任务类型自动切换 GLM / Codex / DeepSeek。
