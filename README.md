# Wallery-Qt

> 幕间 —— 一款用 **PySide6 + QFluentWidgets** 重构的无边框精美壁纸应用。

[English below](#wallery-qt-1)

---

## 简介

Wallery-Qt 是经典壁纸应用 Wallery 的 **PySide6 重写版**。它保留了原版「多来源、一键换壁纸」的核心理念，同时用现代化的 Fluent 设计语言重塑了整个界面：无边框窗口、毛玻璃卡片、流畅的悬停动效，以及完整的系统托盘常驻体验。

应用聚合了 **Bing / Wallhaven / NASA / Pexels / Unsplash** 五大壁纸来源，支持按分辨率自动匹配屏幕、收藏与本地下载、定时自动切换、跨来源随机出图，并提供深色 / 浅色 / 跟随系统三套主题与中英双语界面。

## 截图

> 截图占位（Screenshots placeholder）：正式截图将在后续补充。

## 功能特性

- **无边框 Fluent UI**：基于 QFluentWidgets 的现代化界面，毛玻璃卡片与流畅动效。
- **五大来源 + 热门分类**：Bing 每日一图、Wallhaven、NASA 天文图、Pexels、Unsplash，并按来源提供热门分类快捷筛选。
- **分辨率感知**：根据主屏分辨率（如 1920×1080）自动改写并挑选最合适尺寸的图片 URL。
- **收藏与下载**：一键收藏到本地（上限 100 张，去重），或下载原图到资源管理器。
- **定时切换**：支持每天 / 12 小时 / 6 小时 / 1 小时自动轮换桌面壁纸。
- **跨库随机**：从已加载来源中随机抽取一张设为壁纸。
- **系统托盘**：常驻托盘，支持下一张 / 跳过 / 复制链接 / 保存 / 打开来源页 / 打开界面 / 退出。
- **深 / 浅 / 跟随系统主题**：即时切换，持久化保存。
- **中英双语**：界面文案内置中英字典，跟随系统语言或手动切换。

## 安装与运行

要求 **Python 3.11+**（开发环境使用 3.13）。

```bash
pip install -r requirements.txt
python main.py
```

如需独立可执行文件，可在 `发行版/` 目录获取预编译的 Windows 安装包，或从 Release 页面下载。

## 下载

- GitHub Release：<https://github.com/vinewood/Wallery-Qt/releases>
- 预编译 Windows 包：`Wallery-Qt_v2.0.0_Windows_x64.exe`（约 104 MB，`--onefile --windowed` 打包）

## API Key 配置

Pexels、Unsplash、NASA 三个来源需要在 **设置页** 填入各自的 API Key 后才能使用（NASA 内置公开 `DEMO_KEY` 作为回退，无需配置即可试用）：

- **Pexels**：<https://www.pexels.com/api/> 申请 `API Key`。
- **Unsplash**：<https://unsplash.com/developers> 申请 `Access Key`。
- **NASA**：<https://api.nasa.gov/> 申请 `DEMO_KEY`（可选，默认已内置公开回退）。

所有 Key 仅保存在本地用户配置目录（如 `%APPDATA%/wallery`），**绝不会硬编码进源码或提交到仓库**。

## 技术栈

- **PySide6 6.11**（Qt 绑定）
- **PySide6-Fluent-Widgets (QFluentWidgets) 1.11**（Fluent 设计组件）
- **requests**（同步 HTTP）
- 异步缩略图与列表加载基于 `QThreadPool` / `QRunnable`
- 桌面壁纸通过 `ctypes.SystemParametersInfoW` 设置，锁屏通过 `winreg` 写入注册表

## 与原 Tauri 版 Wallery 的关系

本项目是 [Wallery（Tauri + Rust 原版）](https://github.com/vinewood/Wallery) 的 **PySide6 重制版**，初衷是用更轻量的 Python 技术栈获得同等甚至更好的桌面体验，并补足原版在跨平台与定制性上的局限。功能定位保持一致，界面与内部实现完全重写。

## 许可证

[MIT License](./LICENSE) © vinewood

---

# Wallery-Qt

> Wallery — the interlude. A beautiful frameless wallpaper app **rebuilt with PySide6 + QFluentWidgets**.

## Introduction

Wallery-Qt is the **PySide6 rewrite** of the classic wallpaper app Wallery. It keeps the original "multi-source, one-click wallpaper" philosophy while reshaping the entire UI with a modern Fluent design language: a frameless window, acrylic cards, smooth hover animations, and a full system-tray resident experience.

It aggregates **Bing / Wallhaven / NASA / Pexels / Unsplash**, and supports resolution-aware image selection, local favorites & downloads, scheduled auto-rotation, cross-source random picks, dark / light / system themes, and a bilingual (zh/en) interface.

## Screenshots

> Screenshots placeholder — official captures to be added later.

## Features

- **Frameless Fluent UI** powered by QFluentWidgets with acrylic cards and smooth animations.
- **Five sources + hot categories**: Bing daily, Wallhaven, NASA APOD, Pexels, Unsplash, with per-source hot category filters.
- **Resolution aware**: rewrites & picks the best-sized URL for your primary screen (e.g. 1920×1080).
- **Favorites & download**: one-click favorite (cap 100, deduplicated) or download the original to Explorer.
- **Scheduled switching**: daily / 12h / 6h / 1h automatic desktop rotation.
- **Cross-source random**: pick a random wallpaper from loaded sources.
- **System tray**: resident tray with next / skip / copy link / save / open source page / show window / quit.
- **Dark / Light / Follow-system themes**: instant switch, persisted.
- **Bilingual (zh / en)**: built-in string dictionary, follows system or manual switch.

## Install & Run

Requires **Python 3.11+** (dev used 3.13).

```bash
pip install -r requirements.txt
python main.py
```

For a standalone executable, grab the prebuilt Windows package from the Release page.

## Download

- GitHub Release: <https://github.com/vinewood/Wallery-Qt/releases>
- Prebuilt Windows: `Wallery-Qt_v2.0.0_Windows_x64.exe` (~104 MB, `--onefile --windowed`)

## API Keys

Pexels, Unsplash and NASA require their API Key entered in the **Settings** page (NASA ships with a public `DEMO_KEY` fallback so it works out of the box):

- **Pexels**: get an `API Key` at <https://www.pexels.com/api/>
- **Unsplash**: get an `Access Key` at <https://unsplash.com/developers>
- **NASA**: get a `DEMO_KEY` at <https://api.nasa.gov/> (optional, public fallback built in)

All keys are stored only in the local user config dir (e.g. `%APPDATA%/wallery`) — **never hardcoded in source or committed**.

## Tech Stack

- **PySide6 6.11** (Qt bindings)
- **PySide6-Fluent-Widgets (QFluentWidgets) 1.11** (Fluent components)
- **requests** (sync HTTP)
- Async thumbnails / listing via `QThreadPool` / `QRunnable`
- Desktop wallpaper via `ctypes.SystemParametersInfoW`; lock screen via `winreg`

## Relation to the original Tauri Wallery

This project is the **PySide6 remake** of [Wallery (original Tauri + Rust)](https://github.com/vinewood/Wallery). The goal was a lighter Python stack with equal-or-better desktop experience and fewer cross-platform constraints. Feature scope is aligned; UI and internals are fully rewritten.

## License

[MIT License](./LICENSE) © vinewood
