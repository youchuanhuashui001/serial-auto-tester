# Git 工作流程指南

在实际开发中，Git 的工作流程会根据团队规模和项目需求有所不同。作为开发者，掌握最基础且最被广泛使用的几种工作流，能让你在绝大多数团队中游刃有余。

以下是三种最常见的 Git 工作流程：

---

## 1. 功能分支工作流 (Feature Branch Workflow) —— 行业最通用

这是目前大多数企业和团队（尤其是使用 GitHub/GitLab 的团队）采用的核心工作流。**核心思想是：所有的开发工作都在独立的分支上进行，不直接修改主分支。**

**标准操作步骤：**

1. **同步主分支**：在开始新工作前，确保本地主分支是最新的。
```bash
git checkout main
git pull origin main
```

2. **创建功能分支**：基于最新的主分支，创建一个具有描述性名称的新分支。
```bash
git checkout -b feature/add-spi-driver
```

3. **开发与提交**：在分支上编写代码，并进行多次逻辑清晰的提交。（如果你中途需要切换分支，可以用 `git stash` 来暂存未完成的代码）。
```bash
git add .
git commit -m "feat: add initial SPI driver implementation"
```

4. **保持分支更新（推荐使用 Rebase）**：如果开发周期较长，主分支可能有新的更新，建议变基（Rebase）以保持提交历史整洁（在 Linux 和嵌入式开发中非常推崇）。
```bash
git fetch origin
git rebase origin/main
```

5. **推送到远程并提交合并请求 (PR/MR)**：
```bash
git push -u origin feature/add-spi-driver
```

6. **代码审查与合并**：团队成员 Review 代码后，在 GitHub 网页上将该分支合并入 `main`（通常选择 "Merge pull request" 或 "Squash and merge"）。

7. **本地分支清理**：GitHub 上合并完成后，本地需要同步并清理：
```bash
# 切回 main 分支
git checkout main

# 拉取合并后的最新代码
git pull origin main

# 删除本地的功能分支（已合并，安全删除）
git branch -d feature/add-spi-driver

# 删除远程的功能分支（如果 GitHub 上没有自动删除）
git push origin --delete feature/add-spi-driver

# 一键清理所有远程已删除但本地还残留的跟踪分支
git fetch --prune
```

---

## 2. Gitflow 工作流 (适用于大型、有固定发布周期的项目)

Gitflow 是一种非常严格的分支模型，适合需要进行复杂版本控制和定期发布产品的团队。它定义了五种主要分支：

* **`master` / `main`**：永远只存储随时可以发布到生产环境的代码。
* **`develop`**：日常开发的主分支，包含所有下一次发布需要的功能。
* **`feature/...`**：基于 `develop` 创建，用于开发新功能，完成后合并回 `develop`。
* **`release/...`**：基于 `develop` 创建，用于准备发布新版本（主要用来修 Bug、改版本号），完成后同时合并进 `master` 和 `develop`。
* **`hotfix/...`**：基于 `master` 创建，用于紧急修复生产环境的 Bug，完成后同时合并进 `master` 和 `develop`。

---

## 3. Forking 工作流 (开源社区/跨团队合作)

这种工作流主要用于开源项目或权限控制极其严格的内部大团队。开发者没有直接向主仓库推送代码的权限。

**标准操作步骤：**

1. 在网页端将官方主仓库 **Fork** 到自己的个人账户下。
2. `git clone` 自己账号下的仓库到本地。
3. 添加官方主仓库为上游（Upstream）：`git remote add upstream <官方仓库地址>`。
4. 本地创建分支，开发并推送到**自己的**远程仓库。
5. 在网页端向官方主仓库发起 **Pull Request (PR)**。
6. 定期拉取上游代码保持同步：`git pull upstream main`。

---

## 4. Commit Message 规范

好的提交信息能让 `git log` 变成项目的变更日志。推荐采用 **Conventional Commits** 规范：

```
<类型>(<作用域>): <描述>

<可选的正文>

<可选的脚注>
```

### 常用类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新增功能 | `feat: 增加 flash comtest 测试项` |
| `fix` | 修复 Bug | `fix: 修复 OTP 测试超时问题` |
| `docs` | 文档修改 | `docs: 更新 git 工作流程文档` |
| `refactor` | 重构（不改变功能） | `refactor: 优化串口读取逻辑` |
| `chore` | 构建/工具/杂项 | `chore: 去掉 HTML 邮件支持` |
| `test` | 测试相关 | `test: 增加 SPI 驱动单元测试` |
| `style` | 格式/空白/分号等 | `style: 去掉多余的空行` |

### 示例

```bash
# 简洁提交
git commit -m "feat: 增加 flash comtest 测试项"

# 带正文的提交
git commit -m "fix: 修复 OTP 锁定后测试未检测 lock 状态

在阶段2中，flash otptest 锁定后需要验证 region 的 lock 状态，
之前的逻辑直接跳过了状态检测。"
```

---

## 5. `git merge` vs `git rebase`

两者都用于整合分支变更，但对提交历史的影响不同：

| 特性 | `git merge` | `git rebase` |
|------|-------------|--------------|
| 历史记录 | 保留完整分支历史，产生合并节点 | 线性历史，无合并节点 |
| 提交图 | 分叉后汇合，有交叉线 | 干净的一条直线 |
| 冲突处理 | 一次性解决所有冲突 | 逐个 commit 解决冲突 |
| 适用场景 | PR 合并、公共分支 | 保持功能分支更新 |
| 安全性 | 安全，不改写历史 | 改写历史，**不要对已推送的提交 rebase** |

### 典型用法

```bash
# Merge：将功能分支合并到 main（通常由 PR 自动完成）
git checkout main
git merge feature/add-spi-driver

# Rebase：在功能分支上追赶 main 的最新进度
git checkout feature/add-spi-driver
git fetch origin
git rebase origin/main
# 如果有冲突，解决后：
git add .
git rebase --continue
```

> **黄金法则**：只对**本地未推送**的提交执行 rebase，不要 rebase 已推送到远程的公共提交。

---

## 6. 常用 Git 命令速查

### 基础操作

```bash
git status                         # 查看工作区状态
git diff                           # 查看未暂存的修改
git diff --cached                  # 查看已暂存待提交的修改
git log --oneline -20              # 查看最近 20 条提交 (单行)
git log --oneline --graph --all    # 图形化显示所有分支
```

### 分支管理

```bash
git branch                         # 列出本地分支
git branch -a                      # 列出所有分支（含远程）
git checkout -b feature/xxx        # 创建并切换到新分支
git branch -d feature/xxx          # 删除已合并的分支
git branch -D feature/xxx          # 强制删除分支
```

### 暂存与恢复

```bash
git stash                          # 暂存当前未提交的修改
git stash list                     # 查看暂存列表
git stash pop                      # 恢复最近一次暂存并删除记录
git stash apply                    # 恢复但保留暂存记录
```

### 撤销与回退

```bash
git checkout -- <file>             # 丢弃工作区某个文件的修改
git reset HEAD <file>              # 取消暂存（保留修改）
git reset --soft HEAD~1            # 撤销上一次提交（保留修改在暂存区）
git reset --hard HEAD~1            # 彻底回退上一次提交（慎用！丢失修改）
git revert <commit>                # 创建新提交来撤销某次提交（安全）
```

### 远程操作

```bash
git remote -v                      # 查看远程仓库
git fetch origin                   # 拉取远程更新（不合并）
git pull origin main               # 拉取并合并
git push origin feature/xxx        # 推送分支到远程
git push -u origin feature/xxx     # 推送并设置上游跟踪
```

---

## 7. 分支命名规范

保持一致的分支命名能让团队快速理解分支用途：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能开发 | `feature/add-i2c-test` |
| `fix/` 或 `bugfix/` | Bug 修复 | `fix/otp-lock-timeout` |
| `hotfix/` | 紧急线上修复 | `hotfix/serial-crash` |
| `refactor/` | 代码重构 | `refactor/test-framework` |
| `docs/` | 文档更新 | `docs/update-readme` |
| `release/` | 版本发布准备 | `release/v1.2.0` |

---

## 总结建议

- **小团队日常协作** → **功能分支工作流**（首选）
- **复杂版本迭代** → **Gitflow**
- **开源社区贡献** → **Forking 工作流**
- **提交信息** → 遵循 Conventional Commits 规范
- **保持分支更新** → 优先使用 `rebase` 而非 `merge`
