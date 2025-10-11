#!/usr/bin/env python3
from pathlib import Path
import re
import datetime as dt
import html

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
ASSETS_DIR = OUT / "assets"

MONTH_DIR_RE = re.compile(r"^20\d{4}$")         # 例: 202501
DAY_FILE_RE  = re.compile(r"^(20\d{6})\.txt$")  # 例: 20250101.txt

STYLE_CSS = """
/* ---------- Base & Theme ---------- */
:root {
  --bg: #ffffff;
  --fg: #1c1c1c;
  --muted: #636a73;
  --border: #e8eaee;
  --accent: #3a86ff;
  --card: #ffffff;
  --shadow: 0 1px 2px rgba(0,0,0,.06), 0 6px 24px -16px rgba(0,0,0,.15);
  --radius: 12px;
  --container: 980px;
  --pad: 18px;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans JP", Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f1115;
    --fg: #e8eef5;
    --muted: #97a0aa;
    --border: #20242b;
    --accent: #7aa2ff;
    --card: #131720;
    --shadow: 0 1px 2px rgba(0,0,0,.5), 0 10px 30px -20px rgba(0,0,0,.6);
  }
}
:root[data-theme="light"] {
  --bg: #ffffff;
  --fg: #1c1c1c;
  --muted: #636a73;
  --border: #e8eaee;
  --accent: #3a86ff;
  --card: #ffffff;
  --shadow: 0 1px 2px rgba(0,0,0,.06), 0 6px 24px -16px rgba(0,0,0,.15);
}
:root[data-theme="dark"] {
  --bg: #0f1115;
  --fg: #e8eef5;
  --muted: #97a0aa;
  --border: #20242b;
  --accent: #7aa2ff;
  --card: #131720;
  --shadow: 0 1px 2px rgba(0,0,0,.5), 0 10px 30px -20px rgba(0,0,0,.6);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--fg);
  background: var(--bg);
  font-family: var(--font);
  line-height: 1.75;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  font-size: clamp(15px, 1.02vw + 12px, 18px);
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
code, pre, kbd, samp { font-family: var(--mono); font-size: .95em; }

/* ---------- Layout ---------- */
.container { max-width: var(--container); margin-inline: auto; padding-inline: var(--pad); }
header.site {
  position: sticky; top: 0; z-index: 50;
  backdrop-filter: saturate(120%) blur(6px);
  background: color-mix(in hsl, var(--bg) 88%, transparent);
  border-bottom: 1px solid var(--border);
}
.site-inner { display: flex; align-items: center; gap: 10px; padding-block: 12px; }
.brand { font-weight: 700; letter-spacing: .2px; }
.brand a { color: inherit; }
.grow { flex: 1; }
.toolbar {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
}
.btn {
  border: 1px solid var(--border);
  background: var(--card);
  border-radius: 999px;
  padding: 6px 12px;
  box-shadow: var(--shadow);
  cursor: pointer;
  color: inherit;
}
.btn:hover { transform: translateY(-1px); }
.btn:active { transform: translateY(0); }

.theme-toggle { font-size: .9rem; }

main { padding-block: 22px 48px; }
footer.site { border-top: 1px solid var(--border); color: var(--muted); }
footer.site .container { padding-block: 28px; font-size: .9rem; }

.skip-link {
  position: absolute; left: -9999px; top: -9999px;
}
.skip-link:focus {
  left: 12px; top: 12px; background: var(--card); padding: 8px 12px; border-radius: 8px;
  outline: 2px solid var(--accent);
}

/* ---------- Components ---------- */
.notice {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 12px 14px;
  color: var(--muted);
  font-size: .95rem;
}

.grid {
  display: grid; gap: 14px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  box-shadow: var(--shadow);
}

.month-card .title { font-weight: 700; }
.month-card .meta { color: var(--muted); font-size: .9rem; margin-top: 4px; }

.breadcrumbs { color: var(--muted); font-size: .9rem; margin-top: 6px; }
.breadcrumbs a { color: inherit; }

.page-title { margin: 18px 0 10px; font-size: clamp(1.2rem, 2vw + 1rem, 2rem); }

/* ---------- Month layout ---------- */
.month-layout { display: grid; gap: 24px; grid-template-columns: 1fr; }
@media (min-width: 900px) {
  .month-layout { grid-template-columns: 240px 1fr; align-items: start; }
  .toc { position: sticky; top: 68px; }
}
.toc .box { position: relative; }
.toc h3 { font-size: 1rem; margin: 0 0 6px; color: var(--muted); }
.toc ul { list-style: none; margin: 0; padding: 0; max-height: 60vh; overflow: auto; }
.toc li { padding: 6px 0; border-bottom: 1px dashed var(--border); }
.toc a { color: inherit; }
.toc .count { color: var(--muted); font-size: .9rem; }

.filter {
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
  margin: 6px 0 6px;
}
.filter input[type="search"] {
  flex: 1;
  border: 1px solid var(--border);
  background: var(--bg);
  color: inherit;
  border-radius: 10px;
  padding: 8px 10px;
  min-width: 220px;
}
.filter .stat { color: var(--muted); font-size: .9rem; }

.entry {
  scroll-margin-top: 76px;
}
.entry header {
  display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px; padding-bottom: 6px;
}
.entry h2 { font-size: 1.15rem; margin: 0; }
.entry time { color: var(--muted); font-size: .95rem; }
.entry .tools { margin-left: auto; display: flex; gap: 8px; }
.entry .tools .btn { font-size: .85rem; padding: 4px 10px; }

.entry p { margin: 10px 0; }
.entry a { word-break: break-all; }

:target.entry { outline: 2px solid var(--accent); border-radius: 8px; }

/* Back to top */
.back-to-top {
  position: fixed; right: 16px; bottom: 16px;
  border-radius: 999px; padding: 10px 12px;
  border: 1px solid var(--border); background: var(--card);
  box-shadow: var(--shadow);
  cursor: pointer;
  display: none;
}
.back-to-top.show { display: inline-flex; }

/* Code blocks */
pre {
  border: 1px solid var(--border);
  background: color-mix(in hsl, var(--card), var(--bg) 8%);
  padding: 10px 12px;
  overflow: auto;
  border-radius: 8px;
}
"""

APP_JS = r"""
(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const docEl = document.documentElement;

  // ---- Theme toggle: system -> dark -> light ----
  function applyTheme(mode) {
    if (mode === 'system') {
      docEl.removeAttribute('data-theme');
    } else {
      docEl.setAttribute('data-theme', mode);
    }
    localStorage.setItem('theme', mode);
    const label = $('#theme-label');
    if (label) {
      const emoji = mode === 'dark' ? '🌙' : mode === 'light' ? '☀️' : '🖥️';
      label.textContent = `テーマ: ${mode} ${emoji}`;
    }
  }
  function initTheme() {
    const saved = localStorage.getItem('theme') || 'system';
    applyTheme(saved);
  }
  function nextTheme(current) {
    return current === 'system' ? 'dark' : current === 'dark' ? 'light' : 'system';
  }

  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    const themeBtn = $('#theme-toggle');
    if (themeBtn) {
      themeBtn.addEventListener('click', () => {
        const cur = localStorage.getItem('theme') || 'system';
        applyTheme(nextTheme(cur));
      });
    }

    // ---- Back to top ----
    const back = $('#back-to-top');
    if (back) {
      const onScroll = () => {
        const y = window.scrollY || document.documentElement.scrollTop;
        back.classList.toggle('show', y > 800);
      };
      window.addEventListener('scroll', onScroll, { passive: true });
      back.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
      onScroll();
    }

    // ---- Copy link button ----
    $$('.copy-link').forEach(btn => {
      btn.addEventListener('click', async () => {
        const href = btn.getAttribute('data-href');
        const url = new URL(href, window.location.href).toString();
        try {
          await navigator.clipboard.writeText(url);
          btn.textContent = 'リンクをコピー ✓';
          setTimeout(() => (btn.textContent = 'リンクをコピー'), 1500);
        } catch {
          window.prompt('このURLをコピーしてください:', url);
        }
      });
    });

    // ---- Filter on month pages ----
    const filter = $('#filter-input');
    const entries = $$('.entry');
    const stat = $('#filter-stat');
    if (filter && entries.length) {
      const toc = $('#toc-list');
      filter.addEventListener('input', () => {
        const q = filter.value.trim().toLowerCase();
        let visible = 0;
        entries.forEach(el => {
          const text = el.innerText.toLowerCase();
          const ok = !q || text.includes(q);
          el.style.display = ok ? '' : 'none';
          if (ok) visible += 1;
        });
        if (stat) stat.textContent = q ? `表示 ${visible} 件` : `全 ${entries.length} 件`;
        // TOC also filter
        if (toc) {
          $$('#toc-list li').forEach(li => {
            const targetId = $('a', li).getAttribute('href').slice(1);
            const entry = document.getElementById(targetId);
            li.style.display = entry && entry.style.display !== 'none' ? '' : 'none';
          });
        }
      });
    }
  });
})();
"""

def month_label(yyyymm: str) -> str:
    y, m = int(yyyymm[:4]), int(yyyymm[4:])
    return f"{y}年{m:02d}月"

WEEKDAYS_JP = "月火水木金土日"
def weekday_jp(date: dt.date) -> str:
    # Monday=0 ... Sunday=6
    return WEEKDAYS_JP[date.weekday()]

def text_to_html(text: str) -> str:
    # 段落分割 + URL自動リンク + HTMLエスケープ
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    paras = [p.strip("\n") for p in re.split(r"\n\s*\n", text)]
    url_re = re.compile(r"(https?://[^\s<]+)")
    parts = []
    for p in paras:
        esc = html.escape(p)
        esc = url_re.sub(r'<a href="\1" target="_blank" rel="noopener">\1</a>', esc)
        esc = esc.replace("\n", "<br>")
        parts.append(f"<p>{esc}</p>")
    return "\n".join(parts)

def render_page(title: str, body_html: str, breadcrumb=None, asset_base="./", description="") -> str:
    bc_html = ""
    if breadcrumb:
        bc_html = '<nav class="breadcrumbs">' + " &raquo; ".join(breadcrumb) + "</nav>"
    now_iso = dt.datetime.now().isoformat(timespec="seconds")
    desc = html.escape(description or title)
    if asset_base and not asset_base.endswith('/'):
        asset_base = asset_base + '/'
    return f"""<!doctype html>
<html lang="ja" data-page-title="{html.escape(title)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="{asset_base}assets/favicon.svg">
<link rel="stylesheet" href="{asset_base}assets/style.css">
<script defer src="{asset_base}assets/app.js"></script>
</head>
<body>
<a class="skip-link" href="#main">本文へスキップ</a>
<header class="site">
  <div class="container site-inner">
    <div class="brand"><a href="{asset_base}index.html">ブログ</a></div>
    <div class="grow"></div>
    <div class="toolbar">
      <button id="theme-toggle" class="btn theme-toggle" aria-label="テーマ切り替え"><span id="theme-label">テーマ</span></button>
    </div>
  </div>
</header>
<main id="main" class="container">
  <h1 class="page-title">{html.escape(title)}</h1>
  {bc_html}
  {body_html}
</main>
<footer class="site">
  <div class="container">
    <div>最終更新: {now_iso}</div>
    <div>Powered by GitHub Pages &amp; Python</div>
  </div>
</footer>
<button id="back-to-top" class="back-to-top" aria-label="トップへ戻る">▲</button>
</body>
</html>"""

def write_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "style.css").write_text(STYLE_CSS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "app.js").write_text(APP_JS.strip() + "\n", encoding="utf-8")
    favicon = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3a86ff"/><stop offset="1" stop-color="#9b5cff"/></linearGradient></defs>
  <rect width="64" height="64" rx="14" fill="url(#g)"/>
  <path d="M14 34h36" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
  <path d="M14 22h24" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
  <path d="M14 46h18" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
</svg>"""
    (ASSETS_DIR / "favicon.svg").write_text(favicon, encoding="utf-8")

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    write_assets()

    months_meta = []

    month_dirs = sorted(
        (p for p in ROOT.iterdir() if p.is_dir() and MONTH_DIR_RE.match(p.name)),
        key=lambda p: p.name,
        reverse=True
    )

    for month_dir in month_dirs:
        yyyymm = month_dir.name
        entries = []
        for f in month_dir.iterdir():
            m = DAY_FILE_RE.match(f.name)
            if not m:
                continue
            day_str = m.group(1)
            if day_str[:6] != yyyymm:
                continue
            date = dt.datetime.strptime(day_str, "%Y%m%d").date()
            txt = f.read_text(encoding="utf-8")
            entries.append({
                "date": date,
                "date_str": day_str,
                "content_html": text_to_html(txt),
                "filename": f.name
            })

        entries.sort(key=lambda e: e["date"], reverse=True)

        month_out = OUT / yyyymm
        month_out.mkdir(parents=True, exist_ok=True)

        # TOC
        toc_items = [f'<li><a href="#{e["date_str"]}">{e["date"].strftime("%Y-%m-%d")}</a></li>' for e in entries]
        toc_html = (
            '<aside class="toc">'
            '  <div class="box card">'
            '    <h3>この月の目次</h3>'
            f'    <p class="count" id="filter-stat">全 {len(entries)} 件</p>'
            f'    <ul id="toc-list">{"".join(toc_items)}</ul>'
            '  </div>'
            '</aside>'
        )

        # Filter
        filter_html = (
            '<div class="filter">'
            '  <input id="filter-input" type="search" placeholder="この月の検索…（例: 雪 写真）" aria-label="この月の検索">'
            '</div>'
        )

        # Entries
        if entries:
            sections = []
            for e in entries:
                w = weekday_jp(e["date"])
                sections.append(
                    f'<article class="card entry" id="{e["date_str"]}">'
                    f'  <header>'
                    f'    <h2><a href="#{e["date_str"]}">{e["date"].strftime("%Y-%m-%d")}（{w}）</a></h2>'
                    f'    <time datetime="{e["date"].isoformat()}">{e["date"].isoformat()}</time>'
                    f'    <div class="tools"><button class="btn copy-link" data-href="#{e["date_str"]}">リンクをコピー</button></div>'
                    f'  </header>'
                    f'  {e["content_html"]}'
                    f'</article>'
                )
            entries_html = "\n".join(sections)
        else:
            entries_html = '<div class="notice">まだ記事がありません。</div>'

        body_html = (
            f"{filter_html}"
            '<div class="month-layout">'
            f'  {toc_html}'
            f'  <section class="entries" aria-label="記事一覧">{entries_html}</section>'
            '</div>'
        )

        page_html = render_page(
            f"{month_label(yyyymm)}のブログ",
            f'<nav class="breadcrumbs"><a href="../index.html">トップ</a> &raquo; {month_label(yyyymm)}</nav>' + body_html,
            breadcrumb=None,
            asset_base="../",
            description=f"{month_label(yyyymm)}の記録"
        )
        (month_out / "index.html").write_text(page_html, encoding="utf-8")

        newest = entries[0]["date"] if entries else None
        months_meta.append({
            "yyyymm": yyyymm,
            "label": month_label(yyyymm),
            "num": len(entries),
            "newest": newest
        })

    # Top
    if months_meta:
        items = []
        for m in months_meta:
            newest_text = m["newest"].strftime("%Y-%m-%d") if m["newest"] else "—"
            items.append(
                '<li class="month-card card">'
                f'  <a class="month-link" href="./{m["yyyymm"]}/">'
                f'    <div class="title">{m["label"]}</div>'
                f'    <div class="meta">{m["num"]}件 ・ 最新 {newest_text}</div>'
                '  </a>'
                '</li>'
            )
        body = '<ul class="grid months-grid" style="list-style:none; padding-left:0;">' + "\n".join(items) + "</ul>"
    else:
        body = '<div class="notice">まだ月別フォルダがありません。例: <code>202501/20250101.txt</code></div>'

    index_html = render_page("ブログ", body, asset_base="./", description="月別アーカイブ一覧")
    (OUT / "index.html").write_text(index_html, encoding="utf-8")

if __name__ == "__main__":
    build()

