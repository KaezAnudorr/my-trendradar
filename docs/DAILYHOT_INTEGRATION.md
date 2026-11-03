# DailyHotApi 接入验证

## 结论：适合与 TrendRadar 在同一个 Actions job 中临时运行

不需要另购常驻服务器。每次定时任务先启动 DailyHotApi，TrendRadar 通过本机 RSS 地址读取数据，生成报告后结束服务。它不会提供全天在线的公共 API。

当前仅验证可行性，未把新增源加入正式订阅。现有 15 个 RSS 源、来源分组、豆瓣移除及 AI/推送开关保持原配置。

## 实测结果

测试日期：2026-11-03。
上游版本：imsyy/DailyHotApi@36c77e3bd891c11642d314cfb229bf31646704de。
[Actions 验证记录](https://github.com/KaezAnudorr/my-trendradar/actions/runs/41606559825)。

文档公共实例 api-hot.imsyy.top 在 GitHub Actions 上无法解析域名，16 条候选路由全部无法访问。

同一个 Actions 中构建并临时运行上游项目，检测 RSS XML、非空标题和 HTTP(S) 文章链接：

| 路由 | 条目 | 结果 |
|---|---:|---|
| guokr | 30 | 通过 |
| ifanr | 20 | 通过 |
| geekpark | 20 | 通过 |
| 51cto | 50 | 通过 |
| hellogithub | 20 | 通过 |
| yystv | 12 | 通过 |
| weread | 20 | 通过 |
| smzdm | 50 | 通过 |
| github | 15 | 通过 |
| huxiu | 20 | 通过 |
| 36kr | 50 | 通过 |
| csdn | — | HTTP 500 |
| linuxdo | — | HTTP 500 |
| producthunt | — | HTTP 500 |
| gameres | 0 | 空订阅 |
| hackernews | 30 | 28 条有合格链接，2 条不合格，未列为完整通过 |

“通过”表示本次实际抓取通过，不保证后续持续可用；这里未执行 TrendRadar 完整抓取到推送的新增源集成测试。

## 推荐接入方式

1. 在现有抓取 job 中检出固定版本 DailyHotApi，安装依赖、构建。
2. 临时启动服务并检查就绪。
3. 用 RSS 地址，例如 `http://127.0.0.1:6688/ifanr?rss=true`，配置新增来源。
4. 在同一个 job 中运行 TrendRadar，复用现有 RSS、报告、AI 和通知路径。
5. 任务结束关闭临时服务。

优先考虑爱范儿、极客公园、HelloGitHub、游研社、果壳；已有 GitHub 趋势、虎嗅、36氪的来源不应直接重复加入。

## 时间含义必须区分

上游 `src/utils/getRSS.ts` 将 RSS 项目的发布时间设置为接口 `updateTime`，并非每篇文章原始发布时间。因此这类源应作为“热榜快照”，不能直接解释为“最近三天发表的文章”。接入时需与现有文章型 RSS 的时效含义区分，避免旧文章持续被刷新为新文章。

项目文档：https://github.com/imsyy/DailyHotApi
GitHub runner 文档：https://docs.github.com/en/actions/concepts/runners/github-hosted-runners
