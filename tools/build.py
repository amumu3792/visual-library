# -*- coding: utf-8 -*-
"""
build.py — 云端构建入口（本地迁移与 GitHub Actions 跑同一份）

  1) 消费暂存区：视觉资料库/用户补充/暂存区.md 里的新条目并入 用户补充.md
  2) 生成 design-knowledge-base.html（仓库根）与 视觉资料库/styles-overview.html/.csv
  3) 合并三视图首页 index.html（仓库根）

纯标准库，无第三方依赖。kb_core 的 ROOT 按本文件位置自定位为仓库根目录。
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kb_core


def main():
    merged, kept = kb_core.consume_staging()
    for t in merged:
        print('暂存区已入库：', t)
    for t, r in kept:
        print('暂存区保留（格式不完整，待修正）：', t, '—', r)
    s = kb_core.write_merged_html()
    print('知识库页：风格 %d · 提示词模板 %d · 用户新增 %d · 合计 %d'
          % (s['styles'], s['templates'], s['user'], s['total']))
    n = kb_core.write_table_html()
    print('总览表：%d 个风格' % n)
    import merge_homepage
    merge_homepage.main([])
    print('构建完成')


if __name__ == '__main__':
    main()
