# -*- coding: utf-8 -*-
"""
视觉设计知识库 · 共享核心（唯一真相源）

只读取本地文件，不碰网络。负责：
  - 解析 112 个风格文件夹（styles/）-> 设计手法
  - 解析 21 个 GPT 提示词模板（视觉资料库/GPT-IMAGE-PROMPT-LIBRARY.md）
  - 把两者合并成单文件 HTML（design-knowledge-base.html）

收藏（给已有卡片打标）由网页内 ⭐ 星标（浏览器本地存储）实现；用户自己「往库里新增的提示词」则走「暂存区 → 用户补充.md」本地 md 通道，双击同步即并入 HTML，与 ⭐ 收藏完全分开。

图片相对路径以 F:/ai电商图片 为根解析，配合本地 http 服务或 file:// 均可看。
"""
import re, os, json, glob, base64, hashlib, html, csv, urllib.request
# （云端版）已去掉未使用的 PIL 导入：全文从未调用，纯标准库即可运行

def _norm(s):
    """归一化（去空白+转小写），用于去重比对。"""
    return re.sub(r'\s+', '', (s or '').lower())

ROOT = os.environ.get('KB_ROOT') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 云端版：仓库根目录（原写死 F:/ai电商图片）
STYLES_DIR = os.path.join(ROOT, 'AI-Visual-Prompt-Cookbook-main', 'styles')
# GPT 提示词模板源文件：曾经被挪到「GPT提示词库」子目录，导致脚本按老路径找不到、
# 21 个模板整段消失。改为运行时多候选探测，文件再被移动也不会静默丢内容。
def _find_gpt_md():
    for p in [
        os.path.join(ROOT, '视觉资料库', 'GPT提示词库', 'GPT-IMAGE-PROMPT-LIBRARY.md'),
        os.path.join(ROOT, '视觉资料库', 'GPT-IMAGE-PROMPT-LIBRARY.md'),
    ]:
        if os.path.exists(p):
            return p
    return None
GPT_MD = _find_gpt_md()
THUMB_CACHE = os.path.join(ROOT, '.kb-thumb-cache')

# ---------- image reference (相对路径，不内嵌) ----------
def _embed_image(src, max_width=360, quality=75):
    """图片统一用相对路径引用（相对于 F:/ai电商图片 根），不内嵌 base64。

    原因：之前把 224 张图全部 base64 内嵌，把 HTML 撑到 26MB+，浏览器直接卡死、
    图片反而一张都显示不出来，且「点一下同步」就会重写整库导致内容丢失。
    改用相对路径后：HTML 只有几百 KB，双击 HTML（file://）或经本地 http 服务都能正常看图。
    """
    return src
OUT = os.path.join(ROOT, 'design-knowledge-base.html')
# GPT 模板里的 Twitter 等远程示例图，同步时落地到的本地目录
GPT_TWITTER_DIR = os.path.join(ROOT, '视觉资料库', 'GPT提示词库', 'twitter图片')

# ---------- 用户新增提示词（暂存区 → 用户补充.md → 并入 HTML） ----------
# 注意：这是「往库里加新内容」的通道，与网页 ⭐ 收藏（浏览器本地）完全分开。
# 不带任何登录 / 删改后端，纯本地 md 存储。
USER_DIR = os.path.join(ROOT, '视觉资料库', '用户补充')
USER_MD = os.path.join(USER_DIR, '用户补充.md')
USER_IMG_DIR = os.path.join(USER_DIR, '图片')
USER_STAGING_MD = os.path.join(USER_DIR, '暂存区.md')

# 用户删除内置条目时记录的排除列表（本地删除不删源文件，GitHub 同步后也不会复活）
EXCLUDED_JSON = os.path.join(ROOT, '视觉资料库', 'excluded.json')

def load_excluded():
    if not os.path.exists(EXCLUDED_JSON):
        return set()
    try:
        return set(json.load(open(EXCLUDED_JSON, encoding='utf-8')))
    except Exception:
        return set()

def save_excluded(ids):
    os.makedirs(os.path.dirname(EXCLUDED_JSON), exist_ok=True)
    with open(EXCLUDED_JSON, 'w', encoding='utf-8') as f:
        json.dump(sorted(ids), f, ensure_ascii=False, indent=2)

def exclude_entry(id_):
    s = load_excluded()
    s.add(id_)
    save_excluded(s)

def unexclude_entry(id_):
    s = load_excluded()
    s.discard(id_)
    save_excluded(s)
STAGING_TEMPLATE = (
    '# 暂存区（新提示词输入区）\n'
    '\n'
    '> 平时把**新**提示词粘在下面，每条用 `## 标题` 开头。\n'
    '> 双击「同步本地.bat」后，这里的内容会自动搬进「用户新增」知识库，并**自动清空本暂存区**——你不用手动删。\n'
    '> 图：用 `![[图片链接]]` 或 `![](图片链接)`；提示词：用三个反引号包住，或直接写一段文字。\n'
    '>\n'
    '> 下面示例不会进入知识库（仅供抄格式）：\n'
    '<!--\n'
    '## 示例标题\n'
    '![[https://示例图片.jpg]]\n'
    '提示词：\n'
    '```\n'
    '把提示词粘在这里\n'
    '```\n'
    '-->\n'
)

# ---------- style classifier ----------
def classify_style(name, category, summary):
    t = (name + ' ' + category + ' ' + summary).lower()
    rules = [
        ('3D / C4D', ['c4d', '3d', 'clay', 'render', 'blender', 'octane', 'toy', 'avatar']),
        ('漫画 / 二次元', ['manga', 'comic', 'anime', '机甲', '漫', '二次元', 'manga']),
        ('编辑 / 杂志', ['editorial', 'newsprint', 'magazine', 'zine', '报刊', '杂志', 'editorial']),
        ('手绘 / 涂鸦', ['doodle', 'sketch', 'crayon', 'hand', 'drawn', '涂鸦', '手绘', '蜡笔', 'catalog']),
        ('贴纸 / 拼贴', ['sticker', 'collage', 'cutout', '贴纸', '拼贴']),
        ('印刷 / 复印风', ['halftone', 'xerox', 'risograph', 'riso', '复印', '网点', 'ransom']),
        ('鱼眼 / 摄影', ['fisheye', 'photo', 'fashion', 'film', '鱼眼', '摄影', 'bubble']),
        ('食品 / 产品', ['food', 'recipe', 'menu', 'product', '食品', '菜单', '产品', '包装']),
        ('字体 / 海报', ['type', 'poster', 'typo', '字体', '海报', '字', 'megatype', 'kinetic']),
        ('国风 / 文化', ['chinese', 'ink', 'dynasty', '壁画', '敦煌', '国风', '水墨', '工笔', 'perspective']),
        ('游戏 / IP', ['game', 'pixel', 'rpg', '游戏', '像素', 'dossier']),
    ]
    for label, kws in rules:
        if any(k in t for k in kws):
            return label
    return '其他 / 综合'

# ---------- parse styles ----------
def parse_styles():
    items = []
    for d in sorted(glob.glob(os.path.join(STYLES_DIR, '*/'))):
        slug = os.path.basename(os.path.normpath(d))
        jp = os.path.join(d, 'style.json')
        if not os.path.exists(jp):
            continue
        try:
            data = json.load(open(jp, encoding='utf-8'))
        except Exception:
            continue
        vd = data.get('visual_deconstruction', {}) or {}
        cp = data.get('color_palette', {}) or {}
        it = data.get('image_treatment', {}) or {}
        name = data.get('style_name', slug)
        category = vd.get('style_category', '') if isinstance(vd, dict) else ''
        mood = vd.get('mood', '') if isinstance(vd, dict) else ''
        summary = data.get('style_summary', '')
        palette = (cp.get('dominant', []) if isinstance(cp, dict) else []) or []
        accents = (cp.get('accents', []) if isinstance(cp, dict) else []) or []
        prompt = data.get('prompt_template', '')
        rendering = it.get('rendering_mode', '') if isinstance(it, dict) else ''
        coarse = classify_style(name, category, summary)
        img16 = f'AI-Visual-Prompt-Cookbook-main/styles/{slug}/{slug}-16x9.jpg'
        img9 = f'AI-Visual-Prompt-Cookbook-main/styles/{slug}/{slug}-9x16.jpg'
        images = [
            {'src': img16, 'ratio': '16:9', 'label': '横版 16:9', 'w': 16, 'h': 9},
            {'src': img9, 'ratio': '9:16', 'label': '竖版 9:16', 'w': 9, 'h': 16},
        ]
        items.append({
            'id': 'style:' + slug,
            'type': '风格库',
            'slug': slug,
            'name': name,
            'category': coarse,
            'categoryRaw': category,
            'mood': mood,
            'summary': summary,
            'palette': palette[:6],
            'accents': accents[:4],
            'rendering': rendering,
            'prompt': prompt,
            'ratios': ['16:9', '9:16'],
            'images': images,
            'jsonPath': f'AI-Visual-Prompt-Cookbook-main/styles/{slug}/style.json',
            'exampleCount': len(data.get('examples', []) or []),
        })
    return items

# ---------- parse GPT templates ----------
def parse_gpt():
    gpt_md = _find_gpt_md()
    if not gpt_md:
        return []
    # 本地 ![[...]] 图片相对于 GPT 源文件所在目录的 obsdin图片/ 子目录
    gpt_dir = os.path.dirname(gpt_md)
    gpt_rel = os.path.relpath(gpt_dir, ROOT).replace(os.sep, '/')
    text = open(gpt_md, encoding='utf-8').read()
    text = re.sub(r'<a id="[^"]+"></a>\s*\n', '', text)
    lines = text.split('\n')
    templates = []
    section = ''
    cur = None
    prompt_buf = []
    in_prompt = False

    def finalize():
        nonlocal cur, prompt_buf, in_prompt
        if cur is None:
            return
        raw = '\n'.join(prompt_buf).strip()
        raw = re.sub(r'```[a-zA-Z]*', '', raw).strip()
        cur['prompt'] = raw
        tw = sum(1 for im in cur['images'] if im['kind'] == 'twitter')
        loc = [im for im in cur['images'] if im['kind'] == 'local']
        for im in cur['images']:
            if im['kind'] == 'twitter':
                im['label'] = 'Twitter 示例（合集图）'
                im['ratio'] = '参考'
            else:
                im['label'] = '本地示例'
                im['ratio'] = '参考'
        nm = cur['name'] + cur['category']
        if any(k in nm for k in ['游戏实机', '角色设定', '像素资产', '地景档案', '旅游攻略', '轮廓宇宙']):
            cur['ratios'] = ['横版 16:9']
        else:
            cur['ratios'] = ['竖版 9:16']
        cur['twitterCount'] = tw
        cur['localCount'] = len(loc)
        templates.append(cur)
        cur = None
        prompt_buf = []
        in_prompt = False

    for line in lines:
        m2 = re.match(r'^##\s+(.+)$', line)
        m3 = re.match(r'^###\s+(\d+)\.\s+(.+)$', line)
        if m2 and not line.startswith('###'):
            finalize()
            section = re.sub(r'^[一二三四五六七八九十]+、', '', m2.group(1).strip())
            continue
        if m3:
            finalize()
            cur = {'id': 'tpl:' + m3.group(1), 'type': '提示词模板', 'num': m3.group(1),
                   'name': m3.group(2).strip(), 'category': section, 'images': []}
            in_prompt = False
            prompt_buf = []
            continue
        if cur is None:
            continue
        if not in_prompt:
            for m in re.finditer(r'!\[[^\]]*\]\((https?://[^)]+)\)', line):
                url = m.group(1)
                local = _download_gpt_image(url)
                cur['images'].append({'src': local or url, 'kind': 'local' if local else 'url'})
            for m in re.finditer(r'!\[\[([^\]]+)\]\]', line):
                cur['images'].append({'src': gpt_rel + '/obsdin图片/' + m.group(1).strip(), 'kind': 'local'})
        if re.match(r'^\*\*提示词', line):
            if not in_prompt:
                in_prompt = True
                prompt_buf = []
            continue
        if in_prompt:
            if re.match(r'^\*\*使用要点', line) or re.match(r'^##', line):
                in_prompt = False
                continue
            prompt_buf.append(line)
    finalize()
    for t in templates:
        li = 1
        for im in t['images']:
            if im['kind'] == 'local':
                im['label'] = f'本地示例 {li}'
                li += 1
    return templates

# ---------- parse user-added collections (自行粘贴同步) ----------
def _is_valid_image_bytes(b):
    """按文件头（magic bytes）判断是不是真图片，杜绝把 403/HTML 错误页当图存下来。"""
    if not b:
        return False
    if b[:8] == b'\x89PNG\r\n\x1a\n':
        return True
    if b[:3] == b'\xff\xd8\xff':
        return True
    if b[:6] in (b'GIF87a', b'GIF89a'):
        return True
    if b[:4] == b'RIFF' and b[8:12] == b'WEBP':
        return True
    return False


def _is_magic_ok(path):
    try:
        with open(path, 'rb') as f:
            return _is_valid_image_bytes(f.read(16))
    except Exception:
        return False



def _download_gpt_image(url):
    """GPT 模板里的 Twitter 等远程示例图：同步时下载到本地
    （视觉资料库/GPT提示词库/twitter图片/），返回本地相对路径；
    失败（离线 / 防盗链）返回 None，调用方回退远程 URL（离线时由网页 SVG 占位兜底）。
    只接受真图片文件头；已存在且有效则复用，不重复下载。"""
    try:
        gpt_md = _find_gpt_md()
        if not gpt_md:
            return None
        gpt_dir = os.path.dirname(gpt_md)
        tw_dir = os.path.join(gpt_dir, 'twitter图片')
        gpt_rel = os.path.relpath(gpt_dir, ROOT).replace(os.sep, '/')
        os.makedirs(tw_dir, exist_ok=True)
        m = re.search(r'\.(png|jpe?g|gif|webp)(?:[?#]|$)', url, re.I)
        ext = ('.' + m.group(1).lower()) if m else '.jpg'
        if ext == '.jpeg':
            ext = '.jpg'
        h = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
        fn = f'tw_{h}{ext}'
        local = os.path.join(tw_dir, fn)
        rel = f'{gpt_rel}/twitter图片/{fn}'
        if os.path.exists(local) and _is_magic_ok(local):
            return rel                       # 已有且是有效图，复用
        if os.path.exists(local):
            os.remove(local)                 # 旧文件损坏，先清掉
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0', 'Referer': 'https://twitter.com/'})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if _is_valid_image_bytes(data):      # 下载内容必须是真图片才落盘
            with open(local, 'wb') as f:
                f.write(data)
            return rel
        if os.path.exists(local):
            os.remove(local)
        return None
    except Exception:
        return None


# ---------- 用户新增提示词解析 ----------
def _download_user_image(url):
    """用户新增里的远程图：同步时下载到本地（视觉资料库/用户补充/图片/），返回本地相对路径；
    失败回退远程 URL（离线时由网页 SVG 占位兜底）。只接受真图片文件头；已存在且有效则复用。"""
    try:
        os.makedirs(USER_IMG_DIR, exist_ok=True)
        m = re.search(r'\.(png|jpe?g|gif|webp)(?:[?#]|$)', url, re.I)
        ext = ('.' + m.group(1).lower()) if m else '.png'
        if ext == '.jpeg':
            ext = '.jpg'
        h = hashlib.md5(url.encode('utf-8')).hexdigest()[:12]
        fn = f'remote_{h}{ext}'
        local = os.path.join(USER_IMG_DIR, fn)
        rel = os.path.relpath(local, ROOT).replace(os.sep, '/')
        if os.path.exists(local) and _is_magic_ok(local):
            return rel
        if os.path.exists(local):
            os.remove(local)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if _is_valid_image_bytes(data):
            with open(local, 'wb') as f:
                f.write(data)
            return rel
        if os.path.exists(local):
            os.remove(local)
        return None
    except Exception:
        return None


def parse_user_additions(md_path=None):
    """解析用户新增 md（默认 用户补充.md）。每条 `## 标题` 为一个条目。
    返回 item 列表（type='用户新增'）。标题下所有非图非引用文字算正文/描述；
    提示词优先级 = 代码块 / `提示词:` 行 > 整段正文。只要「有标题 + (有图 或 有文字)」就保留。"""
    md_path = md_path or USER_MD
    if not os.path.exists(md_path):
        return []
    text = open(md_path, encoding='utf-8').read()
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)   # 去掉模板示例注释块
    blocks = re.split(r'\n##\s+', '\n' + text)
    items = []
    for b in blocks[1:]:
        title = b.split('\n', 1)[0].strip()
        if not title:
            continue
        body = b.split('\n', 1)[1] if '\n' in b else ''
        images = []
        for m in re.finditer(r'!\[\[([^\]]+)\]\]', body):
            raw = m.group(1).strip()
            if raw.lower().startswith('http'):
                local = _download_user_image(raw)
                images.append({'src': local or raw, 'kind': 'local' if local else 'url'})
            else:
                images.append({'src': raw, 'kind': 'local'})
        for m in re.finditer(r'!\[[^\]]*\]\((https?://[^)]+)\)', body):
            local = _download_user_image(m.group(1))
            images.append({'src': local or m.group(1), 'kind': 'local' if local else 'url'})
        prompt = ''
        cb = re.search(r'```(?:[a-zA-Z]*)\n(.*?)```', body, re.S)
        if cb:
            prompt = cb.group(1).strip()
        else:
            pm = re.search(r'提示词[:：]\s*\n?(.*)', body)
            if pm:
                prompt = pm.group(1).strip()
        body_clean = re.sub(r'!\[\[[^\]]+\]\]', '', body)
        body_clean = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', body_clean)
        body_clean = re.sub(r'```.*?```', '', body_clean, flags=re.S)
        body_clean = re.sub(r'提示词[:：].*', '', body_clean, flags=re.S)
        summary = '\n'.join(l.strip() for l in body_clean.strip().split('\n') if l.strip())
        if not (images or summary or prompt):
            continue
        if not prompt and summary:
            prompt = summary
        items.append({
            'id': 'user:' + title,
            'type': '用户新增',
            'name': title,
            'category': '用户新增',
            'summary': summary,
            'prompt': prompt,
            'ratios': ['竖版 9:16'],
            'images': [{'src': im['src'], 'kind': im['kind'], 'label': '用户示例', 'ratio': '参考'} for im in images],
        })
    return items


def ensure_staging():
    os.makedirs(USER_DIR, exist_ok=True)
    if not os.path.exists(USER_STAGING_MD):
        with open(USER_STAGING_MD, 'w', encoding='utf-8') as f:
            f.write(STAGING_TEMPLATE)


def consume_staging():
    """把暂存区里的有效条目搬进 用户补充.md（永久库），并自动清空暂存区。
    返回 (merged[标题列表], kept[(标题,原因)])。无效条目保留在暂存区并附原因注释。"""
    ensure_staging()
    text = open(USER_STAGING_MD, encoding='utf-8').read()
    staging_only = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    entries = re.split(r'\n##\s+', '\n' + staging_only)[1:]
    existing = set()
    if os.path.exists(USER_MD):
        for t in re.findall(r'\n##\s+([^\n]+)', open(USER_MD, encoding='utf-8').read()):
            existing.add(_norm(t))
    merged, kept, appended = [], [], []
    for e in entries:
        title = e.split('\n', 1)[0].strip()
        if not title:
            continue
        has_img = ('![[' in e) or ('![' in e and '](' in e)
        body_no_img = re.sub(r'!\[\[[^\]]+\]\]', '', e)
        has_text = bool(body_no_img.strip())
        if not (has_img or has_text):
            kept.append((title, '既无图片也无任何文字内容'))
            continue
        if _norm(title) in existing:
            continue   # 已存在，跳过并清出暂存区
        merged.append(title)
        existing.add(_norm(title))
        appended.append('## ' + e.rstrip() + '\n')
    if appended:
        os.makedirs(USER_DIR, exist_ok=True)
        with open(USER_MD, 'a', encoding='utf-8') as f:
            f.write('\n' + '\n'.join(appended))
    new_staging = STAGING_TEMPLATE
    for title, reason in kept:
        new_staging += f'\n<!-- 跳过：{title}（{reason}） -->\n## {title}\n'
    with open(USER_STAGING_MD, 'w', encoding='utf-8') as f:
        f.write(new_staging)
    return merged, kept


# ---------- build all ----------
def build_all():
    styles = parse_styles()
    templates = parse_gpt()
    user_items = parse_user_additions()
    excluded = load_excluded()
    all_items = styles + templates + user_items
    # 过滤掉用户已删除的内置条目
    all_items = [it for it in all_items if it.get('id') not in excluded]
    styles = [it for it in styles if it.get('id') not in excluded]
    templates = [it for it in templates if it.get('id') not in excluded]
    # 图片统一为相对路径（不内嵌 base64），HTML 轻量、浏览器直接加载
    for it in all_items:
        for im in it.get('images', []):
            im['src'] = _embed_image(im['src'])
    return styles, templates, all_items

# ---------- HTML template (单文件，内嵌 DATA) ----------
HTML_TMPL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root{
    --bg:#f5f6f8; --panel:#fff; --ink:#1f2329; --muted:#6b7280; --line:#e5e7eb;
    --blue:#2563eb; --blue-soft:#eff4ff; --orange:#ea580c; --orange-soft:#fff3eb;
    --green:#059669; --code:#f3f4f6;
  }
  *{box-sizing:border-box;}
  body{margin:0;font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
       background:var(--bg);color:var(--ink);line-height:1.6;}
  header{padding:22px 28px 14px;background:linear-gradient(135deg,#1e293b,#334155);color:#fff;}
  header h1{margin:0;font-size:22px;}
  header p{margin:6px 0 0;color:#cbd5e1;font-size:13px;}
  .toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;padding:16px 28px;
           background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20;}
  .toolbar input[type=text]{padding:9px 12px;border:1px solid var(--line);border-radius:8px;
           font-size:14px;width:260px;}
  .chips{display:flex;gap:6px;flex-wrap:wrap;}
  .chip{padding:6px 13px;border:1px solid var(--line);border-radius:999px;background:#fff;
        font-size:13px;cursor:pointer;color:var(--muted);user-select:none;}
  .chip.active{background:var(--blue);color:#fff;border-color:var(--blue);}
  select{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;background:#fff;}
  .count{margin-left:auto;color:var(--muted);font-size:13px;}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:18px;padding:24px 28px 80px;}
  .card{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:14px;overflow:hidden;
        cursor:pointer;transition:transform .15s,box-shadow .15s;display:flex;flex-direction:column;}
  .card:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(0,0,0,.10);}
  .card .thumbwrap{position:relative;width:100%;aspect-ratio:4/3;background:#eef1f5;overflow:hidden;}
  .card .thumbwrap img{width:100%;height:100%;object-fit:cover;display:block;}
  .card .body{padding:11px 13px 14px;}
  .card .nm{font-weight:700;font-size:14px;line-height:1.35;margin:0 0 7px;
            display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
  .badge{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;margin:0 4px 4px 0;font-weight:600;}
  .b-style{background:var(--blue-soft);color:var(--blue);}
  .b-tpl{background:var(--orange-soft);color:var(--orange);}
  .b-user{background:#f3e8ff;color:#7c3aed;}
  .b-cat{background:#f1f5f9;color:#475569;}
  .b-ratio{background:#ecfdf5;color:var(--green);}
  .card .meta{font-size:12px;color:var(--muted);margin-top:6px;}
  .favstar{position:absolute;top:8px;right:8px;width:34px;height:34px;border:none;border-radius:50%;
           background:rgba(255,255,255,.88);color:#94a3b8;font-size:20px;line-height:34px;text-align:center;
           cursor:pointer;z-index:4;box-shadow:0 2px 6px rgba(0,0,0,.12);transition:transform .12s,color .12s,background .12s;
           display:flex;align-items:center;justify-content:center;padding:0;}
  .favstar:hover{transform:scale(1.12);background:#fff;}
  .favstar.fav{color:#f59e0b;background:#fff;}
  .favstar svg{width:22px;height:22px;fill:currentColor;}
  .delbtn{position:absolute;top:8px;right:50px;width:34px;height:34px;border:none;border-radius:50%;
          background:rgba(255,255,255,.88);color:#ef4444;font-size:16px;line-height:34px;text-align:center;
          cursor:pointer;z-index:4;box-shadow:0 2px 6px rgba(0,0,0,.12);transition:transform .12s,background .12s;
          display:flex;align-items:center;justify-content:center;padding:0;}
  .delbtn:hover{transform:scale(1.12);background:#fff;color:#dc2626;}
  .modal{display:none;position:fixed;inset:0;background:rgba(15,23,42,.82);z-index:1000;
         overflow-y:auto;padding:30px 16px;}
  .modal.open{display:block;}
  .modal-inner{background:var(--panel);max-width:1080px;margin:0 auto;border-radius:16px;overflow:hidden;
               display:grid;grid-template-columns:1.15fr 1fr;min-height:60vh;}
  .gal{background:#0f172a;display:flex;flex-direction:column;position:relative;}
  .gal-main{flex:1;display:flex;align-items:center;justify-content:center;padding:18px;min-height:340px;}
  .gal-main img{max-width:100%;max-height:62vh;object-fit:contain;border-radius:8px;box-shadow:0 4px 18px rgba(0,0,0,.4);}
  .ratio-badge{position:absolute;top:14px;left:14px;background:rgba(37,99,235,.92);color:#fff;
               font-size:12px;font-weight:700;padding:4px 10px;border-radius:8px;z-index:3;}
  .gal-nav{position:absolute;top:50%;transform:translateY(-50%);background:rgba(255,255,255,.85);
           border:none;width:40px;height:40px;border-radius:50%;font-size:20px;cursor:pointer;z-index:3;}
  .gal-nav.prev{left:10px;} .gal-nav.next{right:10px;}
  .gal-foot{padding:10px 14px;background:#1e293b;display:flex;align-items:center;gap:10px;}
  .gal-foot .counter{color:#cbd5e1;font-size:12px;}
  .thumbs{display:flex;gap:8px;overflow-x:auto;padding:8px;background:#1e293b;}
  .thumbs img{height:54px;width:auto;border-radius:5px;cursor:pointer;opacity:.55;border:2px solid transparent;}
  .thumbs img.active{opacity:1;border-color:#60a5fa;}
  .info{padding:26px 28px;overflow-y:auto;max-height:86vh;}
  .info h2{margin:0 0 4px;font-size:21px;}
  .info .sub{color:var(--muted);font-size:13px;margin-bottom:14px;}
  .info .row{margin:12px 0;}
  .info .k{font-size:12px;color:var(--muted);font-weight:600;margin-bottom:4px;}
  .info .v{font-size:14px;}
  .swatches{display:flex;gap:6px;flex-wrap:wrap;}
  .sw{width:30px;height:30px;border-radius:7px;border:1px solid rgba(0,0,0,.1);}
  .prompt-box{position:relative;background:var(--code);border:1px solid var(--line);border-radius:10px;
              padding:14px 14px 14px;font-family:"SFMono-Regular",Consolas,monospace;font-size:12.5px;
              line-height:1.6;white-space:pre-wrap;word-break:break-word;max-height:300px;overflow:auto;color:#1f2937;}
  .copy-btn{position:absolute;top:8px;right:8px;background:#fff;border:1px solid #dbe3ea;color:var(--blue);
            border-radius:7px;padding:4px 11px;font-size:12px;cursor:pointer;}
  .copy-btn:hover{background:var(--blue-soft);}
  .close{position:fixed;top:18px;right:24px;background:#fff;border:none;border-radius:50%;width:42px;height:42px;
         font-size:22px;cursor:pointer;z-index:1001;box-shadow:0 3px 10px rgba(0,0,0,.25);}
  .note{font-size:12px;color:var(--muted);background:#f8fafc;border:1px dashed var(--line);
        border-radius:8px;padding:8px 11px;margin-top:10px;}
  .linkrow a{color:var(--blue);text-decoration:none;font-size:13px;}
  .manage-btn{margin-top:10px;padding:7px 16px;border:none;border-radius:8px;background:var(--blue);color:#fff;
              font-size:13px;cursor:pointer;display:inline-block;}
  .manage-btn:hover{background:#1d4ed8;}
  .mgr{position:absolute;top:8px;left:8px;display:flex;gap:5px;z-index:6;}
  .mgr-btn{width:30px;height:30px;border:none;border-radius:50%;background:rgba(255,255,255,.92);
           font-size:13px;line-height:30px;text-align:center;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.18);}
  .mgr-btn.del:hover{background:#fee2e2;color:#dc2626;}
  .mgr-btn.ren:hover{background:#e0f2fe;color:#0369a1;}
  .loginmask{position:fixed;inset:0;background:rgba(15,23,42,.6);display:none;z-index:1100;
             align-items:center;justify-content:center;}
  .loginmask.open{display:flex;}
  .loginbox{background:#fff;border-radius:14px;padding:24px 28px;width:320px;max-width:90vw;box-shadow:0 10px 40px rgba(0,0,0,.3);}
  .loginbox h3{margin:0 0 12px;font-size:17px;}
  .loginbox input{width:100%;padding:10px 12px;border:1px solid #d1d5db;border-radius:8px;font-size:14px;margin-bottom:10px;box-sizing:border-box;}
  .loginbox .row{display:flex;gap:10px;justify-content:flex-end;}
  .loginbox button{padding:8px 16px;border:none;border-radius:8px;font-size:14px;cursor:pointer;}
  .loginbox .ok{background:var(--blue);color:#fff;}
  .loginbox .ok:hover{background:#1d4ed8;}
  .loginbox .cancel{background:#f1f5f9;color:#475569;}
  .loginmsg{font-size:13px;min-height:18px;margin-bottom:8px;}
  .loginmsg.err{color:#dc2626;}
  .loginmsg.ok{color:#059669;}
  @media(max-width:760px){.modal-inner{grid-template-columns:1fr;}.toolbar input[type=text]{width:100%;}}
</style>
</head>
<body>
<header>
  <h1>🎨 视觉设计知识库总览</h1>
  <p>__SUBTITLE__</p>
</header>
<div class="toolbar">
  <input type="text" id="search" placeholder="搜索名称 / 分类 / 提示词…">
  <div class="chips" id="srcChips">
    <span class="chip active" data-v="all">全部来源</span>
    <span class="chip" data-v="风格库">风格库</span>
    <span class="chip" data-v="提示词模板">提示词模板</span>
    <span class="chip" data-v="用户新增">用户新增</span>
    <span class="chip" data-v="我的收藏">我的收藏</span>
  </div>
  <div class="chips" id="ratioChips">
    <span class="chip active" data-v="all">全部画幅</span>
    <span class="chip" data-v="横">横版 16:9</span>
    <span class="chip" data-v="竖">竖版 9:16</span>
  </div>
  <select id="catSel"><option value="all">全部分类</option></select>
  <span class="count" id="count"></span>
</div>
<div class="grid" id="grid"></div>

<div class="modal" id="modal">
  <button class="close" id="closeBtn">×</button>
  <div class="modal-inner">
    <div class="gal">
      <span class="ratio-badge" id="ratioBadge"></span>
      <button class="gal-nav prev" id="prevBtn">‹</button>
      <button class="gal-nav next" id="nextBtn">›</button>
      <div class="gal-main"><img id="galImg" src="" alt="" onerror="this.onerror=null;this.src=_ph();"></div>
      <div class="gal-foot"><span class="counter" id="galCounter"></span></div>
      <div class="thumbs" id="thumbs"></div>
    </div>
    <div class="info" id="info"></div>
  </div>
</div>

<script>
const DATA = __DATA__;
const grid = document.getElementById('grid');
const search = document.getElementById('search');
const catSel = document.getElementById('catSel');
const countEl = document.getElementById('count');
let state = { src:'all', ratio:'all', cat:'all', q:'' };
const API = location.origin;
const fileOnly = location.protocol === 'file:';
// 任何图片加载失败都回退为自包含的 SVG 占位（不隐藏元素、不插节点，绝不裂图标、绝不污染其它图）
function _ph(){
  return 'data:image/svg+xml;utf8,'+encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="320">'+
    '<rect width="100%" height="100%" fill="#eef1f5"/>'+
    '<text x="50%" y="50%" font-family="sans-serif" font-size="18" fill="#94a3b8" '+
    'text-anchor="middle" dominant-baseline="middle">🖼 图片缺失</text></svg>');
}
const FAV_KEY = 'kb_favorites_v1';
function getFavs(){ try{ return new Set(JSON.parse(localStorage.getItem(FAV_KEY)) || []); }catch(e){ return new Set(); } }
function saveFavs(set){ localStorage.setItem(FAV_KEY, JSON.stringify(Array.from(set))); }
function isFav(id){ return getFavs().has(id); }
function toggleFavCard(id, btn){
  const set = getFavs();
  const on = !set.has(id);
  if(on) set.add(id); else set.delete(id);
  saveFavs(set);
  btn.classList.toggle('fav', on);
  updateFavChipCount();
  if(state.src==='我的收藏') render();
}
function updateFavChipCount(){
  const n = getFavs().size;
  const chip = document.querySelector('#srcChips .chip[data-v="我的收藏"]');
  if(chip) chip.textContent = n ? `我的收藏 (${n})` : '我的收藏';
}
function deleteUserEntry(id){
  const title = (id||'').startsWith('user:') ? id.slice(5) : id;
  if(!title) return;
  if(!confirm('确定删除《'+title+'》？此操作会从知识库永久移除（需通过「启动管理器」打开网页才生效）。')) return;
  fetch('/api/delete-entry',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({title:title})})
  .then(r=>r.json())
  .then(d=>{
    if(d.ok){ alert('已删除，刷新中…'); location.reload(); }
    else if(d.code==='NO_SERVER'){ alert('删除需要后端服务：请通过双击「启动管理器.bat」打开本网页，再点删除。'); }
    else { alert(d.msg||'删除失败'); }
  })
  .catch(e=>{ alert('网络错误，请确认是通过「启动管理器.bat」打开的网页：'+e); });
}

const cats = Array.from(new Set(DATA.map(d=>d.category))).sort();
cats.forEach(c=>{const o=document.createElement('option');o.value=c;o.textContent=c;catSel.appendChild(o);});

function esc(s){return (s||'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));}

function filtered(){
  const q = state.q.trim().toLowerCase();
  return DATA.filter(d=>{
    if(state.src!=='all'){
      if(state.src==='我的收藏'){
        const favs = getFavs();
        if(favs.has(d.id)) return true;
        return false;
      }
      if(d.type!==state.src) return false;
    }
    if(state.cat!=='all' && d.category!==state.cat) return false;
    if(state.ratio!=='all'){
      const rs = (d.ratios||[]).join(' ');
      if(state.ratio==='横' && !rs.includes('16:9')) return false;
      if(state.ratio==='竖' && !rs.includes('9:16') && !rs.includes('竖版')) return false;
    }
    if(q){
      const hay = (d.name+' '+d.category+' '+d.categoryRaw+' '+(d.prompt||'')+' '+(d.summary||'')).toLowerCase();
      if(!hay.includes(q)) return false;
    }
    return true;
  });
}

function render(){
  const list = filtered();
  countEl.textContent = `共 ${list.length} 项`;
  grid.innerHTML = list.map(d=>{
    const thumb = d.images[0] ? d.images[0].src : '';
    let srcBadge;
    if(d.type==='风格库') srcBadge='<span class="badge b-style">风格库</span>';
    else if(d.type==='用户新增') srcBadge='<span class="badge b-user">用户新增</span>';
    else srcBadge='<span class="badge b-tpl">提示词模板</span>';
    const ratioBadges = (d.ratios||[]).map(r=>`<span class="badge b-ratio">${esc(r)}</span>`).join('');
    const imgN = d.images.length;
    const favClass = isFav(d.id) ? 'fav' : '';
    const starBtn = `<button class="favstar ${favClass}" onclick="event.stopPropagation(); toggleFavCard('${d.id}', this)" title="收藏 / 取消收藏" aria-label="收藏">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 17.27l6.18 3.73-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73-1.64 7.03z"/></svg>
    </button>`;
    const mgrCtl = (d.type==='用户新增')
      ? `<button class="delbtn" onclick="event.stopPropagation(); deleteUserEntry('${d.id}')" title="删除此条目">🗑</button>`
      : '';
    return `<div class="card" data-id="${d.id}">
      ${starBtn}
      ${mgrCtl}
      <div class="thumbwrap"><img class="thumb" src="${thumb}" loading="lazy" onerror="this.onerror=null;this.src=_ph();"></div>
      <div class="body">
        <p class="nm">${esc(d.name)}</p>
        ${srcBadge}<span class="badge b-cat">${esc(d.category)}</span>
        <div>${ratioBadges}</div>
        <div class="meta">${imgN} 张示例图 · ${d.type==='风格库'?'含横版+竖版':'提示词模板'}</div>
      </div></div>`;
  }).join('');
  grid.querySelectorAll('.card').forEach(c=>c.onclick=()=>openDetail(c.dataset.id));
  updateFavChipCount();
}

document.getElementById('srcChips').onclick=e=>{
  if(!e.target.dataset.v)return;
  state.src=e.target.dataset.v;
  setActive('srcChips',e.target);render();
};
document.getElementById('ratioChips').onclick=e=>{
  if(!e.target.dataset.v)return;
  state.ratio=e.target.dataset.v;
  setActive('ratioChips',e.target);render();
};
function setActive(group,el){document.querySelectorAll('#'+group+' .chip').forEach(c=>c.classList.remove('active'));el.classList.add('active');}
search.oninput=()=>{state.q=search.value;render();};
catSel.onchange=()=>{state.cat=catSel.value;render();};

const modal=document.getElementById('modal');
let cur=null, gi=0;
function openDetail(id){
  cur = DATA.find(d=>d.id===id); if(!cur)return;
  gi=0;
  document.getElementById('info').innerHTML = buildInfo(cur);
  bindThumbs();
  showImg(0);
  modal.classList.add('open');
  document.body.style.overflow='hidden';
}
function buildInfo(d){
  let h=`<h2>${esc(d.name)}</h2><div class="sub">${d.type==='风格库'?'风格/海报设计手法':'GPT 提示词模板'} · ${esc(d.category)}</div>`;
  if(d.type==='风格库'){
    if(d.mood) h+=`<div class="row"><div class="k">情绪 / 调性</div><div class="v">${esc(d.mood)}</div></div>`;
    if(d.summary) h+=`<div class="row"><div class="k">风格概述</div><div class="v">${esc(d.summary)}</div></div>`;
    if(d.palette&&d.palette.length) h+=`<div class="row"><div class="k">主色调</div><div class="swatches">${d.palette.map(c=>`<span class="sw" style="background:${esc(c)}" title="${esc(c)}"></span>`).join('')}</div></div>`;
    if(d.rendering) h+=`<div class="row"><div class="k">渲染模式</div><div class="v">${esc(d.rendering)}</div></div>`;
    h+=`<div class="row"><div class="k">可用画幅</div><div class="v"><span class="badge b-ratio">16:9 横版</span><span class="badge b-ratio">9:16 竖版</span></div></div>`;
    h+=`<div class="note">切换到竖版：把提示词中的 <code>{ASPECT_RATIO}</code> 替换为 <code>9:16</code>；横版替换为 <code>16:9</code>。</div>`;
    h+=`<div class="row linkrow"><a href="${esc(d.jsonPath)}" target="_blank" rel="noopener">打开 style.json ↗</a></div>`;
  } else {
    if(d.images.length){
      const parts=[];
      if(d.twitterCount) parts.push(`Twitter 合集图 ${d.twitterCount} 张`);
      if(d.localCount) parts.push(`本地示例 ${d.localCount} 张`);
      h+=`<div class="note">示例图说明：${parts.join(' · ')}。单张合集图内含多个生成示例，已作为独立可翻看幻灯片呈现。</div>`;
    }
  }
  h+=`<div class="row"><div class="k">提示词（点击复制）</div>
      <div class="prompt-box"><button class="copy-btn" onclick="copyPrompt(this)">复制</button>${esc(d.prompt)}</div></div>`;
  return h;
}
function showImg(i){
  if(!cur)return;
  const n=cur.images.length; gi=(i+n)%n;
  const im=cur.images[gi];
  document.getElementById('galImg').src=im.src;
  document.getElementById('ratioBadge').textContent = im.label + (im.ratio&&im.ratio!=='参考' ? ' · '+im.ratio : '');
  document.getElementById('galCounter').textContent = `${gi+1} / ${n}` + (n>1?'（可左右翻看）':'');
  document.querySelectorAll('#thumbs img').forEach((t,idx)=>t.classList.toggle('active',idx===gi));
}
function bindThumbs(){
  document.getElementById('thumbs').innerHTML = cur.images.map((im,i)=>
    `<img src="${im.src}" data-i="${i}" onerror="this.onerror=null;this.src=_ph();">`).join('');
  document.querySelectorAll('#thumbs img').forEach(t=>t.onclick=()=>showImg(+t.dataset.i));
}
document.getElementById('prevBtn').onclick=()=>showImg(gi-1);
document.getElementById('nextBtn').onclick=()=>showImg(gi+1);
document.getElementById('closeBtn').onclick=closeModal;
modal.onclick=e=>{if(e.target===modal)closeModal();};
function closeModal(){modal.classList.remove('open');document.body.style.overflow='';}
document.addEventListener('keydown',e=>{
  if(!modal.classList.contains('open'))return;
  if(e.key==='Escape')closeModal();
  if(e.key==='ArrowLeft')showImg(gi-1);
  if(e.key==='ArrowRight')showImg(gi+1);
});
function copyPrompt(btn){
  const txt=btn.parentElement.innerText.replace('复制','').trim();
  navigator.clipboard.writeText(txt).then(()=>{btn.textContent='已复制✓';setTimeout(()=>btn.textContent='复制',1500);});
}

</script>
</body>
</html>'''

def build_html(all_items, n_styles, n_tpl):
    n_user = sum(1 for d in all_items if d.get('type') == '用户新增')
    title = f'视觉设计知识库总览 · {n_styles} 风格 + {n_tpl} 提示词'
    parts = [f'「{n_styles} 套风格/海报设计手法」', f'「{n_tpl} 个 GPT 提示词模板」']
    if n_user:
        parts.append(f'「你自己新增的 {n_user} 条提示词」')
    subtitle = ('融合了' + '、'.join(parts) +
                '· 点击卡片查看可翻看的示例图与提示词，点右上角 ⭐ 即可收藏，收藏后在「我的收藏」中查看')
    data_json = json.dumps(all_items, ensure_ascii=False)
    html = HTML_TMPL.replace('__DATA__', data_json)
    html = html.replace('__TITLE__', title)
    html = html.replace('__SUBTITLE__', subtitle)
    return html

def write_merged_html():
    """解析风格库 + 提示词模板 + 用户新增，写出合并知识库 HTML。返回统计 dict。"""
    styles, templates, all_items = build_all()
    html = build_html(all_items, len(styles), len(templates))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    summary = {
        'styles': len(styles),
        'templates': len(templates),
        'user': sum(1 for d in all_items if d.get('type') == '用户新增'),
        'total': len(all_items),
        'out': OUT,
        'size': len(html),
    }
    return summary

# ========== 表格视图（styles-overview.html）生成 ==========
# 单一真相源：相对路径、不内嵌 base64、纯本地读取。两个同步脚本都调用本函数，
# 不再依赖已删除的 sync-readme.py（那正是「点同步就崩 / 表格页变 0 字节」的根因）。
REPO_RAW = "https://raw.githubusercontent.com/VigoZhao/AI-Visual-Prompt-Cookbook/main/"

def local_json_path(slug):
    return os.path.join(STYLES_DIR, slug, "style.json")

def find_local_image(slug, hint):
    d = os.path.join(STYLES_DIR, slug)
    if not os.path.isdir(d):
        return ""
    for j in sorted(glob.glob(os.path.join(d, "*.jpg"))):
        if hint in os.path.basename(j).lower():
            return j
    return ""

def _rel(path):
    if not path:
        return ""
    return os.path.relpath(path, ROOT).replace(os.sep, "/")

def abs_display(path):
    return os.path.abspath(path).replace("\\", "/")

def local_styles_list():
    """直接从本地 styles/ 读 style.json 生成表格所需结构（不联网）。"""
    out = []
    for d in sorted(glob.glob(os.path.join(STYLES_DIR, '*/'))):
        slug = os.path.basename(os.path.normpath(d))
        jp = os.path.join(d, 'style.json')
        if not os.path.exists(jp):
            continue
        try:
            data = json.load(open(jp, encoding='utf-8'))
        except Exception:
            continue
        out.append({
            'slug': slug,
            'name': data.get('style_name', slug),
            'description': data.get('style_summary', ''),
        })
    return out

def build_row_for_table(style):
    """为表格视图取 prompt/图片/json（优先本地，缺失回退 GitHub raw）。"""
    slug, name, desc = style["slug"], style["name"], style["description"]
    prompt_text = ""
    ljson = local_json_path(slug)
    if os.path.exists(ljson):
        try:
            with open(ljson, encoding="utf-8") as f:
                data = json.load(f)
            prompt_text = data.get("prompt_template", "") or data.get("style_summary", "")
        except Exception:
            pass
    if not prompt_text:
        prompt_text = desc
    if os.path.exists(ljson):
        json_link = _rel(ljson)
        json_csv = json_link  # 云端版：CSV 里也用相对路径（原为本机绝对路径）
    else:
        json_link = json_csv = REPO_RAW + f"styles/{slug}/style.json"
    local_16 = find_local_image(slug, "16x9")
    img16 = _rel(local_16) if local_16 else (REPO_RAW + f"styles/{slug}/{slug}-16x9.jpg")
    local_9 = find_local_image(slug, "9x16") or find_local_image(slug, "1x1")
    img9 = _rel(local_9) if local_9 else (REPO_RAW + f"styles/{slug}/{slug}-9x16.jpg")
    return {
        "title": name, "slug": slug, "description": desc, "prompt": prompt_text,
        "size1": img16, "size1_csv": img16,  # 云端版：相对路径
        "size2": img9, "size2_csv": img9,  # 云端版：相对路径
        "json": json_link, "json_csv": json_csv,
    }

def thumb_cell(path, label):
    if not path:
        return '<span class="na">—</span>'
    src = html.escape(path)
    return f'<img class="thumb" src="{src}" alt="{html.escape(label)}" onerror="this.onerror=null;this.src=_ph();" onclick="openLightbox(\'{src}\', \'{html.escape(label)}\')">'

def generate_table_html(rows):
    total = len(rows)
    html_rows = []
    for i, r in enumerate(rows, 1):
        prompt_escaped = html.escape(r["prompt"]).replace("\\", "\\\\").replace("'", "\\'")
        prompt_cell = (
            '<div class="prompt-wrap">'
            f'<button class="copy-btn" onclick="copyPrompt(this, \'{prompt_escaped}\')">复制</button>'
            f'<div class="prompt" ondblclick="copyPrompt(this, \'{prompt_escaped}\')">{html.escape(r["prompt"])}</div>'
            '</div>'
        )
        html_rows.append(
            "<tr>"
            f'<td class="idx">{i}</td>'
            f'<td class="title">{html.escape(r["title"])}</td>'
            f'<td>{prompt_cell}</td>'
            f'<td class="size">{thumb_cell(r["size1"], "16:9")}</td>'
            f'<td class="size">{thumb_cell(r["size2"], "9:16")}</td>'
            f'<td class="json"><a href="{html.escape(r["json"])}" target="_blank">style.json ↗</a></td>'
            "</tr>"
        )
    rows_html = "".join(html_rows)
    html_tpl = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>Styles 总览表（{total} 个）</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
       margin:0; padding:20px; background:#f6f7f9; color:#1c1e21; }}
h1 {{ font-size:20px; margin:0 0 4px; }}
.sub {{ color:#65676b; font-size:13px; margin-bottom:14px; }}
.controls {{ margin-bottom:12px; display:flex; gap:10px; flex-wrap:wrap; align-items:center; }}
.controls input {{ padding:7px 10px; border:1px solid #ccd0d5; border-radius:6px; font-size:13px; width:280px; }}
.controls .count {{ color:#65676b; font-size:13px; }}
table {{ border-collapse:collapse; width:100%; background:#fff; border-radius:8px; overflow:hidden;
        box-shadow:0 1px 3px rgba(0,0,0,.08); table-layout:auto; }}
th, td {{ border-bottom:1px solid #eaecef; padding:8px 10px; text-align:left; vertical-align:top; font-size:13px; }}
th {{ background:#f0f2f5; position:sticky; top:0; z-index:2; cursor:pointer; user-select:none; white-space:nowrap; }}
th:hover {{ background:#e4e6eb; }}
.idx {{ width:40px; color:#8a8d91; text-align:center; }}
.title {{ max-width:170px; min-width:120px; word-break:break-word; font-weight:600; line-height:1.4; }}
.size {{ white-space:nowrap; width:90px; text-align:center; }}
.thumb {{ height:70px; width:auto; max-width:120px; object-fit:cover; border-radius:4px;
         cursor:pointer; border:1px solid #e1e4e8; background:#fff; transition:transform .15s; }}
.thumb:hover {{ transform:scale(1.05); border-color:#1877f2; }}
.json {{ width:80px; white-space:nowrap; }}
.json a {{ color:#1877f2; text-decoration:none; }}
.json a:hover {{ text-decoration:underline; }}
.na {{ color:#b0b3b8; }}
.prompt-wrap {{ position:relative; padding-top:24px; min-width:260px; }}
.copy-btn {{ position:absolute; top:4px; right:4px; padding:2px 8px; font-size:11px;
            color:#1877f2; background:#fff; border:1px solid #dbe3ea; border-radius:4px;
            cursor:pointer; line-height:1.4; }}
.copy-btn:hover {{ background:#f0f7ff; border-color:#1877f2; }}
.prompt {{ max-height:120px; overflow:auto; line-height:1.5;
          font-family:"SFMono-Regular", Consolas, monospace; font-size:12px; color:#333;
          background:#fafbfc; border:1px solid #eee; border-radius:4px; padding:6px; }}
tr:hover {{ background:#f7f8fa; }}
#lb {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.88); z-index:1000;
      justify-content:center; align-items:center; flex-direction:column; }}
#lb.active {{ display:flex; }}
#lb img {{ max-width:92vw; max-height:82vh; object-fit:contain; border-radius:6px;
          box-shadow:0 10px 40px rgba(0,0,0,.5); }}
#lb .lb-cap {{ color:#fff; margin-top:10px; font-size:14px; opacity:.85; }}
#lb .lb-close {{ position:absolute; top:18px; right:24px; color:#fff; font-size:36px;
                line-height:1; cursor:pointer; opacity:.75; font-weight:300; }}
#lb .lb-close:hover {{ opacity:1; }}
</style></head>
<body>
<h1>Styles 总览表</h1>
<div class="sub">共 {total} 个风格 · 表头：标题 / 提示词 / 尺寸1(16:9) / 尺寸2(9x16) / json · 点击缩略图悬浮预览；点击/双击提示词“复制”按钮可复制</div>
<div class="controls">
  <input id="q" placeholder="搜索标题或提示词…" oninput="filterTable()">
  <span class="count" id="cnt"></span>
</div>
<table id="tbl">
<thead><tr>
<th onclick="sortBy(0)">#</th>
<th onclick="sortBy(1)">标题</th>
<th onclick="sortBy(2)">提示词</th>
<th>尺寸1</th><th>尺寸2</th><th>json</th>
</tr></thead>
<tbody>
{rows_html}
</tbody></table>

<div id="lb" onclick="if(event.target===this) closeLightbox()">
  <span class="lb-close" onclick="closeLightbox(); event.stopPropagation();">&times;</span>
  <img id="lb-img" src="" alt="" onerror="this.onerror=null;this.src=_ph();">
  <div class="lb-cap" id="lb-cap"></div>
</div>

<script>
function filterTable() {{
  var q = document.getElementById('q').value.toLowerCase();
  var trs = document.querySelectorAll('#tbl tbody tr');
  var n = 0;
  trs.forEach(function(tr){{
    var t = tr.innerText.toLowerCase();
    var show = t.indexOf(q) > -1;
    tr.style.display = show ? '' : 'none';
    if (show) n++;
  }});
  document.getElementById('cnt').innerText = '显示 ' + n + ' / {total}';
}}
var asc = true;
function sortBy(col) {{
  var tbl = document.getElementById('tbl');
  var rowsArr = Array.from(tbl.tBodies[0].rows);
  rowsArr.sort(function(a,b){{
    var x = a.cells[col].innerText.trim().toLowerCase();
    var y = b.cells[col].innerText.trim().toLowerCase();
    return asc ? x.localeCompare(y) : y.localeCompare(x);
  }});
  asc = !asc;
  rowsArr.forEach(function(r){{ tbl.tBodies[0].appendChild(r); }});
}}
function openLightbox(src, cap) {{
  var lbImg=document.getElementById('lb-img');
  lbImg.src = src;
  document.getElementById('lb-cap').innerText = cap || '';
  document.getElementById('lb').classList.add('active');
  document.body.style.overflow = 'hidden';
}}
function closeLightbox() {{
  document.getElementById('lb').classList.remove('active');
  document.getElementById('lb-img').src = '';
  document.body.style.overflow = '';
}}
function copyPrompt(el, text) {{
  navigator.clipboard.writeText(text).then(function(){{
    var btn = (el && el.tagName === 'BUTTON') ? el : el.previousElementSibling;
    if (!btn || btn.tagName !== 'BUTTON') btn = el.parentElement.querySelector('.copy-btn');
    var old = btn.innerText;
    btn.innerText = '已复制';
    setTimeout(function(){{ btn.innerText = old; }}, 1200);
  }}).catch(function(err){{
    alert('复制失败，请手动选择复制');
  }});
}}
document.addEventListener('keydown', function(e){{ if(e.key==='Escape') closeLightbox(); }});
filterTable();
</script>
</body></html>'''
    # 任何图片加载失败都回退为自包含 SVG 占位（不隐藏、不插节点，绝不裂图标、绝不污染其它图）
    html_tpl += '''
<script>
function _ph(){
  return 'data:image/svg+xml;utf8,'+encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="320">'+
    '<rect width="100%" height="100%" fill="#eef1f5"/>'+
    '<text x="50%" y="50%" font-family="sans-serif" font-size="18" fill="#94a3b8" '+
    'text-anchor="middle" dominant-baseline="middle">图片缺失</text></svg>');
}
</script>
'''
    return html_tpl

def generate_csv(rows):
    path = os.path.join(ROOT, '视觉资料库', 'styles-overview.csv')
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["标题", "提示词", "尺寸1", "尺寸2", "json"])
        for r in rows:
            w.writerow([r["title"], r["prompt"], r["size1_csv"], r["size2_csv"], r["json_csv"]])

def write_table_html():
    """重建 styles-overview.html + .csv（相对路径，不内嵌，纯本地）。返回风格数。"""
    rows = [build_row_for_table(st) for st in local_styles_list()]
    out_html = os.path.join(ROOT, '视觉资料库', 'styles-overview.html')
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(generate_table_html(rows))
    generate_csv(rows)
    return len(rows)


# ---------- 收藏条目管理（后端管理器 kb-manager 调用） ----------
if __name__ == '__main__':
    s = write_merged_html()
    print(f"风格库 {s['styles']} · 提示词 {s['templates']} · 用户新增 {s['user']} · 合计 {s['total']}")
    print('已写出', s['out'], '大小', s['size'])
    n = write_table_html()
    print(f"表格已更新：{n} 个风格 -> 视觉资料库/styles-overview.html")
