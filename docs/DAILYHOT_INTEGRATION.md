# 消息源选择与 DailyHot 接入

## 在现有 Actions 中读取新增来源

定时抓取会临时构建并运行固定版本 DailyHotApi，将选定来源转换为 TrendRadar 已支持的 JSON Feed，再与现有 RSS 一起生成报告。无需常驻服务器，任务结束后临时服务随 runner 退出。

- 基础订阅：15 个，仍保存在 `config/config.yaml`。
- DailyHot 补充：11 个，配置在 `integrations/dailyhot/feeds.yaml`。
- 默认来源总数：26 个 RSS/JSON Feed，另有原来的 11 个热榜平台。
- AI、通知开关没有开启；手动 AI/飞书测试工作流也使用相同新增源。
- 豆瓣不加入。DailyHot 的 CSDN、LinuxDo、Product Hunt、GameRes 等失败或空源不加入。

## 重复来源按内容完整度选，而不是按条数硬替换

2026-11-03 在同一 GitHub Actions runner 中对比；下表是接口返回数量，尚未经过现有文章时效过滤。

| 来源 | 对比结果 | 正式选择 |
|---|---|---|
| IT之家 | 旧 RSSHub 10 条；DailyHot 48 条但仅 39 个不同链接，抽查链接返回 404；官方 RSS 60 条，均有摘要和发布时间 | 改用官方 RSS，保留原 feed ID 和 1 天时效 |
| Hacker News | 旧原生源默认 20 条；DailyHot 返回 30 条，其中 28 条有 HTTP(S) 链接，缺文章时间及摘要；原生源 count=30 实测 30 条且元数据完整 | 原生源扩到 30 条 |
| GitHub 趋势 | 两边同样 15 个仓库；现有源保留 owner/repo 完整名称，15 条有描述，DailyHot 14 条有描述 | 保留现有源，不重复加 |
| V2EX 热门 | 两边都是相同的 9 个帖子；现有源有发布时间，DailyHot 无 | 保留现有源 |
| 知乎日报 | 两边都是相同的 4 篇；现有源有摘要和时间，DailyHot 无 | 保留现有源 |
| 少数派 | 最新文章 10 条与热门精选 40 条不重合；热门精选含较早发表的文章 | 保留最新源，并单独加入热门精选快照 |
| 36氪 | 现有 20 条是 newsflashes 快讯；DailyHot 50 条是 /p/ 人气文章，不重合 | 两个栏目互补，分别保留 |
| 虎嗅 | 现有 20 条是前沿科技文章；DailyHot 20 条是 /moment/ 24 小时快讯，不重合 | 两个栏目互补，分别保留 |
| 掘金 | 现有 12 条为 AI 编程栏目，有摘要和时间；DailyHot 50 条为泛开发热榜，缺摘要和时间 | 保留现有 AI 编程源，不用泛榜替代 |

[九组对比及逐篇证据](https://github.com/KaezAnudorr/my-trendradar/actions/runs/41608730077)。
[官方 RSS、HN 扩容和 IT 链接的补充实测](https://github.com/KaezAnudorr/my-trendradar/actions/runs/41609565315)。

## 新增的 11 个来源

果壳、爱范儿、极客公园、51CTO、HelloGitHub、游研社、微信读书、什么值得买，以及少数派热门精选、36氪人气文章、虎嗅24小时快讯。

新增源在名称中标注“快照”。文章型原生 RSS 继续按原来的 1/3/7 天时效筛选；快照源展示当前榜单，`max_age_days: 0`，保留全部条目，不把旧发表时间与“仍在榜”混淆。

## 保留原始元数据，不伪造发布时间

上游 RSS 模式把每条文章的 pubDate 都设为接口更新时间。这里改读 JSON 数据，以 `timestamp` 中的文章时间生成 `date_published`；上游没有提供文章时间时留空，不用抓取时间填充。摘要、作者、原文链接会保留，同源重复链接去重，空标题或非 HTTP(S) 链接不加入。

每个来源导出后，使用 TrendRadar 自身 RSSParser 检查条目没有丢失，再启用到本次 runner 的配置中。永久配置不写入 localhost 地址，因此原来的本地/Docker 入口仍可读取原先 15 个来源。

## 查看运行结果或调整来源

- 新增列表：`integrations/dailyhot/feeds.yaml`，删除一行即可取消一个新增源。
- 共用 Actions：`.github/actions/dailyhot/action.yml`。
- 转换及运行时配置：`tools/dailyhot_feeds.py`。
- 在抓取任务的 Artifacts 下载 `dailyhot-integration`，其中 `integration-results.json` 包含每个来源的实际条数、时间覆盖和失败原因，其他 JSON 是本次可复查的原始订阅快照。
- 单源失败会产生 Actions warning，跳过该新增源，保留现有订阅；DailyHot 启动失败也会明确告警。
- 手动 AI/飞书测试仅由 workflow_dispatch 触发，修改工作流不再自动调用模型或发送消息。
- 上游固定在 `imsyy/DailyHotApi@36c77e3bd891c11642d314cfb229bf31646704de`。

项目文档：https://github.com/imsyy/DailyHotApi
HN count 参数：https://hnrss.github.io/
