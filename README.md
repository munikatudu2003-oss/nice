# memo 一键部署脚本（macOS）

执行以下命令即可完成 Homebrew 检查、memo 安装与基础测试：

```bash
bash memo_setup_macos.sh
```

## 脚本内容

- 自动检测并安装 Homebrew（若未安装）
- 通过 `antoniorodr/memo` tap 安装 `memo`
- 运行 `memo --help` 可用性检查
- 尝试创建一条测试备忘录和一条测试提醒事项

> 若测试阶段提示权限问题，请前往：
> **系统设置 → 隐私与安全性 → 完全磁盘访问**，为终端授予权限后重试。
