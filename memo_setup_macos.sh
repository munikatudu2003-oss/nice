#!/usr/bin/env bash
set -euo pipefail

log() { printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
warn() { printf '\n[WARN] %s\n' "$*"; }

require_macos() {
  if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "此脚本仅支持 macOS。"
    exit 1
  fi
}

ensure_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    log "Homebrew 已安装：$(brew --version | head -n1)"
    return
  fi

  log "检测到未安装 Homebrew，开始安装..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi

  command -v brew >/dev/null 2>&1 || {
    echo "Homebrew 安装失败，请手动检查。"
    exit 1
  }
  log "Homebrew 安装完成。"
}

install_memo() {
  if command -v memo >/dev/null 2>&1; then
    log "memo 已存在：$(memo --version 2>/dev/null || echo '无法读取版本')"
    return
  fi

  log "添加 tap：antoniorodr/memo"
  brew tap antoniorodr/memo

  log "安装 memo"
  brew install memo

  if ! command -v memo >/dev/null 2>&1; then
    warn "memo 未在 PATH 中，尝试执行 brew link memo"
    brew link memo || true
  fi

  command -v memo >/dev/null 2>&1 || {
    echo "memo 安装失败，请执行 'brew doctor' 后重试。"
    exit 1
  }

  log "memo 安装完成：$(memo --version 2>/dev/null || echo '已安装，但版本读取失败')"
}

run_smoke_tests() {
  log "开始基础可用性检查"
  memo --help >/dev/null

  local note_title="测试备忘录 $(date '+%Y%m%d-%H%M%S')"
  local reminder_title="测试提醒 $(date '+%Y%m%d-%H%M%S')"

  warn "即将创建测试数据：\n- 备忘录：${note_title}\n- 提醒事项：${reminder_title}"

  if memo notes -a "$note_title" >/dev/null 2>&1; then
    log "备忘录创建成功"
  else
    warn "备忘录创建失败，通常是因为尚未授予终端“完全磁盘访问”。"
  fi

  if memo reminders -a "$reminder_title" --due-date "2026-03-10" >/dev/null 2>&1; then
    log "提醒事项创建成功"
  else
    warn "提醒事项创建失败，通常是因为尚未授予终端权限。"
  fi

  warn "如遇权限问题：系统设置 → 隐私与安全性 → 完全磁盘访问，给终端授权后重试。"
}

main() {
  require_macos
  ensure_homebrew
  install_memo
  run_smoke_tests

  log "全部流程执行完成。你现在可以运行：memo notes / memo reminders"
}

main "$@"
