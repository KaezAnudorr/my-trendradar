"""Self-contained source-card reading layout for generated reports."""

STYLE = r"""
<style id="source-dashboard-style">
body { --paper:#fff; --canvas:#f6f7f9; --ink:#24262d; --muted:#858a95; --line:#eceef1; --accent:#ed5b54;
 background:var(--canvas)!important; color:var(--ink); font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif; }
body.dark-mode { --paper:#22252c; --canvas:#17191f; --ink:#eceef3; --muted:#9ba1ae; --line:#343842; --accent:#ff8178; }
body .container, body.wide-mode .container { max-width:1480px; width:100%; margin:0 auto; padding:36px 40px; background:none; box-shadow:none; border-radius:0; }
body .header { background:none!important; color:var(--ink); padding:0 0 24px; border-radius:0; box-shadow:none; overflow:visible; }
.header-watermark,.toggle-wide-btn { display:none!important; }
body .header-title { color:var(--ink); font-size:29px; font-weight:750; letter-spacing:-1px; text-align:left; padding-left:52px; margin:0 0 8px; line-height:42px; }
.header-title:before { content:'T'; position:absolute; left:0; top:0; width:40px; height:40px; border-radius:13px; background:#ed5b54; color:white; text-align:center; font-size:26px; font-weight:800; letter-spacing:-2px; }
.dashboard-subtitle { margin:0 0 24px 52px; color:var(--muted); font-size:13px; text-align:left; }
body .save-buttons { position:absolute; top:2px; right:0; left:auto; width:auto; justify-content:flex-end; gap:8px; }
body .save-btn,body .save-dropdown-trigger,body .toggle-dark-btn { background:var(--paper)!important; color:var(--ink)!important; border:1px solid var(--line); border-radius:9px; height:36px; box-shadow:none; }
body .header-info { display:flex; flex-wrap:wrap; gap:10px 26px; margin:0; padding:17px 22px; border:1px solid var(--line); border-radius:13px; background:var(--paper); }
body .info-item { display:flex; align-items:baseline; gap:9px; padding:0; min-width:0; flex:none; }
body .info-label { color:var(--muted)!important; font-size:12px; margin:0; }
body .info-value { color:var(--ink)!important; font-size:14px; font-weight:650; }
body .content { padding:0; background:none; }
.dashboard-toolbar { display:flex; align-items:center; justify-content:space-between; gap:16px; margin:0 0 24px; }
.dashboard-filters { display:flex; gap:6px; flex-shrink:0; }
.dashboard-filters button { border:0; background:transparent; color:var(--muted); font:inherit; font-size:14px; padding:10px 17px; border-radius:9px; cursor:pointer; }
.dashboard-filters button[aria-pressed="true"] { background:var(--ink); color:var(--paper); font-weight:650; }
body .search-bar { display:block!important; width:300px; margin:0; padding:0; }
body .search-input { width:100%; background:var(--paper)!important; color:var(--ink)!important; border:1px solid var(--line)!important; border-radius:10px; padding:11px 15px; font-size:13px; box-shadow:none; }
.dashboard-section-label { display:flex; align-items:baseline; gap:12px; font-size:18px; font-weight:700; margin:6px 0 17px; color:var(--ink); }
.dashboard-section-label span { font-size:12px; color:var(--muted); font-weight:400; }
body .rss-section { margin:0 0 34px; padding:0; border:0; background:none!important; }
body .rss-section-header { display:none; }
body .rss-feeds-grid,.dashboard-hot-grid { display:grid!important; grid-template-columns:repeat(3,minmax(0,1fr)); gap:20px; margin:0 0 32px; }
body .feed-group,body .word-group { display:flex; flex-direction:column; min-width:0; margin:0!important; padding:0!important; border:1px solid var(--line)!important; border-radius:15px; background:var(--paper)!important; box-shadow:0 3px 14px #20273503; overflow:hidden; }
body .feed-header,body .word-header { display:flex; align-items:center; padding:19px 20px 16px!important; margin:0!important; border-bottom:1px solid var(--line)!important; background:none!important; cursor:default; gap:10px; min-height:65px; }
body .feed-name,body .word-name { color:var(--ink)!important; font-size:16px; font-weight:700; line-height:24px; }
body .feed-name:before,body .word-name:before { content:attr(data-initial); display:inline-flex; align-items:center; justify-content:center; background:var(--canvas); color:var(--source-color); width:29px; height:29px; border-radius:9px; margin-right:9px; font-size:14px; vertical-align:middle; }
body .feed-count,body .word-count { margin-left:auto; white-space:nowrap; background:none!important; color:var(--muted)!important; font-size:12px; font-weight:400; }
body .word-info { display:flex; width:100%; align-items:center; }
.word-index,.tab-bar-wrapper { display:none!important; }
.source-list { height:364px; overflow:auto; padding:4px 19px; scrollbar-width:thin; scrollbar-color:var(--line) transparent; overscroll-behavior:contain; }
body .rss-item,body .news-item { display:grid; grid-template-columns:23px minmax(0,1fr); column-gap:10px; padding:13px 0!important; margin:0; border:0!important; border-bottom:1px solid var(--line)!important; background:none!important; border-radius:0; }
.source-rank,body .news-number { grid-column:1; grid-row:1 / span 2; width:21px; height:21px; margin:2px 0 0!important; border-radius:6px; color:#969ba5!important; background:var(--canvas)!important; font-size:11px; font-weight:650; text-align:center; line-height:21px; padding:0; flex:none; }
.source-list>:nth-child(1) .source-rank,.source-list>:nth-child(1) .news-number { background:#fff0ef!important; color:#e9524b!important; }
.source-list>:nth-child(2) .source-rank,.source-list>:nth-child(2) .news-number { background:#fff3e7!important; color:#ed943e!important; }
.source-list>:nth-child(3) .source-rank,.source-list>:nth-child(3) .news-number { background:#fff8dd!important; color:#c5a12c!important; }
body .rss-title,body .news-content { grid-column:2; grid-row:1; min-width:0; margin:0; }
body .rss-link,body .news-link { font-size:14px; line-height:1.7; font-weight:450; color:var(--ink)!important; text-decoration:none; }
body .rss-link:hover,body .news-link:hover { color:var(--accent)!important; }
body .rss-meta { grid-column:2; grid-row:2; margin:5px 0 0; font-size:11px; color:var(--muted); }
body .rss-author { display:none; }
body .news-header { margin:0 0 4px; font-size:11px; color:var(--muted); }
body .news-title { margin:0; }
body .rss-time,body .time-info { color:var(--muted)!important; }
body .badge-new { background:none!important; color:var(--accent)!important; font-size:9px; padding:0; }
.source-footer { display:flex; justify-content:space-between; align-items:center; padding:12px 20px; font-size:11px; color:var(--muted); border-top:1px solid var(--line); }
.source-expand { border:0; background:none; color:var(--muted); font-size:12px; cursor:pointer; padding:3px 0 3px 8px; }
.source-expand:hover { color:var(--accent); }
.source-expanded .source-list { height:auto; max-height:none; }
body .word-group.collapsed .news-item { display:grid; }
body.exporting-report .source-list { height:auto; overflow:visible; }
body.exporting-report .dashboard-toolbar,body.exporting-report .source-expand { display:none!important; }
body .section-divider { border-top:0; padding-top:0; }
.dashboard-empty { padding:45px 0; color:var(--muted); text-align:center; }
[hidden] { display:none!important; }
body .footer { border-top:1px solid var(--line); background:none!important; color:var(--muted); margin:24px 0 0; padding:22px 0; }
body .ai-section { border:1px solid var(--line); border-radius:15px; overflow:hidden; background:var(--paper); margin:0 0 24px; }
@media(min-width:1500px) { body .container,body.wide-mode .container { max-width:1640px; } body .rss-feeds-grid,.dashboard-hot-grid { grid-template-columns:repeat(4,minmax(0,1fr)); } }
@media(max-width:1050px) { body .rss-feeds-grid,.dashboard-hot-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } body .container,body.wide-mode .container { padding:28px 24px; } }
@media(max-width:650px) { body .container,body.wide-mode .container { padding:23px 16px; } body .header-title { font-size:24px; } .dashboard-subtitle { font-size:11px; max-width:200px; } body .save-buttons { top:5px; } body .save-btn-group { display:none; } body .header-info { gap:12px 20px; padding:15px; } body .info-label { font-size:11px; } body .info-value { font-size:12px; } .dashboard-toolbar { flex-direction:column; align-items:stretch; gap:13px; } body .search-bar { width:100%; } .dashboard-filters button { padding:9px 14px; } body .rss-feeds-grid,.dashboard-hot-grid { grid-template-columns:minmax(0,1fr); gap:16px; } .source-list { height:345px; } }
@media print { .source-list { height:auto; overflow:visible; } .dashboard-toolbar,.source-expand { display:none!important; } }
</style>
"""

SCRIPT = r"""
<script id="source-dashboard-script">
document.addEventListener('DOMContentLoaded', function() {
    document.title = 'TrendRadar · 我的资讯';
    document.querySelector('.header-title').textContent = '我的资讯';
    const subtitle = document.createElement('p');
    subtitle.className = 'dashboard-subtitle';
    subtitle.textContent = 'TrendRadar / 按来源，发现值得读的内容';
    document.querySelector('.header-title').after(subtitle);
    const content = document.querySelector('.content');
    const toolbar = document.createElement('div');
    toolbar.className = 'dashboard-toolbar';
    toolbar.innerHTML = '<nav class="dashboard-filters" aria-label="资讯类型"><button data-kind="all" aria-pressed="true">全部资讯</button><button data-kind="rss" aria-pressed="false">RSS 订阅</button><button data-kind="hot" aria-pressed="false">热榜</button><button data-kind="ai" aria-pressed="false">AI 简报</button></nav>';
    toolbar.append(document.querySelector('.search-bar'));
    content.prepend(toolbar);
    const hotGrid = document.createElement('div');
    hotGrid.className = 'dashboard-hot-grid';
    document.querySelectorAll('.word-group[data-tab-index]').forEach(card => hotGrid.append(card));
    document.querySelectorAll('.tab-bar-wrapper').forEach(tabs => tabs.remove());
    document.querySelectorAll('.hotlist-section').forEach(section => section.remove());
    const hotLabel = document.createElement('h2');
    hotLabel.className = 'dashboard-section-label';
    hotLabel.innerHTML = '热门榜单 <span>完整榜单 · 推送仅新增</span>';
    toolbar.after(hotLabel, hotGrid);
    const rssSections = Array.from(document.querySelectorAll('.rss-section'));
    rssSections.forEach(section => {
        const label = document.createElement('h2');
        label.className = 'dashboard-section-label';
        label.innerHTML = '我的订阅 <span>文章按时效筛选 · 榜单为当前快照</span>';
        section.prepend(label);
        hotLabel.before(section);
    });
    const colors = ['#e36558','#429c88','#638cce','#bb8c45','#9774be','#49a1b0'];
    const cards = Array.from(document.querySelectorAll('.feed-group,.word-group[data-tab-index]'));
    cards.forEach((card, index) => {
        card.classList.remove('collapsed');
        card.style.display = '';
        const name = card.querySelector('.feed-name,.word-name');
        card.dataset.sourceName = name.textContent.trim();
        name.dataset.initial = Array.from(card.dataset.sourceName)[0];
        card.style.setProperty('--source-color', colors[index % colors.length]);
        card.dataset.kind = card.classList.contains('feed-group') ? 'rss' : 'hot';
        const list = document.createElement('div');
        list.className = 'source-list';
        list.tabIndex = 0;
        list.setAttribute('aria-label',card.dataset.sourceName + '资讯列表');
        Array.from(card.querySelectorAll('.rss-item,.news-item')).forEach((item,i) => {
            if (item.classList.contains('rss-item')) {
                const rank = document.createElement('span');
                rank.className = 'source-rank';
                rank.textContent = i + 1;
                item.prepend(rank);
            }
            list.append(item);
        });
        card.append(list);
        const footer = document.createElement('div');
        footer.className = 'source-footer';
        const count = document.createElement('span');
        count.textContent = list.children.length + ' 条资讯';
        const expand = document.createElement('button');
        expand.className = 'source-expand';
        expand.textContent = '展开阅读 ↗';
        expand.setAttribute('aria-expanded','false');
        expand.addEventListener('click', () => {
            const expanded = card.classList.toggle('source-expanded');
            expand.textContent = expanded ? '收起 ↑' : '展开阅读 ↗';
            expand.setAttribute('aria-expanded',String(expanded));
        });
        footer.append(count, expand);
        card.append(footer);
    });
    const ai = document.querySelector('.ai-section');
    const empty = document.createElement('div');
    empty.className = 'dashboard-empty';
    empty.hidden = true;
    content.append(empty);
    let kind = 'all';
    const search = document.querySelector('.search-input');
    search.removeAttribute('oninput');
    search.placeholder = '搜索标题或消息来源…';
    search.setAttribute('aria-label','搜索标题或消息来源');
    function filter() {
        const query = search.value.trim().toLowerCase();
        let visible = 0;
        cards.forEach(card => {
            let matches = 0;
            card.querySelectorAll('.rss-item,.news-item').forEach(item => {
                const title = item.querySelector('.rss-title,.news-title').textContent;
                item.hidden = !(card.dataset.sourceName + ' ' + title).toLowerCase().includes(query);
                if (!item.hidden) matches++;
            });
            card.hidden = !matches || (kind !== 'all' && kind !== card.dataset.kind);
            if (!card.hidden) visible++;
        });
        rssSections.forEach(section => { section.hidden = !Array.from(section.querySelectorAll('.feed-group')).some(card => !card.hidden); });
        hotGrid.hidden = !Array.from(hotGrid.children).some(card => !card.hidden);
        hotLabel.hidden = hotGrid.hidden;
        if (ai) ai.hidden = (kind !== 'all' && kind !== 'ai') || (!!query && !ai.textContent.toLowerCase().includes(query));
        empty.hidden = visible > 0 || (ai && !ai.hidden);
        empty.textContent = kind === 'ai' && !ai ? '本次快照未生成 AI 简报。' : '没有匹配的内容，换个关键词试试。';
    }
    toolbar.querySelectorAll('[data-kind]').forEach(button => button.addEventListener('click', () => {
        kind = button.dataset.kind;
        toolbar.querySelectorAll('[data-kind]').forEach(other => other.setAttribute('aria-pressed',String(other === button)));
        filter();
    }));
    search.addEventListener('input',filter);
    filter();
});
</script>
"""
