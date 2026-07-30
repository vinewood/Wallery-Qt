"""Minimal i18n layer (zh / en) equivalent to the original t('ns.key') system.

Language is driven by ``config.language``: ``"auto"`` detects from the OS
locale (zh* -> zh, otherwise en). UI code calls :func:`t` for every string.
"""
from __future__ import annotations

import sys

from app.config import get_config

_LANG = "zh"  # resolved at init

_STRINGS: dict = {
    "zh": {
        "app": {"title": "幕间 · Wallery", "version": "Version 1.0.0"},
        "tabs": {
            "browse": "浏览",
            "favorites": "收藏",
            "sources": "来源",
            "categories": "品类",
            "settings": "设置",
            "about": "关于",
        },
        "browse": {
            "count": "共 {} 张",
            "loading": "正在从 {} 加载…",
            "refresh": "刷新",
            "empty": "没有可用的壁纸，请检查网络或来源设置",
            "page": "第 {} 页",
            "prev": "上一页",
            "next": "下一页",
        },
        "favorites": {
            "title": "我的收藏 ({})",
            "empty": "还没有收藏壁纸，浏览时点击 ♡ 按钮添加",
        },
        "sources": {
            "title": "壁纸来源",
            "default": "默认",
            "api_key": "API Key（输入后自动保存）",
            "api_key_placeholder": "粘贴你的 {} API Key…",
            "saved": "已保存 {} 的 API Key",
            "no_key_needed": "此来源无需 API Key",
        },
        "categories": {
            "title": "我的品类",
            "add": "添加",
            "placeholder": "输入品类名称，回车添加",
            "wallhaven": "Wallhaven 热门",
            "pexels": "Pexels 热门",
            "unsplash": "Unsplash 热门",
            "suggestions": "热门建议（点击添加）",
            "mine": "我的品类",
            "added": "已添加品类",
            "exists": "品类已存在",
            "removed": "已删除品类",
        },
        "settings": {
            "title": "设置",
            "schedule": "定时切换",
            "set_desktop": "桌面壁纸",
            "set_lock_screen": "登录界面壁纸",
            "auto_start": "开机自启",
            "frequency": "更新频率",
            "update_now": "🔄 立即换一张",
            "download": "下载设置",
            "download_path": "保存路径",
            "download_default": "Pictures/Wallery（默认）",
            "change": "更改",
            "open_after": "下载后打开文件夹",
            "update": "软件更新",
            "latest": "已是最新版本 v1.0.0",
            "freq_daily": "每天",
            "freq_12h": "每12小时",
            "freq_6h": "每6小时",
            "freq_1h": "每小时",
            "language": "界面语言",
            "theme": "主题",
            "theme_dark": "深色",
            "theme_light": "浅色",
            "theme_auto": "跟随系统",
        },
        "about": {
            "title": "关于 Wallery",
            "story1": "Wallery（幕间）是一款免费、开源的桌面壁纸工具。",
            "story2": "我们从「幕间」二字出发：在忙碌的一天里，让一张好看的壁纸成为你与工作之间的小小喘息。",
            "story3": "聚合 Bing、Wallhaven、NASA、Pexels、Unsplash 等来源，按需切换、定时轮播。",
            "story4": "完全本地运行，不收集任何数据。",
            "free": "100% 免费",
            "open": "MIT 开源",
            "size": "~100MB 安装包",
            "mem": "<15MB 内存",
            "sponsor": "赞助我们",
            "site": "官网",
            "github": "GitHub",
            "gitee": "Gitee",
        },
        "tray": {
            "next": "下一张壁纸",
            "skip": "跳过今天",
            "copy_url": "复制图片链接",
            "save": "保存当前壁纸",
            "open_src": "打开来源页面",
            "open_wnd": "打开程序界面",
            "settings": "设置…",
            "quit": "退出 Wallery",
            "tooltip": "Wallery 幕间",
        },
        "common": {
            "set_wallpaper": "设为壁纸",
            "favorite": "收藏",
            "unfavorite": "取消收藏",
            "download": "下载",
            "all": "全部",
            "set_ok": "已设为壁纸",
            "download_ok": "已下载到 {}", "download_fail": "下载失败：{}",
            "fav_ok": "已收藏",
            "fav_del": "已取消收藏",
            "fav_limit": "收藏已达上限（100）",
            "fav_dup": "已在收藏中",
            "no_key": "请先在来源设置中配置 {} 的 API Key",
            "all_failed": "所有来源均获取失败",
            "copied": "已复制图片链接",
            "saved_current": "已保存当前壁纸",
            "open_src": "已打开来源页面",
            "config_err": "配置错误",
            "need_restart": "语言/主题更改将在重启后完全生效",
        },
        "card": {"source": "来源", "no_url": "无效图片"},
    },
    "en": {
        "app": {"title": "Wallery", "version": "Version 1.0.0"},
        "tabs": {
            "browse": "Browse",
            "favorites": "Favorites",
            "sources": "Sources",
            "categories": "Categories",
            "settings": "Settings",
            "about": "About",
        },
        "browse": {
            "count": "{} wallpapers",
            "loading": "Loading from {}…",
            "refresh": "Refresh",
            "empty": "No wallpapers available, check network or source settings",
            "page": "Page {}",
            "prev": "Prev",
            "next": "Next",
        },
        "favorites": {
            "title": "My Favorites ({})",
            "empty": "No favorites yet — click ♡ on a wallpaper to add one",
        },
        "sources": {
            "title": "Wallpaper Sources",
            "default": "Default",
            "api_key": "API Key (auto-saved)",
            "api_key_placeholder": "Paste your {} API Key…",
            "saved": "Saved API Key for {}",
            "no_key_needed": "No API Key required for this source",
        },
        "categories": {
            "title": "My Categories",
            "add": "Add",
            "placeholder": "Type a category, press Enter",
            "wallhaven": "Wallhaven Hot",
            "pexels": "Pexels Hot",
            "unsplash": "Unsplash Hot",
            "suggestions": "Hot suggestions (click to add)",
            "mine": "My Categories",
            "added": "Category added",
            "exists": "Category already exists",
            "removed": "Category removed",
        },
        "settings": {
            "title": "Settings",
            "schedule": "Auto Switch",
            "set_desktop": "Desktop wallpaper",
            "set_lock_screen": "Lock screen wallpaper",
            "auto_start": "Launch at startup",
            "frequency": "Update frequency",
            "update_now": "🔄 Update Now",
            "download": "Download",
            "download_path": "Save location",
            "download_default": "Pictures/Wallery (default)",
            "change": "Change",
            "open_after": "Open folder after download",
            "update": "Software Update",
            "latest": "Up to date (v1.0.0)",
            "freq_daily": "Daily",
            "freq_12h": "Every 12h",
            "freq_6h": "Every 6h",
            "freq_1h": "Every hour",
            "language": "Language",
            "theme": "Theme",
            "theme_dark": "Dark",
            "theme_light": "Light",
            "theme_auto": "System",
        },
        "about": {
            "title": "About Wallery",
            "story1": "Wallery is a free, open-source desktop wallpaper tool.",
            "story2": "We started from the idea of a 'brief interlude' — a beautiful wallpaper as a small breather between you and your work.",
            "story3": "Aggregating Bing, Wallhaven, NASA, Pexels and Unsplash, switch on demand and rotate on a schedule.",
            "story4": "Runs fully locally; collects no data.",
            "free": "100% Free",
            "open": "MIT Open Source",
            "size": "~100MB installer",
            "mem": "<15MB RAM",
            "sponsor": "Sponsor",
            "site": "Website",
            "github": "GitHub",
            "gitee": "Gitee",
        },
        "tray": {
            "next": "Next Wallpaper",
            "skip": "Skip Today",
            "copy_url": "Copy Image URL",
            "save": "Save Current Wallpaper",
            "open_src": "Open Source Page",
            "open_wnd": "Open App",
            "settings": "Settings…",
            "quit": "Quit Wallery",
            "tooltip": "Wallery",
        },
        "common": {
            "set_wallpaper": "Set Wallpaper",
            "favorite": "Favorite",
            "unfavorite": "Unfavorite",
            "download": "Download",
            "all": "All",
            "set_ok": "Wallpaper set",
            "download_ok": "Downloaded to {}", "download_fail": "Download failed: {}",
            "fav_ok": "Added to favorites",
            "fav_del": "Removed from favorites",
            "fav_limit": "Favorites limit reached (100)",
            "fav_dup": "Already in favorites",
            "no_key": "Configure the {} API Key in Sources first",
            "all_failed": "All sources failed to fetch",
            "copied": "Image URL copied",
            "saved_current": "Current wallpaper saved",
            "open_src": "Source page opened",
            "config_err": "Config error",
            "need_restart": "Language/theme changes apply after restart",
        },
        "card": {"source": "Source", "no_url": "Invalid image"},
    },
}


def _detect_system_lang() -> str:
    import locale
    try:
        loc = locale.getdefaultlocale()[0] or ""
    except Exception:
        loc = ""
    if not loc:
        loc = (sys.argv and "") or ""
    # also check env
    for env in ("LANG", "LANGUAGE", "LC_ALL"):
        v = __import__("os").environ.get(env, "")
        if v:
            loc = v
            break
    return "zh" if loc.lower().startswith("zh") else "en"


def reload_language() -> None:
    """Resolve effective language from config and cache it."""
    global _LANG
    lang = get_config().get_language()
    if lang in ("zh", "en"):
        _LANG = lang
    else:  # auto
        _LANG = _detect_system_lang()


def t(key: str, *args) -> str:
    """Lookup ``ns.sub.sub2`` style key in the active language."""
    node: Any = _STRINGS.get(_LANG, _STRINGS["en"])
    for part in key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            # fallback to english
            node = _STRINGS["en"]
            for part in key.split("."):
                if isinstance(node, dict) and part in node:
                    node = node[part]
                else:
                    return key
            break
    if isinstance(node, str) and args:
        try:
            return node.format(*args)
        except Exception:
            return node
    return node if isinstance(node, str) else key


def current_lang() -> str:
    return _LANG
