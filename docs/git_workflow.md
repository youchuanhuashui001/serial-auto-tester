在实际开发中，Git 的工作流程会根据团队规模和项目需求有所不同。作为开发者，掌握最基础且最被广泛使用的几种工作流，能让你在绝大多数团队中游刃有余。

以下是三种最常见的 Git 工作流程：

### 1. 功能分支工作流 (Feature Branch Workflow) —— 行业最通用

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


3. **开发与提交**：在分支上编写代码，并进行多次逻辑清晰的提交。（*如果你中途需要切换分支，就可以用到你刚才问的 `git stash` 来暂存未完成的代码*）。
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


6. **代码审查与合并**：团队成员 Review 代码后，将该分支合并入 `main`，随后可以删除该功能分支。

---

### 2. Gitflow 工作流 (适用于大型、有固定发布周期的项目)

Gitflow 是一种非常严格的分支模型，适合需要进行复杂版本控制和定期发布产品的团队。它定义了五种主要分支：

* **`master` / `main**`：永远只存储随时可以发布到生产环境的代码。
* **`develop`**：日常开发的主分支，包含所有下一次发布需要的功能。
* **`feature/...`**：基于 `develop` 创建，用于开发新功能，完成后合并回 `develop`。
* **`release/...`**：基于 `develop` 创建，用于准备发布新版本（主要用来修 Bug、改版本号），完成后同时合并进 `master` 和 `develop`。
* **`hotfix/...`**：基于 `master` 创建，用于紧急修复生产环境的 Bug，完成后同时合并进 `master` 和 `develop`。

---

### 3. Forking 工作流 (开源社区/跨团队合作)

这种工作流主要用于开源项目或权限控制极其严格的内部大团队。开发者没有直接向主仓库推送代码的权限。

**标准操作步骤：**

1. 在网页端将官方主仓库 **Fork** 到自己的个人账户下。
2. `git clone` 自己账号下的仓库到本地。
3. 添加官方主仓库为上游（Upstream）：`git remote add upstream <官方仓库地址>`。
4. 本地创建分支，开发并推送到**自己的**远程仓库。
5. 在网页端向官方主仓库发起 **Pull Request (PR)**。
6. 定期拉取上游代码保持同步：`git pull upstream main`。

---

**总结建议：**
如果你是在日常工作中小团队协作，**功能分支工作流**是首选；如果你参与了复杂的固件或软件版本迭代，**Gitflow** 更合适。

你需要我详细说明一下在合并代码时，**`git merge` 和 `git rebase` 的具体区别和使用场景**吗？或者你想了解如何编写规范的 Commit Message 格式？
