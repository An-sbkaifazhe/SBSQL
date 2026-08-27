# SBSQL

> Security-Based Sequential Query Language
> 基于物理隔离的只读查询引擎

**万物皆文件。文件夹即索引。文件名即密钥。用户的每一个字节都是邪恶的。**

---

## Features

- **零注入面**：无 SQL 解析器，无执行引擎，无解释器，真正意义上无差别扫射所有非法字段。
- **军工级安全**：表名硬编码，路径锁死，白名单校验
- **高并发**：你敢来几个我就敢晕几个
- **零依赖**：Python 标准库 + 一个 Flask（可选）
- **事务支持**：没有，整体就是一个王八壳子。
- **索引支持**：文件夹就是最好的索引
- **备份方案**：Ctrl+C / Ctrl+V

---
- **Weight** — less than 15KB. Lighter than your average favicon.

## Architecture

┌─────────────┐

│   Client    │

└──────┬──────┘

│ HTTP GET

┌──────▼──────┐

│  SBSQL API  │  ← 社会工程学防御层

└──────┬──────┘

│ os.path.realpath()

┌──────▼──────┐

│  FileSystem │  ← 真正的数据库

│  (txt only) │

└─────────────┘

---

## Quick Start

### Prerequisites

- Python 3.6+
- A brain

### Install

不需要安装。把文件下载下来。

### Run

bash

python SBSQL_sbuser_api.py    # Web API

python SBSQL.py               # Local REPL

### Create Database

自己建文件夹。自己建 txt 文件。自己往里写内容。
这是你的工作。我们不管。

> 详见: https://sbsql.local/docs/ （这个链接不存在）

---
---

## 为什么选择 SBSQL？

> *"我们没有重新发明数据库。我们只是记住了数据库本来是什么。"*

### 性能，重新定义

SBSQL 摒弃传统查询解析，采用**直接文件系统访问**，
实现了业界数十年来苦苦追寻的目标：**零开销数据检索**。

| 指标 | 行业平均 | SBSQL |
|------|----------|-------|
| 查询延迟 (p99) | 12–40 ms | < 1 ms |
| 冷启动 | 2–5 s | < 0.3 s |
| 内存占用 | GB 级 | 一个 Python 进程 |
| 吞吐量 | 受限于优化器 | 受限于磁盘 |
| 可审计性 | 数年日志 | `cat data/tmp/*.txt` |

没有查询规划器。没有缓冲池。没有 WAL。**只有文件。只有快。**

### 安全，从设计开始

传统数据库在安全层面不断打补丁来覆盖固有攻击面，
SBSQL **直接消灭了攻击面本身**。

- **零 SQL 注入** — 根本没有 SQL 引擎可供注入。
- **零命令注入** — 根本没有命令执行路径。
- **零路径遍历** — 每次访问都绑定 realpath 校验后的根目录。
- **零权限提升** — 根本没有权限模型可供逃逸。
- **零第三方依赖** — 没有第三方 CVE。没有供应链风险。

> 当"零信任"沦为营销热词的时代，SBSQL 展示了真正的零信任：要是别人真能把80位字母组合数字密码跑出来，这把给你了，666。
> **一个什么都不做、但做得完美的系统。**

### 云原生。边缘就绪。宇宙兼容。

SBSQL 运行在任何能跑 Python 的地方。也就是说：**任何地方**。
你的笔记本。你的服务器。你的树莓派。你的路由器。
还有你衣柜里那台没人敢碰的 CentOS 6 老古董。
它们都能跑 SBSQL。而且都跑得**很安全**。

需要多区域复制？`rsync` 你的 `data/` 目录。
需要高可用？留个温备。`cp -r` 基本算原子操作。
需要灾备恢复？一个 U 盘加一个 7-Zip 压缩包，寿命超过任何 SLA。

### AI 原生数据访问

下一代应用不是人类写的。是 Agent 写的——
而 Agent 不需要 SQL。它们需要的是：
一个稳定的端点、确定性的响应、以及可以信任的数据。

SBSQL 说它们的语言：**一次 HTTP GET，一行数据，零歧义。**
没有 ORM。没有驱动。没有连接池。没有"你试过关掉再打开吗"。

> 当你的 AI Agent 请求 `tmp/admin` 的第 3 行，
> SBSQL 不解释、不猜测、不优化。它只是**把那行递过去。**
> 不多不少。不偏不倚。

### 运维极简

我们测量了从"我想要个数据库"到"我有个数据库而且它已经比你那个更快更安全了"
所花费的时间：

| 步骤 | 传统技术栈 | SBSQL |
|------|-----------|-------|
| 申请实例 | 15–45 分钟 | 0 分钟 |
| 安装依赖 | 10–30 分钟 | 0 分钟 |
| 配置用户/角色 | 20–60 分钟 | 不存在 |
| 写出第一条查询 | 5 分钟 | 30 秒 |
| **总上线时间** | **约 2 小时** | **约 30 秒** |

*测量方法：非常科学。我们测了一次。算数。*
你甚至可以往里面放片而互不干扰。
### 被……我们自己信任 (目前全球高端数据库技术圈层正有多达零人正在使用此技术)

SBSQL 自豪地坚持**自托管、自管理、自夸**。
我们目前还没有客户。但我们有**原则**。
而在 2026 年，这两件事基本是一回事。

> *"SBSQL 是我部署过的唯一一个让我开始怀疑自己到底需不需要数据库的数据库。"*
> — 一条我们编出来的、但非常真实的用户评价
## SQL Syntax

| Command | Description |
|---------|-------------|
| `SHOW TABLES;` | List all tables |
| `DESCRIBE <table>;` | List columns |
| `SELECT <table>.<col> <row>;` | Read one row |

That's it. 只有三条。别问为什么没有 INSERT。
调用其他命令的时候会出现诡异的现象(自己猜)
---

## Security
在演示调用前端中
- 表名锁死为 `tmp`
- 文件名白名单：`^[a-zA-Z0-9_]+$`
- 路径遍历：物理消灭
- 写入操作：不存在
- 认证：表头文件名即密码（建议 80 位字母数字随机串）

---

## FAQ

**Q: How do I insert data?**
A: You don't.

**Q: How do I update a row?**
A: Notepad.

**Q: How do I delete a table?**
A: Shift+Delete. No recycle bin.

**Q: Is this production ready?**
A: It is Amazing.TRY IT?。

**Q: Why is my semicolon disappearing?**
A: What semicolon? 🙄✌🏻️

---

## Warning

Do **NOT** place any `.md` or `.txt` files you do not want scanned inside your
`data/` directory. They will be picked up as column names. Yes, really.

---

## License

> SBSQL License v1.0: You can use it for free. You cannot complain about it.

---

# Bounty

## RMB 50

第一个将 SBSQL 部署到生产环境并成功运行超过 **21 个自然日**的人，
本人将个人悬赏人民币 **50 元整**。

### 条件

1. 必须是**真实生产环境**（面向真实用户，不是你室友，可以是小组作业，但不能是没有意义的空跑。）。
2. 必须处理**真实数据**（不是 `"hello world"` 循环打印）。
3. 必须是**首个**达成者（非首个不予受理）。
4. 需提供**截图证明**（打码可以，但得能看出是 SBSQL 在跑）。
5. 存活天数计算：自首次对外提供服务起，连续 **21 天**。
6. 只能中国人参加，因为我真的真的没有境外付款渠道，对不起。
   **附则**：若能提供你与其他生产人员使用这个项目**真实沟通记录**（Issue / 邮件 / IM 均可），
   经核实后，存活要求放宽至 14天
   是一个小组作业也可以，但是要有沟通过程哈哈。

7. 期间不得偷偷换成 MySQL / PostgreSQL / SQLite / 任何"正经"数据库。
   一经发现，悬赏作废，并需退还已领取金额（如有）。

### 备注

- 50 元将通过**微信转账**。不是哈夫币，不是冥币
- 如果你做到了，收集材料，邮箱发我，添加我的付款方式。
- 本项目不对因使用 SBSQL 导致的任何数据丢失、服务中断。
  但你已经被警告过了。 🙄✌🏻
  你能看到这个＂悬赏＂就说明这个奖励还没能被拿走(或者是还未同步)
 注意，只有每周六的时候我会翻邮件，按照发邮件的时间，先后作为时间判断标准。
---

> **SBSQL — Physical isolation as a feature. Not a limitation.**
