# Jev API 示例（Optio）

[![Website](https://img.shields.io/badge/Website-jevai.website-10b981)](https://jevai.website)
[![Playground](https://img.shields.io/badge/Playground-免费试用-34d399)](https://jevai.website/playground)
[![API Docs](https://img.shields.io/badge/Docs-v1%2Fsystemone-gray)](https://jevai.website/docs)
[![Pricing](https://img.shields.io/badge/Pricing-%2410%20%2F%2010万积分-gray)](https://jevai.website/pricing)

通过 **Optio** 调用 **Jev** 决策模型的复制即用示例。Optio 是独立运营的接入网关。Jev 返回类型化的决策——`choice`、`score` 和 yes/no（`noul`），并带校准概率。它不写文章，这正是它的用途。

> Optio 是独立运营的 Jev 调用网关，与 TypeSafe 无关联、未经其认可，也不是其官方产品。Jev 是其所有者的商标。

[English README](README.md)

## 目录内容

| 路径 | 内容 |
|---|---|
| [`examples/curl.sh`](examples/curl.sh) | 一个 yes/no 决策的 curl 示例 — 最小可用请求 |
| [`examples/python.py`](examples/python.py) | 工单分诊：choice + score + yes/no 一次请求，含重试与置信度阈值 |
| [`examples/javascript.mjs`](examples/javascript.mjs) | 相同分诊结构的纯 Node 版本（零依赖） |
| [`skills/jev/SKILL.md`](skills/jev/SKILL.md) | 可安装的 Agent 技能 — `npx skills add sunflower225/jev-api-examples`（或复制进你的 agent skills 目录） |

## 60 秒快速开始

```bash
# 1. 拿 key：到 https://jevai.website 注册 — 送 5 个免费积分，无需信用卡
export JEV_API_KEY="jev_live_your_key"

# 2. 发出第一个决策请求
curl https://jevai.website/api/v1/systemone \
  -H "Authorization: Bearer $JEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "The payments webhook failed twice overnight. Should I wake up the on-call engineer?",
    "questions": {
      "page": {
        "type": "noul",
        "instructions": "Should someone be paged right now?",
        "criteria": {
          "true": "Revenue-impacting or data loss",
          "false": "Can wait until morning"
        }
      }
    }
  }'
```

响应按问题名返回 `answers`，并带 `usage.credits` 和 `latency_ms`。

```json
{
  "request_id": "req_fe17d05411092c4f7f97947a",
  "model": "jev-1.13.0",
  "answers": { "page": { "type": "noul", "noul": 0.91 } },
  "usage": { "input_tokens": 128, "output_tokens": 21, "credits": 1 },
  "latency_ms": 432
}
```

## 心智模型

- **`state`** — 决策所依据的工单、表单或工具调用。字符串、字符串数组或 JSON 对象，最多 100,000 字符。
- **`questions`** — 1 到 8 个命名问题。答案空间预先声明（`choice`：2–20 个选项；`score`：2–10 级），输出始终落在你的类型里。
- **你的代码基于 `answers` 和概率分支** — 路由、拦截或转人工都由阈值决定。Jev 只做判断，策略留在你的代码里。

错误一律返回 `{error: {code, message, request_id}}`。对 `429` / `502` / `529` 做退避重试；`401` / `402` / `422` 不改请求不要重试。

## 成本

1 积分覆盖 1,000 输入 token（每次请求最低 1 积分；输出 token 免费）。典型短决策花费 1 积分 — Starter 10 美元 10 万积分下约 $0.0001。积分永不过期，失败请求不计费。[完整定价 →](https://jevai.website/pricing)

## 没有 key 也能试

[免费 Playground](https://jevai.website/playground) 在浏览器里运行真实模型：匿名每天 30 次，登录 50 次。你在那里看到的 JSON 就是服务器要发送的 JSON。

## 链接

- 文档：https://jevai.website/docs
- Playground：https://jevai.website/playground
- 定价：https://jevai.website/pricing
- 用例：https://jevai.website/use-cases
- 支持：support@jevai.website
