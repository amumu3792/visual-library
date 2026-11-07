# AI Visual Prompt Cookbook — 设计风格知识库

> 本文档是 AI 视觉提示词风格库的底层引用文档，供 AI 检索、匹配和使用 112 套设计风格系统。

## 目录

- [一、项目概述](#design-sec-1)
- [二、目录结构](#design-sec-2)
- [三、style.json 字段说明](#design-sec-3) — 环境变量、风格锚点、视觉解构、色彩规范、提示词模板等 14 个字段
- [四、md 文件说明](#design-sec-4) — 快捷提示词结构
- [五、如何使用](#design-sec-5) — AI 检索风格 / 生成提示词 / 切换画面比例
- [六、完整风格目录](#design-sec-6) — 112 套风格按字母排列，含名称/slug/概述/分类/情绪/色调/渲染
- [七、风格分类索引](#design-sec-7) — 按渲染模式 / 画面比例分类
- [八、Schema 文件](#design-sec-8)
- [九、扩展指南](#design-sec-9) — 新增 / 修改风格
- [十、快速检索速查](#design-sec-10) — 按需求关键词映射到推荐风格 slug

---

<a id="design-sec-1"></a>

## 一、项目概述

本项目是一个结构化的 AI 图像生成风格库，包含 **112 套**独立设计风格系统。每套风格都是一套完整的视觉语言体系，涵盖构图逻辑、色彩规范、字体处理、光影方向、渲染模式、提示词模板和负面提示词，可直接用于 AI 图像生成的风格锁定。

- **风格总数**：112 套
- **每套风格包含**：`style.json`（完整风格系统） + `.md`（快捷复制提示词） + 2 张预览图（16:9 横版 + 9:16 竖版）
- **支持尺寸**：16:9 横版 / 9:16 竖版
- **版本**：style-v2.1 schema

---

<a id="design-sec-2"></a>

## 二、目录结构

```
styles/
├── README.md                          # 风格总索引（旧路径，需更新）
├── [风格slug]/
│   ├── style.json                     # 完整风格系统（权威源文件）
│   ├── [风格slug].md                  # 快捷复制提示词（从 style.json 生成）
│   ├── [风格slug]-16x9.jpg            # 16:9 横版预览图
│   └── [风格slug]-9x16.jpg            # 9:16 竖版预览图
├── DESIGN-REFERENCE.md                # ← 本文档
└── .workbuddy/
    └── memory/                        # 工作记忆
```

<a id="design-sub-01"></a>

### 命名规则

| 元素 | 规则 | 示例 |
|------|------|------|
| 文件夹名 / slug | 全小写连字符 | `acid-lime-3d-streetwear-type-poster-style` |
| style.json | 固定文件名 | `style.json` |
| md 文件 | `{slug}.md` | `acid-lime-3d-streetwear-type-poster-style.md` |
| 横版预览图 | `{slug}-16x9.jpg` | `acid-lime-3d-streetwear-type-poster-style-16x9.jpg` |
| 竖版预览图 | `{slug}-9x16.jpg` | `acid-lime-3d-streetwear-type-poster-style-9x16.jpg` |

<a id="design-sub-02"></a>

### 路径引用方式（md 文件内）

md 文件已移入对应文件夹，所有引用均为相对路径：

![预览图](acid-lime-3d-streetwear-type-poster-style/acid-lime-3d-streetwear-type-poster-style-16x9.jpg) 

```markdown
![预览图](acid-lime-3d-streetwear-type-poster-style/acid-lime-3d-streetwear-type-poster-style-16x9.jpg)  <!-- 子文件夹图片 -->
[style.json](style.json)                                         <!-- 同目录 JSON -->
[风格文件夹](./)                                                  <!-- 当前目录 -->
```

---

<a id="design-sec-3"></a>

## 三、style.json 字段说明

每套风格的 `style.json` 是权威源文件，包含以下顶层字段：

<a id="design-sub-03"></a>

### 3.1 基础信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `style_name` | string | 风格完整名称（英文，带空格和首字母大写） |
| `style_slug` | string | 风格标识符（全小写连字符，与文件夹名一致） |
| `style_version` | string | 风格版本号，如 `"1.0.0"` |
| `style_summary` | string | 一句话风格概述，描述核心视觉特征 |

<a id="design-sub-04"></a>

### 3.2 环境变量 `environment_variables`

定义风格的可替换变量，AI 生成时填入具体值。所有风格共用同一套变量名：

| 变量名 | 说明 |
|--------|------|
| `SUBJECT` | 主体：人物、吉祥物、物体或群体 |
| `SUBJECT_ACTION` | 主体的动作或姿态 |
| `PRODUCT_OR_PROP` | 产品、道具、工具或配件 |
| `LOCATION` | 场景、地点、环境设定 |
| `BACKGROUND_ELEMENTS` | 背景次要元素：道具、贴纸、标签等 |
| `MAIN_TEXT` | 主标题文字 |
| `SECONDARY_TEXT` | 副标题或辅助文案 |
| `ACCENT_SYMBOL` | 装饰符号：贴纸、图标、徽章等 |
| `WARDROBE_STYLE` | 服装造型、材质、表面处理方向 |
| `STYLE_FIDELITY_ANCHORS` | 风格保真锚点：必须保持可见的风格特征 |
| `SOURCE_CONTENT_TO_AVOID` | 需要规避的原始来源内容 |
| `ASPECT_RATIO` | 画面比例：`"9:16"` 或 `"16:9"` |

<a id="design-sub-05"></a>

### 3.3 风格保真锚点 `style_fidelity_anchors`

字符串数组，列出该风格**必须保持可见的核心视觉特征**。AI 生成时需确保这些特征全部呈现。

<a id="design-sub-06"></a>

### 3.4 来源规避清单 `source_content_to_avoid`

字符串数组，列出该风格**不得复制或再现的原始来源内容**，包括人物形象、品牌标识、特定文字、平台 UI 等。

<a id="design-sub-07"></a>

### 3.5 视觉解构 `visual_deconstruction`

对象，包含 10 个维度的风格分析：

| 子字段 | 说明 |
|--------|------|
| `style_category` | 风格分类定位 |
| `composition_logic` | 构图逻辑 |
| `subject_placement` | 主体位置策略 |
| `camera_angle_or_perspective` | 镜头角度与透视 |
| `typography_style` | 字体风格 |
| `color_palette_behavior` | 色彩行为 |
| `graphic_elements` | 图形元素 |
| `texture_and_finish` | 质感与表面处理 |
| `lighting` | 光影方向 |
| `mood` | 情绪氛围 |

<a id="design-sub-08"></a>

### 3.6 构图规则 `composition`

| 子字段 | 说明 |
|--------|------|
| `primary_structure` | 字符串数组，主要构图步骤 |
| `vertical_9x16` | 竖版构图说明 |
| `horizontal_16x9` | 横版构图说明 |

<a id="design-sub-09"></a>

### 3.7 字体规范 `typography`

| 子字段 | 说明 |
|--------|------|
| `headline` | 主标题字体风格 |
| `secondary_text` | 副标题字体风格 |
| `text_orientation` | 文字方向 |
| `text_behavior` | 文字使用规则 |

<a id="design-sub-10"></a>

### 3.8 色彩规范 `color_palette`

| 子字段 | 说明 |
|--------|------|
| `dominant` | 字符串数组，主色调 |
| `accents` | 字符串数组，辅助色/点缀色 |
| `behavior` | 色彩使用规则 |

<a id="design-sub-11"></a>

### 3.9 图像处理 `image_treatment`

| 子字段 | 说明 |
|--------|------|
| `rendering_mode` | 渲染模式（如 C4D、手绘、摄影等） |
| `surface_quality` | 表面质感 |
| `lighting` | 光照 |
| `depth` | 景深 |
| `post_processing` | 后期处理 |

<a id="design-sub-12"></a>

### 3.10 设计规则 `design_rules` / `do` / `avoid`

- `design_rules`：字符串数组，核心设计规则
- `do`：字符串数组，推荐做法
- `avoid`：字符串数组，需要避免的做法

<a id="design-sub-13"></a>

### 3.11 提示词模板 `prompt_template`

完整的 AI 提示词模板字符串，使用 `{变量名}` 占位符引用环境变量。填入具体值后可直接用于图像生成。

<a id="design-sub-14"></a>

### 3.12 负面提示词 `negative_prompt`

逗号分隔的负面提示词字符串，列出生成时需要避免的所有元素。

<a id="design-sub-15"></a>

### 3.13 示例 `examples`

数组，每套风格包含 3-4 个示例用例，每个示例结构：

```json
{
  "case_name": "用例名称",
  "values": {
    "SUBJECT": "...",
    "SUBJECT_ACTION": "...",
    "PRODUCT_OR_PROP": "...",
    "LOCATION": "...",
    "BACKGROUND_ELEMENTS": "...",
    "MAIN_TEXT": "...",
    "SECONDARY_TEXT": "...",
    "ACCENT_SYMBOL": "...",
    "WARDROBE_STYLE": "...",
    "STYLE_FIDELITY_ANCHORS": "...",
    "SOURCE_CONTENT_TO_AVOID": "..."
  }
}
```

---

<a id="design-sec-4"></a>

## 四、md 文件说明

每个 `.md` 文件是从 `style.json` 自动生成的快捷提示词，结构：

1. **风格名称**（H1 标题）
2. **预览图**（16:9 横版，相对路径引用）
3. **风格概述**（一段话描述）
4. **Copy Prompt**（可直接复制的完整提示词代码块，含默认示例值）
5. **Full Style**（style.json 和文件夹链接）

> md 文件底部注释：`<!-- Generated by scripts/generate-copy-prompts.py. Do not edit manually. -->`

---

<a id="design-sec-5"></a>

## 五、如何使用

<a id="design-sub-16"></a>

### 5.1 AI 检索风格

**按需求匹配风格的推荐流程：**

1. 明确需求关键词（行业、情绪、色彩、渲染类型、画面比例等）
2. 查阅下方「完整风格目录」，按 `category`（风格分类）和 `mood`（情绪氛围）匹配
3. 打开对应文件夹的 `style.json` 获取完整风格系统
4. 使用 `prompt_template` + 环境变量值生成最终提示词
5. 参考预览图确认视觉效果

**按色彩匹配：** 查阅目录中的 `主色调` 列，找到符合品牌色或需求色调的风格。

**按渲染类型匹配：** 查阅目录中的 `渲染模式` 列，区分 3D 渲染、手绘、摄影、拼贴等。

**按情绪匹配：** 查阅目录中的 `情绪氛围` 列，匹配活泼、严肃、怀旧、赛博等调性。

<a id="design-sub-17"></a>

### 5.2 生成提示词

**方式一：使用 md 快捷提示词（快速）**

直接打开 `{slug}/{slug}.md`，复制 Copy Prompt 代码块中的文本，替换其中的主体、动作、产品等值即可。

**方式二：使用 style.json 模板（精确）**

1. 读取 `style.json` 中的 `prompt_template` 字段
2. 将 `{ASPECT_RATIO}`、`{SUBJECT}` 等占位符替换为具体值
3. 同时使用 `negative_prompt` 作为负面提示词
4. 参考 `style_fidelity_anchors` 确保风格特征完整

**方式三：参考示例用例（学习）**

阅读 `examples` 数组中的 3-4 个示例，了解不同场景下环境变量的填法，照此模式创作新用例。

<a id="design-sub-18"></a>

### 5.3 切换画面比例

每套风格同时支持 16:9 和 9:16：
- 修改 `ASPECT_RATIO` 环境变量为 `"16:9"` 或 `"9:16"`
- 参照 `composition.vertical_9x16` 或 `composition.horizontal_16x9` 调整构图
- 预览图分别对应 `{slug}-16x9.jpg` 和 `{slug}-9x16.jpg`

---

<a id="design-sec-6"></a>

## 六、完整风格目录

> 以下按字母顺序列出全部 112 套风格。每条包含：风格名称、slug、概述、风格分类、情绪氛围、主色调、渲染模式。

<a id="design-sub-19"></a>

### A

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 1 | Acid Lime 3D Streetwear Type Poster Style | `acid-lime-3d-streetwear-type-poster-style` | 光泽 C4D 街头海报系统：浅色工作室空间、超大黑色块体排版、酸橙色记号笔笔触 | Glossy C4D youth-fashion poster | 时髦、活泼、略带赛博 | cool pale gray, off-white, deep black, acid lime | C4D 3D 渲染 |
| 2 | Analog Sticker Diary Portrait Poster Style | `analog-sticker-diary-portrait-poster-style` | 怀旧模拟日记拼贴肖像系统：大侧面插画主体、奶油方格纸背景 | 模拟日记拼贴肖像 | 怀旧、温暖 | — | 手绘插画 |
| 3 | Backseat Transit Doodle Letter Poster Style | `backseat-transit-doodle-letter-poster-style` | 真实后座交通照片转化为高能旅行海报 | 旅行海报 | 活力、旅行 | — | 摄影 + 涂鸦 |

<a id="design-sub-20"></a>

### B

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 4 | Black Cutout Food Card Ad | `black-cutout-food-card-ad-style` | 黑底食品推广风格：不规则奶油纸卡片、手刷中文大字、剪贴食品摄影 | 手工中文街头食品广告 | 便宜、手工、温暖、响亮 | — | 照片拼贴 |
| 5 | Blue Bubble Fisheye Action Poster Style | `blue-bubble-fisheye-action-poster-style` | 白底青年文化动作海报：矩形鱼眼照片、超大蓝色排版 | 青年文化动作海报 | 活力 | — | 鱼眼摄影 |
| 6 | Blue Chinese Perspective Type Canyon Style | `blue-chinese-perspective-type-canyon-style` | 中文排版海报系统：极端一点透视走廊 | 中文排版海报 | 紧迫、响亮、压缩、零售广告 | — | 透视排版 |
| 7 | Blue Halftone Ransom Zine Poster Style | `blue-halftone-ransom-zine-poster-style` | 粗犷钴蓝勒索杂志海报：撕碎白纸碎片、黑色照片复印件 | Ransom zine 海报 | 粗犷、DIY | — | 半调复印 |
| 8 | Blue HUD Macro Creator Tech Poster | `blue-hud-macro-product-poster` | 高密度蓝色创作者科技广告：微距 3D 硬件、超大棱纹手套、电蓝 HUD 面板 | 3D 创作者科技海报 | 未来感、产品发布 | — | C4D 3D 渲染 |
| 9 | Blue Lime Kinetic Comic Type Poster Style | `blue-lime-kinetic-comic-type-poster-style` | 响亮平面漫画海报：电蓝网格纸、超大霓虹绿 | 漫画海报 | 响亮、活力 | — | 平面漫画 |
| 10 | Bold Anime Reaction Thumbnail Style | `bold-anime-reaction-thumbnail-style` | 高冲击力动漫网页缩略图：超大反应角色、粗体黄色标题 | 动漫缩略图 | 高冲击、夸张 | — | 动漫插画 |
| 11 | Bold Block Mascot Poster Style | `bold-block-mascot-poster-style` | 密集平面海报：巨型黑色展示字体、粗壮白色吉祥物 | 吉祥物海报 | 活泼、直率 | — | 平面插画 |

<a id="design-sub-21"></a>

### C

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 12 | Chromatic Fisheye Orbit Pop Poster Style | `chromatic-fisheye-orbit-pop-poster-style` | 高调流行海报：极端鱼眼摄影、凸面玻璃穹顶构图 | 流行海报 | 高调、流行 | — | 鱼眼摄影 |
| 13 | Clean Triptych Travel Vlog Thumbnail Style | `clean-triptych-travel-vlog-thumbnail-style` | 干净旅行 Vlog 缩略图：三块垂直摄影面板、超大标题 | 旅行缩略图 | 干净、整洁 | — | 摄影拼贴 |
| 14 | Cobalt Megatype Roadside Travel Editorial | `cobalt-megatype-roadside-travel-editorial-style` | 怀旧路边旅行编辑海报：裁切钴蓝超大字体 | 旅行编辑海报 | 怀旧、旅行 | — | 编辑设计 |
| 15 | Cobalt Torn Didone Portrait Editorial | `cobalt-torn-didone-portrait-editorial-style` | 稀疏时尚编辑海报：暖纸场地、居中半调肖像 | 时尚编辑 | 稀疏、优雅 | — | 半调印刷 |
| 16 | Cobalt Xerox Script Editorial Poster | `cobalt-xerox-script-editorial-poster-style` | 压缩对抗性钴蓝编辑海报：碎片化 grotesk 标题 | 编辑海报 | 对抗、压缩 | — | 复印拼贴 |
| 17 | Coral Window Megatype Motion Poster | `coral-window-megatype-motion-poster-style` | 触感编辑动态海报：珊瑚红纸场地、冷色窗户 | 动态编辑海报 | 动感而克制 | coral red, pale powder blue, charcoal | 编辑设计 |
| 18 | Cozy Bedroom Doodle Companion Snapshot Style | `cozy-bedroom-doodle-companion-snapshot-style` | 随意低光家居照片：大平面 2D 抱枕玩伴合成 | 家居照片 | 温馨、随意 | — | 摄影 + 2D 合成 |
| 19 | Crayon Catalog Doodle Poster Style | `crayon-catalog-doodle-poster-style` | 稀疏产品目录海报：儿童蜡笔画风格 | 产品目录海报 | 童趣、手工 | — | 蜡笔手绘 |
| 20 | Cream Smoke City Manga Poster Style | `cream-smoke-city-manga-poster-style` | 竖版和横版插画系统：精细漫画墨线、巨大烟雾城市 | 城市漫画插画 | 烟雾、城市 | — | 漫画插画 |
| 21 | Crimson Ink Manga Dossier | `crimson-ink-manga-dossier` | 高密度漫画编辑档案海报：戏剧性前缩插画英雄、超大标题 | 漫画编辑档案 | 戏剧性、密集 | — | 手绘漫画 |
| 22 | Crimson Noir Newsprint Editorial | `crimson-noir-newsprint-editorial-style` | 精英文化杂志封面：纪念性灰度肖像、窄版红黑刊头 | 文化杂志封面 | 严肃、知性、电影感 | — | 灰度摄影 |
| 23 | Cyan Grain Macro Megatype Poster | `cyan-grain-macro-megatype-poster-style` | 稀疏实验编辑海报：极度放大的微距照片 | 实验编辑海报 | 实验、稀疏 | — | 微距摄影 |
| 24 | Cyan Red Shockwave Type Poster Style | `cyan-red-shockwave-type-poster-style` | 平面插画海报：饱和青色场地、超大红色块体排版 | 平面流行海报 | 噪杂、庆祝、快速 | — | 平面插画 |

<a id="design-sub-22"></a>

### D

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 25 | Dusk Cyan Layered Type Poster Style | `dusk-cyan-layered-type-poster-style` | 全出血黄昏照片海报：深蓝剪影、超大青白排版 | 摄影编辑海报 | 平静、电影感、怀旧 | — | 摄影叠加排版 |

<a id="design-sub-23"></a>

### E

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 26 | Electric Blue Cutout Manga Poster Style | `electric-blue-cutout-manga-poster-style` | 饱和电蓝场地插画海报：锐利白色剪贴、漫画能量 | 电蓝漫画海报 | 独立、活力 | — | 漫画插画 |
| 27 | Electric Blue Silhouette Product Launch Style | `electric-blue-silhouette-product-launch-style` | 稀疏高端消费科技发布海报：黑色负空间、蓝色剪影 | 消费电子海报 | 安静、高端、悬念 | — | 极简合成 |
| 28 | Electric Cobalt Motion Type Poster | `electric-cobalt-motion-type-poster-style` | 高能社区活动海报：全出血运动模糊照片 + 超大排版 | 社区活动海报 | 高能 | deep cobalt blue, ultramarine, royal blue | 摄影 + 排版 |

<a id="design-sub-24"></a>

### F

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 29 | Fantasy Scribble Mascot Poster Style | `fantasy-scribble-mascot-poster-style` | 原始手绘奇幻海报：超大不均字母、霓虹记号笔吉祥物 | 奇幻手绘海报 | 梦幻、有趣、奇异 | — | 手绘记号笔 |
| 30 | Folded Diamond Perspective Type Poster Style | `folded-diamond-perspective-type-poster-style` | 大胆极简编辑海报：低角度英雄摄影在菱形透视框内 | 极简编辑海报 | 大胆、极简 | — | 摄影 + 排版 |
| 31 | Folded Newspaper Product Ad Style | `folded-newspaper-product-ad-style` | 折叠大报产品广告：密集双语报纸排版、写实产品 | 报纸广告 | 大胆、诱人、编辑 | — | 摄影 + 排版 |
| 32 | Foreshortened Gradient Impact Ad Style | `foreshortened-gradient-impact-ad-style` | 高端动态广告系统：虫眼超广角照片、前缩主体 | 动态广告 | 高端、动感 | — | 超广角摄影 |

<a id="design-sub-25"></a>

### G

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 33 | Gothic Cat Doodle Photo Collage Style | `gothic-cat-doodle-photo-collage-style` | 戏剧建筑摄影 + 卡通涂鸦猫拼贴 | 照片插画拼贴 | 哥特、俏皮 | — | 摄影 + 涂鸦 |

<a id="design-sub-26"></a>

### H

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 34 | Halftone Assemblage Metaphor PSA Poster Style | `halftone-assemblage-metaphor-psa-poster-style` | 稀疏复古 PSA 海报：一类材料排列成隐喻形状 | 复古 PSA 海报 | 公共服务、象征 | — | 半调摄影 |
| 35 | Hot Ink Comic Poster | `hot-ink-comic-poster` | 响亮平面漫画传单：芥末黄场地、珊瑚红剪贴 | 漫画传单 | 活泼、嘈杂、手工 | — | 平面漫画 |

<a id="design-sub-27"></a>

### I

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 36 | Ice Cyan Megatype Action Poster Style | `ice-cyan-megatype-action-poster-style` | 动态编辑动作海报：冰白画布、超大深青排版 | 体育文化编辑海报 | 竞争、活力、抱负 | — | 摄影 + 排版 |
| 37 | Impact Burst Halftone Comic Poster Style | `impact-burst-halftone-comic-poster-style` | 响亮复古漫画海报：粗黑墨线、平涂高饱和色 | 复古漫画海报 | 响亮、复古 | — | 漫画半调 |

<a id="design-sub-28"></a>

### J

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 38 | Jade Glyph Grocer Collage Poster Style | `jade-glyph-grocer-collage-poster-style` | 稀疏东亚杂货海报：暖奶油纸、超大翡翠绿字 | 杂货海报 | 朴素、东亚 | — | 拼贴插画 |
| 39 | Jagged Red Street Photo Event Poster Style | `jagged-red-street-photo-event-poster-style` | 高冲击街头活动海报：黑白纪实照片 + 红色锯齿 | 街头活动海报 | 城市、手工、原生 | paper white, B&W photo gray, hot red | 摄影 + 排版 |

<a id="design-sub-29"></a>

### K

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 40 | K-Pop Apocalypse Ransom Zine Style | `k-pop-apocalypse-ransom-zine-style` | 极繁 K-pop 时尚杂志拼贴：中央肖像剪贴、揉皱纸 | K-pop 时尚杂志 | 极繁、叛逆 | — | 拼贴 |
| 41 | Kinetic Editorial Photo Collage | `kinetic-editorial-photo-collage-style` | 高能动作海报：错落摄影瓷砖在白空间上 | 动作海报 | 青春、果断、快速 | white, black, pale sky blue | 摄影拼贴 |
| 42 | Kinetic Geometric Doodle Cutouts | `kinetic-geometric-doodle-cutouts` | 稀疏俏皮插画：角色由超大几何涂鸦剪贴组装 | 几何涂鸦插画 | 友好、轻盈、幽默 | — | 几何插画 |
| 43 | Kinetic Luxury Street Fashion Cover Style | `kinetic-luxury-street-fashion-cover-style` | 高端街头时尚杂志封面：侧面行走摄影 | 街头时尚封面 | 高端、街头 | stone beige, concrete gray, asphalt black | 时尚摄影 |

<a id="design-sub-30"></a>

### L

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 44 | Lime Loop Megatype Action Poster | `lime-loop-megatype-action-poster-style` | 高能工作室动作海报：俯拍广角照片 + 超大排版 | 体育编辑海报 | 大胆、现代 | studio white, forest green | 摄影 + 排版 |
| 45 | Liquid Chrome Clearance Poster Style | `liquid-chrome-clearance-poster-style` | 高冲击商业海报：光泽液态铬 3D 排版 | 赛博零售海报 | 超现实、赛博 | acid lime, chartreuse, mint | 3D 渲染 |
| 46 | Loose Scribble Riso Print Style | `loose-scribble-riso-print-style` | 稀疏手工 Riso/丝网印海报：大简化主体 | Riso 印刷海报 | 亲密、俏皮、手工 | — | Riso 丝网印 |
| 47 | Luxury Perspective Checkerboard Editorial | `luxury-perspective-checkerboard-editorial` | 高时尚编辑海报：低角度奢华摄影、红白棋盘格 | 高时尚编辑 | 奢华、高端 | studio white, signal red, deep black | 时尚摄影 |

<a id="design-sub-31"></a>

### M

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 48 | Manga Dossier Blueprint Poster | `manga-dossier-blueprint-poster` | 做旧漫画角色档案海报：奶油纸边距、超大蓝图网格 | 漫画档案海报 | 档案、做旧 | — | 漫画 + 蓝图 |
| 49 | Market Brush Produce Poster Style | `market-brush-produce-poster-style` | 稀疏生鲜市场海报：暖象牙纸、超大笔刷产品 | 市场海报 | 朴素、新鲜 | — | 笔刷插画 |
| 50 | Metro Doodle Snapshot Diary | `metro-doodle-snapshot-diary-style` | 手持城市交通照片拼贴：地铁、公交、电车 | 交通日记 | 城市、日记 | — | 摄影 + 涂鸦 |
| 51 | Mono Noir Type Portrait Poster Style | `mono-noir-type-portrait-poster-style` | 黑白编辑海报：高对比肖像 + 排版 | 黑白编辑 | 安静、克制 | — | 黑白摄影 |
| 52 | Monochrome Grid Sneaker Tech Spec | `monochrome-grid-sneaker-tech-spec` | 黑白运动鞋产品分析海报：超大球鞋、技术网格 | 运动鞋技术海报 | 技术、分析 | — | 黑白摄影 |
| 53 | Monochrome Xerox Sports Dossier | `monochrome-xerox-sports-dossier` | 黑白复印编辑拼贴：超大裁切主体 | 体育编辑拼贴 | 复古、档案 | — | 复印拼贴 |
| 54 | Mountain Trail Monster Doodle Poster Style | `mountain-trail-monster-doodle-poster-style` | 户外徒步照片 + 平面手绘怪兽玩伴 | 户外 + 涂鸦 | 户外、俏皮 | — | 摄影 + 手绘 |
| 55 | Multi-Color Beverage Splash Ad System Style | `multi-color-beverage-splash-ad-system-style` | 饮料发布广告系统：四套色彩变体模板 | 饮料广告 | 商业、活力 | — | 摄影 + 合成 |

<a id="design-sub-32"></a>

### N

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 56 | Naive Marker PSA Poster Style | `naive-marker-psa-poster-style` | 友好手绘公共服务海报：粗不规则记号笔轮廓 | PSA 海报 | 友好、手工 | — | 记号笔手绘 |
| 57 | Naive Marker Quote Card Style | `naive-marker-quote-card-style` | 高瘦手绘荒诞引语卡片：粗糙黑色记号笔 | 引语卡片 | 荒诞、自制、冷面 | — | 记号笔手绘 |
| 58 | Neon Doodle Gallery Snapshot | `neon-doodle-gallery-snapshot-style` | 随意手机照片 + 混乱霓虹数字记号笔涂鸦 | 画廊快照 | 霓虹、混乱 | — | 手机摄影 + 数字涂鸦 |
| 59 | Neon Kinetic Typographic Poster | `neon-kinetic-typographic-poster-style` | 戏剧性户外编辑海报：低角度生活摄影 + 超大排版 | 户外编辑海报 | 戏剧、动态 | — | 摄影 + 排版 |
| 60 | Neon Outdoor Diary Longform Collage Style | `neon-outdoor-diary-longform-collage-style` | 高瘦移动优先户外日记海报：炭黑画布、纪实摄影 | 户外日记 | 活力、个人、户外 | — | 摄影 + 拼贴 |
| 61 | Neon Plush Gadget Pop 3D Style | `neon-plush-gadget-pop-3d-style` | 光泽玩具广告 3D 风格：酸橙工作室、毛绒小工具 | 玩具广告 3D | 俏皮、触感、收藏 | — | C4D 3D 渲染 |
| 62 | Neon Stadium 3D Hero Type Poster Style | `neon-stadium-3d-hero-type-poster-style` | 超饱和 3D 活动海报：玩具感英雄、极端低角度 | 3D 活动海报 | 快速、英雄、俏皮 | — | C4D 3D 渲染 |
| 63 | Neon Type Photo Scribble Poster | `neon-type-photo-scribble-poster-style` | 高冲击活动海报：有毒霓虹色场、巨大黑色排版 | 活动海报 | 竞争、响亮、城市 | — | 摄影 + 涂鸦 |

<a id="design-sub-33"></a>

### O

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 64 | Olive Scribble Sports Poster Style | `olive-scribble-sports-poster-style` | 动态平面编辑插画：灰白纸、大橄榄绿 | 体育编辑插画 | 快速、原生、编辑 | — | 手绘插画 |
| 65 | Orange Brush Mascot Action Poster Style | `orange-brush-mascot-action-poster-style` | 稀疏橙白黑平面插画：白色吉祥物、超大橙色 | 吉祥物海报 | 活力 | — | 平面插画 |

<a id="design-sub-34"></a>

### P

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 66 | Photo Illustration Overlay Poster | `photo-illustration-overlay-poster-style` | 真实城市照片 + 超大高饱和平面 2D 卡通人物合成 | 照片插画合成 | 城市、卡通 | — | 摄影 + 2D 合成 |
| 67 | Pink Anime Motorcycle Spec Poster Style | `pink-anime-motorcycle-spec-poster-style` | 密集运动档案海报：原创动漫骑手 + 英雄摩托 | 摩托档案海报 | 活力、时尚、技术 | — | 动漫插画 |
| 68 | Playful Marker Grounding Poster Style | `playful-marker-grounding-poster-style` | 天真手绘海报：奶油纸边距、松散记号笔拼贴 | PSA 手绘海报 | 俏皮、手工、童趣 | — | 记号笔手绘 |
| 69 | Playful Mascot Doodle Snapshot Style | `playful-mascot-doodle-snapshot-style` | 随意真实社交照片 + 卡通角色涂鸦叠加 | 社交照片 + 涂鸦 | 俏皮 | — | 摄影 + 手绘 |
| 70 | Plush City Festival Mobile Poster | `plush-city-festival-mobile-poster-style` | 明亮移动活动海报：真实城市地标 + 柔软毛绒吉祥物 | 活动海报 | 明亮、柔软 | — | 摄影 + 3D 合成 |
| 71 | Plush Comic Toy Product Poster Style | `plush-comic-toy-product-poster-style` | 响亮玩具产品海报：毛绒英雄、复古奶油海报 | 玩具产品海报 | 响亮、复古 | — | 漫画 + 3D |
| 72 | Pop Bubble Letter Photo Poster Style | `pop-bubble-letter-photo-poster-style` | 有力照片插画海报：中央低角度时尚肖像 + 泡泡字母 | 照片插画海报 | 有力、时尚 | — | 摄影 + 排版 |
| 73 | Prismatic Glass Animal Weekend Editorial | `prismatic-glass-animal-weekend-editorial` | 稀疏黑色编辑海报：超大半透明动物雕塑 | 编辑海报 | 稀疏、棱镜 | — | 3D 渲染 |

<a id="design-sub-35"></a>

### Q

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 74 | Quiet Luxury Furniture Nameplate Poster Style | `quiet-luxury-furniture-nameplate-poster-style` | 高端家具编辑海报：暖灰白工作室、超大铭牌排版 | 家具目录海报 | 高端、安静 | — | 产品摄影 + 排版 |

<a id="design-sub-36"></a>

### R

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 75 | Red Black Manga Tabloid Poster Style | `red-black-manga-tabloid-poster-style` | 密集黑白猩红漫画小报海报：超大压缩排版 | 漫画小报 | 密集、戏剧 | — | 漫画插画 |
| 76 | Red Yellow Grunge Skate Cover Style | `red-yellow-grunge-skate-cover-style` | 原始地下动作文化杂志封面：超大扭曲红黄标题 | 滑板杂志封面 | 粗犷、怀旧、嘈杂 | — | 拼贴 |
| 77 | Red Yellow Product Trophy Collage Style | `red-yellow-product-trophy-collage-style` | 快餐广告牌产品拼贴：饱和红黄海报色 | 产品拼贴广告 | 快速、商业 | — | 摄影 + 拼贴 |
| 78 | Retro Future Chrome Portrait Dossier | `retro-future-chrome-portrait-dossier` | 复古未来编辑肖像：不对称技术档案侧面 | 复古未来肖像 | 复古、未来 | — | 合成 |
| 79 | Rough Animation Pet Sketch Storyboard Style | `rough-animation-pet-sketch-storyboard-style` | 松散动画开发草图风格：暖米色纸 | 动画草图 | 松散、温馨 | — | 手绘草图 |
| 80 | Rough Ink Music Doodle Poster Style | `rough-ink-music-doodle-poster-style` | 粗糙手绘墨水海报：超大深绿黑刷子字母 | 音乐涂鸦海报 | 俏皮、手工、温馨 | — | 手绘墨水 |
| 81 | Rough Marker Monster Poster Style | `rough-marker-monster-poster-style` | 天真儿童海报：粗黑记号笔轮廓、粗糙蜡笔粉彩 | 儿童海报 | 天真、俏皮 | — | 记号笔 + 蜡笔 |

<a id="design-sub-37"></a>

### S

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 82 | Scarlet Block Cutout Doodle Book Cover Style | `scarlet-block-cutout-doodle-book-cover-style` | 文学封面系统：白纸场地、超大猩红衬线字 | 书籍封面 | 文学、荒诞 | — | 剪贴插画 |
| 83 | Scarlet Court Photo Type Poster | `scarlet-court-photo-type-poster-style` | 饱和动作广告海报：平面猩红场地、硬边蓝色照片 | 动作广告 | 动感 | scarlet red, electric court blue, cyan blue | 摄影 + 排版 |
| 84 | Scarlet Megatype Action Collage Style | `scarlet-megatype-action-collage-style` | 高冲击动作海报：饱和猩红场地、超大对角排版 | 体育编辑拼贴 | 高冲击 | — | 摄影 + 丝网印 |
| 85 | School Grid Paper Cutout Poster | `school-grid-paper-cutout-poster` | 稀疏怀旧海报：暖教室网格纸、手绘竖排文字 | 怀旧校园海报 | 怀旧、安静、手工 | — | 手绘 |
| 86 | Sky Blue Home Life Doodle Poster Style | `sky-blue-home-life-doodle-poster-style` | 天真平面海报：全天空蓝场地、白色房屋形内嵌 | 家居海报 | 俏皮、年轻、温馨 | — | 平面手绘 |
| 87 | Sky Blue Lucky Tag Doodle Poster Style | `sky-blue-lucky-tag-doodle-poster-style` | 稀疏平面涂鸦海报：饱和天空蓝、粗白标题 | 幸运涂鸦海报 | 明亮、幸运、俏皮 | — | 平面手绘 |
| 88 | Soft Analog Future Editorial Poster | `soft-analog-future-editorial-poster-style` | 安静模拟未来编辑海报：暖奶油纸、黑色新哥特字 | 模拟未来编辑 | 安静、未来 | — | 编辑设计 |
| 89 | Subway Doodle Photo Hybrid | `subway-doodle-photo-hybrid-style` | 手机拍摄城市交通海报：纪实地铁或街道照片 + 涂鸦 | 交通照片 + 涂鸦 | 城市、纪实 | — | 手机摄影 + 涂鸦 |
| 90 | Sun-Faded Scenic Editorial Poster | `sun-faded-scenic-editorial-poster` | 怀旧风景编辑海报：巨大暖象牙衬线标题 | 风景编辑 | 怀旧、褪色 | — | 摄影 + 排版 |
| 91 | Sunburst Fisheye Bubble Type Poster Style | `sunburst-fisheye-bubble-type-poster-style` | 超低角度鱼眼夏日生活海报：近距摄影主体 | 夏日生活海报 | 夏日、活力 | — | 鱼眼摄影 |
| 92 | Sunlit Architectural Fashion Editorial | `sunlit-architectural-fashion-editorial` | 精致户外高时尚编辑摄影：低角度建筑 | 高时尚编辑 | 精致、奢华 | sunlit ivory, warm stone beige, sand taupe | 时尚摄影 |
| 93 | Sunlit Coastal Product Blitz | `sunlit-coastal-product-blitz` | 高密度写实海岸产品广告：日光桌面英雄产品 | 海岸产品广告 | 日光、商业 | turquoise ocean blue, sky blue, weathered wood brown | 产品摄影 |
| 94 | Sunlit Kinetic Block Type Photo Poster | `sunlit-kinetic-block-type-photo-poster-style` | 高能编辑体育生活海报：全出血日光照片 + 排版 | 体育生活海报 | 高能 | sky blue, cyan blue, warm cream | 摄影 + 排版 |
| 95 | Sunlit Supermodel Nameplate Editorial | `sunlit-supermodel-nameplate-editorial` | 暖色模拟时尚编辑海报：户外超模照片 + 排版 | 时尚编辑 | 轻松奢华 | — | 时尚摄影 |
| 96 | Sunny 3D Avatar Campaign Style | `sunny-3d-avatar-campaign-style` | 明亮社交活动海报：光泽玩具感 3D 头像 | 社交活动海报 | 明亮、活泼 | electric sky blue, cloud white, grass green | C4D 3D 渲染 |
| 97 | Surreal Fish Doodle Landmark Photo Collage Style | `surreal-fish-doodle-landmark-photo-collage-style` | 明亮旅行照片拼贴：超大平面 2D 卡通旅行者、奇幻鱼 | 旅行拼贴 | 奇幻、旅行 | — | 摄影 + 2D 合成 |
| 98 | Surreal Megatype Dossier Collage | `surreal-megatype-dossier-collage` | 密集新编辑海报：纪念性白色填充和轮廓排版叠加 | 新编辑拼贴 | 密集、超现实 | — | 拼贴 |

<a id="design-sub-38"></a>

### T

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 99 | Teenage Skate Scribble Screenprint Poster Style | `teenage-skate-scribble-screenprint-poster-style` | 复古滑板杂志海报：扭曲中央滑板手剪贴、奶油纸 | 滑板杂志海报 | 复古、粗犷 | — | 丝网印 |
| 100 | Tokyo Kawaii Travel Collage Poster | `tokyo-kawaii-travel-collage-poster-style` | 极繁日本城市旅行拼贴：粗体目的地排版、可爱贴纸 | 旅行拼贴 | 可爱、极繁 | — | 拼贴 |
| 101 | Tri Color Hardcut Portrait Poster Style | `tri-color-hardcut-portrait-poster-style` | 干净三色硬切肖像海报：平面青色背景、珊瑚色肖像 | 三色肖像海报 | 干净、平面 | — | 平面插画 |
| 102 | Turquoise Red Techno Manga Poster Style | `turquoise-red-techno-manga-poster-style` | 复古科技漫画海报：奶油纸、巨大红色展示字 | 科技漫画海报 | 复古、科技 | — | 漫画插画 |

<a id="design-sub-39"></a>

### U

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 103 | Urban Photo Ink Beast Collage Style | `urban-photo-ink-beast-collage-style` | 超现实编辑拼贴：巨型平面墨水野兽 + 微型剧场 | 编辑拼贴 | 超现实 | — | 摄影 + 墨水插画 |
| 104 | Urban Transit Doodle Diary Style | `urban-transit-doodle-diary-style` | 原始城市快照个人视觉日记：真实公共空间照片 | 城市日记 | 原始、个人 | — | 摄影 + 涂鸦 |

<a id="design-sub-40"></a>

### V

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 105 | Vermilion Photocopy Tension Editorial | `vermilion-photocopy-tension-editorial` | 对抗性编辑海报：超大裁切黑白照片、朱红色 | 编辑海报 | 紧张、内省、叛逆 | — | 复印 + 排版 |

<a id="design-sub-41"></a>

### W

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 106 | Warm Fisheye Product Impact Ad Style | `warm-fisheye-product-impact-ad-style` | 高冲击产品广告：超广角近距摄影、隧道暖色渐变 | 产品广告 | 高冲击 | — | 鱼眼摄影 |

<a id="design-sub-42"></a>

### X

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 107 | Xerox Neon Editorial Collage | `xerox-neon-editorial-collage-style` | 高冲击编辑海报：超大做旧黑色标题、霓虹色场 | 编辑拼贴 | 反叛、动感、手工 | — | 复印 + 霓虹 |

<a id="design-sub-43"></a>

### Y

| # | 风格名称 | slug | 概述 | 分类 | 情绪 | 主色调 | 渲染 |
|---|---------|------|------|------|------|--------|------|
| 108 | Y2K Grunge Hip-Hop Cutout Poster Style | `y2k-grunge-hiphop-cutout-poster-style` | Y2K 垃圾嘻哈杂志拼贴海报：超大照片剪贴、酸色 | Y2K 嘻哈杂志 | 垃圾、嘻哈 | — | 拼贴 |
| 109 | Y2K Mirror UI Scribble Collage Style | `y2k-mirror-ui-scribble-collage-style` | 粗糙 Y2K 照片拼贴：广角闪光摄影、漂浮桌面 UI | Y2K 拼贴 | 粗糙、数字 | — | 摄影 + 数字拼贴 |
| 110 | Y2K Streetwear Sticker Collage Style | `y2k-streetwear-sticker-collage-style` | 密集 Y2K 街头照片拼贴：超大剪贴主体、贴纸道具 | Y2K 街头拼贴 | 响亮、俏皮、街头 | — | 摄影拼贴 |
| 111 | Yellow Black Manga Food Zine Ad Style | `yellow-black-manga-food-zine-ad-style` | 密集日本漫画风食品和产品杂志广告：黑墨线 | 漫画食品广告 | 密集、漫画 | ink black, manga yellow, cream paper white | 漫画插画 |
| 112 | Yellow Graffiti Fisheye Manga Street Poster Style | `yellow-graffiti-fisheye-manga-street-poster-style` | 混合街头海报：冷色鱼眼城市照片 + 大漫画墨水涂鸦 | 街头海报 | 混合、街头 | — | 鱼眼摄影 + 漫画 |

---

<a id="design-sec-7"></a>

## 七、风格分类索引

<a id="design-sub-44"></a>

### 按渲染模式分类

| 渲染模式               | 相关风格 slug                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **C4D / 3D 渲染**    | `acid-lime-3d-streetwear-type-poster-style`, `blue-hud-macro-product-poster`, `liquid-chrome-clearance-poster-style`, `neon-plush-gadget-pop-3d-style`, `neon-stadium-3d-hero-type-poster-style`, `prismatic-glass-animal-weekend-editorial`, `sunny-3d-avatar-campaign-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **摄影 + 涂鸦/合成**     | `backseat-transit-doodle-letter-poster-style`, `cozy-bedroom-doodle-companion-snapshot-style`, `gothic-cat-doodle-photo-collage-style`, `metro-doodle-snapshot-diary-style`, `mountain-trail-monster-doodle-poster-style`, `neon-doodle-gallery-snapshot-style`, `photo-illustration-overlay-poster-style`, `playful-mascot-doodle-snapshot-style`, `plush-city-festival-mobile-poster-style`, `subway-doodle-photo-hybrid-style`, `surreal-fish-doodle-landmark-photo-collage-style`, `urban-transit-doodle-diary-style`, `urban-photo-ink-beast-collage-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **手绘 / 记号笔 / 蜡笔**  | `analog-sticker-diary-portrait-poster-style`, `crayon-catalog-doodle-poster-style`, `fantasy-scribble-mascot-poster-style`, `kinetic-geometric-doodle-cutouts`, `naive-marker-psa-poster-style`, `naive-marker-quote-card-style`, `olive-scribble-sports-poster-style`, `playful-marker-grounding-poster-style`, `rough-animation-pet-sketch-storyboard-style`, `rough-ink-music-doodle-poster-style`, `rough-marker-monster-poster-style`, `school-grid-paper-cutout-poster`, `sky-blue-home-life-doodle-poster-style`, `sky-blue-lucky-tag-doodle-poster-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **漫画 / 动漫插画**      | `blue-lime-kinetic-comic-type-poster-style`, `bold-anime-reaction-thumbnail-style`, `cream-smoke-city-manga-poster-style`, `crimson-ink-manga-dossier`, `electric-blue-cutout-manga-poster-style`, `hot-ink-comic-poster`, `impact-burst-halftone-comic-poster-style`, `pink-anime-motorcycle-spec-poster-style`, `red-black-manga-tabloid-poster-style`, `turquoise-red-techno-manga-poster-style`, `yellow-black-manga-food-zine-ad-style`, `yellow-graffiti-fisheye-manga-street-poster-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **摄影 + 排版（编辑/广告）** | `chromatic-fisheye-orbit-pop-poster-style`, `clean-triptych-travel-vlog-thumbnail-style`, `cobalt-megatype-roadside-travel-editorial-style`, `cobalt-torn-didone-portrait-editorial-style`, `coral-window-megatype-motion-poster-style`, `dusk-cyan-layered-type-poster-style`, `electric-cobalt-motion-type-poster-style`, `folded-diamond-perspective-type-poster-style`, `folded-newspaper-product-ad-style`, `foreshortened-gradient-impact-ad-style`, `ice-cyan-megatype-action-poster-style`, `jagged-red-street-photo-event-poster-style`, `kinetic-editorial-photo-collage-style`, `kinetic-luxury-street-fashion-cover-style`, `lime-loop-megatype-action-poster-style`, `luxury-perspective-checkerboard-editorial`, `neon-kinetic-typographic-poster-style`, `neon-outdoor-diary-longform-collage-style`, `neon-type-photo-scribble-poster-style`, `pop-bubble-letter-photo-poster-style`, `quiet-luxury-furniture-nameplate-poster-style`, `scarlet-court-photo-type-poster-style`, `scarlet-megatype-action-collage-style`, `sun-faded-scenic-editorial-poster`, `sunburst-fisheye-bubble-type-poster-style`, `sunlit-architectural-fashion-editorial`, `sunlit-coastal-product-blitz`, `sunlit-kinetic-block-type-photo-poster-style`, `sunlit-supermodel-nameplate-editorial`, `vermilion-photocopy-tension-editorial`, `warm-fisheye-product-impact-ad-style`, `y2k-grunge-hiphop-cutout-poster-style`, `y2k-mirror-ui-scribble-collage-style`, `y2k-streetwear-sticker-collage-style` |
| **拼贴 / 复印 / Riso** | `blue-halftone-ransom-zine-poster-style`, `cobalt-xerox-script-editorial-poster-style`, `crimson-noir-newsprint-editorial-style`, `cyan-grain-macro-megatype-poster-style`, `halftone-assemblage-metaphor-psa-poster-style`, `k-pop-apocalypse-ransom-zine-style`, `loose-scribble-riso-print-style`, `manga-dossier-blueprint-poster`, `monochrome-xerox-sports-dossier`, `red-yellow-grunge-skate-cover-style`, `red-yellow-product-trophy-collage-style`, `retro-future-chrome-portrait-dossier`, `scarlet-block-cutout-doodle-book-cover-style`, `surreal-megatype-dossier-collage`, `teenage-skate-scribble-screenprint-poster-style`, `tokyo-kawaii-travel-collage-poster-style`, `xerox-neon-editorial-collage-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **平面设计 / 排版海报**    | `blue-chinese-perspective-type-canyon-style`, `bold-block-mascot-poster-style`, `cyan-red-shockwave-type-poster-style`, `electric-blue-silhouette-product-launch-style`, `jade-glyph-grocer-collage-poster-style`, `orange-brush-mascot-action-poster-style`, `soft-analog-future-editorial-poster-style`, `tri-color-hardcut-portrait-poster-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **黑白 / 单色**        | `mono-noir-type-portrait-poster-style`, `monochrome-grid-sneaker-tech-spec`, `monochrome-xerox-sports-dossier`, `crimson-noir-newsprint-editorial-style`, `vermilion-photocopy-tension-editorial`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **食品广告**           | `black-cutout-food-card-ad-style`, `yellow-black-manga-food-zine-ad-style`, `multi-color-beverage-splash-ad-system-style`, `market-brush-produce-poster-style`, `sunlit-coastal-product-blitz`, `red-yellow-product-trophy-collage-style`, `folded-newspaper-product-ad-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **鱼眼摄影**           | `blue-bubble-fisheye-action-poster-style`, `chromatic-fisheye-orbit-pop-poster-style`, `sunburst-fisheye-bubble-type-poster-style`, `warm-fisheye-product-impact-ad-style`, `yellow-graffiti-fisheye-manga-street-poster-style`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

<a id="design-sub-45"></a>

### 按画面比例

所有 112 套风格均支持 **16:9 横版** 和 **9:16 竖版**，每套风格文件夹内含两张对应预览图。

---

<a id="design-sec-8"></a>

## 八、Schema 文件

完整的 JSON Schema 定义位于项目根目录：

```
schemas/style-v2.1.schema.json
```

可用于验证新增 style.json 文件的格式合规性。

---

<a id="design-sec-9"></a>

## 九、扩展指南

<a id="design-sub-46"></a>

### 新增风格

1. 在 `styles/` 下新建文件夹，命名为 `{slug}`（全小写连字符）
2. 编写 `style.json`，遵循 v2.1 schema，填入所有必填字段
3. 放入 2 张预览图：`{slug}-16x9.jpg` 和 `{slug}-9x16.jpg`
4. 使用 `scripts/generate-copy-prompts.py` 生成对应的 `.md` 文件
5. 更新本知识库文档的风格目录

<a id="design-sub-47"></a>

### 修改风格

1. 直接编辑对应文件夹的 `style.json`
2. 重新运行生成脚本更新 `.md` 文件
3. `.md` 文件底部注释标记为自动生成，请勿手动编辑

---

<a id="design-sec-10"></a>

## 十、快速检索速查

> AI 收到图像生成需求时，按以下关键词映射快速定位风格：

| 需求关键词 | 推荐风格 slug（举例） |
|-----------|---------------------|
| 3D 玩具/潮玩 | `acid-lime-3d-streetwear-type-poster-style`, `neon-plush-gadget-pop-3d-style`, `sunny-3d-avatar-campaign-style` |
| 食品/餐饮广告 | `black-cutout-food-card-ad-style`, `yellow-black-manga-food-zine-ad-style`, `market-brush-produce-poster-style` |
| 漫画/动漫 | `bold-anime-reaction-thumbnail-style`, `crimson-ink-manga-dossier`, `electric-blue-cutout-manga-poster-style` |
| 时尚/编辑 | `cobalt-torn-didone-portrait-editorial-style`, `kinetic-luxury-street-fashion-cover-style`, `sunlit-supermodel-nameplate-editorial` |
| 旅行/风景 | `clean-triptych-travel-vlog-thumbnail-style`, `cobalt-megatype-roadside-travel-editorial-style`, `sun-faded-scenic-editorial-poster` |
| 科技/产品 | `blue-hud-macro-product-poster`, `electric-blue-silhouette-product-launch-style`, `monochrome-grid-sneaker-tech-spec` |
| 手绘/涂鸦 | `naive-marker-psa-poster-style`, `school-grid-paper-cutout-poster`, `crayon-catalog-doodle-poster-style` |
| 复古/怀旧 | `hot-ink-comic-poster`, `teenage-skate-scribble-screenprint-poster-style`, `loose-scribble-riso-print-style` |
| 黑白/极简 | `mono-noir-type-portrait-poster-style`, `electric-blue-silhouette-product-launch-style`, `prismatic-glass-animal-weekend-editorial` |
| Y2K/赛博 | `y2k-grunge-hiphop-cutout-poster-style`, `liquid-chrome-clearance-poster-style`, `y2k-mirror-ui-scribble-collage-style` |
| 中文排版 | `blue-chinese-perspective-type-canyon-style`, `jade-glyph-grocer-collage-poster-style`, `black-cutout-food-card-ad-style` |
| 体育/动作 | `ice-cyan-megatype-action-poster-style`, `scarlet-megatype-action-collage-style`, `olive-scribble-sports-poster-style` |
| 鱼眼/超广角 | `blue-bubble-fisheye-action-poster-style`, `chromatic-fisheye-orbit-pop-poster-style`, `warm-fisheye-product-impact-ad-style` |
| PSA/公益 | `naive-marker-psa-poster-style`, `halftone-assemblage-metaphor-psa-poster-style`, `playful-marker-grounding-poster-style` |

---

*本文档最后更新：2026-08-10*
*风格总数：112 套 | Schema 版本：v2.1*
