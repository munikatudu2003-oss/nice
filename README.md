# GitHub 推送快速命令

把你的真实仓库地址替换到下面的 `<REPO_URL>`，然后按顺序执行。

## 1) 设置当前仓库身份（仅当前仓库生效）

```bash
git config user.name "你的 GitHub 用户名"
git config user.email "你的 GitHub 邮箱"
```

## 2) 添加远端 origin

```bash
git remote add origin <REPO_URL>
```

如果已存在 origin：

```bash
git remote set-url origin <REPO_URL>
```

## 3) 推送 main 到远端

```bash
git push -u origin main
```

如果当前分支不是 `main`，先重命名：

```bash
git branch -M main
git push -u origin main
```
