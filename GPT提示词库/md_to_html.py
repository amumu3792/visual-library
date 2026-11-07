# -*- coding: utf-8 -*-
"""Convert the design knowledge-base markdown files into standalone, navigable HTML.
Handles two image sources:
  - Twitter external images: ![](https://pbs.twimg.com/...)  -> <img src="https...">
  - Obsidian local images:  ![[Pasted image X.png]]          -> <img src="obsdin图片/Pasted image X.png">
Generates a fixed TOC sidebar with working anchor links (custom CJK-safe slug).
"""
import re
import os
import markdown

# --- CJK-safe slugify (keeps Chinese chars, used for heading ids + TOC) ---
def slugify(text):
    text = text.strip().lower()
    text = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', text)  # keep word chars, CJK, space, hyphen
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text or 'section'

def convert(md_path, html_path, image_subdir=None, title=None):
    with open(md_path, 'r', encoding='utf-8') as f:
        md = f.read()

    # 1) Strip previously injected explicit <a id> anchors (avoid duplicate ids)
    md = re.sub(r'<a id="[^"]+"></a>\s*\n', '', md)

    # 2) Convert Obsidian local images to standard markdown with relative path
    if image_subdir:
        def obs_repl(m):
            name = m.group(1).strip()
            return f'![{name}]({image_subdir}/{name})'
        md = re.sub(r'!\[\[([^\]]+)\]\]', obs_repl, md)

    # 3) Markdown -> HTML
    md_html = markdown.markdown(
        md,
        extensions=['tables', 'fenced_code', 'sane_lists', 'attr_list'],
        extension_configs={},
    )

    # 4) Assign ids to h2/h3 and build nested TOC
    used = {}
    toc_items = []  # (level, text, anchor)
    current_h2 = None

    def heading_repl(m):
        level = int(m.group(1))
        inner = m.group(2)
        # strip tags to get plain text for slug + label
        plain = re.sub(r'<[^>]+>', '', inner).strip()
        base = slugify(plain)
        anchor = base
        if anchor in used:
            used[anchor] += 1
            anchor = f'{base}-{used[anchor]}'
        else:
            used[anchor] = 0
        toc_items.append((level, plain, anchor))
        return f'<h{level} id="{anchor}" class="doc-heading">{inner}</h{level}>'

    md_html = re.sub(r'<h([23])>(.*?)</h\1>', heading_repl, md_html, flags=re.DOTALL)

    # 5) Build TOC HTML (skip the in-page "目录" section)
    toc_html_parts = []
    open_ul = False
    skip_text = '目录'
    filtered = [t for t in toc_items if t[1] != skip_text]
    for i, (level, text, anchor) in enumerate(filtered):
        if level == 2:
            if open_ul:
                toc_html_parts.append('</ul>')
                open_ul = False
            toc_html_parts.append(
                f'<li class="toc-h2"><a href="#{anchor}" data-target="{anchor}">{text}</a></li>')
        else:  # h3
            # find preceding h2 to nest under
            prev_h2_idx = None
            for j in range(i - 1, -1, -1):
                if filtered[j][0] == 2:
                    prev_h2_idx = j
                    break
            if not open_ul and prev_h2_idx is not None:
                toc_html_parts.append('<ul class="toc-sub">')
                open_ul = True
            toc_html_parts.append(
                f'<li class="toc-h3"><a href="#{anchor}" data-target="{anchor}">{text}</a></li>')
    if open_ul:
        toc_html_parts.append('</ul>')
    toc_html = '\n'.join(toc_html_parts)

    # 6) Assemble final HTML
    doc_title = title or os.path.splitext(os.path.basename(md_path))[0]
    html = TEMPLATE.replace('{{TITLE}}', doc_title)
    html = html.replace('{{TOC}}', toc_html)
    html = html.replace('{{CONTENT}}', md_html)
    html = html.replace('{{IMG_NOTE}}',
                        '本地图片引用自 obsdin图片/ 子文件夹，需与本 HTML 同目录打开。' if image_subdir else '')

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Wrote {html_path}  (headings={len(toc_items)}, toc entries={len(filtered)})')


TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<style>
  :root {
    --bg: #f7f8fa; --panel: #ffffff; --ink: #1f2329; --muted: #6b7280;
    --line: #e5e7eb; --accent: #2563eb; --accent-soft: #eff4ff; --code-bg: #f3f4f6;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", Roboto, sans-serif;
    color: var(--ink); background: var(--bg); line-height: 1.7;
  }
  .layout { display: flex; min-height: 100vh; }
  /* Sidebar */
  .sidebar {
    width: 300px; flex: 0 0 300px; position: sticky; top: 0; align-self: flex-start;
    height: 100vh; overflow-y: auto; background: var(--panel); border-right: 1px solid var(--line);
    padding: 22px 16px;
  }
  .sidebar h1 { font-size: 15px; margin: 0 0 14px; color: var(--ink); }
  .sidebar .hint { font-size: 12px; color: var(--muted); margin: 0 0 16px; }
  .toc-nav { list-style: none; margin: 0; padding: 0; font-size: 13.5px; }
  .toc-nav li { margin: 2px 0; }
  .toc-h2 > a {
    display: block; padding: 6px 10px; border-radius: 7px; color: var(--ink);
    text-decoration: none; font-weight: 600;
  }
  .toc-sub { list-style: none; margin: 2px 0 6px; padding: 0 0 0 14px; }
  .toc-h3 > a {
    display: block; padding: 4px 10px; border-radius: 6px; color: var(--muted);
    text-decoration: none; font-weight: 400; border-left: 2px solid var(--line);
  }
  .toc-nav a:hover { background: var(--accent-soft); color: var(--accent); }
  .toc-nav a.active { background: var(--accent-soft); color: var(--accent); font-weight: 700; }
  .toc-h3 > a.active { border-left-color: var(--accent); color: var(--accent); }
  /* Content */
  .content { flex: 1 1 auto; min-width: 0; padding: 40px 56px 120px; }
  .content-inner { max-width: 920px; margin: 0 auto; background: var(--panel);
    border: 1px solid var(--line); border-radius: 14px; padding: 40px 48px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04); }
  .doc-heading { scroll-margin-top: 24px; margin-top: 38px; }
  h1.doc-heading { font-size: 26px; border-bottom: 2px solid var(--line); padding-bottom: 10px; }
  h2.doc-heading { font-size: 21px; color: #111827; border-left: 4px solid var(--accent); padding-left: 12px; }
  h3.doc-heading { font-size: 17px; color: #1f2937; }
  p { margin: 10px 0; }
  a { color: var(--accent); }
  img { max-width: 100%; height: auto; display: block; margin: 16px auto;
    border: 1px solid var(--line); border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 14px; }
  th, td { border: 1px solid var(--line); padding: 8px 10px; text-align: left; vertical-align: top; }
  th { background: var(--code-bg); font-weight: 600; }
  tr:nth-child(even) td { background: #fafafa; }
  pre { background: var(--code-bg); border: 1px solid var(--line); border-radius: 10px;
    padding: 16px; overflow-x: auto; font-size: 13px; line-height: 1.55; }
  code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    background: var(--code-bg); padding: 2px 5px; border-radius: 4px; font-size: 13px; }
  pre code { background: none; padding: 0; }
  blockquote { margin: 14px 0; padding: 8px 16px; border-left: 3px solid var(--accent);
    background: var(--accent-soft); color: #374151; border-radius: 0 8px 8px 0; }
  ul, ol { padding-left: 24px; }
  li { margin: 4px 0; }
  .menu-toggle { display: none; }
  @media (max-width: 860px) {
    .layout { flex-direction: column; }
    .sidebar { position: static; width: 100%; height: auto; border-right: none;
      border-bottom: 1px solid var(--line); }
    .content { padding: 20px 14px 80px; }
    .content-inner { padding: 22px 18px; }
  }
</style>
</head>
<body>
<div class="layout">
  <nav class="sidebar">
    <h1>📚 {{TITLE}}</h1>
    <p class="hint">{{IMG_NOTE}}</p>
    <ul class="toc-nav">
{{TOC}}
    </ul>
  </nav>
  <main class="content">
    <div class="content-inner">
{{CONTENT}}
    </div>
  </main>
</div>
<script>
  // Smooth-scroll + active highlight
  const links = Array.from(document.querySelectorAll('.toc-nav a'));
  const map = new Map();
  links.forEach(a => {
    const id = a.getAttribute('data-target');
    const el = document.getElementById(id);
    if (el) map.set(el, a);
    a.addEventListener('click', e => {
      e.preventDefault();
      el && el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.replaceState(null, '', '#' + id);
    });
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const a = map.get(en.target);
        if (a) a.classList.add('active');
      }
    });
  }, { rootMargin: '0px 0px -70% 0px', threshold: 0 });
  map.forEach((a, el) => observer.observe(el));
</script>
</body>
</html>
'''

if __name__ == '__main__':
    base = r'F:/ai电商图片/视觉资料库'
    convert(
        os.path.join(base, 'GPT-IMAGE-PROMPT-LIBRARY.md'),
        os.path.join(base, 'GPT-IMAGE-PROMPT-LIBRARY.html'),
        image_subdir='obsdin图片',
        title='GPT-Image-2 提示词模板知识库',
    )
    styles = r'F:/ai电商图片/AI-Visual-Prompt-Cookbook-main/styles'
    convert(
        os.path.join(styles, 'DESIGN-REFERENCE.md'),
        os.path.join(styles, 'DESIGN-REFERENCE.html'),
        image_subdir=None,
        title='视觉风格库 · 设计引用知识库 (112 套)',
    )
    print('ALL DONE')
