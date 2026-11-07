# -*- coding: utf-8 -*-
"""
merge_homepage.py — 仓库版合并脚本（布局A）

把「风格总览表 styles-overview」和「设计参考 DESIGN-REFERENCE」并列合并进
知识库首页，生成顶部带三个导航按钮的 index.html。由 tools/build.py 调用，
本地与 GitHub Actions 跑同一份。

默认路径按仓库布局（本文件在 <仓库>/tools/ 下）：
  知识库页  <仓库>/design-knowledge-base.html
  总览表    <仓库>/视觉资料库/styles-overview.html
  设计参考  <仓库>/视觉资料库/风格库说明/DESIGN-REFERENCE.html
  输出      <仓库>/index.html
布局A 下数据路径（视觉资料库/... 前缀）在仓库里原样成立，不再需要削前缀处理。

原理：
- 知识库页是主体，原样保留，内容包进 #kbView（默认显示）
- 风格总览表包进 #soView、设计参考包进 #drView（默认隐藏），顶部导航按钮切换
- 两份外来页面的 CSS 全部加视图前缀隔离，互不污染
- 风格总览表的全局函数名统一加 so 前缀，避免和知识库页的同名函数（copyPrompt 等）打架
- 设计参考里 file:///F:/... 的本地绝对路径图片改成相对路径，线上也能显示
- 风格总览表的缩略图加 loading="lazy"，不在当前视图时不抢加载
"""
import argparse
import os
import re
import sys

NAV_HTML = """
<div id="topNav">
  <button type="button" data-view="kb" class="tn-btn active">📚 知识库总览</button>
  <button type="button" data-view="so" class="tn-btn">🗂 风格总览表</button>
  <button type="button" data-view="dr" class="tn-btn">📖 设计参考 · 风格库说明</button>
</div>
"""

NAV_CSS = """
#topNav{position:sticky;top:0;z-index:900;display:flex;gap:8px;align-items:center;
  padding:10px 16px;background:#111827;box-shadow:0 2px 10px rgba(0,0,0,.25)}
#topNav .tn-btn{appearance:none;border:1px solid #374151;background:#1f2937;color:#e5e7eb;
  font-size:14px;font-weight:600;padding:8px 16px;border-radius:999px;cursor:pointer}
#topNav .tn-btn:hover{background:#374151}
#topNav .tn-btn.active{background:#2563eb;border-color:#2563eb;color:#fff}
#drView{background:#f7f8fa}
#soView{background:#fff;padding:0 16px}
"""

TOGGLE_JS = """
<script>
(function(){
  var views = {
    kb: document.getElementById('kbView'),
    so: document.getElementById('soView'),
    dr: document.getElementById('drView')
  };
  var btns = Array.from(document.querySelectorAll('#topNav .tn-btn'));
  function show(view){
    Object.keys(views).forEach(function(k){ views[k].hidden = (k !== view); });
    btns.forEach(function(b){ b.classList.toggle('active', b.getAttribute('data-view') === view); });
    window.scrollTo(0, 0);
  }
  btns.forEach(function(b){
    b.addEventListener('click', function(){ show(b.getAttribute('data-view')); });
  });
  // 若打开时带着某份文档内部章节的锚点，切到它所在的视图
  if (location.hash && location.hash.length > 1) {
    var t = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (t && views.dr.contains(t)) show('dr');
    else if (t && views.so.contains(t)) show('so');
  }
})();
</script>
"""

# 风格总览表的全局函数 → 加 so 前缀（和知识库页的同名函数隔离）
SO_RENAMES = ['filterTable', 'sortBy', 'openLightbox', 'closeLightbox', 'copyPrompt', '_ph']


def scope_css(css: str, scope: str) -> str:
    """把一段 CSS 的每个选择器都加上 scope 前缀；@media 递归处理；其余 @规则原样。"""
    out = []
    i, n = 0, len(css)
    buf = ""
    while i < n:
        ch = css[i]
        if ch == '{':
            prelude = buf.strip()
            buf = ""
            depth = 1
            j = i + 1
            while j < n and depth:
                if css[j] == '{':
                    depth += 1
                elif css[j] == '}':
                    depth -= 1
                j += 1
            inner = css[i + 1:j - 1]
            low = prelude.lower()
            if low.startswith('@media'):
                out.append(prelude + '{' + scope_css(inner, scope) + '}')
            elif low.startswith('@'):
                out.append(prelude + '{' + inner + '}')
            else:
                sels = []
                for s in prelude.split(','):
                    s = s.strip()
                    if not s:
                        continue
                    if s in (':root', 'html', 'body'):
                        sels.append(scope)
                    elif s == '*':
                        sels.append(scope)
                        sels.append(scope + ' *')
                    else:
                        sels.append(scope + ' ' + s)
                out.append(', '.join(sels) + '{' + inner + '}')
            i = j
        else:
            buf += ch
            i += 1
    if buf.strip():
        out.append(buf)
    return '\n'.join(out)


def extract_all(pattern, text):
    return re.findall(pattern, text, re.S)


def extract(pattern, text):
    m = re.search(pattern, text, re.S)
    return m.group(1) if m else ""


def main(argv=None):
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录
    ap = argparse.ArgumentParser()
    ap.add_argument('--kb', default=os.path.join(base, 'design-knowledge-base.html'))
    ap.add_argument('--so', default=os.path.join(base, '视觉资料库', 'styles-overview.html'))
    ap.add_argument('--dr', default=os.path.join(base, '视觉资料库', '风格库说明', 'DESIGN-REFERENCE.html'))
    ap.add_argument('--out', default=os.path.join(base, 'index.html'))
    args = ap.parse_args(argv)

    for p in (args.kb, args.so, args.dr):
        if not os.path.isfile(p):
            print('找不到文件：' + p)
            sys.exit(1)

    kb = open(args.kb, encoding='utf-8').read()
    so = open(args.so, encoding='utf-8').read()
    dr = open(args.dr, encoding='utf-8').read()

    # --- 拆设计参考 ---
    dr_css = scope_css(extract(r'<style[^>]*>(.*?)</style>', dr), '#drView')
    dr_body = extract(r'<body[^>]*>(.*?)</body>', dr)
    dr_js = extract(r'<script[^>]*>(.*?)</script>', dr)
    dr_body = dr_body.replace('file:///F:/ai电商图片/', '')
    dr_body = dr_body.replace('file:///F:\\ai电商图片\\', '')
    dr_js = dr_js.replace("querySelectorAll('.toc-nav a')", "querySelectorAll('#drView .toc-nav a')")
    dr_js = dr_js.replace("function updateSpy() {",
                           "function updateSpy() {\n    if (document.getElementById('drView').hidden) return;")

    # --- 拆风格总览表 ---
    so_css = scope_css(extract(r'<style[^>]*>(.*?)</style>', so), '#soView')
    so_body = extract(r'<body[^>]*>(.*?)</body>', so)
    so_js = '\n'.join(extract_all(r'<script[^>]*>(.*?)</script>', so))
    for name in SO_RENAMES:
        so_body = so_body.replace(name + '(', 'so' + name + '(')
        so_js = so_js.replace(name + '(', 'so' + name + '(')
    so_js = re.sub(r'\basc\b', 'soAsc', so_js)
    so_body = so_body.replace('<img ', '<img loading="lazy" ')

    # --- 组装 ---
    kb = kb.replace('</head>', '<style>' + NAV_CSS + '\n' + dr_css + '\n' + so_css + '</style>\n</head>', 1)
    kb = re.sub(r'<body[^>]*>', lambda m: m.group(0) + NAV_HTML + '<div id="kbView">', kb, count=1)
    idx = kb.rfind('<script')
    if idx == -1:
        print('知识库页里没找到 script，结构不对，停止。')
        sys.exit(1)
    views = ('</div>\n'
             '<div id="soView" hidden>\n' + so_body + '\n<script>' + so_js + '</script>\n</div>\n'
             '<div id="drView" hidden>\n' + dr_body + '\n<script>' + dr_js + '</script>\n</div>\n'
             + TOGGLE_JS + '\n')
    kb = kb[:idx] + views + kb[idx:]

    _d = os.path.dirname(args.out)
    if _d:
        os.makedirs(_d, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(kb)
    print('已生成合并版首页：' + args.out)


if __name__ == '__main__':
    main()
