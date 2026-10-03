# -*- coding: utf-8 -*-
"""术语大全日更 · 待入库 backlog 生成器。
把按技术体系整理的候选术语（full schema）落盘到 data/term_backlog.json，
供每日自动化脚本逐条取出、追加进 data/terms.json 后重新构建部署。

字段与 data/terms.json 完全一致：
  id, ch, speak, cn, en, anti, fix, bad, good, tip(list), plat{web,app,mini}, vd_bad, vd_good
说明：
  - ch 必须落在 0..10（对齐 gen_vibecode.py 的 CHAPTERS）
  - plat 三键必填（模板 t['plat'][state.plat] 直接取值）
  - vd_bad/vd_good 是前后对照小样，复用 m-* 演示类（m-phone/m-bar/m-body/m-line 等）
"""
import json
import os

BACKLOG = [
    {
        "id": "breadcrumb",
        "ch": 0,
        "speak": "进了一个很深的页面，只能靠浏览器返回键一层层退，不知道自己在站点哪一层",
        "cn": "面包屑导航",
        "en": "Breadcrumb Navigation",
        "anti": "深层页面没有层级指示，用户靠返回键一层层退，容易迷路、不知道当前在哪一层的什么位置",
        "fix": "顶部放一条「首页 / 分类 / 当前页」的可点击路径，随时能跳回任意上层，明示当前所处层级",
        "bad": "<!-- 深层页没有面包屑，只能靠浏览器返回键一层层退 -->",
        "good": "<nav class='crumb'><a href='/'>首页</a> / <a href='/fe'>前端</a> / <span>详情</span></nav>",
        "tip": [
            "面包屑最后一项是当前页，不可点击",
            "层级用「/」或「>」分隔，保持统一",
            "移动端可只留「返回上级 + 当前页」避免过长",
            "当前页加 aria-current='page' 利于无障碍"
        ],
        "plat": {
            "web": "语义用 nav + aria-label='breadcrumb'，当前项 aria-current='page'",
            "app": "顶栏左返回箭头 + 标题即等效面包屑，深层用多级返回",
            "mini": "用 navigation-bar 的返回按钮表达层级关系"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar'>商品详情</div><div class='m-body'><div style='font-size:11px;color:#999'>深层页没有路径指示</div><div style='margin-top:8px;font-size:10px;color:#bbb'>只能靠返回键一层层退…</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-crumb'><a href='#'>首页</a> / <a href='#'>前端</a> / <b>详情</b></div><div class='m-body'><div style='font-size:11px;color:#333'>随时跳回任意上层</div></div></div>"
    },
    {
        "id": "infinite-scroll",
        "ch": 4,
        "speak": "列表内容很多，一页塞不完，又不想让用户疯狂翻页找下一页",
        "cn": "无限滚动加载",
        "en": "Infinite Scroll",
        "anti": "一次性渲染上千条，首屏直接卡死；或翻页按钮藏得太深，用户懒得翻",
        "fix": "滚到底部自动加载下一批，配合骨架/loading 提示，分批渲染保持流畅",
        "bad": "/* 一次 render 5000 条，首屏直接卡死 */",
        "good": "if(scrollBottom < 50) loadNextPage(); // 触底加载下一批",
        "tip": [
            "用 IntersectionObserver 监听底部哨兵元素比 scroll 计算更省心",
            "必须给「加载中」和「到底了」两种提示",
            "做防抖/加锁避免一次触发多次请求",
            "超长列表考虑虚拟滚动只渲染可视区"
        ],
        "plat": {
            "web": "IntersectionObserver 监听底部哨兵，零 scroll 计算",
            "app": "FlatList 的 onEndReached 原生支持触底加载",
            "mini": "scroll-view 的 bindscrolltolower 事件"
        },
        "vd_bad": "<div class='m-phone m-scroll'><div class='m-bar s'>卡死</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>",
        "vd_good": "<div class='m-phone m-scroll'><div class='m-bar'>列表</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div style='font-size:10px;color:#2E8B72;text-align:center;margin-top:4px'>加载中…</div></div>"
    },
    {
        "id": "responsive-breakpoint",
        "ch": 5,
        "speak": "同一套布局在手机和电脑上都挤成一团，或在大屏上空一大片",
        "cn": "响应式断点",
        "en": "Responsive Breakpoint",
        "anti": "不做断点适配，手机上表格挤爆、电脑上内容窄成一条很浪费",
        "fix": "用媒体查询在不同宽度套用不同布局，移动端单列、桌面多列",
        "bad": ".g{ grid-template-columns:repeat(4,1fr); } /* 手机也挤 4 列 */",
        "good": "@media(min-width:768px){ .g{ grid-template-columns:repeat(4,1fr); } }",
        "tip": [
            "常用断点 640 / 768 / 1024 / 1280",
            "优先移动优先（min-width）写法，向后兼容",
            "用 auto-fit + minmax 减少断点数量",
            "别只盯着某款设备宽度，按内容断点"
        ],
        "plat": {
            "web": "媒体查询 + 移动优先，断点覆盖主流视口",
            "app": "Flex/约束布局天然响应式，少断点",
            "mini": "rpx 自适应单位 + 条件样式"
        },
        "vd_bad": "<div class='m-phone'><div class='m-body'><div style='display:grid;grid-template-columns:repeat(4,1fr);gap:3px'><span style='height:14px;background:#E7C9C4;border-radius:3px'></span><span style='height:14px;background:#E7C9C4;border-radius:3px'></span><span style='height:14px;background:#E7C9C4;border-radius:3px'></span><span style='height:14px;background:#E7C9C4;border-radius:3px'></span></div><div style='font-size:9px;color:#bbb;margin-top:6px'>手机挤 4 列</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-body'><div style='display:grid;grid-template-columns:1fr;gap:4px'><span style='height:14px;background:#BFE0CE;border-radius:3px'></span><span style='height:14px;background:#BFE0CE;border-radius:3px'></span></div><div style='font-size:9px;color:#2E8B72;margin-top:6px'>手机单列</div></div></div>"
    },
    {
        "id": "lazyload",
        "ch": 6,
        "speak": "页面一堆图，首屏还没滚到就全加载，白白浪费流量还拖慢打开速度",
        "cn": "图片懒加载",
        "en": "Image Lazy Loading",
        "anti": "所有 img 一上来就请求，首屏外的大图也占带宽，打开慢、流量浪费",
        "fix": "用 loading='lazy' 或 IntersectionObserver，滚到视口才加载图片",
        "bad": "<img src='big.jpg'> /* 首屏外也立刻下载 */",
        "good": "<img src='big.jpg' loading='lazy' alt='说明文字'>",
        "tip": [
            "原生 loading='lazy' 最简单零依赖",
            "关键首屏图不要懒加载，否则白屏",
            "记得写 alt 利于无障碍和 SEO",
            "配合 decoding='async' 防主线程阻塞"
        ],
        "plat": {
            "web": "原生 loading='lazy' 已覆盖主流浏览器，关键图用 fetchpriority='high'",
            "app": "RN 用 FlatList 懒渲染 + 占位图",
            "mini": "image 组件的 lazy-load 属性"
        },
        "vd_bad": "<div class='m-phone m-scroll'><div class='m-bar s'>流量浪费</div><div style='height:30px;background:#eee9e1;border-radius:4px;margin:6px 0'></div><div style='height:30px;background:#eee9e1;border-radius:4px;margin:6px 0'></div><div style='height:30px;background:#eee9e1;border-radius:4px;margin:6px 0'></div><div style='font-size:9px;color:#bbb'>首屏外也在下载</div></div>",
        "vd_good": "<div class='m-phone m-scroll'><div class='m-bar'>省流量</div><div style='height:30px;background:linear-gradient(135deg,#C8442E,#A8351F);border-radius:4px;margin:6px 0'></div><div style='height:30px;background:#eee9e1;border-radius:4px;margin:6px 0'></div><div style='font-size:9px;color:#2E8B72'>只加载看得见的</div></div>"
    },
    {
        "id": "floating-label",
        "ch": 7,
        "speak": "输入框没有固定标签，placeholder 一输入就消失，填完回头看不知道这格填的是什么",
        "cn": "浮动标签输入框",
        "en": "Floating Label Input",
        "anti": "只用 placeholder 当标签，输入后文字消失，长表单填到一半忘了每格该填啥",
        "fix": "label 默认当占位提示，获得焦点或已有内容时上浮缩小成小标签，始终可见",
        "bad": "<input placeholder='手机号'>",
        "good": "input:focus + label, input:not(:placeholder-shown) + label{ transform:translateY(-18px) scale(.8); }",
        "tip": [
            "浮动靠 :placeholder-shown 判断是否有值",
            "输入框需保留 placeholder=' ' 空格占位触发判断",
            "上浮标签颜色用 accent 与主输入区分",
            "移动端上浮后字号别太小，保证可读"
        ],
        "plat": {
            "web": "纯 CSS 用 :placeholder-shown + 相邻兄弟选择器，无需 JS",
            "app": "RN 用 react-native-paper 的 TextInput mode='outlined' 自带",
            "mini": "用 cover-view + 聚焦事件切换 class 模拟"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar'>注册</div><div class='m-body'><div style='border:1px solid #ddd;border-radius:8px;padding:9px 10px;color:#bbb;font-size:11px'>手机号</div><div style='margin-top:12px;color:#bbb;font-size:10px'>填完上面，回头看不知道这格填的啥</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>注册</div><div class='m-body'><div style='position:relative;border:1px solid #C8442E;border-radius:8px;padding:12px 10px 6px'><div style='position:absolute;top:2px;left:10px;font-size:8px;color:#C8442E'>手机号</div><div style='font-size:12px;color:#333'>138****8888</div></div><div style='margin-top:8px;font-size:10px;color:#2E8B72'>标签一直浮在上面</div></div></div>"
    },
    {
        "id": "input-validate",
        "ch": 7,
        "speak": "表单提交后才告诉用户哪填错了，白白浪费一次提交还得重填",
        "cn": "实时输入校验",
        "en": "Inline Input Validation",
        "anti": "点提交才校验，错误一堆弹出来，用户得回过头重填，体验很差",
        "fix": "输入失焦或实时校验，错的项立刻标红给提示，对了给绿色对勾",
        "bad": "/* 只有点提交才校验，错误一坨 */",
        "good": "onblur=validate(); if(!ok) showError('手机号格式不对');",
        "tip": [
            "失焦时校验比每次按键更友好，不打扰输入",
            "错误信息贴着字段下方，别用中断式弹窗",
            "校验通过给绿色对勾增强信心",
            "提交前再整体校验一遍兜底"
        ],
        "plat": {
            "web": "onblur/oninput 校验 + aria-invalid 标记错误项",
            "app": "用 react-hook-form 等库做实时校验",
            "mini": "bindblur 事件触发字段校验"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar s'>提交后</div><div class='m-body'><div style='font-size:10px;color:#C8442E'>手机号格式不对</div><div style='font-size:10px;color:#C8442E'>密码至少8位</div><div style='font-size:10px;color:#C8442E'>邮箱格式不对</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>实时校验</div><div class='m-body'><div style='border:1px solid #C8442E;border-radius:8px;padding:8px 10px;font-size:11px;color:#333'>138****8888</div><div style='font-size:10px;color:#C8442E;margin-top:3px'>手机号格式不对</div></div></div>"
    },
    {
        "id": "password-toggle",
        "ch": 7,
        "speak": "输密码时完全看不见，容易输错还得重来，也没法核对",
        "cn": "密码可见切换",
        "en": "Password Visibility Toggle",
        "anti": "密码框只能盲打，输错一位全重输，没有核对机会",
        "fix": "输入框后加个小眼睛图标，点击在明文/圆点之间切换",
        "bad": "<input type='password'> /* 全程盲打 */",
        "good": "<input :type=\"show?'text':'password'\"><button @click='show=!show'>眼睛</button>",
        "tip": [
            "切换按钮用眼睛开/合图标区分状态",
            "默认隐藏，切换时给短暂明文即可",
            "切换后保持输入框焦点不丢",
            "别只用 emoji 当图标，配文字说明"
        ],
        "plat": {
            "web": "按钮用 type=button 防止误提交，aria-label 标状态",
            "app": "TextInput secureTextEntry 配合图标按钮",
            "mini": "password 属性 + 图标切换"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar'>登录</div><div class='m-body'><div style='border:1px solid #ddd;border-radius:8px;padding:9px 10px;letter-spacing:2px;font-size:12px;color:#333'>••••••••</div><div style='margin-top:10px;font-size:10px;color:#bbb'>盲打，输错全重输</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>登录</div><div class='m-body'><div style='position:relative;border:1px solid #C8442E;border-radius:8px;padding:9px 28px 9px 10px;font-size:12px;color:#333'>abc12345<div style='position:absolute;right:8px;top:9px;font-size:11px;color:#C8442E'>👁</div></div><div style='margin-top:8px;font-size:10px;color:#2E8B72'>点眼睛可核对</div></div></div>"
    },
    {
        "id": "search-filter",
        "ch": 7,
        "speak": "列表很长，用户想找一项得自己肉眼翻，或者等搜索结果页才出",
        "cn": "搜索框即时筛选",
        "en": "Live Search Filter",
        "anti": "搜完才出结果页，或列表不支持过滤，长列表全靠用户手翻",
        "fix": "输入即过滤，边打边出匹配项，无需点搜索按钮",
        "bad": "/* 必须点搜索才出结果，长列表手翻 */",
        "good": "oninput=render(list.filter(x=>x.includes(q)))",
        "tip": [
            "输入即过滤，别等回车",
            "无结果给空状态而不是空白",
            "大数据量做防抖 200ms 防抖动",
            "高亮匹配关键字更易读"
        ],
        "plat": {
            "web": "oninput + 防抖过滤，无需发请求",
            "app": "FlatList 的 filter 实时更新数据源",
            "mini": "bindinput 过滤本地列表"
        },
        "vd_bad": "<div class='m-phone m-scroll'><div class='m-bar'>长列表</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div style='font-size:10px;color:#bbb'>肉眼翻找…</div></div>",
        "vd_good": "<div class='m-phone m-scroll'><div class='m-bar'>搜索</div><div style='margin:6px 0;padding:6px 8px;background:#f4f1ea;border-radius:6px;font-size:10px;color:#333'>🔍 输入关键字</div><div style='font-size:10px;color:#2E8B72'>匹配项 3 条</div><div class='m-line'></div><div class='m-line'></div></div>"
    },
    {
        "id": "multi-step",
        "ch": 7,
        "speak": "一大张表单几十个字段怼脸上，用户一看填写压力就放弃",
        "cn": "多步表单向导",
        "en": "Multi-step Form Wizard",
        "anti": "几十个字段一屏铺开，填写压力大、容易中途放弃",
        "fix": "拆成 2~4 步，每步少量字段 + 进度条 + 上一步/下一步",
        "bad": "/* 20 个字段一屏，填写压力大 */",
        "good": "step=1; next(){ if(validate(step)) step++; }",
        "tip": [
            "用进度条/步骤条降低焦虑感",
            "每步独立校验通过才放行下一步",
            "允许「上一步」回改且不丢已填数据",
            "最后一步才真正提交"
        ],
        "plat": {
            "web": "前端状态保存每步数据，刷新可续填",
            "app": "Stepper 组件天然支持分步填写",
            "mini": "分步页 + 全局表单缓存"
        },
        "vd_bad": "<div class='m-phone m-scroll'><div class='m-bar s'>放弃</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>第 2 / 3 步</div><div class='m-body'><div style='height:5px;background:#C8442E;border-radius:3px;width:66%'></div><div style='margin-top:10px;font-size:11px;color:#333'>本步只需填 3 项</div><div style='flex:1'></div><div style='font-size:10px;color:#938E85'>上一步 · 下一步</div></div></div>"
    },
    {
        "id": "btn-debounce",
        "ch": 8,
        "speak": "点按钮没反应（网络慢），用户连点好几次，结果重复提交、重复下单",
        "cn": "防重复点击",
        "en": "Debounce Button Click",
        "anti": "请求没返回时按钮还能点，用户连点导致重复提交或重复下单",
        "fix": "点击后立即禁用或加锁，请求完成/失败才恢复，或做节流",
        "bad": "<button onclick='submit()'>提交</button> /* 可连点 */",
        "good": "async function submit(){ if(loading)return; loading=true; await api(); loading=false; }",
        "tip": [
            "点击即置 disabled 或加锁，防并发重复",
            "失败也要恢复可点，别卡死",
            "网络慢时显示 loading 态",
            "支付等场景必须幂等兜底"
        ],
        "plat": {
            "web": "点击即 disabled + 请求锁，防重复提交",
            "app": "按钮 disabled 态 + 请求锁变量",
            "mini": "bindtap 里加锁变量防重复触发"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar s'>重复提交</div><div class='m-body'><div style='font-size:10px;color:#C8442E'>提交中…</div><div style='font-size:10px;color:#C8442E'>提交中…</div><div style='font-size:10px;color:#C8442E'>提交中…</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>防重复</div><div class='m-body'><div style='background:#C8442E;color:#fff;border-radius:8px;padding:9px;text-align:center;font-size:11px;opacity:.6'>提交中…（已禁用）</div></div></div>"
    },
    {
        "id": "fab",
        "ch": 8,
        "speak": "核心操作（如发帖、加号）藏在三层级菜单里，用户根本找不到",
        "cn": "悬浮操作按钮",
        "en": "Floating Action Button (FAB)",
        "anti": "核心操作埋在二级「更多」菜单，入口深，使用率极低",
        "fix": "右下角悬浮一个主操作按钮，一眼可见、随时可点",
        "bad": "/* 核心操作藏在「更多」二级菜单 */",
        "good": ".fab{ position:fixed; right:16px; bottom:16px; border-radius:50%; }",
        "tip": [
            "FAB 只放一个最高频的核心操作",
            "避开底部安全区（见安全区适配）",
            "移动端尺寸 ≥56px 易点",
            "可点击展开成多个子操作"
        ],
        "plat": {
            "web": "fixed 定位右下角，注意不被内容遮挡",
            "app": "RN 用 FAB 组件，自动处理安全区",
            "mini": "fixed 浮层 + 安全区偏移"
        },
        "vd_bad": "<div class='m-phone'><div class='m-body'><div style='font-size:10px;color:#bbb'>核心操作藏在</div><div style='display:inline-block;margin-top:6px;padding:4px 10px;background:#f4f1ea;border-radius:6px;font-size:10px;color:#999'>更多 ▾</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-body'></div><div style='position:absolute;right:12px;bottom:14px;width:34px;height:34px;border-radius:50%;background:#C8442E;color:#fff;font-size:18px;display:flex;align-items:center;justify-content:center'>+</div></div>"
    },
    {
        "id": "icon-btn",
        "ch": 8,
        "speak": "一排功能用文字按钮占地方，或者图标没有点击反馈、看不出能点",
        "cn": "图标按钮",
        "en": "Icon Button",
        "anti": "纯图标没有语义、没有反馈，用户不知道点哪；或图标当文字用占空间",
        "fix": "高频操作用语义化图标 + tooltip，保证 ≥44px 点击区，hover/active 有反馈",
        "bad": "<span>⚙</span> /* 没点击区没反馈 */",
        "good": "<button class='icon-btn' aria-label='设置' title='设置'>⚙</button>",
        "tip": [
            "图标按钮必须给 aria-label/title 说清含义",
            "点击区 ≥44px 保证可点",
            "hover/active 有底色反馈",
            "别用 emoji 当唯一图标，配文字"
        ],
        "plat": {
            "web": "button + aria-label，悬停出 tooltip",
            "app": "IconButton 组件自带点击态",
            "mini": "加 icon 的 button 组件"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar'>设置</div><div class='m-body'><div style='font-size:16px;color:#bbb'>⚙</div><div style='font-size:10px;color:#bbb;margin-top:8px'>没反馈，不知能点</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>设置</div><div class='m-body'><div style='width:40px;height:40px;border-radius:10px;background:#f4f1ea;display:flex;align-items:center;justify-content:center;font-size:16px;color:#C8442E'>⚙</div><div style='font-size:10px;color:#2E8B72;margin-top:8px'>悬停出 tooltip</div></div></div>"
    },
    {
        "id": "toast",
        "ch": 9,
        "speak": "操作结果（保存成功、已复制）要么弹个框打断用户，要么啥提示都没有",
        "cn": "轻提示 Toast",
        "en": "Toast Notification",
        "anti": "用小对话框打断操作流，或操作完毫无反馈，用户不确定是否成功",
        "fix": "非关键信息用底部/顶部短暂 Toast 自动消失，不打断当前操作",
        "bad": "alert('保存成功') /* 阻塞对话框 */",
        "good": "toast('已保存'); // 2 秒自动消失，不打断",
        "tip": [
            "Toast 只放非阻断的轻提示",
            "2~3 秒自动消失，别常驻",
            "重要/危险操作才用确认框",
            "多个 Toast 别叠罗汉"
        ],
        "plat": {
            "web": "fixed 定位 + 自动计时移除，别用 alert",
            "app": "RN Toast 组件原生支持",
            "mini": "showToast API"
        },
        "vd_bad": "<div class='m-phone'><div class='m-overlay'><span>确定？</span><span style='background:#fff;color:#333;padding:4px 12px;border-radius:6px'>OK</span></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-body'></div><div style='position:absolute;bottom:14px;left:24px;right:24px;background:rgba(26,26,26,.92);color:#fff;font-size:10px;text-align:center;padding:7px;border-radius:8px'>已保存</div></div>"
    },
    {
        "id": "confirm-dialog",
        "ch": 9,
        "speak": "危险操作（删除、提交）一点就生效，没给反悔机会",
        "cn": "确认对话框",
        "en": "Confirm Dialog",
        "anti": "删除等危险操作直接执行，误触没法挽回",
        "fix": "危险操作前弹确认框，明确后果 + 取消/确认两个出口",
        "bad": "onclick='delete()' /* 误触直接没 */",
        "good": "if(confirm('确定删除？不可恢复')) delete();",
        "tip": [
            "危险操作必须二次确认",
            "确认框写清「后果」而非只问确定吗",
            "取消是默认高亮项，防误确认",
            "别用原生 confirm 太丑，可自绘"
        ],
        "plat": {
            "web": "自绘 modal + 焦点陷阱，Esc 取消",
            "app": "AlertDialog 组件",
            "mini": "showModal 确认框"
        },
        "vd_bad": "<div class='m-phone'><div class='m-body'><div style='font-size:10px;color:#C8442E'>已删除</div><div style='font-size:10px;color:#bbb;margin-top:6px'>误触，没了</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-overlay'><span>确定删除？</span><span style='font-size:9px;color:#ccc'>不可恢复</span><span style='display:flex;gap:8px'><b style='background:#fff;color:#333;padding:4px 12px;border-radius:6px'>取消</b><b style='background:#C8442E;padding:4px 12px;border-radius:6px'>删除</b></span></span></div></div>"
    },
    {
        "id": "action-sheet",
        "ch": 9,
        "speak": "一个触发点要展开好几个选项，用居中对话框显得很重",
        "cn": "底部弹窗（动作面板）",
        "en": "Action Sheet / Bottom Sheet",
        "anti": "多个选项用居中弹窗，移动端显得笨重、遮挡多",
        "fix": "从底部滑出动作面板，列出选项 + 取消，符合移动端单手习惯",
        "bad": "/* 居中弹窗塞一堆按钮，移动端笨重 */",
        "good": ".sheet{ position:fixed; bottom:0; transform:translateY(0); }",
        "tip": [
            "移动端从底部滑出更符合单手操作",
            "顶部留半透明遮罩",
            "最下面是「取消」独立项",
            "选项多时面板内可滚动"
        ],
        "plat": {
            "web": "fixed 底部 + 遮罩，滑入动画",
            "app": "BottomSheet 组件原生支持",
            "mini": "半屏 popup 从底部弹出"
        },
        "vd_bad": "<div class='m-phone'><div class='m-overlay'><span style='background:#fff;color:#333;padding:8px 14px;border-radius:8px;margin:3px'>分享</span><span style='background:#fff;color:#333;padding:8px 14px;border-radius:8px;margin:3px'>收藏</span><span style='background:#fff;color:#333;padding:8px 14px;border-radius:8px;margin:3px'>举报</span></div></div>",
        "vd_good": "<div class='m-phone'><div style='position:absolute;inset:0;background:rgba(26,26,26,.4)'></div><div style='position:absolute;bottom:0;left:0;right:0;background:#fff;border-radius:12px 12px 0 0;padding:10px'><div style='font-size:10px;color:#333;text-align:center;padding:6px'>分享</div><div style='font-size:10px;color:#333;text-align:center;padding:6px'>收藏</div><div style='font-size:10px;color:#C8442E;text-align:center;padding:6px;margin-top:4px'>取消</div></div></div>"
    },
    {
        "id": "drawer-panel",
        "ch": 9,
        "speak": "导航或筛选条件没地方放，堆在页面里占正文",
        "cn": "侧边抽屉弹层",
        "en": "Side Drawer Panel",
        "anti": "菜单/筛选堆在正文区，挤占内容，层级混乱",
        "fix": "从左侧/右侧滑出抽屉，平时收起，需要时拉出",
        "bad": "/* 筛选条件常驻挤占正文 */",
        "good": ".drawer{ position:fixed; left:0; transform:translateX(-100%); }",
        "tip": [
            "抽屉配半透明遮罩，点遮罩关闭",
            "滑出方向按内容：筛选常右、导航常左",
            "记得可手势/按钮关闭",
            "抽屉内滚动独立，不带动页面"
        ],
        "plat": {
            "web": "fixed 侧边 + transform 滑入 + 遮罩",
            "app": "Drawer 导航组件",
            "mini": "popup 抽屉方向 left/right"
        },
        "vd_bad": "<div class='m-phone m-scroll'><div class='m-bar'>列表</div><div style='font-size:9px;color:#999;margin:6px 0'>筛选：价格 品牌 颜色 尺寸 分类</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-drawer'><span>全部</span><span class='on'>价格</span><span>品牌</span><span>颜色</span><span>尺寸</span></div><div style='position:absolute;inset:0;background:rgba(26,26,26,.25)'></div></div>"
    },
    {
        "id": "tooltip",
        "ch": 9,
        "speak": "图标或缩写不知道啥意思，hover 也没说明，只能猜",
        "cn": "文字气泡提示",
        "en": "Tooltip",
        "anti": "图标/缩写无说明，用户不敢点，靠猜",
        "fix": "悬停/长按图标给出气泡说明，移开即消失",
        "bad": "<button>ⓘ</button> /* 不知啥意思 */",
        "good": "<button aria-label='帮助' title='查看使用说明'>ⓘ</button>",
        "tip": [
            "Tooltip 是解释而非替代标签",
            "移动端用长按/点击触发（无 hover）",
            "气泡别挡住操作元素",
            "内容要短，一句说清"
        ],
        "plat": {
            "web": "title 属性最简单，复杂用自绘气泡",
            "app": "Tooltip 组件 onPress 长按触发",
            "mini": "长按弹出气泡"
        },
        "vd_bad": "<div class='m-phone'><div class='m-bar'>工具栏</div><div class='m-body'><div style='font-size:18px;color:#bbb'>ⓘ ? ★</div><div style='font-size:10px;color:#bbb;margin-top:8px'>啥意思？只能猜</div></div></div>",
        "vd_good": "<div class='m-phone'><div class='m-bar'>工具栏</div><div class='m-body'><div style='font-size:18px;color:#C8442E'>ⓘ</div><div style='position:absolute;top:46px;left:18px;background:#1F6FB2;color:#fff;font-size:9px;padding:5px 8px;border-radius:6px'>查看使用说明</div></div></div>"
    }
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "data", "term_backlog.json")
    # 语义去重：跳过主术语库已存在的 cn / en，避免重复术语
    ex_path = os.path.join(here, "data", "terms.json")
    ex_cn, ex_en = set(), set()
    if os.path.exists(ex_path):
        ex = json.load(open(ex_path, encoding="utf-8"))["terms"]
        ex_cn = {t["cn"] for t in ex}
        ex_en = {t["en"].lower() for t in ex}
    kept, skipped = [], []
    for t in BACKLOG:
        if t["cn"] in ex_cn or t["en"].lower() in ex_en:
            skipped.append(t["id"])
            continue
        kept.append(t)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"source": "码译·VibeCode 术语大全日更 backlog",
                   "note": "每日自动化从中取若干条追加进 terms.json 后重建部署",
                   "terms": kept}, f, ensure_ascii=False, indent=2)
    print("wrote %d backlog terms -> %s" % (len(kept), out))
    if skipped:
        print("skipped %d 已存在术语: %s" % (len(skipped), ", ".join(skipped)))


if __name__ == "__main__":
    main()
