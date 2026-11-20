# AutoTest Pro（Python 版）

一个**从 0 到 1 搭建**的接口自动化测试框架。核心目标：让接口用例用 YAML 描述，框架负责解析、变量关联、断言、执行与报告，测试结果全部来自真实 HTTP 调用。

> 说明：这是本人独立设计与实现的个人练习项目，未包装成企业生产平台。

## 技术栈

Python 3 · requests · PyYAML · pytest · 标准库 http.server（内置 Mock API）· ThreadPoolExecutor

## 核心能力

| 能力 | 说明 |
|---|---|
| YAML 用例 DSL | `request` / `assertions` / `extract` / `variables` / `dataSource` 五段式描述 |
| 变量上下文 | `${var}` 占位符替换，支持父子作用域；**未知变量原样保留**，便于排错 |
| 参数关联 | 上游用例 `extract` 的 token/orderId 自动注入下游用例 |
| 结构化断言 | status_code / json_path / body_contains / response_time，支持 eq/ne/gt/gte/lt/lte/contains/not_null |
| JSONPath 读取 | 自研轻量读取器，支持 `$.data.token`、`$.data[0].id` |
| 数据驱动 | CSV 多行自动展开为多条用例 |
| 依赖感知调度 | 有 `${...}` 依赖或 `extract` 的用例走顺序组；无依赖用例才并发，避免上下文串味 |
| 双格式报告 | HTML + JSON，含每条断言的 expected / actual 与真实响应耗时 |
| 内置 Mock API | 标准库实现 login / orders / products / health，动态端口，零外部依赖 |
| 安全细节 | YAML 使用 `safe_load`；日志对 Authorization 头脱敏；HTTP 5s 超时 |

## 快速开始

```bash
pip install -r requirements.txt
python run_demo.py sequential      # 顺序执行
python run_demo.py parallel        # 并发执行
python -m pytest                   # 单元测试
```

运行结束后生成 `reports/report.html` 与 `reports/report.json`。

## 实测结果

本地一次顺序执行的真实输出（非编造）：

```
Total=8 Passed=8 Failed=0 PassRate=100.0% Duration=~60ms
```

## 设计要点

1. **为什么有依赖的用例必须顺序执行**：并发 worker 各自持有子上下文，若 login 在子上下文提取 token，create_order 在另一个子上下文里读不到。因此含 `${...}` 或 `extract` 的用例强制走顺序组，共享同一 VariableContext。
2. **未知变量为何原样保留**：`${missing}` 若被替换成空串，请求会静默发出错误参数；保留原样能让测试者一眼发现配置缺失。
3. **断言的 expected/actual 全量落报告**：失败时能直接看到期望值与实际响应，不需要复现。
4. **报告数字全部运行时测量**：响应耗时用 `time.perf_counter()`，不写死任何性能数据。

## 姊妹项目

TestHub（自动化测试管理平台）会调用本框架的 CLI 执行用例，解析 `report.json` 回填平台统计与质量门禁。
