# -*- coding: utf-8 -*-
# 生成器：把术语数据写成「静态 HTML 卡片 + JS 交互」的单文件工作台
# 单一数据源 => 同时产出 SEO 友好的静态卡片 + 工坊所需的 JS 数据
import json, io, re, os

# ----------------------------------------------------------------------------
# 章节
# ----------------------------------------------------------------------------
CHAPTERS = ["导航", "布局与对齐", "尺寸与排版", "定位与层级", "交互与动效", "响应式与适配", "性能与无障碍", "表单输入", "按钮操作", "弹窗遮罩", "动效"]

# 每章「口诀 / 万能公式」——照搬 Nav Pattern Lab 的「位置+展开+滚动」万能公式思路，
# 把每个组件章抽象成 2~3 个可组合的维度，做成章节头下方的公式条（ch 索引对齐 CHAPTERS）
CHAPTER_FORMULA = {
 0: ("导航模式", ["位置 · 吸顶/侧边/面包屑", "展开 · 下拉/巨型/抽屉/全屏", "滚动 · 锚点/收缩"]),
 1: ("布局与对齐", ["方向 · row / column", "对齐 · start/center/end", "弹性 · flex / grid"]),
 2: ("尺寸与排版", ["字号阶梯", "行高节奏", "字重层级"]),
 3: ("定位与层级", ["定位 · static→sticky", "层级 · z-index", "堆叠上下文"]),
 4: ("交互与动效", ["触发 · hover/click/focus", "属性 · transform/opacity", "曲线 · easing"]),
 5: ("响应式与适配", ["断点 · breakpoint", "流式 · fluid/clamp", "安全区 · safe-area"]),
 6: ("性能与无障碍", ["避重排/重绘", "语义化标签", "可聚焦 focus"]),
 7: ("表单输入", ["标签", "输入态 · focus", "校验反馈"]),
 8: ("按钮操作", ["状态 · 默认/悬停/按下/禁用", "反馈 · 点击/加载"]),
 9: ("弹窗遮罩", ["触发器", "层级 · 遮罩 z-index", "关闭 · 遮罩/ESC/按钮"]),
 10: ("动效", ["属性 · transform/opacity 优先", "曲线 · cubic-bezier", "时长 · ms"]),
}
# 章节展示顺序：高频交互组件前置，基础视觉/工程章在后（ci 为 CHAPTERS 索引，与术语 ch 对应）
CH_DISPLAY = [0, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6]

# ----------------------------------------------------------------------------
# 术语数据（口语 -> 反模式 -> 正解 -> 错/对代码 -> 提示词要点 -> 三端坑点）
# 字段: id, ch(章节序号), speak(用户口语), cn(中文名·直白), en(英文术语),
#       anti(反模式), fix(正解), bad(错误代码), good(正确代码),
#       tip(list), plat{web,app,mini}
# ----------------------------------------------------------------------------
T = []
def add(id, ch, speak, cn, en, anti, fix, bad, good, tip, plat):
    T.append(dict(id=id, ch=ch, speak=speak, cn=cn, en=en, anti=anti, fix=fix,
                  bad=bad, good=good, tip=tip, plat=plat))

# ===================== 0. 导航（交互组件旗舰章） =====================
add("nav-sticky", 0, "滚动的时候顶部的导航栏要一直停在那儿别跟着滚走", "导航栏悬浮吸顶", "Sticky Header / Affix Navbar",
    "用 position:fixed 但没给下方内容留 top 偏移，结果导航栏盖住了正文第一行",
    "用 position:sticky; top:0 让导航栏滚到顶部就吸住，下方内容自然流式排列，不用手动补位",
    ".nav{ position:fixed; top:0; } /* 内容被遮住，需要额外 padding-top 补位 */",
    ".nav{ position:sticky; top:0; z-index:50; background:#fff; } /* 下方内容不用补位 */",
    ["优先 sticky 而非 fixed，省去手动 padding 补位", "加背景色加轻微阴影区分吸顶态", "移动端注意安全区，吸顶栏底部留阴影"],
    {"web": "sticky 兼容性良好；注意父容器不能有 overflow:hidden 否则失效",
     "app": "RN 用 scroll 监听或 react-navigation 的 header 吸顶",
     "mini": "页面内用 scroll-view 的 bindscroll 自己实现吸顶"})
add("nav-sidebar", 0, "左边放一排菜单，右边是内容，像后台管理那样", "左侧边栏导航", "Sidebar / Navigation Drawer",
    "用 float 左栏、内容用 margin-left 硬顶，窗口一窄就错位重叠",
    "用 flex 横向布局：左栏定宽不伸缩，右栏 flex:1 自动占剩余宽度",
    ".side{ float:left; width:200px; } .main{ margin-left:210px; } /* 窄屏重叠 */",
    ".layout{ display:flex; } .side{ width:200px; flex:none; } .main{ flex:1; min-width:0; }",
    ["flex 横向布局替代 float", "侧栏固定宽度 flex:none，内容 flex:1", "移动端侧栏改为抽屉（汉堡按钮唤出）"],
    {"web": "flex 布局最稳；响应式断点下转抽屉",
     "app": "Drawer 或底部 Tab 更常见于移动端",
     "mini": "微信侧边栏用自定义组件或官方 Drawer"})
add("nav-crumb", 0, "在页面上方显示『首页 / 分类 / 当前页』这种路径", "面包屑导航", "Breadcrumb",
    "只放一个标题，用户不知道自己从哪一层进来，也回不去上一级",
    "在页头放一组用 / 或 大于号 分隔的层级链接，最后一级高亮且不可点",
    "<h1>商品详情</h1> <!-- 用户不知道上一级在哪 -->",
    "<nav class='crumb'><a>首页</a><span>/</span><a>数码</a><span>/</span><b>商品详情</b></nav>",
    ["最后一级用 b 加粗且不可点", "分隔符用 / 或 大于号 统一", "移动端可只保留『返回上一级』箭头"],
    {"web": "语义用 nav 且加 aria-label='breadcrumb'",
     "app": "顶栏返回箭头加当前页标题",
     "mini": "navigation-bar 返回键加标题"})
add("nav-dropdown", 0, "鼠标移上去或者点一下，下面展开子菜单", "下拉子菜单", "Dropdown Menu / Submenu",
    "把所有二级入口平铺成一长串链接，页面又长又乱",
    "一级菜单项 hover 或 click 展开一个浮层子菜单，浮层用 absolute 定位",
    "<ul><li>产品</li><li>子产品A</li><li>子产品B</li><li>关于</li></ul>",
    ".menu li:hover .sub{ display:block; } .sub{ position:absolute; top:100%; left:0; }",
    ["浮层用 absolute 定位，注意别被父级 overflow 裁剪", "hover 展开要兼顾点击（移动端无 hover）", "子菜单加阴影圆角，和主菜单区分"],
    {"web": "hover 展开加键盘上下键导航",
     "app": "用底部弹窗或展开列表替代 hover",
     "mini": "小程序无 hover，用 bindtap 展开或跳转新页"})
add("nav-mega", 0, "鼠标移到『商品分类』，展开一个很大的面板，里面分好几列", "巨型菜单", "Mega Menu",
    "用普通小下拉只塞三五个字，内容多就挤、看不清",
    "hover 时展开一个宽面板，内部用多列网格 grid 归类展示大量入口",
    "<div class='dd'>3 个小链接挤在一起</div>",
    ".mega{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; width:600px; }",
    ["宽面板内部用 grid 分列归类", "每列给个小标题分组", "移动端降级为多级抽屉或独立分类页"],
    {"web": "grid 布局分列；注意浮层宽度与视口",
     "app": "不适合 hover，改用分类页或抽屉",
     "mini": "用分类页或 scroll-view 横滑分类"})
add("nav-hamburger", 0, "手机上点左上角三条杠，从侧面滑出一个菜单", "汉堡菜单抽屉", "Hamburger Menu / Off-canvas Drawer",
    "桌面那排菜单直接堆到手机上，挤成一团看不清也点不准",
    "窄屏隐藏横排菜单，显示汉堡图标，点击后用 transform:translateX 从侧边滑出抽屉",
    "/* 手机上把 8 个菜单平铺，互相挤压 */",
    ".drawer{ transform:translateX(-100%); transition:.3s; } .drawer.open{ transform:translateX(0); }",
    ["用 transform 做滑入（性能优于 left）", "抽屉外点击或遮罩关闭", "打开时锁 body 滚动，关闭恢复"],
    {"web": "transform 加 transition；遮罩层半透明",
     "app": "Drawer 组件原生支持手势",
     "mini": "小程序用 view 加 animation 或官方 drawer"})
add("nav-overlay", 0, "点一下菜单，整个屏幕变成导航页，大图标大链接", "全屏遮罩导航", "Full-screen Overlay Navigation",
    "只弹个小小的菜单，选项密密麻麻，手机上根本不好点",
    "点击后用 fixed 全屏半透明遮罩盖住页面，里面放超大间距的导航链接，再给个关闭按钮",
    "<div class='tiny'>小菜单 5 个挤一起</div>",
    ".overlay{ position:fixed; inset:0; background:rgba(0,0,0,.9); display:flex; flex-direction:column; } .overlay a{ font-size:22px; padding:18px; }",
    ["全屏遮罩用 position:fixed; inset:0", "链接字号大、间距大，便于手机点击", "务必给明显的关闭或返回按钮"],
    {"web": "inset:0 加 flex 纵向排列",
     "app": "Modal 或全屏页面切换",
     "mini": "用 cover-view 或独立页面"})
add("nav-anchor", 0, "页面右边有一排小圆点，点一下跳到对应那一段", "锚点导航", "Anchor Navigation / Scrollspy",
    "长文章没有导航，用户不知道下面有什么，也回不到顶",
    "右侧放一组锚点链接，点击平滑滚动到对应区块；滚动时高亮当前区块",
    "<!-- 一整页长文，无任何跳转入口 -->",
    "<nav class='anchor'><a href='#s1'>一</a><a href='#s2'>二</a></nav> /* 加 scrollIntoView 与 scrollspy */",
    ["锚点用 id 加 scrollIntoView 平滑滚动", "滚动时高亮当前段（scrollspy）", "移动端可折叠为『目录』按钮"],
    {"web": "scroll-behavior:smooth 加 IntersectionObserver",
     "app": "SectionList 原生索引",
     "mini": "scroll-into-view 加自定义索引"})
add("nav-shrink", 0, "往下滑的时候，顶部大图大标题慢慢缩成一条小导航条", "滚动收缩头部", "Collapsing Header / Scroll-shrink Toolbar",
    "头部一直那么大，占着屏幕，滑一点内容就被挡很多",
    "监听滚动，头部从大尺寸（含大图、搜索框）过渡到紧凑尺寸（仅 logo 加菜单），用 transform 或 height 过渡",
    "/* 头部固定 200px 高，滚动也不变，挡视野 */",
    "header.classList.toggle('compact', scrollY>80); /* CSS 用 height/transform 过渡 */",
    ["滚动阈值触发 compact 类", "用 CSS transition 平滑缩放", "收缩态保留核心入口（logo/搜索/菜单）"],
    {"web": "scroll 监听加 class 切换加 transition",
     "app": "Animated.Header 原生支持",
     "mini": "onPageScroll 加动态 style 或官方导航栏 API"})

# ===================== 1. 布局与对齐 =====================
add("center-icon", 1, "图标和文字对不齐，总是高低错落", "图标和文字垂直居中", "Vertical Centering / align-items",
    "用 margin-top 负数或 line-height 硬凑，换个字体或字号就又歪了",
    "包一层 flex 容器，用 align-items:center 让图标和文字落在同一条中轴线上",
    ".ico{ vertical-align:middle; margin-top:-3px; } /* 只对行内元素近似生效，基线不对齐 */",
    ".row{ display:flex; align-items:center; gap:6px; } /* 图标与文字同中轴，换字号也不歪 */",
    ["强调用 flex 的 align-items 而非 margin 凑", "图标用 inline-flex 避免基线缝隙", "多行文字仍要垂直居中时用 align-items:center"],
    {"web":"直接 flex + align-items:center；注意 inline 元素基线问题",
     "app":"RN 用 alignItems:'center'，且默认主轴是纵向",
     "mini":"用 flex 布局 + align-items，rpx 控制图标尺寸"})

add("center-both", 1, "让一个盒子在屏幕正中间", "水平垂直都居中", "Perfect Centering",
    "用 top/left 50% 忘了配 transform，元素永远偏右下角",
    "现代做法：父级 display:flex + justify-content/align-items 都 center",
    ".box{ position:absolute; top:50%; left:50%; } /* 只位移没回拉，永远偏右下 */",
    ".wrap{ display:flex; justify-content:center; align-items:center; min-height:100vh; } /* 一行搞定 */",
    ["优先用 flex 居中，少写 position", "absolute 居中必须配 transform:translate(-50%,-50%)",
     "不确定高度时用 flex 比 absolute 稳"],
    {"web":"flex 居中或 absolute+transform，二选一别混",
     "app":"RN 父容器加 justifyContent/alignItems:'center'",
     "mini":"wxss 同样支持 flex 居中，无特殊坑"})

add("equal-width", 1, "一排几个东西平分宽度", "等分布局", "Equal Width / flex:1",
    "给每个写死 width:25%，加个间距或边框就溢出换行",
    "容器 display:flex，子项 flex:1 自动平分，间距用 gap",
    ".col{ width:25%; float:left; } /* 间距/边框会让总和超 100% 换行 */",
    ".row{ display:flex; gap:12px; } .col{ flex:1; } /* 自动平分，加间距也不溢出 */",
    ["用 flex:1 代替写死百分比", "间距交给容器的 gap 而不是子项 margin", "等高列 flex 默认就对齐"],
    {"web":"flex:1 + gap，最稳",
     "app":"RN 子项 flex:1 即可平分",
     "mini":"flex:1 在 wxss 同样有效"})

add("space-between", 1, "左边标题右边按钮，贴两边", "两端对齐", "Space Between",
    "用 text-align:justify 或一堆 margin 硬推，换行就乱",
    "flex 容器加 justify-content:space-between，两端贴边中间均分",
    ".bar span{ margin:0 10px; } /* 手动推，元素一多就歪 */",
    ".bar{ display:flex; justify-content:space-between; align-items:center; }",
    ["两端对齐用 space-between", "三个以上元素用 space-between 会自动均分剩余", "垂直方向用 align-items 控制"],
    {"web":"标准 flex 属性，放心用",
     "app":"RN 用 justifyContent:'space-between'",
     "mini":"wxss 支持 justify-content"})

add("ellipsis", 1, "文字太长把页面撑破了", "文字溢出省略号", "Text Overflow Ellipsis",
    "只写 overflow:hidden，文字被切掉却没有省略号，像坏了一样",
    "三件套：white-space:nowrap + overflow:hidden + text-overflow:ellipsis",
    ".t{ overflow:hidden; } /* 文字硬切，没省略号，用户以为卡了 */",
    ".t{ white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }",
    ["三件套缺一不可", "多行省略要用 -webkit-line-clamp", "容器必须有明确宽度"],
    {"web":"-webkit-line-clamp 做两行/三行省略",
     "app":"RN 用 numberOfLines 属性",
     "mini":"wxss 支持 text-overflow，多行用 line-clamp"})

add("sticky-top", 1, "滚动时想让顶栏一直跟着", "吸顶（滚动固定）", "Sticky Top",
    "用 position:fixed 把元素钉死，结果脱离文档流把下面的内容盖住",
    "用 position:sticky; top:0，它会在滚到顶部时自动吸住，不脱离流",
    ".nav{ position:fixed; top:0; } /* 脱离文档流，下方内容被遮 */",
    ".nav{ position:sticky; top:0; z-index:10; background:#fff; } /* 滚到顶才吸住 */",
    ["吸顶首选 sticky 而非 fixed", "sticky 要父容器没设 overflow:hidden", "记得给背景色，不然内容透出来"],
    {"web":"sticky 现代浏览器都支持",
     "app":"RN 用 stickyHeaderIndices 或 ScrollView",
     "mini":"scroll-view 的 sticky 用 scroll-into-view 近似实现"})

add("equal-height", 1, "一行里几个卡片高度不一样丑", "等高列", "Equal Height Columns",
    "给每个写死 height，内容一多就溢出或留白",
    "flex 容器里子项默认 align-items:stretch，自动等高",
    ".card{ height:200px; } /* 写死高度，内容多就溢出 */",
    ".row{ display:flex; } .card{ flex:1; } /* 默认 stretch 自动等高 */",
    ["flex 默认就等高，别写死 height", "想顶部对齐才用 align-items:flex-start", "grid 也能自动等高"],
    {"web":"flex stretch 或 grid 都可",
     "app":"RN 同 flex 默认等高",
     "mini":"wxss flex 默认等高"})

add("inline-gap", 1, "几个元素横排，中间总有莫名缝隙", "inline-block 间隙", "Inline-block Whitespace Gap",
    "以为是 margin 问题疯狂调，其实是标签间的换行被当成空格",
    "改用 flex 布局，或给父级 font-size:0 再给子项还原字号",
    "<span>甲</span> <span>乙</span> /* 换行产生 4px 缝隙，调 margin 无效 */",
    ".row{ display:flex; gap:8px; } /* 彻底没有换行空格问题 */",
    ["横排首选 flex + gap", "必须 inline-block 时父级 font-size:0", "float 布局也有类似缝隙坑"],
    {"web":"flex 解决一切",
     "app":"RN 无此问题，默认 flex",
     "mini":"wxss 同 web"})

add("neg-margin", 1, "想微调位置用了负数 margin", "负边距陷阱", "Negative Margin",
    "用负 margin 把元素拉到该去的位置，一换内容/屏幕就错位",
    "位置调整交给 flex/grid 的对齐与 gap，少碰 margin 尤其是负值",
    ".x{ margin-left:-12px; margin-top:-4px; } /* 凑位置，脆弱易错 */",
    ".wrap{ display:flex; align-items:center; gap:10px; } /* 用布局而非 margin 凑 */",
    ["能用布局解决就别用 margin 凑", "负值 margin 在不同盒模型下表现不一致", "间距统一用 gap"],
    {"web":"flex/gap 替代负 margin",
     "app":"RN 用 padding/margin 正数即可",
     "mini":"wxss 同 web"})

add("flex-wrap", 1, "一排放不下却硬挤成一团", "流式换行排列", "Flex Wrap",
    "只设 flex 不设 wrap，元素被压缩变形也不换行",
    "容器加 flex-wrap:wrap，放不下自动换到下一行",
    ".row{ display:flex; } /* 子项被压扁也不换行 */",
    ".row{ display:flex; flex-wrap:wrap; gap:10px; } /* 放不下就换行 */",
    ["横向排标签/卡片用 wrap", "配合 gap 控制换行间距", "想不换行才用 nowrap"],
    {"web":"flex-wrap 标准支持",
     "app":"RN flexWrap:'wrap'",
     "mini":"wxss 支持 flex-wrap"})

add("two-col", 1, "左边固定宽右边占满", "左固定右自适应两栏", "Fixed+Fluid Two Column",
    "两边各写 50%，左边图标一变就错位",
    "用 flex：左边定宽，右边 flex:1 自动占剩余",
    ".l{ width:120px; } .r{ width:calc(100% - 120px); } /* 加减稍错就溢出 */",
    ".box{ display:flex; } .l{ width:120px; flex:none; } .r{ flex:1; }",
    ["固定侧 flex:none 防被压缩", "自适应侧 flex:1", "grid 用 120px 1fr 更直观"],
    {"web":"flex 或 grid 120px 1fr",
     "app":"RN 同 flex 写法",
     "mini":"wxss 同 web"})

add("baseline", 1, "几个大小不同的字不在一条线上", "基线对齐", "Baseline Alignment",
    "用 vertical-align:middle 导致大字号元素整体偏移",
    "理解 baseline：vertical-align:baseline 让文字底部对齐；图标才用 middle",
    ".big, .small{ vertical-align:middle; } /* 文字用 middle 反而错位 */",
    ".txt{ vertical-align:baseline; } .ico{ vertical-align:middle; } /* 各司其职 */",
    ["文字用 baseline，图标/图片用 middle", "flex 下用 align-items 控制整盒对齐", "表格单元格默认 baseline"],
    {"web":"vertical-align 规则一致",
     "app":"RN 用 textAlign 或 alignItems",
     "mini":"wxss 同 web"})

# ===================== 2. 尺寸与排版 =====================
add("clamp", 2, "字号想跟着屏幕大小变", "响应式字号", "Clamp / Fluid Type",
    "写死 font-size:16px，大屏小得像蚂蚁，小屏又挤",
    "用 clamp(最小, 理想vw, 最大) 让字号在区间内随屏幕平滑变化",
    "h1{ font-size:48px; } /* 写死，移动端巨大 PC 端又小 */",
    "h1{ font-size:clamp(28px, 5vw, 48px); } /* 随屏幕在 28~48 间变化 */",
    ["clamp 三参：最小/理想/最大", "理想值用 vw 跟随视口", "正文别太大，14-18px 合适"],
    {"web":"clamp 现代浏览器都支持",
     "app":"RN 用 Dimensions 算或百分比",
     "mini":"rpx 本身随屏自适应，少用 vw"})

add("hairline", 2, "1px 的线在手机上变粗了一截", "高清 1px 边框", "Hairline Border / 0.5px",
    "直接 border:1px，在 2x/3x 屏被渲染成 2-3px 显粗",
    "用 transform:scale 缩放伪元素，或 border-width:0.5px（新设备）",
    ".line{ border-bottom:1px solid #ddd; } /* 高清屏变 2px 显粗 */",
    ".line{ position:relative; } .line::after{ content:''; position:absolute; left:0; right:0; bottom:0; border-bottom:1px solid #ddd; transform:scaleY(.5); transform-origin:0 100%; }",
    ["高清屏用 scale 缩放出 0.5px", "也可用 box-shadow 模拟细线", "0.5px 在部分安卓不被识别"],
    {"web":"scale 伪元素最稳",
     "app":"RN 用 StyleSheet.hairlineWidth",
     "mini":"rpx 下 1rpx 近似物理 0.5px，直接用"})

add("line-height", 2, "字挤在一起看不清", "行高可读性", "Line Height Readability",
    "line-height 用 px 写死，换字号行距就错位",
    "line-height 用无单位倍数（如 1.6），随字号自动缩放",
    "p{ line-height:24px; font-size:18px; } /* 改字号行距不变，显挤 */",
    "p{ line-height:1.6; font-size:16px; } /* 行距=字号×1.6，永远协调 */",
    ["正文 1.5-1.7 最舒适", "用无单位值而非 px", "标题可收紧到 1.2-1.3"],
    {"web":"无单位 line-height 通用",
     "app":"RN lineHeight 要 number（无单位）",
     "mini":"wxss 同 web"})

add("font-weight", 2, "标题正文一个粗细没层次", "字重层次", "Font Weight Hierarchy",
    "全用 400，靠加大字号区分，层次弱",
    "建立 400/500/600/700 的字重阶梯，配合字号拉出层级",
    "h3{ font-weight:400; font-size:18px; } /* 和正文一样重，分不清 */",
    "h3{ font-weight:600; } .sub{ font-weight:400; color:#888; } /* 轻重分明 */",
    ["标题 600-700，正文 400", "同一屏别超过 3 种字重", "用字重+颜色双保险分层"],
    {"web":"系统字体字重齐全",
     "app":"RN fontWeight 用 '400'/'700' 字符串",
     "mini":"wxss font-weight 同 web"})

add("letter-spacing", 2, "字挨太紧或太松", "字间距调整", "Letter Spacing",
    "靠加空格调间距，中英文混排更乱",
    "用 letter-spacing 控制字距，中文标题可略放大显精致",
    "h1{ padding:0 4px; } /* 用空格凑，不可控 */",
    "h1{ letter-spacing:1px; } /* 精确控制字距 */",
    ["标题可加 0.5-1px 显精致", "正文一般不动字距", "英文 large 字距更有设计感"],
    {"web":"letter-spacing 标准",
     "app":"RN letterSpacing（无单位，px）",
     "mini":"wxss 同 web"})

add("web-font", 2, "想用个特别的字体", "自定义字体", "Web Font / @font-face",
    "塞一个好几 MB 的字体文件，首屏卡半天",
    "用 @font-face 只引需要的字重，并 font-display:swap 避免空白",
    "@import url(big-font.css); /* 整包加载，首屏白屏 */",
    "@font-face{ font-family:'X'; src:url(x.woff2) format('woff2'); font-display:swap; }",
    ["用 woff2 体积最小", "font-display:swap 防白屏", "只引用到的字重/字符"],
    {"web":"woff2 + preload",
     "app":"RN 用自定义字体需 bundled",
     "mini":"wxss 不支持 @font-face，只能用系统字体"})

add("text-indent", 2, "段落开头想空两格", "首行缩进", "Text Indent",
    "用加空格或 padding 缩进，换行又不对了",
    "用 text-indent:2em，随字号自动是两字符宽",
    "p{ padding-left:2em; } /* 整段缩进，不是首行 */",
    "p{ text-indent:2em; } /* 仅首行缩进两字 */",
    ["首行缩进用 text-indent:2em", "em 单位跟随字号", "网页正文现在少用缩进，看风格"],
    {"web":"text-indent 标准",
     "app":"RN 无原生，用 padding 模拟",
     "mini":"wxss 支持 text-indent"})

add("justify", 2, "一段文字两端对齐更整齐", "两端对齐", "Text Justify",
    "用 justify 后单词间距被拉得忽大忽小很难看",
    "中文可用 text-align:justify；英文长文才用，并配 hyphens",
    "p{ text-align:justify; } /* 英文单词间距忽大忽小 */",
    "p{ text-align:justify; text-justify:inter-character; } /* 中文按字符对齐更匀 */",
    ["中文用 inter-character 更匀", "英文慎用，易产生大缝隙", "移动端窄栏不建议两端对齐"],
    {"web":"text-justify 支持",
     "app":"RN 无 justify，需富文本组件",
     "mini":"wxss 支持 text-align:justify"})

# ===================== 3. 定位与层级 =====================
add("z-index", 3, "弹窗盖不住别的元素", "层级管理（z-index）", "Z-index / Stacking",
    "到处写 z-index:9999，新弹窗永远盖不住旧的",
    "建立层级规范（如遮罩 1000、弹窗 1001、Toast 2000），别随手堆大数",
    ".a{ z-index:9999; } .b{ z-index:99999; } /* 数字失控，互相覆盖 */",
    ":root{ --z-mask:1000; --z-modal:1001; --z-toast:2000; } .modal{ z-index:var(--z-modal); }",
    ["用 CSS 变量统一管理层级", "别无脑写 9999", "z-index 只在定位元素上生效"],
    {"web":"配合 stacking context 理解",
     "app":"RN 无 z-index，用 elevation 或顺序",
     "mini":"wxss 支持 z-index，但原生组件永远在上"})

add("overlay", 3, "弹窗底下要有一层半透明蒙版", "遮罩层", "Overlay / Mask",
    "蒙版没铺满或没挡点击，点空白处弹窗关不掉",
    "固定定位铺满全屏的半透明层，并拦截点击",
    ".mask{ background:rgba(0,0,0,.5); } /* 没定位没铺满，盖不住 */",
    ".mask{ position:fixed; inset:0; background:rgba(0,0,0,.5); } /* 铺满+拦截 */",
    ["fixed + inset:0 铺满", "蒙版要能点它关闭弹窗", "层级要低于弹窗本体高于内容"],
    {"web":"inset:0 简洁写法",
     "app":"RN 用绝对定位铺满 + 透明层",
     "mini":"小程序用 cover-view 盖原生组件"})

add("fixed-center", 3, "把弹窗钉在屏幕中间", "固定定位居中", "Fixed Centering",
    "top/left 50% 后忘了 translate，弹窗偏在右下",
    "fixed 定位 + left/top:50% + transform:translate(-50%,-50%)",
    ".pop{ position:fixed; top:50%; left:50%; } /* 偏右下角 */",
    ".pop{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); }",
    ["fixed 居中必须配 transform 回拉", "或用 flex 居中父级", "移动端注意键盘弹起遮挡"],
    {"web":"translate 回拉最常用",
     "app":"RN 居中用 alignItems+justifyContent",
     "mini":"小程序用 flex 居中容器即可"})

add("stacking", 3, "明明 z-index 很大却还是被盖", "层叠上下文", "Stacking Context",
    "在不懂层叠规则时乱调 z-index，越调越乱",
    "理解：z-index 只在同一个层叠上下文里比大小；新上下文会隔离比较",
    "/* 父级有 transform/opacity 形成新上下文，子级 z-index 再大也出不去 */",
    "/* 规则：同上下文比 z-index；创建上下文的属性：transform/opacity/filter/position+z-index */",
    ["z-index 只在同一上下文内有效", "transform/opacity 会创建新上下文", "先理清上下文再调层级"],
    {"web":"层叠规则通用",
     "app":"RN 无此概念，靠组件顺序",
     "mini":"wxss 同 web，但要注意原生组件"})

add("relative", 3, "想让元素相对自己挪一点点", "相对定位", "Relative Positioning",
    "用 margin 挪位置导致后面元素也跟着动",
    "position:relative + top/left 只移动自己，不影响文档流排布",
    ".x{ margin-top:-10px; } /* 自己移了，后面也跟着上移 */",
    ".x{ position:relative; top:-10px; } /* 仅自身偏移，不挤别人 */",
    ["relative 不脱离文档流", "用它做小幅微调或定位锚点", "absolute 的参照物常是 relative 父级"],
    {"web":"relative 标准",
     "app":"RN 用 marginTop 等正数模拟",
     "mini":"wxss 同 web"})

add("absolute", 3, "把元素从正常排版里抽出来摆", "绝对定位", "Absolute Positioning",
    "absolute 后元素乱飞，父级没定位它跑到页面角落",
    "absolute 相对最近的有定位（非 static）的祖先；给父级加 relative 当锚",
    ".child{ position:absolute; top:0; } /* 父级没定位，跑到最外层 */",
    ".parent{ position:relative; } .child{ position:absolute; top:0; left:0; }",
    ["absolute 找最近定位祖先", "父级加 relative 当锚点", "脱离文档流，不再占位置"],
    {"web":"relative+absolute 黄金搭档",
     "app":"RN 用 absolute + 父 relative 同思路",
     "mini":"wxss 同 web"})

add("pseudo", 3, "想在元素前后加个装饰小东西", "伪元素装饰", "::before / ::after",
    "多写一个空标签只为放个装饰，HTML 变脏",
    "用 ::before / ::after 配合 content 加装饰，不污染结构",
    "<i class='dot'></i> /* 只为装饰多写标签 */",
    ".tip::before{ content:''; width:6px; height:6px; border-radius:50%; background:#c8442e; }",
    ["伪元素必须写 content（哪怕空）", "装饰性内容优先伪元素", "清浮动也常用 ::after"],
    {"web":"伪元素标准支持",
     "app":"RN 无伪元素，写独立组件",
     "mini":"wxss 支持 ::before/::after，但注意层级"})

add("scroll-lock", 3, "弹窗出来后背景还能滚", "弹窗滚动锁定", "Scroll Lock / Body Scroll",
    "只盖蒙版不锁滚动，底层列表跟着滚很诡异",
    "弹窗打开时给 body 加 overflow:hidden（移动端还要固定位置）",
    "/* 只加了蒙版，背景照滚 */",
    "body.modal-open{ overflow:hidden; } /* 打开弹窗时给 body 加这个类 */",
    ["开弹窗锁 body 滚动", "移动端用 position:fixed 防回弹", "关闭时记得移除类"],
    {"web":"overflow:hidden + 记录滚动位置",
     "app":"RN 蒙版盖住自然不滚",
     "mini":"小程序用 catchtouchmove 阻止穿透"})

add("fixed-bottom", 3, "底部按钮被手机小黑条挡住", "底部固定 + 安全区", "Fixed Bottom + Safe Area",
    "fixed 贴底没留安全区，iPhone 小黑条挡住按钮",
    "fixed 底部 + padding-bottom:env(safe-area-inset-bottom)",
    ".bar{ position:fixed; bottom:0; } /* 被刘海屏/小黑条挡 */",
    ".bar{ position:fixed; bottom:0; padding-bottom:env(safe-area-inset-bottom); }",
    ["底部固定必加安全区 padding", "viewport 要加 viewport-fit=cover", "高度测算要含安全区"],
    {"web":"env(safe-area-inset-bottom) 生效需 viewport-fit=cover",
     "app":"RN 用 SafeAreaView",
     "mini":"小程序用 env() 同样需 cover 配置"})

# ===================== 4. 交互与动效 =====================
add("hover", 4, "鼠标移上去想变个样", "悬停状态", "Hover State",
    "只改背景色没过渡，鼠标移上去生硬闪一下",
    "用 :hover 改样式并配合 transition 让变化平滑",
    ".btn:hover{ background:#c8442e; } /* 瞬间变，没过渡显生硬 */",
    ".btn{ transition:background .2s; } .btn:hover{ background:#c8442e; }",
    ["hover 配 transition 才顺滑", "移动端没有 hover，要另做 active", "别在 hover 改布局尺寸"],
    {"web":"hover 仅鼠标设备",
     "app":"RN 无 hover，用 Pressable 的 pressed",
     "mini":"小程序无 hover，用 hover-class"})

add("focus-visible", 4, "键盘选中输入框没任何提示", "键盘聚焦样式", "Focus-visible",
    "只写 :focus 或干脆没聚焦样式，键盘用户不知道焦点在哪",
    "用 :focus-visible 只在键盘聚焦时显示轮廓，鼠标点击不显示",
    "/* 没聚焦样式，Tab 切过去毫无反馈 */",
    "input:focus-visible{ outline:2px solid #c8442e; outline-offset:2px; }",
    ["用 focus-visible 区分键鼠", "聚焦轮廓别用 outline:none 直接去掉", "输入框聚焦要给明确反馈"],
    {"web":"focus-visible 现代支持",
     "app":"RN 用 onFocus 加边框",
     "mini":"wxss 支持 :focus，focus-visible 谨慎"})

add("disabled", 4, "按钮不能点却看不出来", "禁用状态", "Disabled State",
    "只加 disabled 属性不换样式，用户以为能点一直戳",
    "disabled 时降低透明度+改光标+去掉阴影，明确告知不可点",
    "button[disabled]{ } /* 没视觉变化，用户不知道禁用 */",
    "button[disabled]{ opacity:.5; cursor:not-allowed; }",
    ["禁用要肉眼可辨（变灰/降透明）", "cursor:not-allowed 提示", "禁用时阻止点击逻辑"],
    {"web":"disabled 属性+样式",
     "app":"RN disabled 属性 + 条件样式",
     "mini":"小程序 button 的 disabled"})

add("transition", 4, "点一下想有点变化动画", "过渡动画", "CSS Transition",
    "直接改样式没过渡，变化像瞬移一样生硬",
    "对会变化的属性加 transition，指定时长与缓动",
    ".box{ width:100px; } .box.big{ width:200px; } /* 瞬变，无动画 */",
    ".box{ transition:width .3s ease; } .box.big{ width:200px; }",
    ["transition 写在被改元素上", "别对 display 做过渡（无效）", "时长 0.2-0.3s 最自然"],
    {"web":"transition 标准",
     "app":"RN 用 Animated / LayoutAnimation",
     "mini":"小程序用 CSS transition，或 wx.createAnimation"})

add("transform", 4, "想让元素移动/放大/旋转", "变换动画", "Transform",
    "用改 top/left 做位移动画，每帧重排卡顿",
    "位移/缩放/旋转用 transform，走 GPU 合成不掉帧",
    ".box{ left:0; } .box.move{ left:100px; } /* 改布局属性，触发重排 */",
    ".box{ transform:translateX(0); } .box.move{ transform:translateX(100px); }",
    ["位移用 translate 而非 top/left", "动画优先 transform/opacity", "配合 will-change 提示浏览器"],
    {"web":"transform 走合成层",
     "app":"RN transform 数组写法",
     "mini":"wxss 支持 transform，注意单位"})

add("easing", 4, "动画太生硬像机器", "缓动曲线", "Easing Curve",
    "用 linear 匀速，动画像幻灯片切换一样死板",
    "用 ease / cubic-bezier 让启动结束有快慢节奏更自然",
    "transition:all .3s linear; /* 匀速，生硬 */",
    "transition:all .3s cubic-bezier(.4,0,.2,1); /* 标准缓动，自然 */",
    ["默认 ease 已比 linear 自然", "cubic-bezier(.4,0,.2,1) 是 Material 标准", "回弹用 overshoot 曲线"],
    {"web":"cubic-bezier 通用",
     "app":"RN Easing 模块",
     "mini":"小程序同 web"})

add("debounce", 4, "边打字边搜索太费", "防抖", "Debounce",
    "input 每次按键都发请求，接口被打爆",
    "防抖：停止输入 N 毫秒后才执行，连续输入只触发最后一次",
    "input.oninput = search; /* 每敲一字请求一次，疯狂打接口 */",
    "function debounce(fn,wait){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),wait);}}",
    ["搜索/输入用防抖 300ms", "防抖=等停了再执行", "和节流区分清楚"],
    {"web":"手写或 lodash.debounce",
     "app":"RN 同逻辑，注意卸载清理",
     "mini":"小程序同 web，注意页面卸载清理定时器"})

add("throttle", 4, "滚动时函数被疯狂调用", "节流", "Throttle",
    "scroll/resize 每帧都算，页面直接卡死",
    "节流：固定时间间隔只执行一次，平滑又省资源",
    "window.onscroll = onScroll; /* 每滚动一像素就执行，卡 */",
    "function throttle(fn,wait){let ok=true;return(...a)=>{if(!ok)return;ok=false;fn(...a);setTimeout(()=>ok=true,wait);}}",
    ["滚动/拖拽用节流", "节流=每隔 N ms 执行一次", "和防抖区分：节流限频率防抖等停止"],
    {"web":"手写或 lodash.throttle",
     "app":"RN 同逻辑",
     "mini":"小程序同 web"})

add("active", 4, "按下按钮没任何反馈", "按下状态", "Active / Pressed",
    "没 :active 样式，点下去毫无反馈像没点上",
    "用 :active 在按下瞬间给反馈（变深/缩小）",
    "/* 点击无反馈，用户不确定有没有点到 */",
    ".btn:active{ transform:scale(.97); background:#a8351f; }",
    ["active 给按下即时反馈", "配合 transform:scale 显灵动", "移动端 active 有时不触发，用 touch"],
    {"web":":active 鼠标/触摸生效",
     "app":"RN Pressable 的 onPressIn",
     "mini":"小程序用 hover-class 兼做按下"})

# ===================== 5. 响应式与适配 =====================
add("viewport", 5, "手机上网页被缩小成一团", "视口设置", "Viewport Meta",
    "没设 viewport，手机按 980px 桌面宽度渲染再缩小",
    "head 加 <meta name=viewport content='width=device-width,initial-scale=1'>",
    "<!-- 没 viewport，移动端按桌面宽度缩显示 -->",
    "<meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>",
    ["移动端必备 viewport", "initial-scale=1 防默认缩放", "想用安全区加 viewport-fit=cover"],
    {"web":"viewport 是移动端第一步",
     "app":"RN 无此概念，天然按设备宽",
     "mini":"小程序默认已按屏宽，无需设"})

add("safe-area", 5, "刘海/小黑条挡住内容", "安全区适配", "Safe Area Inset",
    "内容贴边被刘海、圆角、底部小黑条切掉",
    "用 env(safe-area-inset-*) 给四边留安全间距",
    ".page{ padding:0 12px; } /* 内容被刘海/小黑条切 */",
    ".page{ padding:env(safe-area-inset-top) 12px env(safe-area-inset-bottom); }",
    ["安全区要 viewport-fit=cover 才生效", "顶部刘海/底部小黑条都要留", "全面屏手机必做"],
    {"web":"env() 需 viewport-fit=cover",
     "app":"RN 用 SafeAreaView",
     "mini":"小程序 env() 同样需 cover 配置"})

add("media", 5, "按屏幕大小换样式", "媒体查询断点", "Media Query Breakpoint",
    "写死一套样式，PC 上挤移动端上炸",
    "用 @media 设断点（如 768px）分桌面/平板/手机三套",
    "/* 只有一种布局，任何屏都硬套 */",
    "@media (max-width:768px){ .nav{ flex-direction:column; } }",
    ["常用断点 768/1024", "移动优先：先写小屏再 min-width 扩展", "断点别太多，3 档足够"],
    {"web":"媒体查询标准",
     "app":"RN 用 Dimensions 监听宽度",
     "mini":"小程序用 rpx 自带响应，少数用媒体查询"})

add("autofit", 5, "网格列数想跟着屏宽变", "自适应列数网格", "Grid Auto-fit",
    "写死 4 列，手机上一行挤 4 个看不清",
    "用 grid-template-columns:repeat(auto-fit,minmax(160px,1fr)) 自动换行",
    ".g{ display:grid; grid-template-columns:repeat(4,1fr); } /* 手机挤 4 列 */",
    ".g{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; }",
    ["auto-fit 自动决定列数", "minmax 控制每列最小宽度", "比写媒体查询省心"],
    {"web":"grid auto-fit 现代支持",
     "app":"RN 用 numColumns 或 flex 算",
     "mini":"wxss 支持 grid，但兼容略弱"})

add("vwvh", 5, "想按屏幕比例定位元素", "视口单位", "vw / vh Units",
    "用 px 写高度，不同屏高元素比例全乱",
    "用 vw(视口宽%) / vh(视口高%) 让尺寸跟随屏幕",
    ".banner{ height:300px; } /* 小屏占大半，大屏一小条 */",
    ".banner{ height:40vh; } /* 永远是屏高的 40% */",
    ["全屏弹窗高度用 100vh", "配合 calc 加减固定值", "移动端 100vh 含地址栏坑，用 dvh"],
    {"web":"vh 注意移动端地址栏，用 dvh",
     "app":"RN 用百分比或 Dimensions",
     "mini":"小程序慎用 vh，多用 rpx"})

add("dpr", 5, "高清屏上图片发虚", "高 DPR / 二倍图", "Device Pixel Ratio",
    "只给一张图，2x/3x 屏被拉伸发虚",
    "用 srcset 提供多倍图，或矢量 SVG 永不虚",
    "<img src='a.png'> /* 单图，高清屏发虚 */",
    "<img src='a.png' srcset='a.png 1x, a@2x.png 2x, a@3x.png 3x'>",
    ["高清屏用 2x/3x 图或 SVG", "SVG 矢量天然清晰", "背景图用 image-set 类似处理"],
    {"web":"srcset / picture 元素",
     "app":"RN 用不同分辨率资源或矢量",
     "mini":"小程序用 mode 缩放，优先 SVG/2x"})

add("orientation", 5, "横屏竖屏布局要不一样", "横竖屏适配", "Orientation Media",
    "横屏时布局没调整，元素被拉变形",
    "用 @media (orientation:landscape/portrait) 分横竖屏布局",
    "/* 横屏竖屏同一套，横屏被拉长 */",
    "@media (orientation:landscape){ .layout{ flex-direction:row; } }",
    ["平板/游戏类必做横竖屏", "横屏常把竖向布局改横向", "配合断点一起用"],
    {"web":"orientation 媒体查询",
     "app":"RN 监听维度变化",
     "mini":"小程序 onResize 判断横竖"})

add("tablet", 5, "平板上看手机布局太空", "平板断点适配", "Tablet Breakpoint",
    "只分手机/桌面，平板夹在中间要么挤要么太空",
    "加 1024px 左右平板断点，给中间尺寸单独布局",
    "@media(max-width:768px){} /* 平板(820px)落到桌面档，显空 */",
    "@media(min-width:768px) and (max-width:1024px){ .g{ grid-template-columns:repeat(3,1fr);} }",
    ["三档：<768 手机 / 768-1024 平板 / >1024 桌面", "平板上可适当放宽列数", "iPad 常见 768/820/1024"],
    {"web":"三断点覆盖主流设备",
     "app":"RN 按宽度分流",
     "mini":"小程序平板用 rpx 自适应为主"})

# ===================== 6. 性能与无障碍 =====================
add("reflow", 6, "改个样式整页卡一下", "重排与重绘", "Reflow / Repaint",
    "在循环里反复读改布局属性，触发大量重排卡死",
    "动画只用 transform/opacity（合成层），批量读写避免强制重排",
    "for(...){ el.style.width = i+'px'; } /* 每步强制重排，巨卡 */",
    "/* 动画用 transform/opacity；读改写分开，用 requestAnimationFrame 批量 */",
    ["transform/opacity 不触发重排", "避免循环内读写布局", "用 rAF 批量更新"],
    {"web":"合成层动画最省",
     "app":"RN 用原生驱动动画",
     "mini":"小程序动画走 WXS 避免通信卡顿"})

add("will-change", 6, "动画还是有点卡", "GPU 加速提示", "will-change",
    "给所有元素都加 will-change，反而更卡",
    "只对即将动画的元素提前声明 will-change，用完移除",
    "*{ will-change:transform; } /* 全开合成层，内存爆炸更卡 */",
    ".anim{ will-change:transform; } /* 仅动画元素，结束后移除 */",
    ["will-change 是提示不是开关", "别全局加，按需且用完移除", "滥用反而占内存掉帧"],
    {"web":"will-change 谨慎使用",
     "app":"RN 动画默认走原生线程",
     "mini":"小程序用 WXS / transform 优化"})

add("lazy", 6, "一进页面几十张图一起加载", "图片懒加载", "Lazy Loading",
    "首屏一次性加载所有图，白屏好几秒",
    "用 loading='lazy' 或 IntersectionObserver 滚到才加载",
    "<img src='big.jpg'> /* 全部立刻加载，首屏巨慢 */",
    "<img src='big.jpg' loading='lazy' alt='说明'>",
    ["图片加 loading='lazy'", "长列表用虚拟滚动更彻底", "记得写 alt 利于 SEO 与无障碍"],
    {"web":"loading=lazy 原生支持",
     "app":"RN 用懒加载列表/占位",
     "mini":"小程序用 lazy-load 属性"})

add("semantic", 6, "标签全用 div 堆出来", "语义化标签", "Semantic HTML",
    "满屏 div 套 div，结构和含义全丢失",
    "用 header/nav/main/section/article/footer 表达结构",
    "<div class='header'></div><div class='main'></div> /* 无语义 */",
    "<header></header><nav></nav><main><section><article></article></section></main>",
    ["结构用对标签利于 SEO 与读屏", "div 只当最后的万能容器", "标题层级 h1-h6 别跳级"],
    {"web":"语义标签 SEO 友好",
     "app":"RN 无标签概念，靠组件名",
     "mini":"小程序结构靠 view，语义靠注释"})

add("aria", 6, "读屏软件读不懂按钮", "ARIA 无障碍", "ARIA Attributes",
    "图标按钮没文字，视障用户听不出是干嘛的",
    "用 aria-label / role 给无文字控件补含义，状态用 aria-* 同步",
    "<button class='icon-only'>🔍</button> /* 读屏读出‘按钮’，不知用途 */",
    "<button aria-label='搜索'><svg/></button>",
    ["图标按钮必加 aria-label", "弹窗用 role='dialog' + aria-modal", "动态内容用 aria-live 播报"],
    {"web":"ARIA 提升无障碍评分",
     "app":"RN 用 accessibilityLabel",
     "mini":"小程序用 aria-* 属性"})

add("contrast", 6, "浅灰字配白底看不清", "颜色对比度", "Color Contrast (WCAG)",
    "用 #ccc 灰字配白底，对比度不达标也看不清",
    "正文对比度至少 4.5:1，大字 3:1，用工具校验",
    "color:#ccc; background:#fff; /* 对比度 ~1.6，远低于标准 */",
    "color:#595959; background:#fff; /* 对比度 >4.5，达标清晰 */",
    ["正文对比度≥4.5:1", "用对比度校验工具", "别为了好看牺牲可读性"],
    {"web":"WCAG 对比度影响 SEO 评分",
     "app":"RN 同原则，注意深色模式",
     "mini":"小程序同 web"})

add("keyboard", 6, "只能鼠标点，键盘没法用", "键盘导航", "Keyboard Navigation",
    "自定义控件没处理 Tab/Enter，键盘党用不了",
    "可操作元素加 tabindex，用 Enter/Space 触发，焦点可见",
    "/* 自定义 div 按钮，Tab 切不过去，回车也没反应 */",
    "div[role=button] tabindex=0; onkeydown:if(Enter||Space)click();",
    ["可点击元素要能 Tab 聚焦", "Enter/Space 触发点击", "配合 focus-visible 显示焦点"],
    {"web":"tabindex + 键盘事件",
     "app":"RN 用 focusable 属性",
     "mini":"小程序用 catchtap + 焦点处理"})

add("reduce-motion", 6, "动画晃得人头晕", "减弱动效偏好", "prefers-reduced-motion",
    "满屏动画，晕动症用户看了不适",
    "用 @media (prefers-reduced-motion:reduce) 关闭或减弱动画",
    "/* 所有动画强制播放，无视用户系统设置 */",
    "@media (prefers-reduced-motion:reduce){ *{ animation:none!important; transition:none!important; } }",
    ["尊重系统‘减少动态效果’设置", "无障碍合规项", "关动画而非直接删功能"],
    {"web":"prefers-reduced-motion 标准",
     "app":"RN 读系统设置或提供开关",
     "mini":"小程序同 web"})

add("darkmode", 6, "系统切深色模式页面全白刺眼", "深色模式适配", "Dark Mode / prefers-color-scheme",
    "写死白底黑字，深色模式下要么刺眼要么看不清",
    "用 CSS 变量定义颜色，配合 prefers-color-scheme 切深色",
    "body{ background:#fff; color:#000; } /* 系统深色也不变，刺眼 */",
    ":root{--bg:#fff;--tx:#1a1a1a} @media(prefers-color-scheme:dark){:root{--bg:#1a1a1a;--tx:#eee}}",
    ["颜色用 CSS 变量便于切换", "深色不是简单反色，注意对比度", "图片/图标也要准备深色版"],
    {"web":"prefers-color-scheme 标准",
     "app":"RN 用 Appearance / 主题状态",
     "mini":"小程序用 media 或手动主题切换"})

# ----------------------------------------------------------------------------
# 平台约束（工坊生成提示词用）
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# 前后效果对照（VD）：每个术语的「错误效果」与「正确效果」真实渲染片段
# 纯作者内容，直接注入静态 HTML，既直观好看又利于 SEO 抓取
# 约定：每个值是一个 (bad_html, good_html) 元组，HTML 属性统一用单引号
# ----------------------------------------------------------------------------
# 生成 n 个占位线条（用于可滚动演示）
def L(n, cls="m-line"):
    return ("<div class='%s'></div>" % cls) * n

# 可交互演示的术语 id（前端效果对照区会注入 data-demo 并加「点击体验」提示）
INTERACTIVE = {"nav-sticky","nav-sidebar","nav-crumb","nav-dropdown","nav-mega",
               "nav-hamburger","nav-overlay","nav-anchor","nav-shrink"}
HINT = {
 "nav-sticky":"点「点击试用」或上下滚动 · 看吸顶", "nav-shrink":"点「点击试用」· 看头部收缩",
 "nav-sidebar":"点「点击试用」· 收起/展开侧栏", "nav-crumb":"点「点击试用」· 切换当前位置",
 "nav-dropdown":"点「点击试用」· 展开二级菜单", "nav-mega":"点「点击试用」· 展开巨型菜单",
 "nav-hamburger":"点「点击试用」· 抽屉滑出", "nav-overlay":"点「点击试用」· 全屏展开",
 "nav-anchor":"点「点击试用」· 切换栏目",
}
VHINT_SVG = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3l14 7-6 2-2 6z"/></svg>'

# 导航章新版演示（nv-*）公共片段
NVB = lambda n: "".join(["<div class='nv-blk'></div>"] * n)
NV_ARROW = '<svg class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>'
NV_HAM = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>'
NVI_DASH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>'
NVI_GRID = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z"/></svg>'
NVI_PLUS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v8M8 12h8"/></svg>'
NVI_USER = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>'

add('form-input', 7, '输入框点进去边框要亮起来，让人知道现在在输入', '输入框聚焦高亮', 'Input Focus State',
    '输入框没有任何焦点反馈，用户点进去也看不出当前在哪一格，以为没反应', '输入框获得焦点时用 :focus 加边框变色+柔和阴影（focus ring），明确指示当前输入位置',
    "<input style='border:1px solid #ccc'> /* 点了没任何变化 */",
    'input:focus{ outline:none; border-color:#C8442E; box-shadow:0 0 0 3px rgba(200,68,46,.15); }',
    ['聚焦态用 border + box-shadow 双提示', 'focus ring 用半透明同色，别用生硬 outline', '移动端输入框字号≥16px 防自动放大'],
    {'app': 'RN 用 onFocus 改样式', 'mini': 'wxss 同样支持 :focus', 'web': 'CSS :focus / :focus-visible 即可'})

add('form-select', 7, '一个框，点开能选一个选项，像省市区选择那样', '下拉选择器', 'Select / Dropdown Selector',
    '用原生 select 样式丑且难统一，或自己平铺选项占地方', '做一个自定义下拉：输入框样式的触发器，点击展开浮层选项列表，选中后回填并收起',
    '<select><option>北京</option>...</select> /* 原生样式难控，各端长得不一样 */',
    '.sel{ position:relative } .sel .panel{ position:absolute; top:100%; } /* 触发器+浮层，选中回填 */',
    ['浮层绝对定位，注意被父级 overflow 裁剪', '选中后回填文字并收起面板', '移动端选项行高够大好点按'],
    {'app': 'RN Picker / ActionSheet', 'mini': 'picker 组件或自定义弹层', 'web': '绝对定位浮层+点击外部关闭'})

add('form-switch', 7, '一个能滑动的小开关，开是绿关是灰', '开关切换', 'Switch / Toggle',
    '用两个按钮「开/关」或复选框表示，占地方又不直观', '用一段式 Switch：圆点滑块在轨道上左右移动，开态变绿，关态变灰',
    '<button>开</button><button>关</button> /* 两个按钮，像设置里一堆 */',
    '.sw{ width:48px;height:28px;border-radius:15px;background:#ccc } .sw.on{ background:#1C7A4E } .sw .dot{ transform:translateX(22px) }',
    ['开态用绿、关态用灰，符合直觉', '用 transform 移动圆点（性能优于 left）', '加 transition 让滑动顺滑'],
    {'app': 'RN 直接用 Switch 组件，受控 value/onValueChange', 'mini': '小程序 switch 组件，bindchange 拿勾选状态', 'web': 'input[type=checkbox] 自定义成开关样式'})

add('form-checkbox', 7, '几个小方框，能同时勾选多个', '复选框', 'Checkbox',
    '用文字「是/否」或图片当勾选，点击区域小、状态不清', '用方形复选框：未选空心、选中填充主色并打勾，整行可点，多选独立',
    '□ 选项A  □ 选项B /* 用文字方块，点不准也看不出选中 */',
    '.ck{ width:20px;height:20px;border:2px solid #ccc;border-radius:6px } .ck.on{ background:#C8442E;border-color:#C8442E }',
    ['整行可点，不只小方框', '选中态用填充+对勾明确', '多个独立，互不影响'],
    {'app': 'RN 用 Checkbox 或第三方，受控 checked/onChange', 'mini': '小程序 checkbox 组件，bindchange 拿选中值数组', 'web': 'input[type=checkbox]+label，CSS 自定义勾选样式'})

add('form-radio', 7, '几个圆圈，只能选其中一个', '单选框', 'Radio',
    '用下拉选性别等多一步，或用复选框导致能多选出错', '用圆形单选：同组互斥，选中一个自动取消其他，圆圈内点实心',
    '<select>性别</select> /* 单选却用下拉，多一步 */',
    'input[type=radio]{ } /* 同 name 互斥，选中内点实心圆 */',
    ['同组 name 一致实现互斥', '选中态圆内实心点', '选项文案整行可点'],
    {'app': 'RN Radio 组件或自定义，单选靠状态管理', 'mini': '小程序 radio 组件，同 name 自动互斥', 'web': 'input[type=radio] name 分组，CSS 自定义圆点'})

add('btn-primary', 8, '页面上最显眼那个能点的按钮，一般是主操作', '主按钮', 'Primary Button',
    '所有按钮长得一样，用户分不清哪个是主要操作', '主按钮用实心主色填充、字白，视觉权重最高；次要操作用描边次级按钮区分层级',
    '<button>保存</button><button>取消</button> /* 两个一样，主操作不突出 */',
    '.btn-primary{ background:#C8442E;color:#fff;font-weight:600 } .btn-secondary{ border:1px solid #ccc }',
    ['一个区域只一个主按钮，避免抢焦点', '按下态 scale(.96) 给反馈', '禁用态降透明度+not-allowed'],
    {'app': 'Button 组件 variant', 'mini': 'button 组件 type=primary', 'web': 'CSS 即可，按下态用 :active'})

add('btn-loading', 8, '点按钮之后转个圈，表示正在处理，别让用户以为卡了', '加载按钮', 'Loading Button',
    '点了按钮毫无反应，用户不知道在提交还是卡了，容易重复点', '点击后按钮进入 loading：禁用+转圈图标，1~2 秒处理完恢复，防止重复提交',
    "<button onclick='submit()'>提交</button> /* 点了没反馈，狂点十次 */",
    '.btn.loading{ pointer-events:none;opacity:.8 } .btn .spin{ animation:spin .7s linear infinite }',
    ['loading 时禁用防重复提交', '用 CSS 旋转圈而非 GIF', '处理完及时恢复并给结果提示'],
    {'app': 'ActivityIndicator', 'mini': 'loading 组件 / wx.showLoading', 'web': 'CSS 动画 + disabled'})

add('btn-disabled', 8, '不能点的按钮要变灰，让人知道现在不能操作', '禁用按钮', 'Disabled State',
    '禁用和正常按钮长得一样，用户还去点，困惑', '禁用态降低透明度+灰化+not-allowed 光标，与正常态明显区分',
    '.btn{ background:#C8442E } /* 禁用时还是红色实心，看不出不能点 */',
    '.btn:disabled{ opacity:.45;cursor:not-allowed;background:#C8442E }',
    ['禁用态别只改颜色，加 not-allowed', '不可用也要保证可读性', '满足即用条件后再启用'],
    {'app': 'RN disabled 属性+样式区分，禁止点击逻辑', 'mini': '小程序 button disabled 属性，禁用态样式单独写', 'web': 'button[disabled] 禁用交互，CSS 调灰减透明度'})

add('btn-group', 8, '一排按钮，选其中一个高亮，像日/周/月切换', '按钮组 / 分段控件', 'Button Group / Segmented',
    '三个独立按钮排一起，看不出是单选互斥，容易多选', '用分段控件：一组紧挨的按钮，选中项深色填充，其余浅色，互斥单选',
    '<button>日</button><button>周</button><button>月</button> /* 分开的三个按钮 */',
    '.seg{ border:1px solid #ccc;border-radius:9px;overflow:hidden } .seg span.on{ background:#1A1A1A;color:#fff }',
    ['选中项实心深色，其余描边', '分段间用分隔线或留白', '互斥单选，点击切换'],
    {'app': 'Segmented 控件', 'mini': '可通过 button 组合实现', 'web': 'flex + .on 切换'})

add('btn-icon', 8, '只有图标没有字的圆按钮，比如收藏爱心', '图标按钮', 'Icon Button',
    '图标按钮点了没任何状态变化，用户不知是否生效', '图标按钮用圆形描边容器，点击后填充主色+图标变白表示已激活（如收藏成功）',
    '<button>♥</button> /* 点了和没点一样 */',
    '.icon-btn{ width:40px;height:40px;border-radius:50%;border:1px solid #ccc } .icon-btn.on{ background:#C8442E;color:#fff }',
    ['图标按钮也要有激活态', '圆形容器点击区域≥44px', '加 title/aria-label 说明用途'],
    {'app': 'RN 用 TouchableOpacity 包 Icon 做成 IconButton', 'mini': '小程序用 icon 组件或 image，bindtap 触发', 'web': 'button 内嵌 svg/图标，给 aria-label 说明用途'})

add('modal-dialog', 9, '弹出一个框，让用户确认或填点东西再继续', '模态对话框', 'Modal / Dialog',
    '直接执行危险操作（删除等），没有确认，一错难挽回', '危险操作前弹模态框：半透明遮罩+居中卡片，明确「取消/确认」，点遮罩或取消可关',
    '直接 deleteItem() /* 没有确认，误删没后悔药 */',
    '.modal{ position:fixed;inset:0;background:rgba(0,0,0,.45) } .modal .card{ position:absolute;center }',
    ['危险操作必加确认弹窗', '遮罩点击 / ESC 可关闭', '按钮主次分明，确认用主色'],
    {'app': 'Alert/Dialog 组件', 'mini': 'modal 组件 / wx.showModal', 'web': 'fixed 遮罩 + center 卡片'})

add('modal-drawer', 9, '从屏幕一侧滑出一个面板，放筛选或菜单', '抽屉面板', 'Drawer / Side Panel',
    '筛选项全铺在页面上，内容多就又长又乱', '用侧边抽屉：点按钮从右/左滑出面板，遮罩点击关闭，内容多也不占主区',
    '<div>筛选：全部 / 已购 / 收藏 ...</div> /* 平铺占一整屏 */',
    '.drawer{ position:fixed;top:0;right:0;height:100%;transform:translateX(100%) } .drawer.on{ transform:none }',
    ['用 transform 滑入，性能优于 left', '打开锁背景滚动，关闭恢复', '遮罩点击或✕关闭'],
    {'app': 'RN Drawer/Modal 组件，自带手势与蒙层', 'mini': '小程序用 drawer 或自定义 view+transform 滑出', 'web': 'transform+transition 从侧边滑出，蒙层点击关闭'})

add('toast-msg', 9, '操作完在顶部或底部飘一条小提示，几秒自己消失', '轻提示 Toast', 'Toast / Snackbar',
    '操作完没有任何提示，用户不知道成功还是失败', '轻量提示：固定在屏幕底部/顶部，出现 2~3 秒自动消失，不打断操作',
    '/* 保存成功后页面静默无任何提示，用户怀疑没保存 */\nfunction save(){api.save(data)} /* 没弹 toast，也没 loading */',
    'function toast(msg){ /* 创建固定定位元素，2s 后移除 */ }',
    ['Toast 自动消失，不打断', '位置固定、层级最高', '成功/失败用不同色，可加图标'],
    {'app': 'RN 用 Toast 库（如 react-native-toast-message）', 'mini': '小程序 wx.showToast，注意 icon 与 duration', 'web': 'fixed 居中提示，2-3s 自动消失'})

add('popconfirm', 9, '点删除先弹个小气泡问确定吗，再执行', '气泡确认', 'Popconfirm',
    '一点就执行删除，没有二次确认，误触成本高', '在触发按钮旁弹一个小气泡确认框，点「取消/删除」才执行，减少误操作',
    "<button onclick='del()'>删除</button> /* 一点即删 */",
    '.pop{ position:absolute; } /* 按钮旁浮出小确认卡，确认才执行 */',
    ['比全屏弹窗轻，适合列表内操作', '气泡指向触发元素', '确认/取消两个明确按钮'],
    {'app': 'RN 用 Alert/dialog 或自定义气泡确认', 'mini': '小程序无原生 popconfirm，用弹窗或自定义气泡替代', 'web': '用 Popover/气泡组件，点确认才执行危险操作'})

add('skeleton', 9, '加载时先显示灰条占位，加载完再替换成真实内容', '骨架屏', 'Skeleton Screen',
    '加载时一片空白或一直转圈，用户以为坏了', '加载占位用骨架屏：灰条模拟内容形状，数据与布局先就位，加载完平滑替换',
    '/* 加载时整块空白，或无限 spinner */',
    '.skeleton{ background:linear-gradient(90deg,#eee,#f5f5f5,#eee);animation:shimmer }',
    ['骨架形状贴近真实布局', '用微光动画暗示加载中', '数据到后淡入替换，别闪'],
    {'app': 'RN 用 Skeleton 组件或 view+动画占位', 'mini': '小程序用 view 灰条+动画模拟骨架屏', 'web': 'CSS 渐变+shimmer 动画模拟灰条占位'})

add('anim-fade', 10, '元素出现或消失时用淡入淡出，别硬跳', '淡入淡出', 'Fade Transition',
    '元素瞬间出现/消失，生硬突兀', '进入/离开用 opacity 过渡（0→1 或 1→0）配合轻微位移，平滑自然',
    "el.style.display='block' /* 硬出现 */",
    '.fade{ opacity:0;transition:opacity .3s } .fade.on{ opacity:1 }',
    ['用 opacity + transition 而非 display 直切', '配合 4~8px 位移更生动', '尊重「减少动效」偏好'],
    {'app': 'RN 用 Animated/Reanimated 做 opacity 动画', 'mini': 'wxss transition opacity 或 WXS 做淡入淡出', 'web': 'opacity 过渡实现淡入淡出，transition 控制时长'})

add('anim-flip', 10, '卡片翻个面看背面，像翻牌', '卡片翻转', 'Card Flip / 3D Flip',
    '正反面用两个页面跳转切换，割裂', '用 3D 翻转：容器 preserve-3d，rotateY(180deg) 翻面，正反面都在同一卡',
    "/* 点正面直接跳转到另一个页面看背面，割裂感强 */\n.front{onclick:go('/back')} /* 离开当前卡片上下文 */",
    '.flip{ transform-style:preserve-3d;transition:transform .5s } .flip.on{ transform:rotateY(180deg) }',
    ['父容器 preserve-3d，面 backface-visibility:hidden', '用 rotateY 翻转', '过渡 .4~.6s 自然'],
    {'app': 'RN 用 rotateY 动画或 react-native-flip-card', 'mini': '小程序用 transform:rotateY+preserve-3d 翻牌', 'web': 'transform:rotateY(180deg)+transform-style:preserve-3d'})

add('anim-list', 10, '列表新增项时一个一个淡入进来，好看', '列表入场过渡', 'List Stagger Animation',
    '列表整块刷新，没有过渡，显得卡', '新项进入时逐条淡入+轻微位移，用 transition-delay 做错落感',
    'list.push(item); render() /* 整块重绘，无过渡 */',
    '.li{ opacity:0;transform:translateX(-8px);transition:.3s } .li.on{ opacity:1;transform:none }',
    ['用 transition-delay 做错落感', '位移幅度小（6~10px）', '离场也可做淡出'],
    {'app': 'LayoutAnimation', 'mini': 'wx.createAnimation 逐条', 'web': 'CSS transition + 错落 delay'})

add('anim-progress', 10, '加载或上传时有个进度条跑动，告诉还要多久', '进度条', 'Progress Bar',
    '没有进度反馈，用户不知还要等多久，容易退出', '用进度条：背景槽 + 填充条，width 从 0 过渡到目标，明确进度百分比',
    '/* 一直转圈 spinner，没有真实进度，用户不知还要等多久 */\n.loading{animation:spin 1s infinite} /* 永远 100% 不明 */',
    '.bar{ background:#eee } .bar .fill{ width:0;transition:width 1.4s } .bar.run .fill{ width:100% }',
    ['进度条比无限圈更有确定感', '用 width/transform 过渡', '完成态给成功色'],
    {'app': 'RN 用 ProgressView/自定义 view width 动画', 'mini': '小程序 progress 组件，percent 控制进度', 'web': '用 width 百分比或 progress 元素做进度条'})

add('anim-tab', 10, '多个内容块用标签页切换，点哪个显示哪个', '标签页切换', 'Tabs Transition',
    '多个内容堆在一起全显示，或每次跳转新页', '用 Tab 切换：标题栏选中项高亮，对应面板淡入，内容互斥显示',
    '/* 多块内容全堆在一屏，或点一下跳一个页面 */\n<div class="all">区块A 区块B 区块C...（全平铺无切换）</div>',
    '.tab.on{ background:#1A1A1A;color:#fff } .panel{ display:none } .panel.on{ display:block }',
    ['选中 Tab 高亮，面板互斥显示', '切换可加淡入增强反馈', '移动端 Tab 可横滑'],
    {'app': 'TabView / Segmented', 'mini': 'swiper / tab 组件', 'web': 'display 切换 + 淡入'})

add('card', 1, '把一段内容（标题、图、说明、操作）装进一个有边界、有留白的容器里，让它像一张卡片', '内容卡片', 'Card',
    '卡片没有留白、边框太重、内部元素挤在一起，或阴影过重像浮窗', '卡片用圆角 + 浅边框 + 适度内边距，内容分区清晰；阴影只在悬浮时加深',
    '/* 所有内容平铺一屏无分组，信息密度高到看不懂 */\n<div class="wall">标题 图 文字 按钮 标题 图 文字...（无卡片边界）</div>',
    '.card{ border:1px solid #ECE8E1;border-radius:14px;padding:16px;background:#fff } .card:hover{ box-shadow:0 6px 18px rgba(0,0,0,.08) }',
    ['留白比内容更重要，内边距给足', '阴影克制，别像浮窗', '圆角 10~16px 更亲和'],
    {'app': 'Card / UIView 圆角阴影', 'mini': 'view + CSS 圆角阴影', 'web': 'border + border-radius + 克制阴影'})

add('hover-lift', 10, '让卡片在鼠标悬停（放上鼠标）时轻轻向上浮起一点，并加一点阴影，给出『可以点、有反馈』的感觉', '悬停动效', 'Hover / hover-lift',
    'hover 时只改颜色不加位移，反馈太弱；或位移过大、没有 transition 导致生硬闪烁', '用 :hover 触发 transform: translateY(-4px) 配合 box-shadow 增强，并加 transition 让变化平滑；移动端无 hover 用 :active 兜底',
    'a:hover{ background:#eee } /* 只变色，反馈弱 */',
    '.card{ transition:transform .2s,box-shadow .2s } .card:hover{ transform:translateY(-4px);box-shadow:0 10px 24px rgba(0,0,0,.12) }',
    ['位移幅度小（4~6px）才高级', '必须加 transition 才平滑', '移动端用 :active 替代 hover'],
    {'app': 'RN 用 Pressable pressed 态模拟悬停高亮', 'mini': '小程序 hover-class 加 translateY+阴影', 'web': 'hover 时 translateY(-4px)+阴影，给出浮起感'})

add('carousel', 10, '多张图片或内容可以横向滑动、或自动轮播切换', '轮播图', 'Carousel / Swiper',
    '轮播无限循环没停顿、自动播放太花哨、没有指示点、滑动和点击冲突', '提供指示点 + 左右切换，自动播放留足停留时间，移动端支持手势滑动',
    '/* 多张图直接堆在一起重叠，只能手动一张张翻 */\n<div><img src="a.jpg"><img src="b.jpg"><img src="c.jpg">（全叠一起）</div>',
    '.swiper{ overflow:hidden } .swiper .track{ display:flex;transition:transform .3s } .dot.on{ background:#C8442E }',
    ['指示点告诉用户有几张', '自动播放停留 3~5s 别太急', '移动端手势滑动优先'],
    {'app': 'RN 用横向 ScrollView/第三方 Swiper', 'mini': '小程序 swiper 组件，autoplay+指示点开箱即用', 'web': 'flex 轨道+transform 位移，手势+指示点'})

FORMULA_SVG = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>'

VD = {
  # 导航
  "nav-sticky": (
    "<div class='m-phone m-scroll'><div class='m-bar'>导航栏跟着滚走了</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>",
    "<div class='m-phone m-scroll'><div class='m-bar m-sticky'>导航吸顶 · 上下滚动看它停住</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>"
  ),
  "nav-sidebar": (
    "<div class='m-phone'><div class='m-bar'>≡ 我的网站</div><div class='m-row'><div class='m-side'><i class='on'></i><i></i><i></i><i></i></div><div class='m-body'><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div></div></div>",
    "<div class='m-phone'><div class='m-bar m-act' data-toggle='v-sb'>≡ 我的网站</div><div class='m-row'><div class='m-side v-side'><i class='on'></i><i></i><i></i><i></i></div><div class='m-body'><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div></div></div>"
  ),
  "nav-crumb": (
    "<div class='m-phone'><div class='m-crumb'>首页 / 数码 / <b>详情</b></div><div class='m-body'><div class='m-line'></div><div class='m-line'></div></div></div>",
    "<div class='m-phone'><div class='m-crumb v-crumb'>首页 / 数码 / <b>详情</b></div><div class='m-body'><div class='m-line'></div><div class='m-line'></div></div></div>"
  ),
  "nav-dropdown": (
    "<div class='m-phone'><div style='padding:10px'><div class='m-line'></div><div class='m-line' style='width:60%'></div><div class='m-line' style='width:70%'></div></div></div>",
    "<div class='m-phone'><div style='padding:10px'><div class='m-dd m-act' data-toggle='v-sub'>产品 ▾<div class='m-sub v-sub'><span>子产品A</span><span>子产品B</span><span>子产品C</span></div></div></div></div>"
  ),
  "nav-mega": (
    "<div class='m-phone'><div style='padding:10px'><div class='m-dd' style='width:120px'>分类<div class='m-sub' style='display:block;width:110px'><span>小</span><span>小</span><span>小</span></div></div></div></div>",
    "<div class='m-phone'><div style='padding:10px'><div class='m-act' style='display:inline-block;padding:7px 10px;background:#faf8f4;border:1px solid var(--line-2);border-radius:8px;font-size:11px;width:120px' data-toggle='v-mega'>商品分类 ▾</div><div class='m-mega v-mega'><b>商品分类</b><span>手机</span><span>电脑</span><span>家电</span><span>服饰</span><span>美妆</span><span>食品</span></div></div></div>"
  ),
  "nav-hamburger": (
    "<div class='m-phone'><div class='m-bar m-dead'>☰ 点了没反应</div><div class='m-body'><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div></div>",
    "<div class='m-phone'><div class='m-bar m-act' data-toggle='v-ham'>☰</div><div class='m-drawer v-drawer v-ham'><span>首页</span><span>分类</span><span>我的</span><span>设置</span></div><div class='m-body'><div class='m-line'></div><div class='m-line'></div></div><div class='m-overlay v-ov v-ham'><span>首页</span><span>分类</span><span>我的</span><span>✕ 关闭</span></div></div>"
  ),
  "nav-overlay": (
    "<div class='m-phone'><div class='m-bar'>菜单</div><div class='m-body'><div class='m-line'></div><div class='m-line'></div></div></div>",
    "<div class='m-phone'><div class='m-bar m-act' data-toggle='v-ovl'>菜单</div><div class='m-body'><div class='m-line'></div><div class='m-line'></div></div><div class='m-overlay v-ov2 v-ovl'><span>首页</span><span>分类</span><span>我的</span><span class='m-act' data-close='v-ovl'>✕ 关闭</span></div></div>"
  ),
  "nav-anchor": (
    "<div class='m-phone'><div class='m-body'><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div></div>",
    "<div class='m-phone'><div class='m-body'><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div><div class='m-anchor v-anchor'><i class='on'></i><i></i><i></i></div></div>"
  ),
  "nav-shrink": (
    "<div class='m-phone m-scroll'><div class='m-bar m-big'>LOGO 大标题 搜索框</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>",
    "<div class='m-phone m-scroll'><div class='m-bar m-big v-shrink'>LOGO 大标题 搜索框</div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div><div class='m-line'></div></div>"
  ),
  # 布局与对齐
  "center-icon": (
    "<span style='font-size:24px;line-height:1;vertical-align:top'>🔍</span> <span style='font-size:14px;vertical-align:top;color:#8f2b20'>搜索</span>",
    "<span style='display:inline-flex;align-items:center;gap:7px'><span style='font-size:24px;line-height:1'>🔍</span><span style='font-size:14px;color:#155e3c'>搜索</span></span>"
  ),
  "center-both": (
    "<div style='width:100%;height:56px;border:1px solid #d9d4ca;border-radius:6px;position:relative'><div style='position:absolute;right:6px;bottom:6px;width:30px;height:22px;background:#C0392B;border-radius:4px'></div></div>",
    "<div style='width:100%;height:56px;border:1px solid #d9d4ca;border-radius:6px;display:flex;align-items:center;justify-content:center'><div style='width:30px;height:22px;background:#1C7A4E;border-radius:4px'></div></div>"
  ),
  "equal-width": (
    "<div style='font-size:0'><span style='display:inline-block;width:30%;height:22px;background:#E7C9C4;border-radius:4px;margin:1px'></span><span style='display:inline-block;width:30%;height:22px;background:#E7C9C4;border-radius:4px;margin:1px'></span><span style='display:inline-block;width:30%;height:22px;background:#E7C9C4;border-radius:4px;margin:1px'></span><span style='display:inline-block;width:30%;height:22px;background:#E7C9C4;border-radius:4px;margin:1px'></span></div>",
    "<div style='display:flex;gap:6px'><span style='flex:1;height:22px;background:#BFE0CE;border-radius:4px'></span><span style='flex:1;height:22px;background:#BFE0CE;border-radius:4px'></span><span style='flex:1;height:22px;background:#BFE0CE;border-radius:4px'></span><span style='flex:1;height:22px;background:#BFE0CE;border-radius:4px'></span></div>"
  ),
  "space-between": (
    "<div style='display:flex;gap:6px'><span style='font-size:13px;color:#5B5852'>标题</span><span style='font-size:12px;background:#E7C9C4;color:#8f2b20;padding:3px 9px;border-radius:5px'>按钮</span></div>",
    "<div style='display:flex;justify-content:space-between;align-items:center'><span style='font-size:13px;color:#5B5852'>标题</span><span style='font-size:12px;background:#BFE0CE;color:#155e3c;padding:3px 9px;border-radius:5px'>按钮</span></div>"
  ),
  "ellipsis": (
    "<div style='width:100%;overflow:hidden;white-space:nowrap;background:#E7C9C4;border-radius:5px;padding:5px 8px;font-size:12px;color:#8f2b20'>这是一段特别特别长的文字被硬生生切掉没省略号</div>",
    "<div style='width:100%;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;background:#BFE0CE;border-radius:5px;padding:5px 8px;font-size:12px;color:#155e3c'>这是一段特别特别长的文字被硬生生切掉没省略号</div>"
  ),
  "sticky-top": (
    "<div style='height:58px;position:relative'><div style='background:#E7C9C4;color:#8f2b20;font-size:10px;padding:3px 6px;border-radius:4px'>顶栏脱离流↓</div><div style='background:#F3F0EA;font-size:10px;color:#938E85;padding:3px 6px;margin-top:2px'>正文被遮住</div></div>",
    "<div style='height:58px'><div style='background:#BFE0CE;color:#155e3c;font-size:10px;padding:3px 6px;border-radius:4px'>顶栏吸顶</div><div style='background:#F3F0EA;font-size:10px;color:#938E85;padding:3px 6px;margin-top:2px'>正文照常排列</div></div>"
  ),
  "equal-height": (
    "<div style='display:flex;gap:6px;align-items:flex-start'><div style='width:46px;height:34px;background:#E7C9C4;border-radius:5px;font-size:10px;color:#8f2b20;padding:4px'>短内容</div><div style='width:46px;height:54px;background:#E7C9C4;border-radius:5px;font-size:10px;color:#8f2b20;padding:4px'>长内容把卡片撑高</div></div>",
    "<div style='display:flex;gap:6px;align-items:stretch'><div style='flex:1;background:#BFE0CE;border-radius:5px;font-size:10px;color:#155e3c;padding:4px'>短内容</div><div style='flex:1;background:#BFE0CE;border-radius:5px;font-size:10px;color:#155e3c;padding:4px'>长内容</div></div>"
  ),
  "inline-gap": (
    "<div style='font-size:0'><span style='display:inline-block;background:#E7C9C4;color:#8f2b20;font-size:11px;padding:3px 7px;border-radius:4px'>甲</span> <span style='display:inline-block;background:#E7C9C4;color:#8f2b20;font-size:11px;padding:3px 7px;border-radius:4px'>乙</span></div><div style='font-size:9px;color:#938E85;margin-top:4px'>标签间有莫名缝隙</div>",
    "<div style='display:flex;gap:6px'><span style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:3px 7px;border-radius:4px'>甲</span><span style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:3px 7px;border-radius:4px'>乙</span></div><div style='font-size:9px;color:#938E85;margin-top:4px'>flex 无换行缝隙</div>"
  ),
  "neg-margin": (
    "<div style='position:relative;height:46px'><div style='background:#E7C9C4;color:#8f2b20;font-size:10px;padding:4px 7px;border-radius:4px;position:absolute;left:0;top:18px'>用负 margin 硬拉</div><div style='background:#F3F0EA;font-size:10px;color:#938E85;padding:4px 7px;border-radius:4px;position:absolute;left:82px;top:0'>被带偏</div></div>",
    "<div style='display:flex;align-items:center;gap:8px'><div style='background:#BFE0CE;color:#155e3c;font-size:10px;padding:4px 7px;border-radius:4px'>对齐</div><div style='background:#BFE0CE;color:#155e3c;font-size:10px;padding:4px 7px;border-radius:4px'>对齐</div></div>"
  ),
  "flex-wrap": (
    "<div style='display:flex'><span style='background:#E7C9C4;color:#8f2b20;font-size:11px;padding:4px 8px;border-radius:4px;margin:2px'>标签一</span><span style='background:#E7C9C4;color:#8f2b20;font-size:11px;padding:4px 8px;border-radius:4px;margin:2px'>标签二</span><span style='background:#E7C9C4;color:#8f2b20;font-size:11px;padding:4px 8px;border-radius:4px;margin:2px'>标签三</span><span style='background:#E7C9C4;color:#8f2b20;font-size:11px;padding:4px 8px;border-radius:4px;margin:2px'>标签四被压扁</span></div>",
    "<div style='display:flex;flex-wrap:wrap;gap:6px'><span style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:4px 8px;border-radius:4px'>标签一</span><span style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:4px 8px;border-radius:4px'>标签二</span><span style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:4px 8px;border-radius:4px'>标签三</span><span style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:4px 8px;border-radius:4px'>标签四换行</span></div>"
  ),
  "two-col": (
    "<div style='font-size:0'><span style='display:inline-block;width:40%;height:40px;background:#E7C9C4;border-radius:5px'></span><span style='display:inline-block;height:40px;background:#E7C9C4;border-radius:5px;margin-left:120px;width:30%'></span></div><div style='font-size:9px;color:#938E85;margin-top:4px'>固定宽算错就溢出</div>",
    "<div style='display:flex;gap:8px'><div style='width:46px;flex:none;height:40px;background:#BFE0CE;border-radius:5px'></div><div style='flex:1;height:40px;background:#BFE0CE;border-radius:5px'></div></div>"
  ),
  "baseline": (
    "<div><span style='font-size:22px;vertical-align:middle;color:#8f2b20'>大</span><span style='font-size:12px;vertical-align:middle;color:#8f2b20'>小字用 middle 反而错位</span></div>",
    "<div><span style='font-size:22px;vertical-align:baseline;color:#155e3c'>大</span><span style='font-size:12px;vertical-align:baseline;color:#155e3c'>小字 baseline 对齐</span></div>"
  ),
  "card": (
    "<div style='background:#f3f1ed;border-radius:0;padding:6px;font-size:12px;line-height:1.6;color:var(--ink-3)'>内容标题<br>这是直接摊开的文字内容，没有边界、没有留白，一眼看不出哪里是卡片。</div>",
    "<div style='border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;box-shadow:0 2px 8px rgba(60,50,40,.06)'><div style='height:52px;border-radius:6px;background:linear-gradient(135deg,#bfe0ce,#a9d3c4)'></div><div style='font-size:13px;font-weight:700;color:var(--ink);margin-top:8px'>内容卡片</div><div style='font-size:12px;color:var(--ink-2);margin-top:3px;line-height:1.5'>有边界、有留白、有阴影，一眼就是一张卡片</div><div style='margin-top:8px;font-size:12px;color:var(--accent);font-weight:700'>查看详情 →</div></div>"
  ),
  # 尺寸与排版
  "clamp": (
    "<div style='font-size:30px;color:#8f2b20;font-weight:700'>标题</div><div style='font-size:9px;color:#938E85'>写死 30px 小屏巨大</div>",
    "<div style='font-size:clamp(20px,5vw,30px);color:#155e3c;font-weight:700'>标题</div><div style='font-size:9px;color:#938E85'>随屏平滑变化</div>"
  ),
  "hairline": (
    "<div style='border-bottom:2px solid #C0392B;padding-bottom:3px;font-size:11px;color:#8f2b20'>1px 高清屏变粗</div>",
    "<div style='position:relative;padding-bottom:3px;font-size:11px;color:#155e3c'>细线</div><div style='position:absolute;left:0;right:0;bottom:0;border-bottom:1px solid #1C7A4E;transform:scaleY(.5);transform-origin:0 100%'></div>"
  ),
  "line-height": (
    "<div style='line-height:24px;font-size:18px;color:#8f2b20'>行距写死<br>换字号就挤</div>",
    "<div style='line-height:1.6;font-size:16px;color:#155e3c'>行距用倍数<br>永远协调</div>"
  ),
  "font-weight": (
    "<div style='font-weight:400;color:#8f2b20'>标题与正文一样重</div><div style='font-weight:400;color:#938E85;font-size:11px'>分不清层级</div>",
    "<div style='font-weight:700;color:#155e3c'>标题加粗</div><div style='font-weight:400;color:#938E85;font-size:11px'>正文常规</div>"
  ),
  "letter-spacing": (
    "<div style='padding:0 4px;color:#8f2b20;font-weight:700;font-size:15px'>标题间距凑</div>",
    "<div style='letter-spacing:2px;color:#155e3c;font-weight:700;font-size:15px'>标题拉开间距</div>"
  ),
  "web-font": (
    "<div style='color:#8f2b20;font-size:11px'>整包字体加载<br>首屏白屏</div>",
    "<div style='color:#155e3c;font-size:11px'>woff2 + swap<br>即显即载</div>"
  ),
  "text-indent": (
    "<div style='padding-left:2em;color:#8f2b20;font-size:11px'>整段缩进<br>不是首行</div>",
    "<div style='text-indent:2em;color:#155e3c;font-size:11px'>仅首行缩进<br>两字符</div>"
  ),
  "justify": (
    "<div style='text-align:justify;color:#8f2b20;font-size:10px;width:100%'>英文单词间距被拉得忽大忽小很难看</div>",
    "<div style='text-align:justify;text-justify:inter-character;color:#155e3c;font-size:10px;width:100%'>中文按字符均匀对齐</div>"
  ),
  # 定位与层级
  "z-index": (
    "<div style='position:relative;height:50px'><div style='position:absolute;left:0;top:14px;width:60px;height:22px;background:#E7C9C4;border-radius:4px;z-index:1'></div><div style='position:absolute;left:30px;top:6px;width:60px;height:22px;background:#C0392B;border-radius:4px;z-index:2'></div></div><div style='font-size:9px;color:#938E85'>弹窗被按钮盖住</div>",
    "<div style='position:relative;height:50px'><div style='position:absolute;left:0;top:6px;width:60px;height:22px;background:#1C7A4E;border-radius:4px;z-index:10'></div><div style='position:absolute;left:30px;top:14px;width:60px;height:22px;background:#BFE0CE;border-radius:4px;z-index:1'></div></div><div style='font-size:9px;color:#938E85'>弹窗盖在最上</div>"
  ),
  "overlay": (
    "<div style='position:relative;height:50px;border:1px dashed #E7C9C4;border-radius:5px'><div style='position:absolute;right:6px;top:6px;width:26px;height:18px;background:#C0392B;border-radius:3px'></div><div style='font-size:9px;color:#938E85;padding:4px'>无蒙版 点空白关不掉</div></div>",
    "<div style='position:relative;height:50px;border:1px dashed #BFE0CE;border-radius:5px'><div style='position:absolute;inset:0;background:rgba(20,18,15,.35);border-radius:5px'></div><div style='position:absolute;right:6px;top:6px;width:26px;height:18px;background:#1C7A4E;border-radius:3px'></div></div>"
  ),
  "fixed-center": (
    "<div style='position:relative;height:50px;border:1px solid #E7C9C4;border-radius:5px'><div style='position:absolute;top:50%;left:50%;width:26px;height:18px;background:#C0392B;border-radius:3px'></div></div>",
    "<div style='position:relative;height:50px;border:1px solid #BFE0CE;border-radius:5px'><div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:26px;height:18px;background:#1C7A4E;border-radius:3px'></div></div>"
  ),
  "stacking": (
    "<div style='position:relative;height:50px'><div style='position:absolute;left:0;top:0;width:50px;height:30px;background:#E7C9C4;border-radius:4px;z-index:5'></div><div style='position:absolute;left:20px;top:8px;width:50px;height:30px;background:#C0392B;border-radius:4px;z-index:9'></div></div><div style='font-size:9px;color:#938E85'>父级新上下文隔离比较</div>",
    "<div style='position:relative;height:50px'><div style='position:absolute;left:0;top:0;width:50px;height:30px;background:#BFE0CE;border-radius:4px;z-index:9'></div><div style='position:absolute;left:20px;top:8px;width:50px;height:30px;background:#1C7A4E;border-radius:4px;z-index:5'></div></div><div style='font-size:9px;color:#938E85'>理清上下文再调层级</div>"
  ),
  "relative": (
    "<div style='height:46px;position:relative'><div style='background:#E7C9C4;color:#8f2b20;font-size:10px;padding:3px 6px;border-radius:4px'>用 margin 挪</div><div style='background:#F3F0EA;color:#938E85;font-size:10px;padding:3px 6px;border-radius:4px'>后面被带着动</div></div>",
    "<div style='height:46px;position:relative'><div style='background:#BFE0CE;color:#155e3c;font-size:10px;padding:3px 6px;border-radius:4px'>relative 只挪自己</div><div style='background:#F3F0EA;color:#938E85;font-size:10px;padding:3px 6px;border-radius:4px;margin-top:6px'>别人不动</div></div>"
  ),
  "absolute": (
    "<div style='height:48px;border:1px solid #E7C9C4;border-radius:5px'><div style='position:absolute;left:0;top:0;width:40px;height:18px;background:#C0392B;border-radius:3px'></div></div><div style='font-size:9px;color:#938E85'>父级没定位 跑到角落</div>",
    "<div style='height:48px;border:1px solid #BFE0CE;border-radius:5px;position:relative'><div style='position:absolute;left:6px;top:6px;width:40px;height:18px;background:#1C7A4E;border-radius:3px'></div></div><div style='font-size:9px;color:#938E85'>父级 relative 当锚</div>"
  ),
  "pseudo": (
    "<div style='font-size:11px;color:#8f2b20'>多写一个空标签<br>只为装饰</div>",
    "<div style='position:relative;font-size:11px;color:#155e3c;padding-left:12px'>用 ::before 装饰<span style='position:absolute;left:0;top:4px;width:6px;height:6px;border-radius:50%;background:#1C7A4E'></span></div>"
  ),
  "scroll-lock": (
    "<div style='height:50px;overflow:hidden;font-size:9px;color:#938E85;background:#E7C9C4;border-radius:5px;padding:4px'>弹窗开着<br>背景还在滚</div>",
    "<div style='height:50px;overflow:hidden;font-size:9px;color:#155e3c;background:#BFE0CE;border-radius:5px;padding:4px'>弹窗开着<br>背景已锁住</div>"
  ),
  "fixed-bottom": (
    "<div style='position:relative;height:50px;border:1px solid #E7C9C4;border-radius:5px'><div style='position:absolute;left:0;right:0;bottom:0;height:16px;background:#C0392B'></div><div style='position:absolute;right:6px;bottom:2px;font-size:8px;color:#fff'>被小黑条挡</div></div>",
    "<div style='position:relative;height:50px;border:1px solid #BFE0CE;border-radius:5px;padding-bottom:8px'><div style='position:absolute;left:0;right:0;bottom:8px;height:14px;background:#1C7A4E'></div></div>"
  ),
  # 交互与动效
  "hover": (
    "<div style='display:flex;gap:8px'><div style='background:#E7C9C4;color:#8f2b20;font-size:11px;padding:5px 10px;border-radius:5px'>移上去瞬变</div></div>",
    "<div style='display:flex;gap:8px'><div style='background:#BFE0CE;color:#155e3c;font-size:11px;padding:5px 10px;border-radius:5px;transition:background .2s'>平滑过渡</div></div>"
  ),
  "focus-visible": (
    "<div style='border:1px solid #C0392B;border-radius:5px;padding:4px 8px;font-size:11px;color:#8f2b20'>输入框无焦点提示</div>",
    "<div style='border:1px solid #1C7A4E;border-radius:5px;padding:4px 8px;font-size:11px;color:#155e3c;outline:2px solid #1C7A4E;outline-offset:2px'>键盘聚焦有轮廓</div>"
  ),
  "disabled": (
    "<div style='background:#C0392B;color:#fff;font-size:11px;padding:5px 12px;border-radius:5px'>按钮(看不出禁用)</div>",
    "<div style='background:#C0392B;color:#fff;font-size:11px;padding:5px 12px;border-radius:5px;opacity:.45;cursor:not-allowed'>按钮(变灰禁用)</div>"
  ),
  "transition": (
    "<div style='display:flex;gap:8px'><div style='width:22px;height:22px;background:#E7C9C4;border-radius:4px'></div><div style='width:44px;height:22px;background:#8f2b20;border-radius:4px;font-size:9px;color:#fff;text-align:center;padding-top:3px'>瞬变</div></div>",
    "<div style='display:flex;gap:8px'><div style='width:22px;height:22px;background:#BFE0CE;border-radius:4px;transition:width .3s'></div><div style='width:44px;height:22px;background:#1C7A4E;border-radius:4px;font-size:9px;color:#fff;text-align:center;padding-top:3px'>平滑</div></div>"
  ),
  "transform": (
    "<div style='position:relative;height:40px'><div style='position:absolute;left:0;top:14px;width:22px;height:18px;background:#E7C9C4;border-radius:3px'></div><div style='position:absolute;left:24px;top:0;width:22px;height:18px;background:#8f2b20;border-radius:3px;font-size:8px;color:#fff;text-align:center;padding-top:2px'>改left重排</div></div>",
    "<div style='position:relative;height:40px'><div style='position:absolute;left:0;top:11px;width:22px;height:18px;background:#BFE0CE;border-radius:3px'></div><div style='position:absolute;left:0;top:11px;width:22px;height:18px;background:#1C7A4E;border-radius:3px;transform:translateX(24px);font-size:8px;color:#fff;text-align:center;padding-top:2px'>translate合成</div></div>"
  ),
  "easing": (
    "<div style='width:70px;height:8px;background:#E7C9C4;border-radius:4px;position:relative'><div style='position:absolute;left:0;top:0;width:18px;height:8px;background:#8f2b20;border-radius:4px'></div></div><div style='font-size:9px;color:#938E85;margin-top:3px'>linear 匀速生硬</div>",
    "<div style='width:70px;height:8px;background:#BFE0CE;border-radius:4px;position:relative'><div style='position:absolute;left:0;top:0;width:18px;height:8px;background:#1C7A4E;border-radius:4px;transform:translateX(40px)'></div></div><div style='font-size:9px;color:#938E85;margin-top:3px'>缓动有节奏</div>"
  ),
  "debounce": (
    "<div style='font-size:9px;color:#8f2b20'>每敲一字发请求</div><div style='display:flex;gap:2px;margin-top:4px'><span style='width:7px;height:7px;background:#C0392B;border-radius:50%'></span><span style='width:7px;height:7px;background:#C0392B;border-radius:50%'></span><span style='width:7px;height:7px;background:#C0392B;border-radius:50%'></span><span style='width:7px;height:7px;background:#C0392B;border-radius:50%'></span></div>",
    "<div style='font-size:9px;color:#155e3c'>停手才发一次</div><div style='display:flex;gap:2px;margin-top:4px'><span style='width:7px;height:7px;background:#BFE0CE;border-radius:50%'></span><span style='width:7px;height:7px;background:#BFE0CE;border-radius:50%'></span><span style='width:14px;height:7px;background:#1C7A4E;border-radius:4px'></span></div>"
  ),
  "throttle": (
    "<div style='font-size:9px;color:#8f2b20'>滚动每帧都算</div><div style='display:flex;gap:1px;margin-top:4px;flex-wrap:wrap;width:80px'><span style='width:5px;height:5px;background:#C0392B;border-radius:50%'></span><span style='width:5px;height:5px;background:#C0392B;border-radius:50%'></span><span style='width:5px;height:5px;background:#C0392B;border-radius:50%'></span><span style='width:5px;height:5px;background:#C0392B;border-radius:50%'></span><span style='width:5px;height:5px;background:#C0392B;border-radius:50%'></span></div>",
    "<div style='font-size:9px;color:#155e3c'>每隔 N ms 一次</div><div style='display:flex;gap:6px;margin-top:4px'><span style='width:6px;height:6px;background:#1C7A4E;border-radius:50%'></span><span style='width:6px;height:6px;background:#1C7A4E;border-radius:50%'></span><span style='width:6px;height:6px;background:#1C7A4E;border-radius:50%'></span></div>"
  ),
  "active": (
    "<div style='background:#E7C9C4;color:#8f2b20;font-size:11px;padding:5px 12px;border-radius:5px'>按下无反馈</div>",
    "<div style='background:#1C7A4E;color:#fff;font-size:11px;padding:5px 12px;border-radius:5px;transform:scale(.96)'>按下有反馈</div>"
  ),
  # 响应式与适配
  "viewport": (
    "<div style='width:120px;height:44px;border:1px solid #E7C9C4;border-radius:5px;transform:scale(.6);transform-origin:left top;font-size:8px;color:#938E85;padding:3px'>没 viewport 被缩小</div>",
    "<div style='width:120px;height:44px;border:1px solid #BFE0CE;border-radius:5px;font-size:10px;color:#155e3c;padding:3px'>按设备宽度显示</div>"
  ),
  "safe-area": (
    "<div style='position:relative;width:120px;height:46px;background:#E7C9C4;border-radius:6px'><div style='position:absolute;left:0;right:0;top:0;height:9px;background:#C0392B'></div><div style='font-size:8px;color:#8f2b20;padding-top:12px;text-align:center'>内容被刘海切</div></div>",
    "<div style='position:relative;width:120px;height:46px;background:#BFE0CE;border-radius:6px;padding-top:12px'><div style='font-size:8px;color:#155e3c;text-align:center'>留安全区不挡</div></div>"
  ),
  "media": (
    "<div style='width:120px;height:44px;border:1px solid #E7C9C4;border-radius:5px;font-size:8px;color:#938E85;padding:3px'>一套布局硬套大小屏</div>",
    "<div style='width:120px;height:44px;border:1px solid #BFE0CE;border-radius:5px;font-size:10px;color:#155e3c;padding:3px'>按断点切换布局</div>"
  ),
  "autofit": (
    "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:3px;width:120px'><span style='height:14px;background:#E7C9C4;border-radius:3px'></span><span style='height:14px;background:#E7C9C4;border-radius:3px'></span><span style='height:14px;background:#E7C9C4;border-radius:3px'></span><span style='height:14px;background:#E7C9C4;border-radius:3px'></span></div><div style='font-size:8px;color:#938E85'>手机挤 4 列</div>",
    "<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(28px,1fr));gap:3px;width:120px'><span style='height:14px;background:#BFE0CE;border-radius:3px'></span><span style='height:14px;background:#BFE0CE;border-radius:3px'></span><span style='height:14px;background:#BFE0CE;border-radius:3px'></span></div><div style='font-size:8px;color:#938E85'>自动列数</div>"
  ),
  "vwvh": (
    "<div style='width:120px;height:50px;border:1px solid #E7C9C4;border-radius:5px'><div style='height:46px;background:#E7C9C4'></div></div><div style='font-size:8px;color:#938E85'>写死高度比例乱</div>",
    "<div style='width:120px;height:50px;border:1px solid #BFE0CE;border-radius:5px'><div style='height:60%;background:#BFE0CE'></div></div><div style='font-size:8px;color:#938E85'>比例随屏</div>"
  ),
  "dpr": (
    "<div style='width:54px;height:40px;background:repeating-linear-gradient(45deg,#C0392B,#C0392B 3px,#E7C9C4 3px,#E7C9C4 6px);border-radius:4px'></div><div style='font-size:8px;color:#8f2b20'>单图发虚</div>",
    "<div style='width:54px;height:40px;background:#1C7A4E;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:8px;color:#fff'>矢量清晰</div>"
  ),
  "orientation": (
    "<div style='width:120px;height:40px;border:1px solid #E7C9C4;border-radius:5px;font-size:8px;color:#938E85;padding:3px'>横竖同布局被拉变形</div>",
    "<div style='width:120px;height:40px;border:1px solid #BFE0CE;border-radius:5px;font-size:9px;color:#155e3c;padding:3px'>横竖分别适配</div>"
  ),
  "tablet": (
    "<div style='width:120px;height:44px;border:1px solid #E7C9C4;border-radius:5px;font-size:8px;color:#938E85;padding:3px'>平板夹中间太空</div>",
    "<div style='width:120px;height:44px;border:1px solid #BFE0CE;border-radius:5px;font-size:9px;color:#155e3c;padding:3px'>加平板断点填满</div>"
  ),
  # 性能与无障碍
  "reflow": (
    "<div style='font-size:9px;color:#8f2b20'>循环读写布局<br>卡顿</div><div style='width:60px;height:6px;background:#C0392B;border-radius:3px;margin-top:4px'></div>",
    "<div style='font-size:9px;color:#155e3c'>transform 合成<br>流畅</div><div style='width:60px;height:6px;background:#1C7A4E;border-radius:3px;margin-top:4px'></div>"
  ),
  "will-change": (
    "<div style='font-size:9px;color:#8f2b20'>全局加 will-change<br>内存爆炸</div><div style='display:flex;gap:2px;margin-top:4px'><span style='width:8px;height:8px;background:#C0392B;border-radius:2px'></span><span style='width:8px;height:8px;background:#C0392B;border-radius:2px'></span><span style='width:8px;height:8px;background:#C0392B;border-radius:2px'></span></div>",
    "<div style='font-size:9px;color:#155e3c'>仅动画元素加</div><div style='display:flex;gap:2px;margin-top:4px'><span style='width:8px;height:8px;background:#1C7A4E;border-radius:2px'></span></div>"
  ),
  "lazy": (
    "<div style='font-size:9px;color:#8f2b20'>全部立刻加载<br>白屏</div><div style='display:flex;gap:2px;margin-top:4px'><span style='width:9px;height:9px;background:#C0392B;border-radius:2px'></span><span style='width:9px;height:9px;background:#C0392B;border-radius:2px'></span><span style='width:9px;height:9px;background:#C0392B;border-radius:2px'></span></div>",
    "<div style='font-size:9px;color:#155e3c'>滚动到才加载</div><div style='display:flex;gap:2px;margin-top:4px'><span style='width:9px;height:9px;background:#BFE0CE;border-radius:2px'></span><span style='width:9px;height:9px;background:#1C7A4E;border-radius:2px'></span></div>"
  ),
  "semantic": (
    "<div style='font-size:9px;color:#8f2b20'>&lt;div&gt;堆结构&lt;/div&gt;</div>",
    "<div style='font-size:9px;color:#155e3c'>&lt;header&gt;&lt;nav&gt;&lt;main&gt;</div>"
  ),
  "aria": (
    "<div style='display:inline-flex;align-items:center;justify-content:center;width:28px;height:24px;background:#E7C9C4;border-radius:5px;font-size:12px'>🔍</div><div style='font-size:8px;color:#8f2b20'>读屏不知用途</div>",
    "<div style='display:inline-flex;align-items:center;justify-content:center;width:28px;height:24px;background:#BFE0CE;border-radius:5px;font-size:12px' aria-label='搜索'>🔍</div><div style='font-size:8px;color:#155e3c'>有 aria-label</div>"
  ),
  "contrast": (
    "<div style='color:#ccc;background:#fff;font-size:11px;padding:4px 8px;border-radius:5px;border:1px solid #eee'>浅灰字看不清</div>",
    "<div style='color:#595959;background:#fff;font-size:11px;padding:4px 8px;border-radius:5px;border:1px solid #eee'>深灰字清晰</div>"
  ),
  "keyboard": (
    "<div style='background:#E7C9C4;color:#8f2b20;font-size:10px;padding:5px 10px;border-radius:5px'>鼠标才能点</div>",
    "<div style='background:#BFE0CE;color:#155e3c;font-size:10px;padding:5px 10px;border-radius:5px;outline:2px solid #1C7A4E;outline-offset:2px'>Tab 可聚焦</div>"
  ),
  "reduce-motion": (
    "<div style='font-size:9px;color:#8f2b20'>动效常开 易晕</div><div style='width:54px;height:8px;background:#E7C9C4;border-radius:4px;transform:rotate(-3deg)'></div>",
    "<div style='font-size:9px;color:#155e3c'>尊重减少动效</div><div style='width:54px;height:8px;background:#BFE0CE;border-radius:4px'></div>"
  ),
  "darkmode": (
    "<div style='background:#fff;color:#000;font-size:10px;padding:5px 9px;border-radius:5px;border:1px solid #eee'>系统深色也不变</div>",
    "<div style='background:#1a1a1a;color:#eee;font-size:10px;padding:5px 9px;border-radius:5px'>跟随深色模式</div>"
  ),
  # 表单输入
  "form-input": (
    "<div class='demo-stage' style='align-items:center'><div style='width:200px'><label style='font-size:11px;font-weight:700;color:var(--ink-3)'>手机号</label><div style='margin-top:5px;height:38px;border:1px dashed var(--line);border-radius:8px;display:flex;align-items:center;padding:0 11px;color:var(--ink-3);font-size:13px'>点这里输入</div></div><div style='font-size:11px;color:var(--bad);margin-top:6px'>点进去边框不变 · 没反馈</div></div>",
    "<div class='demo-stage' style='align-items:center'><div class='f-field' style='max-width:200px'><label>手机号</label><input class='f-input demo-in' placeholder='点这里输入' type='text'></div></div>"
  ),
  "form-select": (
    "<div class='demo-stage' style='align-items:center'><div style='width:200px;height:38px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:space-between;padding:0 11px;color:var(--ink-3);font-size:13px;pointer-events:none'>请选择城市<span>&#9662;</span></div><div style='font-size:11px;color:var(--bad);margin-top:6px'>只能看不能选</div></div>",
    "<div class='demo-stage' style='align-items:center'><div class='f-sel' data-grp><div class='f-sel-btn'><span class='lbl'>请选择城市</span><span class='ar'>▾</span></div><div class='f-opt'><span data-pick data-txt='北京'>北京</span><span data-pick data-txt='上海'>上海</span><span data-pick data-txt='广州'>广州</span><span data-pick data-txt='深圳'>深圳</span></div></div></div>"
  ),
  "form-switch": (
    "<div class='demo-row' style='gap:12px'><span style='font-size:13px;color:var(--ink-2)'>接收推送通知</span><button style='height:30px;padding:0 14px;border:1px solid var(--line);background:#fff;border-radius:8px;color:var(--ink-2);font-size:13px'>开</button><button style='height:30px;padding:0 14px;border:1px solid var(--line);background:#fff;border-radius:8px;color:var(--ink-2);font-size:13px'>关</button></div>",
    "<div class='demo-row'><div class='f-sw' data-toggle='f-sw'></div><span style='font-size:13px;color:var(--ink-2)'>接收推送通知</span></div>"
  ),
  "form-checkbox": (
    "<div class='demo-row' style='gap:16px'><span style='font-size:13px;color:var(--ink-2)'>&#9744; 阅读条款</span><span style='font-size:13px;color:var(--ink-2)'>&#9744; 订阅周刊</span><span style='font-size:11px;color:var(--bad)'>用文字是/否不直观</span></div>",
    "<div class='demo-row' style='gap:14px'><span class='f-ck' data-check><i>✓</i>阅读条款</span><span class='f-ck' data-check><i>✓</i>订阅周刊</span><span class='f-ck' data-check><i>✓</i>同意推广</span></div>"
  ),
  "form-radio": (
    "<div class='demo-row' style='gap:12px'><span style='font-size:13px;color:var(--ink-2)'>性别</span><div style='width:120px;height:34px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:space-between;padding:0 10px;color:var(--ink-3);font-size:13px;pointer-events:none'>男<span>&#9662;</span></div><span style='font-size:11px;color:var(--bad)'>下拉多一步</span></div>",
    "<div class='demo-row' style='gap:14px'><span class='f-rd' data-pick><i></i>男</span><span class='f-rd' data-pick><i></i>女</span><span class='f-rd' data-pick><i></i>保密</span></div>"
  ),
  # 按钮操作
  "btn-primary": (
    "<div class='demo-row'><button style='height:38px;padding:0 18px;border-radius:9px;background:#efece6;color:#b8b2a8;border:1px solid #e2ded7;font-size:14px'>保存更改</button><span style='font-size:11px;color:var(--bad)'>和背景同色</span></div>",
    "<div class='demo-row'><button class='b-pri' data-press>保存更改</button><button class='b-sec' data-press>取消</button></div>"
  ),
  "btn-loading": (
    "<div class='demo-row'><button style='height:38px;padding:0 18px;border-radius:9px;background:var(--accent);color:#fff;border:none;font-size:14px;opacity:.55'>提交中&#8230;</button><span style='font-size:11px;color:var(--bad)'>点了没反应</span></div>",
    "<div class='demo-row'><button class='b-load' data-load>提交<span class='sp'></span></button></div>"
  ),
  "btn-disabled": (
    "<div class='demo-row'><button style='height:38px;padding:0 18px;border-radius:9px;background:var(--accent);color:#fff;border:none;font-size:14px'>不可点击</button><span style='font-size:11px;color:var(--bad)'>禁用态没区分</span></div>",
    "<div class='demo-row'><button class='b-dis' data-shake>不可点击</button><span style='font-size:12px;color:var(--ink-3)'>（禁用态变灰）</span></div>"
  ),
  "btn-group": (
    "<div class='demo-row' style='gap:8px'><button style='height:36px;padding:0 15px;border:1px solid var(--line);background:#fff;border-radius:9px;color:var(--ink-2);font-size:13px'>日</button><button style='height:36px;padding:0 15px;border:1px solid var(--line);background:#fff;border-radius:9px;color:var(--ink-2);font-size:13px'>周</button><button style='height:36px;padding:0 15px;border:1px solid var(--line);background:#fff;border-radius:9px;color:var(--ink-2);font-size:13px'>月</button></div>",
    "<div class='demo-row'><div class='b-grp' data-grp><span class='on'>日</span><span>周</span><span>月</span></div></div>"
  ),
  "btn-icon": (
    "<div class='demo-row'><button style='width:40px;height:40px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--ink-3);font-size:16px'>&#9829;</button><span style='font-size:11px;color:var(--bad)'>点了没状态</span></div>",
    "<div class='demo-row'><button class='b-ic' data-check>♥</button><span style='font-size:12px;color:var(--ink-3)'>点一下收藏</span></div>"
  ),
  # 弹窗遮罩
  "modal-dialog": (
    "<div class='demo-row' style='gap:8px'><button style='height:34px;padding:0 14px;border-radius:8px;border:1px solid var(--bad);color:var(--bad);background:#fff;font-size:12.5px'>删除</button><span style='font-size:12px;color:var(--bad);text-decoration:line-through'>订单 #123</span></div>",
    "<div class='mo'><button class='xbtn p' style='position:relative;z-index:1'>点击弹出对话框</button><div class='mo-mask' data-close='mo'><div class='mo-card'><h4>删除确认</h4><p>确定要删除这条记录吗？</p><div class='mo-foot'><button class='xbtn' data-close='mo'>取消</button><button class='xbtn p' data-close='mo'>删除</button></div></div></div></div>"
  ),
  "modal-drawer": (
    "<div style='display:flex;flex-direction:column;gap:6px;width:100%'><div style='padding:7px 9px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>全部</div><div style='padding:7px 9px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>已购</div><div style='padding:7px 9px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>收藏</div><div style='padding:7px 9px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>价格区间</div></div>",
    "<div class='dr'><button class='xbtn p' style='position:relative;z-index:1'>☰ 打开抽屉</button><div class='dr-mask' data-close='dr'></div><div class='dr-panel'><div class='dh'>筛选</div><div class='dr-item' data-close='dr'>全部</div><div class='dr-item' data-close='dr'>已购</div><div class='dr-item' data-close='dr'>收藏</div></div></div>"
  ),
  "toast-msg": (
    "<div class='demo-row'><button style='height:34px;padding:0 14px;border-radius:8px;background:var(--accent);color:#fff;border:none;font-size:12.5px'>保存</button><span style='font-size:11px;color:var(--bad)'>操作完没提示</span></div>",
    "<div class='demo-row'><button class='b-pri' data-toast='已保存到本地 ✓'>点一下看提示</button></div>"
  ),
  "popconfirm": (
    "<div class='demo-row' style='gap:8px'><button style='height:34px;padding:0 14px;border-radius:8px;border:1px solid var(--bad);color:var(--bad);background:#fff;font-size:12.5px'>删除</button><span style='font-size:12px;color:var(--bad)'>已删除 &#10003;</span></div>",
    "<div class='demo-row'><div class='pc'><button class='b-sec'>删除</button><div class='pc-box'>确定删除吗？<div class='pc-bt'><button class='pb c' data-close='pc'>删除</button><button class='pb x' data-close='pc'>取消</button></div></div></div></div>"
  ),
  "skeleton": (
    "<div style='width:100%;height:92px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--ink-3);font-size:12px'>加载中&#8230;（空白/一直转）</div>",
    "<div class='demo-row'><div class='sk' data-toggle='sk'><div class='sk-line w1'></div><div class='sk-line w2'></div><div class='sk-line w3'></div><div class='sk-line w4'></div><div class='sk-real'><b>文章标题</b><span>加载完成后显示的真实内容，骨架屏结束。</span></div></div></div>"
  ),
  # 动效
  "anim-fade": (
    "<div class='demo-row'><div style='padding:10px 16px;border-radius:8px;background:var(--accent);color:#fff;font-size:13px'>提示信息</div><span style='font-size:11px;color:var(--bad)'>无过渡 · 生硬</span></div>",
    "<div class='an-wrap'><div class='an-fade'>提示信息</div></div>"
  ),
  "anim-flip": (
    "<div style='display:flex;gap:8px'><div style='flex:1;height:54px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--ink-2)'>正面</div><div style='flex:1;height:54px;border:1px solid var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:12px;color:var(--ink-2)'>背面</div></div>",
    "<div class='an-flip'><div class='inner'><div class='face f'>正面 · 点翻转</div><div class='face b'>背面 · 详情</div></div></div>"
  ),
  "anim-list": (
    "<div style='display:flex;flex-direction:column;gap:5px'><div style='padding:8px 10px;border:1px solid var(--line);border-radius:7px;font-size:12.5px;color:var(--ink-2)'>项目一</div><div style='padding:8px 10px;border:1px solid var(--line);border-radius:7px;font-size:12.5px;color:var(--ink-2)'>项目二</div><div style='padding:8px 10px;border:1px solid var(--line);border-radius:7px;font-size:12.5px;color:var(--ink-2)'>项目三</div></div>",
    "<div class='an-li'><div class='li'>✓ 项目一</div><div class='li'>✓ 项目二</div><div class='li'>✓ 项目三</div></div>"
  ),
  "anim-progress": (
    "<div style='width:100%'><div style='height:8px;border-radius:4px;background:var(--line)'></div><div style='font-size:11px;color:var(--bad);margin-top:6px'>不知还要多久</div></div>",
    "<div class='demo-row'><div style='width:100%;max-width:220px'><div class='an-bar half'><div class='fill'></div></div><div style='font-size:11px;color:var(--good);margin-top:7px'>62% · 正在加载</div></div></div>"
  ),
  "anim-tab": (
    "<div style='display:flex;flex-direction:column;gap:6px'><div style='padding:8px 10px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>简介：这里是简介内容。</div><div style='padding:8px 10px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>评价：这里是用户评价。</div><div style='padding:8px 10px;border:1px solid var(--line);border-radius:7px;font-size:12px;color:var(--ink-2)'>详情：这里是详细参数。</div></div>",
    "<div class='an-tab'><div class='tabs2' data-grp><button class='on' data-pick>简介</button><button data-pick>评价</button><button data-pick>详情</button></div><div class='panels'><div class='p on'>这里是简介内容。</div><div class='p'>这里是用户评价。</div><div class='p'>这里是详细参数。</div></div></div>"
  ),
  "hover-lift": (
    "<div style='border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff;width:100%'><div style='height:48px;border-radius:6px;background:linear-gradient(135deg,#f3d9b0,#e7c9a0)'></div><div style='font-size:13px;font-weight:700;color:var(--ink);margin-top:8px'>静态卡片</div><div style='font-size:11px;color:var(--bad);margin-top:2px'>放上去没反应</div></div>",
    "<div class='hl-card' data-toggle='hl-card'><div style='height:48px;border-radius:6px;background:linear-gradient(135deg,#f3d9b0,#e7c9a0)'></div><div style='font-size:13px;font-weight:700;color:var(--ink);margin-top:8px'>悬停我试试</div><div style='font-size:12px;color:var(--ink-2);margin-top:2px'>放上鼠标 / 点一下，会轻轻浮起</div></div>"
  ),
  "carousel": (
    "<div style='display:flex;flex-direction:column;gap:6px;width:100%'><div style='height:44px;border-radius:6px;background:linear-gradient(135deg,#bfe0ce,#a9d3c4);display:flex;align-items:center;justify-content:center;font-size:12px;color:#2c5a40'>图 1</div><div style='height:44px;border-radius:6px;background:linear-gradient(135deg,#f3d9b0,#e7c9a0);display:flex;align-items:center;justify-content:center;font-size:12px;color:#6b5326'>图 2</div><div style='height:44px;border-radius:6px;background:linear-gradient(135deg,#c9d4f3,#a9b8e7);display:flex;align-items:center;justify-content:center;font-size:12px;color:#3a4170'>图 3</div></div>",
    "<div class='cr'><div class='cr-track'><div class='cr-slide' style='background:linear-gradient(135deg,#bfe0ce,#a9d3c4)'>图 1</div><div class='cr-slide' style='background:linear-gradient(135deg,#f3d9b0,#e7c9a0)'>图 2</div><div class='cr-slide' style='background:linear-gradient(135deg,#c9d4f3,#a9b8e7)'>图 3</div></div><div class='cr-nav'><button data-cr-prev type='button'>‹</button><button data-cr-next type='button'>›</button></div></div>"
  ),
}

INTERACTIVE = set(t["id"] for t in T)  # 全站术语详情页统一采用 data-demo 版式（与导航术语一致）

HINT = {
  "anim-fade": "点「点击试用」淡入",
  "anim-flip": "点「点击试用」翻转",
  "anim-list": "点「点击试用」列表入场",
  "anim-progress": "点「点击试用」跑进度",
  "anim-tab": "点「点击试用」切标签页",
  "btn-disabled": "点「点击试用」看禁用抖动",
  "btn-group": "点「点击试用」切下一项",
  "btn-icon": "点「点击试用」收藏切换",
  "btn-loading": "点「点击试用」看加载态",
  "btn-primary": "点「点击试用」看按下反馈",
  "carousel": "点「点击试用」或左右按钮切换图片",
  "form-checkbox": "点「点击试用」勾选",
  "form-input": "点「点击试用」聚焦输入框",
  "form-radio": "点「点击试用」选一个",
  "form-select": "点「点击试用」展开下拉",
  "form-switch": "点「点击试用」拨动开关",
  "hover-lift": "点「点击试用」· 卡片浮起",
  "modal-dialog": "点「点击试用」弹对话框",
  "modal-drawer": "点「点击试用」开抽屉",
  "nav-anchor": "点「点击试用」· 切换栏目",
  "nav-crumb": "点「点击试用」· 切换当前位置",
  "nav-dropdown": "点「点击试用」· 展开二级菜单",
  "nav-hamburger": "点「点击试用」· 抽屉滑出",
  "nav-mega": "点「点击试用」· 展开巨型菜单",
  "nav-overlay": "点「点击试用」· 全屏展开",
  "nav-shrink": "点「点击试用」· 看头部收缩",
  "nav-sidebar": "点「点击试用」· 收起/展开侧栏",
  "nav-sticky": "点「点击试用」或上下滚动 · 看吸顶",
  "popconfirm": "点「点击试用」气泡确认",
  "skeleton": "点「点击试用」加载完成",
  "toast-msg": "点「点击试用」飘提示"
}

INTENTS = [
  ("all", "全部组件", "浏览全部高频组件", None),
  ("click", "点一下", "按钮 / 开关 / 标签 / 下拉 等点击触发的交互", ["btn-primary", "btn-loading", "btn-disabled", "btn-group", "btn-icon", "popconfirm", "active", "hover", "focus-visible", "nav-dropdown", "nav-mega", "anim-tab"]),
  ("input", "填一下", "输入框 / 表单 / 选择 / 上传 等收集信息的交互", ["form-input", "form-select", "form-switch", "form-checkbox", "form-radio"]),
  ("view", "看一个东西", "弹窗 / 抽屉 / 卡片 / 列表 等展示内容", ["modal-dialog", "modal-drawer", "toast-msg", "skeleton", "nav-sidebar", "nav-hamburger", "nav-overlay", "nav-mega", "nav-crumb", "nav-anchor", "anim-flip", "anim-list"]),
  ("wait", "等一个反馈", "加载中 / 进度 / 轻提示 等状态反馈", ["btn-loading", "skeleton", "toast-msg", "anim-progress"]),
  ("slide", "滑一下翻页", "轮播 / 抽屉滑出 / 滚动驱动 / 翻转 等动效", ["modal-drawer", "nav-hamburger", "anim-flip", "anim-list", "anim-fade", "nav-sidebar", "nav-sticky", "nav-shrink"])
]

AGENT_FOUNDATION = [
  ("Frontend", "前端", "前端基础", "常说的「前端」是用户直接看得到、能点的界面部分，后端是数据和逻辑。"),
  ("Component", "组件", "前端基础", "把反复出现的区块做成组件，改一处全站同步更新。"),
  ("State", "状态管理", "前端基础", "点提交后先显示「保存中」，成功或失败再更新对应提示。"),
  ("Semantic HTML", "语义化标签", "前端基础", "页面缺 H1 会被 SEO 提示；用正确的标签表达结构。"),
  ("Accessibility", "无障碍", "前端基础", "不用鼠标的人用读屏也能正常操作页面。"),
  ("Button", "按钮", "按钮与链接", "加一个点击后执行保存等动作的按钮。"),
  ("Link", "链接", "按钮与链接", "让一段文字可点击跳转到另一个页面。"),
  ("Input", "输入框", "表单", "加一个让用户填邮箱等内容的输入字段。"),
  ("Textarea", "多行输入", "表单", "一行不够，给一段较长的留言用多行输入。"),
  ("Number Input", "数字输入", "表单", "只允许输入数字，最好带加减按钮。"),
  ("Radio", "单选", "表单", "几个选项互斥，选一个就取消上一个。"),
  ("Checkbox", "多选", "表单", "选项不冲突，可以选多个。"),
  ("Switch", "开关", "表单", "像手机设置那样，拨一下开、再拨关。"),
  ("Slider", "滑块", "表单", "用可拖动的滑块来选价格区间等。"),
  ("Select", "下拉选择", "表单", "选项太多，放进可展开的下拉框里选。"),
  ("Date Picker", "日期选择", "表单", "给个日历让用户选日期，而不是手打。"),
  ("Upload", "上传", "表单", "让用户上传自己的图片等文件。"),
  ("Form", "表单", "表单", "做一个填信息再提交的注册页。"),
  ("Label", "字段标签", "表单", "每个输入框前加清楚标签，知道填什么。"),
  ("Table", "表格", "内容展示", "把订单数据排成表格，一行一个订单。"),
  ("Card", "卡片", "内容展示", "每个商品做成可点卡片：图上、名和价在下。"),
  ("Badge", "角标", "内容展示", "在消息图标上显示未读红点数字。"),
  ("Avatar", "头像", "内容展示", "评论里显示头像，知道谁在说话。"),
  ("Tabs", "标签页", "内容展示", "内容太多，用标签页切换不同视图。"),
  ("Segmented", "分段控件", "内容展示", "两三个选项并排，点一个切换，像 iPhone 控件。"),
  ("Collapse", "折叠", "内容展示", "问题先只显示，点开才看答案。"),
  ("Empty", "空状态", "内容展示", "没数据时展示图和引导，而不是白屏。"),
  ("Chart", "图表", "内容展示", "用图表对比半年订单变化，别让人凭颜色猜数值。"),
  ("Chat UI", "聊天界面", "内容展示", "完整聊天窗：消息列表+输入区+发送态+失败重试。"),
  ("Filter", "筛选", "内容展示", "只显示本周、未完成、分配给我的任务。"),
  ("Modal", "模态框", "弹窗反馈", "点按钮在屏幕中央弹框并压暗背景。"),
  ("Drawer", "抽屉", "弹窗反馈", "从右侧拉出详情面板，列表仍可见。"),
  ("Popconfirm", "气泡确认", "弹窗反馈", "删除时在按钮旁问「确定吗」，不开大弹窗。"),
  ("Toast", "轻提示", "弹窗反馈", "角落显示「已保存」几秒后自动消失。"),
  ("Progress", "进度", "弹窗反馈", "显示上传进度，免得以为卡住了。"),
  ("Skeleton", "骨架屏", "弹窗反馈", "加载时先显示灰色占位块，而不是一直转圈。"),
  ("Menu", "菜单", "导航", "功能太多，加个菜单方便找。"),
  ("Breadcrumb", "面包屑", "导航", "页面层级深，顶部显示所在位置并可回退。"),
  ("Steps", "步骤条", "导航", "结算有三步，顶部告诉用户走到哪了。"),
  ("Search", "搜索", "导航", "在项目列表上方加搜索，按名字或关键词快找。"),
  ("Hero", "首屏", "页面区块", "顶部太空，给个大图和标题让人立刻懂。"),
  ("Navbar", "顶部导航", "页面区块", "把主栏目放顶部导航，并标明当前页。"),
  ("CTA", "行动号召", "页面区块", "页面上放醒目的「免费试用」引导点击。"),
  ("Sidebar", "侧边栏", "页面布局", "功能菜单放左侧栏，内容放右侧大区。"),
  ("Responsive", "响应式", "页面布局", "手机宽度下三列变一列，导航和卡片保持。"),
  ("Flex", "弹性布局", "CSS布局", "把按钮排一行、间距均匀、垂直居中。"),
  ("Grid", "网格布局", "CSS布局", "卡片排整齐网格，窄屏自动变两列。"),
  ("Sticky", "吸顶", "CSS布局", "滚动时把导航钉在顶部。"),
  ("Overflow", "溢出", "CSS布局", "卡片底部被挡住？检查是否竖向溢出被裁。"),
  ("Dark Mode", "暗色模式", "视觉", "真正的暗色：文字、边框、图表、代码一起切。"),
  ("Visual Hierarchy", "视觉层级", "视觉", "页面太乱？分层：标题最显、描述次之、按钮最突出。"),
  ("Hover", "悬停", "指针交互", "鼠标移上去变个色，让人知道能点。"),
  ("Focus", "焦点", "指针交互", "用 Tab 键时给清晰焦点轮廓，知道在哪。"),
  ("Disabled", "禁用态", "指针交互", "表单没填完前，提交按钮灰掉不可点。")
]

def agent_terms_base():
    return [{"en": a[0], "cn": a[1], "cat": a[2], "macro": "", "pl": a[3], "url": "https://vibe-hub.org"} for a in AGENT_FOUNDATION]



def build_agent_terms():
    """组件库全量对齐：先放「组件库派生」契约（slug 与组件卡 data-vibe 一一对应），
    再补充基础概念层（slug 不重复才补），保证每个 data-vibe 锚点都能双向解析。"""
    seen = set(); out = []
    # 1) 组件库派生：slug 严格等于 dv_slug(en)，与组件卡 data-vibe 对齐
    for t in T:
        slug = dv_slug(t["en"])
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append({"en": t["en"], "cn": t["cn"], "cat": CHAPTERS[t["ch"]],
                    "macro": "", "pl": t["speak"], "url": "https://vibe-hub.org"})
    # 2) 基础概念层补遗（VibeHub 或内置）：只在 slug 未覆盖时加入，避免重复
    for a in agent_terms_base():
        slug = dv_slug(a["en"])
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(a)
    return out

def load_agent_terms():
    return build_agent_terms()

# 工坊 JS 数据
def terms_js():
    arr = []
    for t in T:
        arr.append("{" + ",".join([
            "id:%s" % json.dumps(t["id"]),
            "ch:%d" % t["ch"],
            "speak:%s" % json.dumps(t["speak"], ensure_ascii=False),
            "cn:%s" % json.dumps(t["cn"], ensure_ascii=False),
            "en:%s" % json.dumps(t["en"], ensure_ascii=False),
            "anti:%s" % json.dumps(t["anti"], ensure_ascii=False),
            "fix:%s" % json.dumps(t["fix"], ensure_ascii=False),
            "tip:%s" % json.dumps(t["tip"], ensure_ascii=False),
            "plat:%s" % json.dumps(t["plat"], ensure_ascii=False),
        ]) + "}")
    intents = "var INTENTS=" + json.dumps(
        [{"k": k, "label": lab, "desc": desc, "ids": (ids or [])} for (k, lab, desc, ids) in INTENTS],
        ensure_ascii=False) + ";"
    agent_json = json.dumps(load_agent_terms(), ensure_ascii=False)
    icons_json = json.dumps(load_icons(), ensure_ascii=False)
    return ("var TERMS=[" + ",".join(arr) + "];\n" + intents
            + "\nvar AGENT_TERMS=" + agent_json + ";\nvar ICONS=" + icons_json + ";")

def morph_js():
    """内联 Morphcons 形变引擎（MIT）：构建时读取 vendor_src/morphicons_engine.js。
    缺失则回退为空（图标仍静态可用）。"""
    import os
    p = "vendor_src/morphicons_engine.js"
    if os.path.exists(p):
        return open(p, encoding="utf-8").read()
    return ""

# ============================================================================
# CSS（编辑部式去 AI 味：纸白底 / 墨黑 / 朱红唯一强调色）
# ============================================================================
CSS = """
:root{
  --paper:#FBFAF7; --surface:#FFFFFF; --ink:#1A1A1A; --ink-2:#5B5852;
  --ink-3:#938E85; --line:#ECE8E1; --line-2:#F3F0EA;
  --accent:#C8442E; --accent-2:#A8351F; --accent-soft:#FBEDE9;
  --good:#1C7A4E; --good-soft:#E7F3EC; --bad:#C0392B; --bad-soft:#F8E8E5;
  --code-bg:#211F1C; --code-tx:#EDEAE4; --code-c:#8A8479;
  --r:12px; --r-lg:16px; --ease:cubic-bezier(.4,0,.2,1);
  --stage:#fbfcfe; --stage-line:#eef0f4;
  --shadow:0 1px 2px rgba(20,18,15,.04),0 10px 30px rgba(20,18,15,.06);
  --shadow-lg:0 2px 6px rgba(20,18,15,.05),0 18px 40px rgba(20,18,15,.08);
  --max:1180px;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{background:var(--paper);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","HarmonyOS Sans","Microsoft YaHei",sans-serif;
  font-size:15px;line-height:1.65;padding-bottom:calc(24px + env(safe-area-inset-bottom))}
.wrap{max-width:var(--max);margin:0 auto;padding:0 18px}
h1,h2,h3,h4{margin:0;font-weight:800;letter-spacing:-.015em;line-height:1.25}
a{color:inherit;text-decoration:none}
button{font-family:inherit;cursor:pointer;border:0;background:none;color:inherit;font-size:inherit}
input,select,textarea{font-family:inherit;font-size:16px;color:inherit}
svg{display:block;flex:none}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,"Cascadia Code",monospace}

/* 顶栏 */
.top{background:rgba(251,250,247,.92);backdrop-filter:saturate(1.2) blur(8px);
  border-bottom:1px solid var(--line);position:sticky;top:0;z-index:80}
.top-in{max-width:var(--max);margin:0 auto;padding:11px 18px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.logo{display:flex;align-items:center;gap:11px;min-width:0}
.logo-ic{width:36px;height:36px;border-radius:9px;background:#C8442E;color:#fff;display:flex;align-items:center;justify-content:center;flex:none}
.logo-tx{font-size:17px;font-weight:800;letter-spacing:-.02em;white-space:nowrap}
.logo-sub{font-size:11px;color:var(--ink-3);margin-top:-1px;white-space:nowrap}
.top-act{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
.tbtn{display:inline-flex;align-items:center;gap:6px;height:36px;padding:0 12px;border:1px solid var(--line);border-radius:9px;background:var(--surface);font-size:13px;color:var(--ink-2);transition:.15s}
.tbtn:hover{border-color:#d8d2c8;color:var(--ink)}
.tbtn.p{background:var(--accent);border-color:var(--accent);color:#fff}
.tbtn.p:hover{background:var(--accent-2);border-color:var(--accent-2)}
@media(max-width:640px){.logo-sub{display:none}.tbtn{height:34px;padding:0 10px;font-size:12px}}

/* Tab */
.tabs{display:flex;gap:4px;background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:4px;margin:16px 0 0;overflow-x:auto}
.tab{flex:1;min-width:92px;height:42px;display:flex;align-items:center;justify-content:center;gap:6px;border-radius:8px;font-size:14px;font-weight:600;color:var(--ink-2);white-space:nowrap;transition:.15s}
.tab.on{background:var(--ink);color:#fff}
.tab span.n{display:inline-block;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--line-2);color:var(--ink-2);font-size:11px;line-height:18px;text-align:center;font-weight:700}
.tab.on span.n{background:rgba(255,255,255,.22);color:#fff}

/* Hero */
.hero{margin-top:18px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:30px 28px;box-shadow:var(--shadow);position:relative;overflow:hidden}
.hero:before{content:"";position:absolute;right:-40px;top:-40px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,var(--accent-soft),transparent 70%);pointer-events:none}
.hero h1{font-size:30px;max-width:760px}
.hero h1 .hl{color:var(--accent)}
.hero p{margin:12px 0 0;font-size:15.5px;color:var(--ink-2);max-width:680px}
.hero .hint{margin-top:16px;display:flex;gap:8px;flex-wrap:wrap}
.chip-soft{font-size:12.5px;color:var(--ink-2);background:var(--line-2);border-radius:20px;padding:5px 12px}

/* 速查布局 */
.lib{display:grid;grid-template-columns:212px 1fr;gap:22px;margin-top:18px;align-items:start}
.cnav-wrap{position:sticky;top:74px;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:10px}
.cnav-wrap .ct{font-size:12px;font-weight:700;color:var(--ink-3);letter-spacing:.04em;padding:4px 8px 8px}
.cnav{display:flex;align-items:center;gap:8px;padding:9px 10px;border-radius:9px;font-size:13.5px;color:var(--ink-2);transition:.12s}
.cnav:hover{background:var(--line-2);color:var(--ink)}
.cnav.on{background:var(--accent-soft);color:var(--accent-2);font-weight:600}
.cnav-cnt{margin-left:auto;font-size:11px;color:var(--ink-3);background:var(--line-2);border-radius:8px;padding:1px 7px}
.cnav.on .cnav-cnt{background:rgba(200,68,46,.14);color:var(--accent-2)}

/* 章节 */
.chap{scroll-margin-top:74px;margin-bottom:26px}
.chap-h{font-size:20px;display:flex;align-items:center;gap:10px;padding-bottom:10px;border-bottom:2px solid var(--ink)}
.chap-no{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:7px;background:var(--accent);color:#fff;font-size:13px}
.chap-cnt{font-size:12.5px;font-weight:600;color:var(--ink-3);margin-left:4px}
.chap-formula{margin:14px 0 2px;background:linear-gradient(120deg,var(--accent-soft),#fdf0ec);border:1px solid #f0d9cf;border-radius:14px;padding:14px 16px}
.chap-formula .cf-t{display:flex;align-items:center;gap:7px;font-size:13px;font-weight:800;color:var(--accent-2);margin-bottom:10px}
.chap-formula .cf-t svg{width:15px;height:15px;flex:none}
.chap-formula .chips{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.chap-formula .chip{background:#fff;border:1px solid #f0d9cf;border-radius:999px;padding:6px 13px;font-size:12.5px;font-weight:700;color:var(--accent-2);white-space:nowrap}
.chap-formula .plus{background:none;border:none;color:var(--ink-3);font-size:17px;font-weight:800;padding:0 1px;line-height:1}

/* 卡片网格 */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px;margin-top:16px}
@media(max-width:560px){.grid{grid-template-columns:1fr}}

.term{background:var(--surface);border:1px solid var(--line);border-radius:var(--r-lg);overflow:hidden;transition:box-shadow .2s var(--ease),border-color .2s var(--ease),transform .2s var(--ease);display:flex;flex-direction:column}
.term:hover{border-color:#e3c9c2;box-shadow:var(--shadow-lg);transform:translateY(-2px)}
.term-hd{padding:16px 16px 12px;display:flex;align-items:flex-start;gap:10px}
.term-hd .nm{flex:1;min-width:0}
.speak{font-size:15.5px;font-weight:800;line-height:1.4;color:var(--ink);letter-spacing:-.01em}
.cn{font-size:13px;color:var(--ink-2);margin-top:4px;font-weight:600}
.en{font-size:11px;color:var(--ink-3);font-family:ui-monospace,Menlo,Consolas,monospace;margin-top:3px;word-break:break-all}
.star{width:32px;height:32px;border-radius:9px;display:flex;align-items:center;justify-content:center;color:#d8d2c8;flex:none;transition:.15s var(--ease)}
.star:hover{background:var(--accent-soft);color:var(--accent)}
.star.on{color:var(--accent)}
.term-bd{padding:0 16px}
.box{font-size:13px;line-height:1.55;padding:10px 12px;border-radius:10px;margin-bottom:8px;border:1px solid transparent}
.box .bx-h{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:700;margin-bottom:3px;letter-spacing:.02em}
.bad{background:var(--bad-soft);border-color:#f0d4cf;color:#8f2b20}
.bad .bx-h{color:var(--bad)}
.good{background:var(--good-soft);border-color:#cfe7da;color:#155e3c}
.good .bx-h{color:var(--good)}
.code{padding:0 15px 12px}
.code-h{font-size:12px;color:var(--ink-3);font-weight:600;display:flex;align-items:center;justify-content:space-between;margin-bottom:6px}
.toggle{height:26px;padding:0 10px;border:1px solid var(--line);border-radius:7px;font-size:11.5px;color:var(--ink-2);background:var(--surface)}
.toggle:hover{border-color:var(--accent);color:var(--accent)}
.code-bd{display:grid;gap:10px}
.cf-note{font-size:12px;color:var(--ink-2);line-height:1.6;margin-top:8px;padding:9px 11px;background:var(--line-2);border-radius:9px}
.cf-note code{background:rgba(0,0,0,.06);padding:1px 5px;border-radius:5px;font-size:11px}
.dv-link{display:inline-block;margin-top:6px;color:var(--accent);font-weight:700;cursor:pointer}
.dv-link:hover{text-decoration:underline}
.cf .cf-h{display:inline-flex;align-items:center;gap:5px;font-size:11.5px;font-weight:700;margin-bottom:4px}
.cf.bad .cf-h{color:var(--bad)} .cf.good .cf-h{color:var(--good)}
.cf pre{margin:0;background:var(--code-bg);border-radius:9px;padding:11px 12px;overflow-x:auto}
.cf code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--code-tx);white-space:pre;line-height:1.6}
.plat{padding:10px 15px;border-top:1px solid var(--line-2);background:#fcfbf9}
.plat-h{font-size:11.5px;font-weight:700;color:var(--ink-3);display:inline-flex;align-items:center;gap:5px;margin-bottom:6px;letter-spacing:.02em}
.plat-row{font-size:12.5px;color:var(--ink-2);display:flex;gap:8px;align-items:flex-start;margin-bottom:4px;line-height:1.5}
.pt{flex:none;font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:6px;color:#fff}
.pt.web{background:#3b6ea5} .pt.app{background:#2e8b72} .pt.mini{background:#c08a2e}
.term-ft{padding:11px 15px;border-top:1px solid var(--line-2);display:flex;gap:8px;flex-wrap:wrap}
.sm{height:34px;padding:0 12px;border-radius:9px;border:1px solid var(--line);font-size:13px;color:var(--ink-2);background:var(--surface);display:inline-flex;align-items:center;gap:6px;transition:.15s var(--ease)}
.sm:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}
.sm.p{background:var(--accent);border-color:var(--accent);color:#fff}
.sm.p:hover{background:var(--accent-2);border-color:var(--accent-2);color:#fff}

/* 导航演示 m- 组件（前后对照小样） */
.m-phone{width:148px;height:186px;border:1.5px solid #e6e8df;border-radius:12px;overflow:hidden;background:#fff;position:relative;display:flex;flex-direction:column}
.m-bar{height:28px;flex:none;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
.m-bar.s{background:#C8442E}
.m-sticky{position:sticky;top:0;z-index:3;box-shadow:0 2px 6px rgba(0,0,0,.18)}
.m-body{flex:1;padding:8px;overflow:hidden}
.m-line{height:7px;background:#eee9e1;border-radius:4px;margin-bottom:6px}
.m-side{width:46px;flex:none;background:#f4f1ea;padding:8px 0;display:flex;flex-direction:column;gap:7px;align-items:center}
.m-side i{width:30px;height:7px;background:#ddd6cb;border-radius:3px}
.m-side i.on{background:var(--accent)}
.m-crumb{font-size:10.5px;color:#938E85;padding:5px 8px;background:#faf8f4;border-bottom:1px solid var(--line-2);white-space:nowrap;overflow:hidden}
.m-crumb b{color:var(--ink)}
.m-dd{position:relative;padding:7px 10px;background:#faf8f4;border:1px solid var(--line-2);border-radius:8px;font-size:11px;width:120px}
.m-sub{position:absolute;top:100%;left:0;margin-top:4px;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 20px rgba(0,0,0,.12);padding:6px;display:flex;flex-direction:column;gap:5px;z-index:4;width:110px}
.m-sub span{font-size:10.5px;padding:4px 6px;background:#f4f1ea;border-radius:5px}
.m-mega{width:140px;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 8px 20px rgba(0,0,0,.12);padding:8px;display:grid;grid-template-columns:1fr 1fr;gap:6px}
.m-mega b{font-size:10px;color:var(--ink-3);grid-column:span 2}
.m-mega span{font-size:10px;background:#f4f1ea;border-radius:5px;padding:4px 5px;text-align:center}
.m-drawer{position:absolute;top:0;left:0;height:100%;width:96px;background:#fff;border-right:1px solid var(--line);box-shadow:4px 0 14px rgba(0,0,0,.12);display:flex;flex-direction:column;gap:8px;padding:10px 9px;z-index:5}
.m-drawer span{font-size:10.5px;background:#f4f1ea;border-radius:6px;padding:6px 5px;text-align:center}
.m-overlay{position:absolute;inset:0;background:rgba(26,26,26,.92);display:flex;flex-direction:column;gap:10px;align-items:center;justify-content:center;z-index:6}
.m-overlay span{color:#fff;font-size:12px;font-weight:600}
.m-anchor{position:absolute;right:6px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:7px;z-index:4}
.m-anchor i{width:7px;height:7px;border-radius:50%;background:#ddd6cb}
.m-anchor i.on{background:var(--accent);width:9px;height:9px}
.m-big{height:64px;background:linear-gradient(135deg,#C8442E,#A8351F);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font-size:11px;font-weight:700;text-align:center}
.m-small{height:30px;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700}
.m-nobar{height:22px;background:#f0ebe2;color:#b3aea3;display:flex;align-items:center;justify-content:center;font-size:10px;margin-bottom:6px}

/* 章节规划路线图 */
.roadmap{margin-top:28px}
.road-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(228px,1fr));gap:12px;margin-top:14px}
.road{background:var(--surface);border:1px dashed var(--line);border-radius:12px;padding:13px 14px}
.road b{display:block;font-size:14px;margin-bottom:5px;color:var(--ink)}
.road span{font-size:12.5px;color:var(--ink-3);line-height:1.65}
.road .soon{display:inline-block;font-size:10.5px;font-weight:700;color:#fff;background:#b3aea3;border-radius:6px;padding:1px 7px;margin-left:6px;vertical-align:middle}
@media(max-width:560px){.road-grid{grid-template-columns:1fr}}

/* 工坊 */
.wk{display:grid;grid-template-columns:1fr;gap:18px;margin-top:18px;align-items:start}
@media(max-width:860px){.wk{grid-template-columns:1fr}}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;box-shadow:var(--shadow)}
.card-hd{padding:14px 16px;border-bottom:1px solid var(--line-2);display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.card-hd h3{font-size:15px}
.card-hd .sub{font-size:12px;color:var(--ink-3)}
.card-bd{padding:15px 16px}
.fld{margin-bottom:15px}
.fld>label{display:block;font-size:12.5px;font-weight:700;color:var(--ink-2);margin-bottom:7px}
.seg{display:flex;gap:6px;flex-wrap:wrap}
.seg button{flex:1;min-width:84px;height:42px;border:1px solid var(--line);border-radius:10px;background:var(--surface);font-size:13.5px;color:var(--ink-2);transition:.12s}
.seg button.on{background:var(--ink);color:#fff;border-color:var(--ink);font-weight:600}
.seg button:hover:not(.on){border-color:#d8d2c8}
.sel{width:100%;height:46px;padding:0 12px;border:1px solid var(--line);border-radius:10px;background:var(--surface);font-size:16px;appearance:none;
  background-image:url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23938E85' stroke-width='2.5' stroke-linecap='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center}
.sel:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.chips{display:flex;flex-wrap:wrap;gap:7px}
.chip{height:36px;padding:0 12px;border-radius:9px;border:1px solid var(--line);background:var(--surface);font-size:13px;color:var(--ink-2);display:inline-flex;align-items:center;gap:6px}
.chip:hover{border-color:#d8d2c8}
.chip.on{background:var(--accent-soft);border-color:#e7b3a8;color:var(--accent-2);font-weight:600}
.swatches{display:flex;flex-wrap:wrap;gap:8px}
.sw{width:40px;height:40px;border-radius:10px;border:2px solid transparent;position:relative;cursor:pointer}
.sw.on{border-color:var(--ink);box-shadow:0 0 0 2px var(--surface) inset}
.out{width:100%;min-height:380px;padding:15px;border:1px solid var(--line);border-radius:12px;background:#fcfbf9;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:13px;line-height:1.75;color:#2b2824;resize:vertical;white-space:pre-wrap}
.out:focus{outline:none;border-color:var(--accent);background:#fff}
.wk-ft{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}

/* 翻译器：大输入框 + 三输出 */
.tr-input-wrap{position:relative}
.tr-input{width:100%;border:1.5px solid var(--line);border-radius:12px;padding:14px 50px 14px 14px;font-size:16px;line-height:1.65;resize:vertical;font-family:inherit;color:var(--ink);background:var(--surface);box-sizing:border-box;display:block}
.tr-input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(200,68,46,.12)}
.tr-mic{position:absolute;right:9px;bottom:11px;width:34px;height:34px;border:none;background:var(--line-2);border-radius:50%;color:var(--ink-2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:.15s}
.tr-mic svg{width:18px;height:18px}
.tr-mic:hover{background:var(--accent);color:#fff}
.tr-mic.on{background:var(--accent);color:#fff;animation:micpulse 1.1s infinite}
@keyframes micpulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.tr-examples{margin-top:13px;display:flex;flex-wrap:wrap;gap:7px;align-items:center}
.ex-label{font-size:13px;color:var(--ink-3);margin-right:2px}
.tr-examples button{font-size:13px;padding:6px 11px;border:1px solid var(--line);background:var(--surface);border-radius:999px;color:var(--ink-2);cursor:pointer;transition:.12s}
.tr-examples button:hover{border-color:var(--accent);color:var(--accent)}
.tr-actions{margin-top:15px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:space-between}
.tr-actions .seg{flex:1;min-width:210px}
.tbtn.big{font-size:15px;padding:11px 24px}
.tbtn.ghost{background:transparent;border:1px dashed var(--line);color:var(--ink-2)}
.tbtn.ghost:hover{border-color:var(--accent);color:var(--accent)}
.out-block{border:1px solid var(--line);border-radius:13px;overflow:hidden;margin-bottom:14px}
.out-block:last-child{margin-bottom:0}
.ob-h{display:flex;align-items:center;gap:9px;padding:10px 14px;background:var(--line-2);font-size:13px;color:var(--ink-2)}
.ob-tag{font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px;background:#fff;border:1px solid var(--line);color:var(--ink-2);flex:none}
.ob-tag.warn{background:#FBF1E6;color:#B5651D;border-color:#F0DCC0}
.ob-tag.good{background:#E9F5EE;color:var(--good);border-color:#C9E8D6}
.plain .ob-tag{background:#EDF1FB;color:#3A5BA0;border-color:#D6E0F2}
.ob-bd{padding:13px 15px;font-size:14px;line-height:1.75;color:var(--ink)}
.ob-bd b{color:var(--accent)}
.tr-adv{border-top:1px dashed var(--line);padding:14px 0 2px;margin-top:13px}
.tr-adv .fld{margin-bottom:12px}
/* 步骤流程指示器（需求翻译器） */
.stepper{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.step{flex:1;min-width:150px;display:flex;align-items:center;gap:11px;background:var(--surface);border:1px solid var(--line);border-radius:13px;padding:12px 14px;box-shadow:var(--shadow)}
.step .n{width:28px;height:28px;flex:none;border-radius:50%;background:var(--accent);color:#fff;font-size:13.5px;font-weight:800;display:flex;align-items:center;justify-content:center}
.step .t{font-size:14px;font-weight:800;color:var(--ink)}
.step .d{font-size:11.5px;color:var(--ink-3);line-height:1.45;margin-top:1px}
/* Agent 语义库 */
.agent-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(238px,1fr));gap:12px;margin-top:14px}
.agent-card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:13px 14px;display:flex;flex-direction:column;gap:5px}
.agent-card .en{font-size:15px;font-weight:800;color:var(--ink)}
.agent-card .cn{font-size:13px;color:var(--accent-2);font-weight:700}
.agent-card .cat{display:inline-block;font-size:10.5px;color:var(--ink-3);background:var(--line-2);border-radius:6px;padding:1px 8px;align-self:flex-start;margin-bottom:2px}
.agent-card .pl{font-size:12.5px;color:var(--ink-2);line-height:1.6}
.agent-card a{font-size:12px;color:var(--accent);font-weight:700;margin-top:2px}
/* AI 语义库：契约层定位卡 + 语义名片 */
.ag-feats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.ag-feat{display:flex;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 13px}
.ag-n{width:26px;height:26px;flex:none;border-radius:8px;background:var(--accent);color:#fff;font-weight:800;font-size:13px;display:flex;align-items:center;justify-content:center}
.ag-t{font-size:13.5px;font-weight:800;color:var(--ink)}
.ag-d{font-size:12px;color:var(--ink-2);line-height:1.6;margin-top:2px}
.agent-card .aj{display:flex;gap:6px;margin-top:4px}
.agent-json{margin:4px 0 0;font-size:11px;line-height:1.55;background:#23221F;color:#E8E4DC;border-radius:9px;padding:10px;overflow:auto;white-space:pre;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.mcp-panel{margin-top:16px;border:1px solid var(--line);border-radius:12px;padding:12px 14px;background:var(--surface)}
.mcp-h{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:12.5px;font-weight:700;color:var(--ink)}
.mcp-code{margin:8px 0 0;font-size:12px;line-height:1.6;background:#23221F;color:#E8E4DC;border-radius:9px;padding:12px;overflow:auto;white-space:pre;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (max-width:768px){ .ag-feats{grid-template-columns:1fr} }
/* AI 图标库 */
.icon-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(148px,1fr));gap:12px;margin-top:4px}
.icon-card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 12px;display:flex;flex-direction:column;align-items:center;gap:10px}
.icon-card svg{width:42px;height:42px;color:var(--icon-color,var(--accent))}
.icon-card .nm{font-size:13px;font-weight:700;color:var(--ink);text-align:center}
.icon-card .copy{margin-top:2px}
/* 颜色选择器 */
.color-bar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:6px 0 14px}
.color-bar .cb-lab{font-size:12px;color:var(--ink-3);margin-right:2px}
.color-dot{width:24px;height:24px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px var(--line);cursor:pointer;transition:transform .12s}
.color-dot:hover{transform:scale(1.12)}
.color-dot.on{box-shadow:0 0 0 2px var(--ink);transform:scale(1.12)}
.color-dot.custom{position:relative;overflow:hidden;background:conic-gradient(red,orange,yellow,lime,aqua,blue,magenta,red)}
.color-dot.custom input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
/* AI 图标库 · 形变动画 */
.morph-panel{display:flex;gap:18px;align-items:center;padding:18px;background:linear-gradient(135deg,#FBFAF7,#F3EFE8);border:1px solid var(--line);border-radius:14px;margin-bottom:16px}
.morph-preview{width:118px;height:118px;flex:none;color:var(--accent);background:#fff;border-radius:18px;box-shadow:0 10px 26px rgba(200,68,46,.12);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:transform .15s}
.morph-preview:active{transform:scale(.96)}
.morph-preview svg{width:74px;height:74px}
.morph-info{flex:1;min-width:0}
.morph-name{font-size:22px;font-weight:800;color:var(--ink);word-break:break-all}
.morph-sub{font-size:13px;color:var(--ink-2);margin:4px 0 12px}
.morph-acts{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
.spring-row{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.spring-lab{font-size:12px;color:var(--ink-3);margin-right:2px}
.icon-search{margin:4px 0 14px}
.inp{width:100%;box-sizing:border-box;padding:10px 12px;border:1px solid var(--line);border-radius:10px;font-size:14px;background:#fff;color:var(--ink);outline:none}
.inp:focus{border-color:var(--accent)}
.icon-card{cursor:pointer;transition:transform .12s,border-color .12s}
.icon-card:hover{transform:translateY(-2px)}
.icon-card.sel{border-color:var(--accent);box-shadow:0 0 0 2px var(--accent-soft)}
/* 为什么这么写（术语白话） */
.why-row{display:flex;gap:12px;padding:10px 0;border-bottom:1px dashed var(--line-2)}
.why-row:last-child{border-bottom:none}
.why-k{flex:none;width:74px;font-size:12.5px;color:var(--ink-3);font-weight:700;padding-top:1px}
.why-v{flex:1;font-size:14px;color:var(--ink);line-height:1.65}
.why-bad .why-v{color:var(--bad)}
.why-good .why-v{color:var(--good)}

/* 收藏 */
.mlist{margin-top:14px}
.mrow{display:flex;align-items:center;gap:12px;padding:13px 15px;border:1px solid var(--line);border-radius:12px;margin-bottom:10px;background:var(--surface)}
.mrow .ic{width:38px;height:38px;border-radius:10px;background:var(--accent-soft);color:var(--accent-2);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;flex:none}
.mrow .tx{flex:1;min-width:0}
.mrow .t1{font-size:14.5px;font-weight:700}
.mrow .t2{font-size:12.5px;color:var(--ink-2)}
.mrow .acts{display:flex;gap:6px;flex:none}
.empty{padding:40px 16px;text-align:center;color:var(--ink-3);font-size:14px}
.empty svg{margin:0 auto 10px;opacity:.45}

.tip{font-size:12.5px;color:var(--ink-3);margin-top:12px;line-height:1.7}
.hide{display:none!important}
.foot{text-align:center;font-size:12px;color:var(--ink-3);padding:26px 0 8px}
.toast{position:fixed;left:50%;bottom:calc(26px + env(safe-area-inset-bottom));transform:translate(-50%,20px);background:var(--ink);color:#fff;padding:11px 18px;border-radius:11px;font-size:14px;opacity:0;pointer-events:none;transition:.22s;z-index:300;max-width:90vw;text-align:center}
.toast.on{opacity:1;transform:translate(-50%,0)}

/* 前后效果对照（真实渲染） */
.vdemo{margin:0 16px 14px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,#fffdfb,#fcfbf9);padding:14px}
.vdemo-h{font-size:11.5px;font-weight:800;color:var(--accent);letter-spacing:.01em;margin-bottom:10px;display:flex;align-items:center;gap:6px;padding-bottom:9px;border-bottom:1px solid var(--line-2)}
.vdemo-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:440px){.vdemo-row{grid-template-columns:1fr}}
.vcell{display:flex;flex-direction:column;min-width:0}
.vb-h{font-size:10.5px;font-weight:800;margin-bottom:7px;display:inline-flex;align-items:center;gap:4px;letter-spacing:.02em}
.vb-h.b{color:var(--bad)} .vb-h.g{color:var(--good)}
.vbx{border-radius:12px;padding:14px 10px;background:var(--stage);border:1px solid var(--stage-line);display:flex;align-items:center;justify-content:center;min-height:88px;overflow:visible;text-align:center}

/* 可交互演示（点击 / 滚动体验） */
.vtips{display:inline-flex;align-items:center;gap:3px;margin-top:6px;font-size:10px;font-weight:700;color:#b5532f;background:var(--accent-soft);border:1px solid #f0d9cf;padding:2px 8px;border-radius:20px;align-self:flex-start}
.vtips svg{width:11px;height:11px;flex:none}
.vbx.good{cursor:pointer;transition:box-shadow .2s var(--ease),transform .12s var(--ease),border-color .2s var(--ease)}
.vbx.good:hover{box-shadow:0 0 0 2px var(--accent-soft);border-color:#eccfc7}
.vbx.good:active{transform:scale(.985)}
.vtry{margin-top:8px;align-self:flex-start;display:inline-flex;align-items:center;gap:5px;font-size:12.5px;font-weight:700;color:#fff;background:var(--accent);border:none;border-radius:9px;padding:8px 15px;cursor:pointer;-webkit-tap-highlight-color:transparent;box-shadow:0 2px 6px rgba(200,68,46,.22)}
.vtry:hover{filter:brightness(1.06)}
.vtry:active{transform:scale(.95)}
.vtry svg{width:13px;height:13px;flex:none}
@media(max-width:400px){.vtry{width:100%;justify-content:center}}
/* 在线对比体验：差距说明 */
.vdemo-diff{margin-top:10px;font-size:11.5px;line-height:1.7;color:var(--ink-2);background:var(--accent-soft);border:1px solid #f0d9cf;border-radius:9px;padding:8px 11px}
.vdemo-diff b{color:var(--accent)}
/* 点击试用通用反馈：高亮「平台提示词」正确做法一侧（before/after 对照的体验感，全站统一） */
.vbx.good.try-pulse{animation:tryPulse .55s ease}
@keyframes tryPulse{0%{box-shadow:0 0 0 0 var(--accent)}55%{box-shadow:0 0 0 5px var(--accent-soft)}100%{box-shadow:0 0 0 0 transparent}}
/* ===== 非导航章大幅前后对照（u-* 演示组件） ===== */
.u-wrap{width:100%;display:flex;flex-direction:column;gap:7px;text-align:left}
.u-cap{font-size:10.5px;font-weight:700;color:#a39d92;letter-spacing:.02em;line-height:1.5}
.u-panel{position:relative;border-radius:10px;background:#fbfaf7;border:1px solid #ece5d8;min-height:96px;display:flex;align-items:center;justify-content:center;gap:10px;padding:12px;overflow:hidden}
.u-ovl{position:absolute;inset:0;background:rgba(32,28,24,.45);display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .25s}
.u-ovl.on{opacity:1;pointer-events:auto}
.u-modal{background:#fff;border-radius:10px;padding:12px 14px;font-size:12px;font-weight:700;color:#3d3a34;box-shadow:0 10px 30px rgba(30,25,20,.28)}
.u-btn{height:34px;padding:0 15px;border-radius:9px;border:0;font-size:12.5px;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:6px;font-family:inherit}
.u-btn.g{background:#1C7A4E;color:#fff}
.u-btn.r{background:#C0392B;color:#fff}
.u-btn.gh{background:#fff;border:1px solid #d9d2c4;color:#5a554c}
.u-tag{padding:5px 10px;border-radius:8px;font-size:11.5px;font-weight:700;background:#fff;border:1px solid #e0d9cc;color:#4a463f;white-space:nowrap}
.u-note{font-size:10px;color:#a39d92}
.u-mono{font-family:ui-monospace,Menlo,Consolas,monospace}
.u-kd{width:11px;height:11px;border-radius:4px;display:inline-block;flex:none}
.u-run .u-kd{animation:u-pulse 2.4s infinite}
.u-rm .u-kd{animation:u-pulse 2.4s infinite}
.u-rm.on .u-kd{animation-play-state:paused}
@keyframes u-pulse{0%,18%{transform:scale(1);opacity:1}40%,86%{transform:scale(.55);opacity:.35}100%{transform:scale(1);opacity:1}}
@keyframes u-blink{0%,42%{opacity:1}58%,90%{opacity:.15}100%{opacity:1}}
.u-blink{animation:u-blink 1.5s infinite}
@keyframes u-fill{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.u-fill{transform-origin:left center;border-radius:99px}
@keyframes u-jit{0%{transform:translateX(0)}25%{transform:translateX(36px)}50%{transform:translateX(72px)}75%{transform:translateX(108px)}100%{transform:translateX(0)}}
.u-jit{animation:u-jit 2.2s steps(4,jump-none) infinite}
.u-jit-sm{animation:u-jit 2.2s cubic-bezier(.45,.05,.2,1) infinite}
@keyframes u-scl{0%{transform:scale(1)}50%{transform:scale(1.28)}100%{transform:scale(1)}}
.u-scl-b{animation:u-scl 2s steps(3,jump-none) infinite}
.u-scl-g{animation:u-scl 2s cubic-bezier(.4,0,.2,1) infinite}
@keyframes u-vscroll{0%,12%{transform:translateY(0)}55%,70%{transform:translateY(-44px)}100%{transform:translateY(0)}}
.u-vscroll{animation:u-vscroll 3.2s ease-in-out infinite}
.u-scroll{height:126px;overflow-y:auto;border-radius:10px;border:1px solid #ece5d8;background:#fbfaf7;text-align:left;-webkit-overflow-scrolling:touch;scrollbar-width:none}
.u-scroll::-webkit-scrollbar{display:none}
.u-stk{position:sticky;top:0;z-index:2}
.u-dk{--ubg:#ffffff;--uink:#26292f;--uline:#e6e0d4}
.u-dk.on{--ubg:#181b21;--uink:#edeff3;--uline:#343947}
.u-theme{background:var(--ubg);color:var(--uink);border:1px solid var(--uline);border-radius:10px;padding:11px 12px;font-size:12px;font-weight:700;transition:background .25s,color .25s,border-color .25s}
.u-lz .im{opacity:.22;transition:opacity .45s}
.u-lz.on .im{opacity:1}
.u-hv{transition:transform .22s cubic-bezier(.4,0,.2,1),box-shadow .22s;cursor:pointer}
.u-hv:hover{transform:translateY(-4px);box-shadow:0 10px 22px rgba(60,50,40,.14)}
.u-hv-b{transition:none;cursor:pointer}
.u-tr-b{width:88px;height:40px;border-radius:9px;background:#E7C9C4;cursor:pointer;flex:none}
.u-tr-b:hover{transform:translateX(48px)}
.u-tr-g{width:88px;height:40px;border-radius:9px;background:#BFE0CE;cursor:pointer;flex:none;transition:transform .35s cubic-bezier(.4,0,.2,1)}
.u-tr-g:hover{transform:translateX(48px)}
.u-tf-b{width:88px;height:40px;border-radius:9px;background:#E7C9C4;cursor:pointer;flex:none;position:relative;left:0;transition:left .35s linear}
.u-tf-b:hover{left:48px}
.u-tf-g{width:88px;height:40px;border-radius:9px;background:#BFE0CE;cursor:pointer;flex:none;transition:transform .35s cubic-bezier(.4,0,.2,1)}
.u-tf-g:hover{transform:translateX(48px)}
.u-ez-b{width:88px;height:40px;border-radius:9px;background:#E7C9C4;cursor:pointer;flex:none;transition:transform .6s linear}
.u-ez-b:hover{transform:translateX(56px)}
.u-ez-g{width:88px;height:40px;border-radius:9px;background:#BFE0CE;cursor:pointer;flex:none;transition:transform .6s cubic-bezier(.34,1.4,.64,1)}
.u-ez-g:hover{transform:translateX(56px)}
.u-ac-b{height:36px;padding:0 16px;border-radius:9px;border:0;background:#1C7A4E;color:#fff;font-size:12.5px;font-weight:800;cursor:pointer;font-family:inherit}
.u-ac-g{height:36px;padding:0 16px;border-radius:9px;border:0;background:#1C7A4E;color:#fff;font-size:12.5px;font-weight:800;cursor:pointer;font-family:inherit;transition:transform .12s,background .12s}
.u-ac-g:active{transform:scale(.93);background:#155e3c}
.u-fi{width:160px;height:36px;border-radius:9px;padding:0 10px;font-size:13px;border:1.5px solid #d9d2c4;background:#fff;font-family:inherit}
.u-fi-b:focus{outline:none}
.u-fi-g:focus{outline:none;border-color:#1C7A4E;box-shadow:0 0 0 3px rgba(28,122,78,.16)}
.m-phone.m-scroll{overflow-y:auto;-webkit-overflow-scrolling:touch;height:176px}
.m-sticky{position:sticky;top:0;z-index:3}
.m-bar.m-sticky{background:var(--accent)}
.m-row{display:flex;flex:1;min-height:0}
.m-side.v-side.on{width:0!important;padding:0!important;opacity:0;overflow:hidden}
.m-act{cursor:pointer;-webkit-tap-highlight-color:transparent}
.m-act:hover{filter:brightness(1.07)}
.m-act:active{transform:scale(.96)}
.m-sub.v-sub,.m-mega.v-mega{display:none}
.m-sub.v-sub.on{display:flex}
.m-mega.v-mega.on{display:grid}
.m-drawer.v-drawer{transform:translateX(-102%);transition:transform .26s ease}
.m-drawer.v-drawer.on{transform:translateX(0)}
.m-overlay.v-ov,.m-overlay.v-ov2{opacity:0;pointer-events:none;transition:opacity .2s}
.m-overlay.v-ov.on,.m-overlay.v-ov2.on{opacity:1;pointer-events:auto}
.m-big{height:42px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;background:var(--ink);color:#fff;transition:height .22s,font-size .22s}
.m-big.shrunk{height:20px;font-size:8px}
.m-small{height:20px;display:flex;align-items:center;justify-content:center;font-size:8px;font-weight:700;background:var(--ink);color:#fff}
.m-dead.shake{animation:dshake .45s}
@keyframes dshake{0%,100%{transform:translateX(0)}20%{transform:translateX(-4px)}40%{transform:translateX(4px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}}
.m-crumb span,.m-crumb b{cursor:pointer}
.m-crumb .on{color:var(--accent)!important}
.m-anchor i{cursor:pointer}

/* ===== 导航章新版流畅演示（nv-*，移植自 Nav Pattern Lab；动效只走 transform/opacity） ===== */
.nv-stage{width:100%;max-width:320px;height:224px;overflow-y:auto;border:1px solid var(--line-2);border-radius:12px;background:#faf8f4;position:relative;text-align:left;-webkit-overflow-scrolling:touch;scroll-behavior:smooth}
.nv-blk{height:34px;background:#eee9df;border-radius:8px;margin:0 12px 10px}
.nv-tip{font-size:11px;color:var(--ink-3);margin:10px 12px}
.nv-page{padding:12px 0 4px}
/* 悬浮吸顶 */
.nv-fnav{position:sticky;top:8px;margin:8px 10px 0;z-index:3;display:flex;align-items:center;justify-content:space-between;background:#fff;border-radius:12px;box-shadow:0 4px 14px rgba(0,0,0,.13);padding:9px 12px;font-size:11.5px;font-weight:700;color:var(--ink)}
.nv-logo{color:var(--accent)}
.nv-links{display:flex;gap:10px;font-weight:600;color:var(--ink-2)}
/* 可折叠侧边栏 */
.nv-sidewrap{display:flex;width:100%;max-width:320px;height:224px;border:1px solid var(--line-2);border-radius:12px;overflow:hidden;background:#fff;text-align:left}
.nv-side{width:128px;flex:none;background:#23262d;color:#e9e7e1;padding:10px 9px;display:flex;flex-direction:column;gap:7px;overflow:hidden;transition:width .3s cubic-bezier(.4,0,.2,1)}
.nv-side.on{width:46px}
.nv-stg{flex:none;width:28px;height:28px;border:0;border-radius:8px;background:rgba(255,255,255,.14);color:#fff;font-size:14px;cursor:pointer;margin-bottom:3px;line-height:1}
.nv-si{display:flex;align-items:center;gap:8px;font-size:11.5px;white-space:nowrap;padding:5px 6px;border-radius:7px}
.nv-si.on,.nv-si:hover{background:rgba(255,255,255,.12)}
.nv-si svg{width:14px;height:14px;flex:none}
.nv-si span{opacity:1;transition:opacity .2s}
.nv-side.on .nv-si span{opacity:0}
.nv-smain{flex:1;padding:12px;min-width:0}
/* 面包屑 */
.nv-crumbox{width:100%;max-width:320px;border:1px solid var(--line-2);border-radius:12px;background:#fff;padding:14px 12px;text-align:left}
.nv-crumb{display:flex;align-items:center;flex-wrap:wrap;gap:6px;font-size:12px;color:#938e85;background:#faf8f4;border:1px solid var(--line-2);border-radius:9px;padding:9px 12px}
.nv-crumb i{font-style:normal;color:#c9c3b8}
.nv-crumb a{cursor:pointer;color:var(--ink-2);position:relative;transition:color .15s}
.nv-crumb a::after{content:"";position:absolute;left:0;bottom:-2px;width:100%;height:1.5px;background:var(--accent);transform:scaleX(0);transform-origin:left;transition:transform .2s}
.nv-crumb a:hover{color:var(--accent)}
.nv-crumb a:hover::after{transform:scaleX(1)}
.nv-crumb b{color:var(--ink)}
.nv-crumb .on{color:var(--accent);font-weight:700}
/* 顶栏 + hover 下拉 / 巨型菜单 */
.nv-barstage{width:100%;max-width:320px;border:1px solid var(--line-2);border-radius:12px;background:#fff;text-align:left}
.nv-topbar{display:flex;align-items:center;gap:12px;background:var(--ink);color:#fff;padding:11px 12px;border-radius:12px 12px 0 0;font-size:11.5px}
.nv-brand{font-weight:800;color:#fff}
.nv-mt{font-weight:600;cursor:default;white-space:nowrap}
.nv-mi{position:relative;cursor:pointer;display:inline-flex;align-items:center;gap:3px}
.nv-mi .arrow{width:10px;height:10px;transition:transform .25s cubic-bezier(.4,0,.2,1)}
.nv-mi:hover .arrow,.nv-mi.on .arrow{transform:rotate(180deg)}
.nv-submenu{position:absolute;top:calc(100% + 8px);left:-8px;min-width:112px;background:#fff;color:var(--ink-2);border:1px solid var(--line);border-radius:10px;box-shadow:0 10px 24px rgba(0,0,0,.14);padding:6px;display:flex;flex-direction:column;gap:2px;opacity:0;visibility:hidden;transform:translateY(-6px);transition:.22s cubic-bezier(.4,0,.2,1);z-index:5}
.nv-mi:hover .nv-submenu,.nv-mi.on .nv-submenu{opacity:1;visibility:visible;transform:none}
.nv-submenu a{font-size:11px;padding:6px 8px;border-radius:6px;color:var(--ink-2);text-decoration:none;white-space:nowrap}
.nv-submenu a:hover{background:var(--accent-soft);color:var(--accent)}
.nv-megap{position:absolute;top:calc(100% + 8px);left:-8px;width:252px;background:#fff;color:var(--ink-2);border:1px solid var(--line);border-radius:12px;box-shadow:0 12px 28px rgba(0,0,0,.15);padding:10px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;opacity:0;visibility:hidden;transform:translateY(-6px);transition:.22s cubic-bezier(.4,0,.2,1);z-index:5}
.nv-mi:hover .nv-megap,.nv-mi.on .nv-megap{opacity:1;visibility:visible;transform:none}
.nv-mc h5{margin:0 0 4px;font-size:10.5px;color:var(--ink)}
.nv-mc a{display:block;font-size:10.5px;padding:3px 0;color:var(--ink-2);text-decoration:none}
.nv-mc a:hover{color:var(--accent)}
/* 汉堡抽屉 */
.nv-phone{position:relative;width:100%;max-width:210px;height:224px;border:1px solid var(--line-2);border-radius:12px;background:#fff;overflow:hidden;text-align:left}
.nv-pbar{height:38px;flex:none;background:var(--ink);color:#fff;display:flex;align-items:center;gap:9px;padding:0 10px;font-size:12px}
.nv-ham{width:30px;height:30px;border:0;background:transparent;color:#fff;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;padding:0}
.nv-ham svg{width:16px;height:16px}
.nv-pbody{padding:12px}
.nv-backdrop{position:absolute;inset:0;background:rgba(20,20,20,.45);opacity:0;pointer-events:none;transition:opacity .25s;z-index:4}
.nv-backdrop.on{opacity:1;pointer-events:auto}
.nv-drawer{position:absolute;top:0;left:0;bottom:0;width:120px;background:#fff;z-index:5;display:flex;flex-direction:column;gap:4px;padding:12px 10px;transform:translateX(-105%);transition:transform .3s cubic-bezier(.4,0,.2,1);box-shadow:6px 0 18px rgba(0,0,0,.14)}
.nv-drawer.on{transform:none}
.nv-drawer a{font-size:12px;font-weight:600;color:var(--ink);padding:8px;border-radius:8px;text-decoration:none}
.nv-drawer a:hover{background:var(--accent-soft);color:var(--accent)}
.nv-dx{position:absolute;top:6px;right:10px;font-size:15px;color:var(--ink-3);cursor:pointer;line-height:1}
/* 全屏遮罩 */
.nv-ovstage{position:relative;width:100%;max-width:320px;height:224px;border:1px solid var(--line-2);border-radius:12px;background:#faf8f4;display:flex;align-items:center;justify-content:center;overflow:hidden;text-align:center}
.nv-openbtn{display:inline-flex;align-items:center;gap:7px;height:38px;padding:0 16px;border:1px solid var(--accent);color:var(--accent);background:#fff;border-radius:10px;font-weight:700;font-size:12.5px;cursor:pointer}
.nv-openbtn svg{width:14px;height:14px}
.nv-ovl{position:absolute;inset:0;background:rgba(24,24,24,.94);display:flex;align-items:center;justify-content:center;opacity:0;pointer-events:none;transition:opacity .28s;z-index:6}
.nv-ovl.on{opacity:1;pointer-events:auto}
.nv-ovx{position:absolute;top:10px;right:14px;font-size:20px;color:#fff;cursor:pointer;line-height:1}
.nv-ovnav{display:flex;flex-direction:column;gap:14px;text-align:center}
.nv-ovnav a{color:#fff;font-size:17px;font-weight:700;text-decoration:none;opacity:0;transform:translateY(12px);transition:.4s cubic-bezier(.4,0,.2,1)}
.nv-ovl.on .nv-ovnav a{opacity:1;transform:none}
.nv-ovl.on .nv-ovnav a:nth-child(1){transition-delay:.05s}
.nv-ovl.on .nv-ovnav a:nth-child(2){transition-delay:.12s}
.nv-ovl.on .nv-ovnav a:nth-child(3){transition-delay:.19s}
.nv-ovl.on .nv-ovnav a:nth-child(4){transition-delay:.26s}
/* 锚点 scrollspy */
.nv-dots{position:absolute;right:8px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:8px;z-index:4}
.nv-dots button{width:9px;height:9px;border-radius:50%;border:0;background:#d8d2c6;cursor:pointer;padding:0;transition:background .2s,transform .2s}
.nv-dots button.on{background:var(--accent);transform:scale(1.25)}
.nv-spyin{padding:12px 24px 12px 12px}
.nv-spyin section{padding:8px 0 14px}
.nv-spyin h5{margin:0 0 8px;font-size:12px;color:var(--ink)}
/* 滚动收缩 */
.nv-hero{height:96px;flex:none;background:linear-gradient(135deg,#C8442E,#A8351F);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:13px;font-weight:800;gap:2px;text-align:center}
.nv-hero small{font-size:10px;font-weight:600;opacity:.85}
.nv-snav{position:sticky;top:0;z-index:3;height:46px;flex:none;display:flex;align-items:center;justify-content:space-between;padding:0 12px;font-size:11.5px;font-weight:700;color:var(--ink);background:rgba(250,248,244,0);transition:height .25s cubic-bezier(.4,0,.2,1),background .25s,box-shadow .25s}
.nv-snav.shrunk{height:32px;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.1)}
.nv-slogo{color:var(--accent)}
.nv-sl{display:flex;gap:10px;font-weight:600;color:var(--ink-2)}
/* 悬停动效 demo：放上鼠标 / 点击都浮起 */
.hl-card{transition:transform .18s ease, box-shadow .18s ease;cursor:pointer;border:1px solid var(--line);border-radius:10px;padding:10px;background:#fff}
.hl-card:hover,.hl-card.on{transform:translateY(-6px);box-shadow:0 10px 22px rgba(60,50,40,.14)}
/* 轮播图 demo：可横向滑动 + 左右按钮切换 */
.cr{width:100%}
.cr-track{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-behavior:smooth;-webkit-overflow-scrolling:touch;border-radius:8px}
.cr-track::-webkit-scrollbar{height:0}
.cr-slide{flex:0 0 100%;height:96px;scroll-snap-align:center;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:15px}
.cr-nav{display:flex;gap:8px;justify-content:center;margin-top:8px}
.cr-nav button{width:34px;height:30px;border:1px solid var(--line);border-radius:8px;background:#fff;cursor:pointer;font-size:15px;color:var(--ink-2);transition:.15s}
.cr-nav button:hover{filter:brightness(1.05)}
.cr-nav button:active{transform:scale(.94)}

/* === 交互组件 demo：表单 / 按钮 / 弹窗 / 动效 === */
.demo-stage{display:flex;flex-direction:column;gap:10px;align-items:stretch;width:100%}
.demo-row{display:flex;gap:8px;align-items:center;flex-wrap:wrap;justify-content:center}
/* 表单 */
.f-field{display:flex;flex-direction:column;gap:5px;text-align:left;width:100%}
.f-field>label{font-size:11px;font-weight:700;color:var(--ink-2)}
.f-input{width:100%;height:38px;border:1px solid var(--line);border-radius:8px;padding:0 11px;font-size:14px;background:#fff;transition:.15s}
.f-input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft)}
.f-sel{position:relative;width:100%;text-align:left}
.f-sel .f-sel-btn{height:38px;border:1px solid var(--line);border-radius:8px;padding:0 11px;display:flex;align-items:center;justify-content:space-between;font-size:14px;background:#fff;cursor:pointer;transition:.15s;color:var(--ink-2)}
.f-sel.on .f-sel-btn{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft);color:var(--ink)}
.f-sel .f-sel-btn .ar{transition:.2s;color:var(--ink-3)}
.f-sel.on .f-sel-btn .ar{transform:rotate(180deg)}
.f-opt{position:absolute;top:calc(100% + 4px);left:0;right:0;background:#fff;border:1px solid var(--line);border-radius:8px;box-shadow:0 10px 26px rgba(0,0,0,.14);padding:5px;display:none;z-index:5;flex-direction:column;gap:2px}
.f-sel.on .f-opt{display:flex}
.f-opt span{padding:7px 9px;border-radius:6px;font-size:13px;cursor:pointer;color:var(--ink-2)}
.f-opt span:hover{background:var(--line-2)} .f-opt span.on{background:var(--accent-soft);color:var(--accent-2);font-weight:600}
.f-sw{width:48px;height:28px;border-radius:15px;background:var(--line);position:relative;cursor:pointer;transition:.2s;flex:none}
.f-sw::after{content:'';position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.25);transition:.2s}
.f-sw.on{background:var(--good)}
.f-sw.on::after{left:23px}
.f-ck{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--ink-2);cursor:pointer}
.f-ck i{width:20px;height:20px;border:1.5px solid var(--line);border-radius:6px;display:flex;align-items:center;justify-content:center;flex:none;color:transparent;transition:.15s;font-size:13px;font-weight:700}
.f-ck.on i{background:var(--accent);border-color:var(--accent);color:#fff}
.f-rd{display:inline-flex;align-items:center;gap:7px;font-size:13px;color:var(--ink-2);cursor:pointer}
.f-rd i{width:19px;height:19px;border:1.5px solid var(--line);border-radius:50%;display:flex;align-items:center;justify-content:center;flex:none}
.f-rd.on i{border-color:var(--accent)} .f-rd.on i::after{content:'';width:10px;height:10px;border-radius:50%;background:var(--accent)}
/* 按钮 */
.b-row{display:flex;gap:9px;align-items:center;flex-wrap:wrap;justify-content:center}
.b-pri{height:38px;padding:0 18px;border-radius:9px;background:var(--accent);color:#fff;font-weight:600;font-size:14px;transition:.12s}
.b-pri.pressed{transform:scale(.95)}
.b-sec{height:38px;padding:0 18px;border-radius:9px;border:1px solid var(--line);background:#fff;color:var(--ink-2);font-size:14px;transition:.12s}
.b-load{height:38px;padding:0 18px;border-radius:9px;background:var(--accent);color:#fff;font-weight:600;font-size:14px;min-width:110px;display:inline-flex;align-items:center;justify-content:center;gap:7px}
.b-load .sp{width:14px;height:14px;border:2px solid rgba(255,255,255,.4);border-top-color:#fff;border-radius:50%;display:none}
.b-load.loading{pointer-events:none;opacity:.85}
.b-load.loading .sp{display:block;animation:dspin .7s linear infinite}
.b-dis{height:38px;padding:0 18px;border-radius:9px;background:var(--accent);color:#fff;font-weight:600;font-size:14px;opacity:.45;cursor:not-allowed}
.b-dis.shake{animation:dshake .45s}
.b-grp{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.b-grp span{height:36px;padding:0 15px;display:inline-flex;align-items:center;font-size:13px;color:var(--ink-2);cursor:pointer;transition:.12s}
.b-grp span+span{border-left:1px solid var(--line)}
.b-grp span.on{background:var(--ink);color:#fff}
.b-ic{width:40px;height:40px;border-radius:50%;border:1px solid var(--line);background:#fff;color:var(--ink-2);display:inline-flex;align-items:center;justify-content:center;cursor:pointer;transition:.12s}
.b-ic.on{background:var(--accent);border-color:var(--accent);color:#fff}
/* 弹窗 */
.mo{position:relative;width:100%;height:140px;border:1px solid var(--line-2);border-radius:10px;background:#f6f4ef;overflow:hidden;display:flex;align-items:center;justify-content:center}
.mo .mo-mask{position:absolute;inset:0;background:rgba(20,18,15,.45);opacity:0;pointer-events:none;transition:.2s;display:flex;align-items:center;justify-content:center}
.mo.on .mo-mask{opacity:1;pointer-events:auto}
.mo .mo-card{width:78%;background:#fff;border-radius:12px;padding:15px;box-shadow:0 14px 40px rgba(0,0,0,.25);transform:scale(.9);transition:.2s}
.mo.on .mo-card{transform:scale(1)}
.mo .mo-card h4{font-size:15px;margin:0 0 6px;color:var(--ink)} .mo .mo-card p{font-size:12.5px;color:var(--ink-2);margin:0 0 12px}
.mo .mo-foot{display:flex;gap:8px;justify-content:flex-end}
.mo .xbtn{height:30px;padding:0 14px;border-radius:8px;border:1px solid var(--line);background:#fff;font-size:12.5px;color:var(--ink-2)}
.mo .xbtn.p{background:var(--accent);border-color:var(--accent);color:#fff}
.dr{position:relative;width:100%;height:140px;border:1px solid var(--line-2);border-radius:10px;background:#f6f4ef;overflow:hidden}
.dr .dr-mask{position:absolute;inset:0;background:rgba(20,18,15,.4);opacity:0;pointer-events:none;transition:.2s}
.dr.on .dr-mask{opacity:1;pointer-events:auto}
.dr .dr-panel{position:absolute;top:0;right:0;height:100%;width:62%;background:#fff;box-shadow:-8px 0 24px rgba(0,0,0,.18);transform:translateX(100%);transition:.25s;padding:14px;display:flex;flex-direction:column;gap:9px;box-sizing:border-box}
.dr.on .dr-panel{transform:translateX(0)}
.dr .dr-panel .dh{font-weight:700;font-size:14px;color:var(--ink)} .dr .dr-item{font-size:13px;color:var(--ink-2);padding:8px 6px;border-radius:8px} .dr .dr-item:hover{background:var(--line-2)}
.pc{position:relative;display:inline-flex}
.pc .pc-box{position:absolute;top:calc(100% + 8px);left:50%;transform:translateX(-50%) scale(.95);background:var(--ink);color:#fff;border-radius:10px;padding:10px 12px;font-size:12.5px;width:158px;opacity:0;pointer-events:none;transition:.16s;z-index:6}
.pc.on .pc-box{opacity:1;transform:translateX(-50%) scale(1);pointer-events:auto}
.pc .pc-box .pc-bt{display:flex;gap:6px;margin-top:9px;justify-content:flex-end}
.pc .pc-bt .pb{height:26px;padding:0 11px;border-radius:7px;font-size:12px;border:none}
.pc .pc-bt .pb.c{background:var(--bad);color:#fff} .pc .pc-bt .pb.x{background:#fff;color:var(--ink-2)}
/* 骨架屏 */
.sk{width:100%;max-width:220px;display:flex;flex-direction:column;gap:9px}
.sk .sk-line{height:11px;border-radius:5px;background:linear-gradient(90deg,#e9e6e0 25%,#f6f4ef 37%,#e9e6e0 63%);background-size:400% 100%;animation:dskel 1.3s ease infinite}
.sk .sk-line.w1{width:68%} .sk .sk-line.w2{width:92%} .sk .sk-line.w3{width:52%} .sk .sk-line.w4{width:80%}
.sk .sk-real{display:none;flex-direction:column;gap:5px;text-align:left;font-size:12.5px;color:var(--ink-2)}
.sk.on .sk-line{display:none} .sk.on .sk-real{display:flex}
.sk .sk-real b{color:var(--ink)}
@keyframes dskel{0%{background-position:100% 0}100%{background-position:-100% 0}}
/* 动效 */
.an-wrap{width:100%;display:flex;flex-direction:column;gap:10px;align-items:center}
.an-fade{width:120px;height:40px;border-radius:9px;background:var(--accent-soft);color:var(--accent-2);display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600;opacity:0;transition:opacity .35s,transform .35s;transform:translateY(6px)}
.an-fade.on{opacity:1;transform:translateY(0)}
.an-flip{width:120px;height:64px;perspective:600px}
.an-flip .inner{position:relative;width:100%;height:100%;transition:transform .5s;transform-style:preserve-3d;cursor:pointer}
.an-flip.flipped .inner{transform:rotateY(180deg)}
.an-flip .face{position:absolute;inset:0;border-radius:10px;backface-visibility:hidden;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600}
.an-flip .face.f{background:var(--accent-soft);color:var(--accent-2)} .an-flip .face.b{background:var(--ink);color:#fff;transform:rotateY(180deg)}
.an-li{display:flex;flex-direction:column;gap:6px;width:100%;max-width:200px}
.an-li .li{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px;color:var(--ink-2);opacity:0;transform:translateX(-8px);transition:.3s}
.an-li.on .li{opacity:1;transform:translateX(0)}
.an-li.on .li:nth-child(2){transition-delay:.12s} .an-li.on .li:nth-child(3){transition-delay:.24s} .an-li.on .li:nth-child(4){transition-delay:.36s}
.an-bar{width:100%;max-width:200px;height:8px;border-radius:5px;background:var(--line-2);overflow:hidden}
.an-bar .fill{height:100%;width:0;background:var(--accent);border-radius:5px;transition:width 1.4s ease}
.an-bar.run .fill{width:100%}
.an-bar.half .fill{width:62%}
.an-tab{display:flex;flex-direction:column;gap:9px;width:100%;max-width:200px}
.an-tab .tabs2{display:flex;gap:4px}
.an-tab .tabs2 button{flex:1;height:32px;border-radius:8px;border:1px solid var(--line);background:#fff;font-size:12.5px;color:var(--ink-2);cursor:pointer;transition:.12s}
.an-tab .tabs2 button.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.an-tab .panels{position:relative}
.an-tab .panels .p{display:none;font-size:12.5px;color:var(--ink-2);padding:10px;border:1px solid var(--line-2);border-radius:8px;background:#fff}
.an-tab .panels .p.on{display:block;animation:dfade .3s}
@keyframes dfade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
@keyframes dspin{to{transform:rotate(360deg)}}

/* 移动端 */
@media(max-width:900px){
  .lib{grid-template-columns:1fr}
  .cnav-wrap{position:static;display:flex;gap:6px;overflow-x:auto;padding:8px}
  .cnav-wrap .ct{display:none}
  .cnav{flex:none;white-space:nowrap;border:1px solid var(--line);background:var(--surface)}
  .cnav-cnt{margin-left:6px}
}
@media(max-width:640px){
  .hero{padding:22px 18px} .hero h1{font-size:24px}
  .wrap{padding:0 14px} .top-in{padding:10px 14px}
}
"""

# ============================================================================
# 组装完整 HTML
# ============================================================================
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="icon" href="/assets/logo.svg">
<title>码译 · VibeCode | 说要做什么，直接拿到可复制的 AI 提示词</title>
<meta name="description" content="面向只会说白话、不懂前端术语的 vibe coding 新手：选一个「让用户点 / 填 / 看」的动作，平台自动翻译成专业 AI 提示词，网页 / App / 小程序差异也帮你分清楚，复制即用。">
<meta name="keywords" content="vibe coding,前端术语,AI提示词,开发术语翻译,垂直居中,响应式,大白话翻译,前端小白,Cursor提示词,小程序适配">
<meta name="author" content="码译 · VibeCode">
<meta name="robots" content="index,follow">
<meta name="renderer" content="webkit">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:title" content="码译 · VibeCode | 说要做什么，直接拿 AI 提示词">
<meta property="og:description" content="不会写提示词？选一个动作（点 / 填 / 看 / 等反馈 / 滑），平台翻成专业提示词，复制给 Cursor、通义灵码、Claude 直接用。">
<meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://vibecode-terms.example.com/">
<script type="application/ld+json">
__JSONLD__
</script>
<style>__CSS__</style>
</head>
<body>

<header class="top">
  <div class="top-in">
    <a class="logo" href="#top">
      <span class="logo-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 6l-5 6 5 6"/><path d="M16 6l5 6-5 6"/></svg></span>
      <span><span class="logo-tx">码译 · VibeCode</span><br><span class="logo-sub">选个动作，直接拿提示词</span></span>
    </a>
    <div class="top-act">
      <button class="tbtn" id="btnExport"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>导出收藏</button>
      <button class="tbtn" id="btnImport"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 8l5-5 5 5"/><path d="M12 3v12"/></svg>导入</button>
      <input type="file" id="fileIn" accept=".json,application/json" class="hide">
    </div>
  </div>
</header>

<div class="wrap" id="top">

  <nav class="tabs" id="tabs">
    <button class="tab on" data-tab="wk">翻译器</button>
    <button class="tab" data-tab="lib">组件库<span class="n" id="nLib">__NLIB__</span></button>
    <button class="tab" data-tab="agent">Agent 语义库</button>
    <button class="tab" data-tab="icons">AI 图标库</button>
    <button class="tab" data-tab="colors">AI 配色</button>
    <button class="tab" data-tab="my">我的收藏<span class="n" id="nMy">0</span></button>
  </nav>

  <section class="hero" id="hero">
    <h1>不要让 AI 去猜，<span class="hl">而是让 AI 去做</span><br>——把一句大白话，翻成 AI 听得懂的专业提示词</h1>
    <p>这是一个给 vibe coding 新手用的 <b>需求翻译器</b>。你不用懂任何前端术语——先选一个想让用户做的动作（点一下 / 填一下 / 看一个东西 / 等一个反馈 / 滑一下翻页），再选平台与风格，页面立刻生成一段<b>能直接复制给 Cursor / 通义灵码 / Claude</b> 的专业提示词。底下「术语白话」抽屉会告诉你为什么这么写。需要查具体效果对照，去「组件库」看每个组件的错误 vs 正确真实渲染。</p>
    <div class="hint">
      <span class="chip-soft">零基础友好</span>
      <span class="chip-soft">复制即用</span>
      <span class="chip-soft">__NTERM__ 个高频术语</span>
      <span class="chip-soft">三端平台区分</span>
      <span class="chip-soft">每个都能点开体验</span>
    </div>
  </section>

  <!-- 速查（组件库） -->
  <div id="pgLib" class="hide">
    <div class="lib">
      <aside class="cnav-wrap">
        <div class="ct">章节</div>
        __CNAV__
      </aside>
      <div class="lib-main">
        <div class="card" style="margin-top:0">
          <div class="card-bd">
            <div class="search" style="position:relative">
              <svg style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#938E85" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
              <input type="text" id="q" placeholder="搜大白话或术语：垂直居中 / 吸顶 / 安全区 / z-index …" autocomplete="off" style="width:100%;height:46px;padding:0 12px 0 36px;border:1px solid var(--line);border-radius:11px;background:#fff;font-size:16px">
            </div>
            <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
              <button class="tbtn" id="btnFavOnly">只看收藏</button>
              <button class="tbtn" id="btnClearQ">清空搜索</button>
            </div>
          </div>
        </div>
        __CHAPTERS__
        __ROADMAP__
      </div>
    </div>
  </div>

  <!-- 工坊（需求选择器，首页） -->
  <div id="pgWk">
    <div class="stepper">
      <div class="step"><span class="n">1</span><div><div class="t">说需求</div><div class="d">大白话 / 语音都行</div></div></div>
      <div class="step"><span class="n">2</span><div><div class="t">看翻译</div><div class="d">确认 + 学个词</div></div></div>
      <div class="step"><span class="n">3</span><div><div class="t">复制用</div><div class="d">贴给 AI 即用</div></div></div>
    </div>
    <div class="wk">
      <!-- 输入卡：大输入框 -->
      <div class="card" style="margin-top:0">
        <div class="card-hd"><h3>描述你想要的效果</h3><span class="sub">不用懂术语，怎么想就怎么写</span></div>
        <div class="card-bd">
          <div class="tr-input-wrap">
            <textarea id="trInput" class="tr-input" rows="3" placeholder="比如：卡片鼠标放上去的时候微微抬起一点，加个阴影"></textarea>
            <button class="tr-mic" id="trMic" type="button" title="语音输入（Chrome 可用，无需联网）" aria-label="语音输入">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>
            </button>
          </div>
          <div class="tr-examples" id="trExamples">
            <span class="ex-label">不知道怎么写？点一个试试：</span>
            <button data-ex="点一下">点一下</button>
            <button data-ex="填一下">填一下</button>
            <button data-ex="看一个东西">看一个东西</button>
            <button data-ex="等个反馈">等个反馈</button>
            <button data-ex="滑一下翻页">滑一下翻页</button>
            <button data-ex="鼠标放上去动一下">鼠标放上去动一下</button>
          </div>
          <div class="tr-actions">
            <div class="seg" id="wkPlat">
              <button data-v="web" class="on">网页 Web</button>
              <button data-v="app">手机 App</button>
              <button data-v="mini">微信小程序</button>
            </div>
            <button class="tbtn p big" id="btnTranslate" type="button">翻译 →</button>
          </div>
          <div class="tip">支持打字、语音（Chrome 内置，无需联网）。截图理解需在线版，这里先用文字描述效果最好。</div>
        </div>
      </div>
      <!-- 输出卡：三样东西 -->
      <div class="card tr-result hide" id="trResult" style="margin-top:0">
        <div class="card-hd"><h3>翻译结果</h3><span class="sub" id="trMatch"></span></div>
        <div class="card-bd">
          <div class="out-block plain">
            <div class="ob-h"><span class="ob-tag">大白话确认</span>这是你想要的效果吗？</div>
            <div class="ob-bd" id="trPlain"></div>
          </div>
          <div class="out-block term">
            <div class="ob-h"><span class="ob-tag warn">专业术语版</span>顺便认识一个词（用多了自然记住）</div>
            <div class="ob-bd" id="trTerm"></div>
          </div>
          <div class="out-block prompt">
            <div class="ob-h"><span class="ob-tag good">一键复制 Prompt</span>直接贴给 Cursor / Claude Code / v0</div>
            <textarea class="out" id="wkOut" spellcheck="false"></textarea>
            <div class="wk-ft">
              <span class="wk-len" id="wkLen" style="margin-right:auto;color:var(--muted,#888);font-size:13px"></span>
              <button class="tbtn p" id="btnCopy">复制提示词</button>
              <button class="tbtn" id="btnSaveWk">收藏这个术语</button>
              <button class="tbtn ghost" id="btnAdvance" type="button">手动精修 ▾</button>
            </div>
            <div class="tr-adv hide" id="trAdv">
              <div class="fld"><label>视觉风格</label><div class="chips" id="wkStyle"></div></div>
              <div class="fld"><label>主色</label><div class="swatches" id="wkColor"></div></div>
              <div class="fld" style="margin-bottom:0"><label>附加要求（可多选）</label><div class="chips" id="wkExtra"></div></div>
              <div class="fld" style="margin-bottom:0"><label>或手动指定组件</label><select class="sel" id="wkTerm"></select></div>
            </div>
          </div>
          <!-- 为什么这么写（术语白话） -->
          <div class="out-block why">
            <div class="ob-h"><span class="ob-tag">术语白话</span>想知道为什么这么写、常见坑在哪？</div>
            <div class="wk-ft">
              <button class="tbtn ghost" id="btnWhy" type="button">展开解释</button>
            </div>
            <div class="ob-bd hide" id="wkWhy"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 收藏 -->
  <div id="pgMy" class="hide">
    <div class="card" style="margin-top:18px">
      <div class="card-hd"><h3>我收藏的术语</h3><span class="sub" id="mySub"></span></div>
      <div class="card-bd">
        <div class="mlist" id="myList"></div>
        <div class="tip">收藏只是书签，方便回头查找；数据只存在你本机浏览器，导出可做备份。</div>
      </div>
    </div>
  </div>

  <!-- Agent 语义库（接 VibeHub 开源词条） -->
  <div id="pgAgent" class="hide">
    <div class="card" style="margin-top:18px">
      <div class="card-hd"><h3>AI 语义库 · 组件契约层</h3><span class="sub">组件库给人看，这一层给 AI 读 · 让 AI 不靠猜</span></div>
      <div class="card-bd">
        <div class="ag-feats">
          <div class="ag-feat"><div class="ag-n">1</div><div><div class="ag-t">语义名片</div><div class="ag-d">每个组件一份机器可读 JSON：什么时候用、怎么定位、边界在哪。AI 读名片干活，不靠猜。</div></div></div>
          <div class="ag-feat"><div class="ag-n">2</div><div><div class="ag-t">MCP 直连</div><div class="ag-d">通过 MCP 暴露给 Cursor / Claude Code：说人话 → 返回组件契约 → 精准定位、修改、组合。</div></div></div>
          <div class="ag-feat"><div class="ag-n">3</div><div><div class="ag-t">定义标准</div><div class="ag-d">组件库是「给人用的组件规范」，语义库是「给 AI 用的组件契约」。前者是基础，后者是叠加在其上的机器可读结构。</div></div></div>
        </div>
        <div class="search" style="position:relative;margin-top:14px">
          <svg style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#938E85" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
          <input type="text" id="aq" placeholder="说人话搜：长留言输入 / 弹窗确认 / 未读红点 …" autocomplete="off" style="width:100%;height:46px;padding:0 12px 0 36px;border:1px solid var(--line);border-radius:11px;background:#fff;font-size:16px">
        </div>
        <div class="chips" id="agentCats" style="margin-top:10px"></div>
        <div class="agent-grid" id="agentGrid"></div>
        <div class="mcp-panel">
          <div class="mcp-h"><span>通过 MCP 暴露给 AI —— Cursor / Claude Code 配置后可直接调用</span><button class="sm" id="btnCopyMcp" type="button">复制 MCP 配置</button></div>
          <pre class="mcp-code" id="mcpCode">// ① 项目里声明（.mcp.json）
{ "mcpServers": { "vibe-semantics": { "command": "npx", "args": ["vibe-semantics-mcp"] } } }

// ② AI 直接说人话调用，拿到的就是契约而不是猜测
find_component({ "intent": "给一段较长的留言做输入" })
→ {
  "$contract": "vibe-semantic/1.0",
  "id": "textarea",
  "zh": "多行输入",
  "category": "表单",
  "intent": "一行不够，给一段较长的留言用多行输入。",
  "locate": "[data-vibe='textarea']"
}</pre>
        </div>
        <div class="tip">契约结构 vibe-semantic/1.0：intent = 触发场景（人话描述），locate = 定位约定（data-vibe 属性），zh / category 与组件库一一对齐。已覆盖组件库全部 __NLIB__ 个组件——每张组件卡上的「在 AI 语义库看契约 →」都能双向解析到这里的契约。</div>
      </div>
    </div>
  </div>

  <!-- AI 图标库：Lucide 开源图标 + Morphcons 形变动画（均内联，零依赖） -->
  <div id="pgIcons" class="hide">
    <div class="card" style="margin-top:18px">
      <div class="card-hd"><h3>AI 图标库</h3><span class="sub">开源 Lucide 图标 · 点一下就能「变形」 · 零依赖</span></div>
      <div class="card-bd">
        <div class="morph-panel">
          <div class="morph-preview" id="morphPreview" title="点我随机变形">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path id="morphPath" d=""></path></svg>
          </div>
          <div class="morph-info">
            <div class="morph-name" id="morphName">bot</div>
            <div class="morph-sub">点下方任意图标，上方大图会丝滑「变形」成它</div>
            <div class="morph-acts">
              <button class="sm copy" id="btnCopyIcon">复制当前 SVG</button>
              <button class="sm" id="btnRandomIcon">随机变形</button>
            </div>
            <div class="spring-row" id="springRow">
              <span class="spring-lab">动画手感</span>
              <button class="chip on" data-spring="smooth">顺滑</button>
              <button class="chip" data-spring="snappy">利落</button>
              <button class="chip" data-spring="bouncy">弹跳</button>
            </div>
            <div class="spring-row" id="springColorRow">
              <span class="spring-lab">图标颜色</span>
              <span class="color-dot on" data-c="reset" style="background:#C8442E" title="默认色"></span>
              <span class="color-dot" data-c="#1A1A1A" style="background:#1A1A1A" title="墨黑"></span>
              <span class="color-dot" data-c="#2E8B72" style="background:#2E8B72" title="青绿"></span>
              <span class="color-dot" data-c="#3B6EA5" style="background:#3B6EA5" title="海蓝"></span>
              <span class="color-dot" data-c="#7A4FB0" style="background:#7A4FB0" title="紫"></span>
              <span class="color-dot custom" title="自定义"><input type="color" value="#E07B39"></span>
            </div>
          </div>
        </div>
        <div class="icon-search"><input id="iconQ" class="inp" placeholder="搜索图标（中/英文，如 机器人 / bot）" /></div>
        <div class="icon-grid" id="iconGrid"></div>
        <div class="tip">图标本体来自开源项目 <b>Lucide</b>（ISC 许可），形变动画引擎来自 <b>Morphcons</b>（MIT 许可），两者均已内联进本页、离线可用。点小图标 → 上方大图变形过去；点「复制 SVG」→ 拿走代码。</div>
      </div>
    </div>
  </div>

  <!-- AI 配色方案库（100 套，SEO 友好：语义化 article + 可读 hex + JSON-LD） -->
  <div id="pgColors" class="hide">
    <div class="card" style="margin-top:18px">
      <div class="card-hd"><h3>AI 配色方案库</h3><span class="sub">100 套网页 / App / 品牌配色 · 色值可一键复制 · 零依赖</span></div>
      <div class="card-bd">
        __COLORS__
      </div>
    </div>
  </div>

  <div class="foot">Vibe Coding 术语词典 · 单文件离线可用 · 数据保存在本机浏览器 · 面向只会说白话的 vibe coding 新手</div>
</div>

<div class="toast" id="toast"></div>

<script>__MORPH_JS__</script>
<script>
__TERMS_JS__
var PLAT = __PLAT__;
var STYLES = ["现代简约","企业级中后台","可爱圆润","暗色主题","玻璃拟态"];
var COLORS = [["#C8442E","朱红"],["#3B6EA5","海蓝"],["#2E8B72","青绿"],["#C08A2E","琥珀"],["#5B5852","石墨"],["#7A4FB0","紫"]];
var EXTRAS = ["无障碍 a11y（键盘+aria）","响应式适配移动端","支持深色模式","关键代码中文注释","包含错误/正确对比","零外部依赖单文件"];

/* ---------- 状态 ---------- */
var KEY = "wb_vibecode_v1";
var favs = {};   // id -> true
var state = { tab:"wk", intent:"all", q:"", favOnly:false, plat:"web",
  style:"现代简约", color:"#C8442E", extras:["零外部依赖单文件","关键代码中文注释"] };
var wkTerm = TERMS.length ? TERMS[0].id : "";
var agentQuery = "", agentCat = "all";

/* ---------- 数据层 ---------- */
function load(){
  try{ var o = JSON.parse(localStorage.getItem(KEY));
    if(o && typeof o==="object"){ favs = o.favs||{}; state = Object.assign(state, o.state||{}); wkTerm = o.wkTerm||wkTerm; }
  }catch(e){}
}
function save(){
  try{ localStorage.setItem(KEY, JSON.stringify({favs:favs, state:state, wkTerm:wkTerm, ver:1})); }catch(e){}
}

/* ---------- 工具 ---------- */
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
function termById(id){ for(var i=0;i<TERMS.length;i++){ if(TERMS[i].id===id) return TERMS[i]; } return null; }
function toast(m){ var t=document.getElementById("toast"); t.textContent=m; t.classList.add("on"); clearTimeout(t._t); t._t=setTimeout(function(){t.classList.remove("on");},1800); }
function copyText(t){ if(navigator.clipboard && navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(function(){toast("已复制到剪贴板");},function(){fallbackCopy(t);}); } else { fallbackCopy(t); } }
function fallbackCopy(t){ var ta=document.createElement("textarea"); ta.value=t; ta.style.position="fixed"; ta.style.opacity="0"; document.body.appendChild(ta); ta.select(); try{document.execCommand("copy"); toast("已复制到剪贴板");}catch(e){toast("复制失败，请手动选择");} document.body.removeChild(ta); }

/* ---------- 计算层 ---------- */
function filteredTerms(){
  var q = state.q.trim().toLowerCase();
  var out = [];
  for(var i=0;i<TERMS.length;i++){
    var t = TERMS[i];
    if(state.favOnly && !favs[t.id]) continue;
    if(q){ var hay=(t.speak+" "+t.cn+" "+t.en+" "+t.anti).toLowerCase(); if(hay.indexOf(q)===-1) continue; }
    out.push(t);
  }
  return out;
}
function buildPrompt(){
  var t = termById(wkTerm); if(!t) return "请先选择术语。";
  var p = PLAT[state.plat];
  var L = [];
  L.push("你是一位资深前端工程师。我正在做【"+p.name+"】项目，想实现【"+t.cn+"】（专业术语："+t.en+"）。");
  L.push("");
  L.push("## 一、我想达到的效果");
  L.push(t.speak + "。");
  L.push("");
  L.push("## 二、规范做法");
  L.push("- 正确思路：" + t.fix);
  L.push("- 请避免的反模式：" + t.anti);
  L.push("");
  L.push("## 三、平台约束（"+p.name+"）");
  L.push(p.cons);
  L.push("- 该平台特别注意：" + t.plat[state.plat]);
  L.push("");
  L.push("## 四、视觉规范");
  L.push("- 整体风格：" + state.style);
  L.push("- 主色：" + state.color + "（中性色用 #5B5852 / #ECE8E1）");
  L.push("- 字号≥16px，间距用 8px 栅格，圆角 10px");
  if(state.extras.length){ L.push(""); L.push("## 五、附加要求"); state.extras.forEach(function(x){ L.push("- "+x); }); }
  L.push("");
  L.push("## 六、交付格式");
  L.push("- 输出完整可运行代码，关键处写中文注释");
  L.push("- 先给 3 行效果描述，再给代码；最后附 50 字以内使用说明");
  return L.join("\\n");
}

/* ---------- 渲染层（单向：只由 refreshAll 调度） ---------- */
function renderNav(){
  var navs = document.querySelectorAll(".cnav");
  var cur = state.favOnly ? -1 : currentChapter();
  navs.forEach(function(n){ n.classList.toggle("on", parseInt(n.getAttribute("data-ch"),10)===cur); });
}
function currentChapter(){
  var secs = document.querySelectorAll(".chap");
  for(var i=0;i<secs.length;i++){
    var r = secs[i].getBoundingClientRect();
    if(r.top <= 120) return parseInt(secs[i].getAttribute("id").replace("chap-",""),10);
  }
  return 0;
}
function renderCards(){
  var list = filteredTerms();
  // 隐藏不匹配的卡片
  document.querySelectorAll(".term").forEach(function(el){
    var t = termById(el.id.replace("t-",""));
    if(!t) return;
    var show = true;
    if(state.favOnly && !favs[t.id]) show=false;
    var q = state.q.trim().toLowerCase();
    if(q){ var hay=(t.speak+" "+t.cn+" "+t.en+" "+t.anti).toLowerCase(); if(hay.indexOf(q)===-1) show=false; }
    el.classList.toggle("hide", !show);
  });
  // 空态
  var emptyEl = document.getElementById("libEmpty");
  if(!list.length){
    if(!emptyEl){ emptyEl=document.createElement("div"); emptyEl.id="libEmpty"; emptyEl.className="empty"; emptyEl.innerHTML='<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>没有匹配的术语，换个说法试试～'; document.querySelector(".lib-main").appendChild(emptyEl); }
    emptyEl.classList.remove("hide");
  } else if(emptyEl){ emptyEl.classList.add("hide"); }
  // 收藏星标状态
  document.querySelectorAll(".star").forEach(function(s){ s.classList.toggle("on", !!favs[s.getAttribute("data-id")]); });
}
function renderCounts(){
  document.getElementById("nLib").textContent = TERMS.length;
  document.getElementById("nMy").textContent = Object.keys(favs).length;
}
function renderMy(){
  var list = document.getElementById("myList");
  var ids = Object.keys(favs);
  document.getElementById("mySub").textContent = ids.length ? ("共 "+ids.length+" 个") : "";
  if(!ids.length){ list.innerHTML = '<div class="empty"><svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>还没有收藏。在「组件库」点卡片右上角的星标即可收藏。</div>'; return; }
  var h="";
  ids.forEach(function(id){ var t=termById(id); if(!t) return;
    h += '<div class="mrow"><div class="ic">'+esc(t.cn.slice(0,2))+'</div><div class="tx"><div class="t1">'+esc(t.cn)+'</div><div class="t2">'+esc(t.speak)+' · '+esc(t.en)+'</div></div><div class="acts"><button class="sm copy" data-id="'+id+'">复制</button><button class="sm dg" data-un="'+id+'">取消收藏</button></div></div>';
  });
  list.innerHTML = h;
}
function renderWk(){
  document.getElementById("wkOut").value = buildPrompt();
  var len = buildPrompt().length;
  document.getElementById("wkLen").textContent = len + " 字";
}
function renderWkWhy(){
  var el = document.getElementById("wkWhy"); if(!el) return;
  var t = termById(wkTerm); if(!t){ el.innerHTML=""; return; }
  var p = t.plat[state.plat] || "";
  el.innerHTML =
    '<div class="why-row"><span class="why-k">用户口语</span><span class="why-v">'+esc(t.speak)+'</span></div>' +
    '<div class="why-row"><span class="why-k">专业术语</span><span class="why-v">'+esc(t.cn)+'（'+esc(t.en)+'）</span></div>' +
    '<div class="why-row why-bad"><span class="why-k">常见反模式</span><span class="why-v">'+esc(t.anti)+'</span></div>' +
    '<div class="why-row why-good"><span class="why-k">正确做法</span><span class="why-v">'+esc(t.fix)+'</span></div>' +
    (p ? '<div class="why-row"><span class="why-k">本平台注意</span><span class="why-v">'+esc(p)+'</span></div>' : '');
}
/* ---------- 翻译器：把大白话翻成术语 + Prompt ---------- */
function matchTerm(input){
  var q = (input||"").trim(); if(!q) return null;
  var ql = q.toLowerCase();
  var clean = q.replace(/[\\s，。、！？,.!?；;：:（）()""''「」—]/g,"");
  var grams=[]; for(var i=0;i<clean.length-1;i++){ grams.push(clean.substr(i,2)); } if(clean.length===1) grams.push(clean);
  if(!grams.length) return null;
  var best=null, bs=0;
  for(var k=0;k<TERMS.length;k++){
    var t=TERMS[k];
    var hay=(t.speak+" "+t.cn+" "+t.en+" "+t.anti+" "+t.fix).toLowerCase();
    var score=0;
    for(var g=0;g<grams.length;g++){ if(hay.indexOf(grams[g])>=0) score++; }
    if(t.cn && ql.indexOf(t.cn.toLowerCase())>=0) score+=4;
    if(t.en && ql.indexOf(t.en.toLowerCase())>=0) score+=4;
    if(t.cn && t.cn.toLowerCase().indexOf(ql)>=0) score+=3;
    if(ql.length<=4 && hay.indexOf(ql)>=0) score+=4;
    if(score>bs){ bs=score; best=t; }
  }
  return bs>=2 ? best : null;
}
function translate(){
  var inputEl=document.getElementById("trInput"); var input=inputEl.value;
  var res=document.getElementById("trResult"); var matchEl=document.getElementById("trMatch");
  if(!input.trim()){ inputEl.classList.add("shake"); setTimeout(function(){inputEl.classList.remove("shake");},500); inputEl.focus(); return; }
  var t=matchTerm(input);
  if(!t){
    res.classList.remove("hide");
    matchEl.textContent="没完全匹配";
    document.getElementById("trPlain").innerHTML="暂时没找到特别贴合的术语。换个更具体的说法，或去「组件库」翻翻看？";
    document.getElementById("trTerm").innerHTML="小提示：描述得具体一点更好命中，例如「卡片鼠标放上去抬起」「点击按钮提交表单」「弹窗确认后再删除」。";
    document.getElementById("wkOut").value=""; document.getElementById("wkLen").textContent="";
    sv(res); return;
  }
  wkTerm=t.id; var sel=document.getElementById("wkTerm"); if(sel) sel.value=t.id;
  matchEl.textContent="匹配到："+t.cn+" · "+t.en;
  document.getElementById("trPlain").innerHTML="我理解你想做：<b>"+esc(t.speak)+"</b>。<br>如果理解得对，直接复制下面的提示词就能用；如果偏了，换个说法再试一次。";
  document.getElementById("trTerm").innerHTML="专业上这叫 <b>"+esc(t.cn)+"（"+esc(t.en)+"）</b>。<br>"+esc(t.fix);
  refreshAll();
  res.classList.remove("hide");
  sv(res);
}
function startVoice(){
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){ toast("当前浏览器不支持语音，换 Chrome 试试"); return; }
  var rec=new SR(); rec.lang="zh-CN"; rec.interimResults=false; rec.maxAlternatives=1;
  var mic=document.getElementById("trMic"); mic.classList.add("on");
  rec.onresult=function(e){ var txt=e.results[0][0].transcript; document.getElementById("trInput").value=txt; mic.classList.remove("on"); translate(); };
  rec.onerror=function(){ mic.classList.remove("on"); toast("语音没听清，再试一次"); };
  rec.onend=function(){ mic.classList.remove("on"); };
  try{ rec.start(); }catch(err){ mic.classList.remove("on"); }
}
function refreshAll(){
  renderNav(); renderCards(); renderCounts(); renderMy(); renderWk(); renderWkWhy();
}

/* ---------- Agent 语义库 / AI 图标库 渲染 ---------- */
var agentList=[];
function agSlug(en){ return (en||"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,""); }
function agContract(t){
  return { "$contract":"vibe-semantic/1.0", "id":agSlug(t.en), "zh":t.cn, "category":t.cat, "intent":t.pl, "locate":"[data-vibe='"+agSlug(t.en)+"']" };
}
function renderAgentCats(){
  var box = document.getElementById("agentCats"); if(!box) return;
  var cats = {}; AGENT_TERMS.forEach(function(t){ cats[t.cat] = 1; });
  var html = '<button class="chip' + (agentCat==="all"?" on":"") + '" data-cat="all">全部</button>';
  Object.keys(cats).forEach(function(c){ html += '<button class="chip' + (agentCat===c?" on":"") + '" data-cat="' + esc(c) + '">' + esc(c) + '</button>'; });
  box.innerHTML = html;
}
function renderAgent(){
  var grid = document.getElementById("agentGrid"); if(!grid) return;
  var q = agentQuery.trim().toLowerCase();
  var list = AGENT_TERMS.filter(function(t){
    if(agentCat!=="all" && t.cat!==agentCat) return false;
    if(q){ var hay=(t.en+" "+t.cn+" "+t.cat+" "+t.pl+" "+agSlug(t.en)).toLowerCase(); if(hay.indexOf(q)===-1) return false; }
    return true;
  });
  agentList = list;
  if(!list.length){ grid.innerHTML = '<div class="empty">没有匹配的语义，换个词试试～</div>'; return; }
  var h = "";
  list.forEach(function(t, i){
    h += '<div class="agent-card"><span class="cat">'+esc(t.cat)+'</span>'
       + '<div class="en">'+esc(t.en)+'</div>'
       + '<div class="cn">'+esc(t.cn)+'</div>'
       + '<div class="pl">'+esc(t.pl)+'</div>'
       + '<div class="aj"><button class="sm aj-toggle" data-i="'+i+'" type="button">语义名片 ▾</button>'
       + '<button class="sm aj-copy" data-i="'+i+'" type="button">复制 JSON</button></div>'
       + '<pre class="agent-json hide" data-i="'+i+'">'+esc(JSON.stringify(agContract(t),null,2))+'</pre></div>';
  });
  grid.innerHTML = h;
}
function iconSvg(it){
  if(it.node && window.canonicalD){
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="'+window.canonicalD(it.node)+'"/></svg>';
  }
  return it.svg || "";
}
var iconQuery="", morphInst=null, curIconNode=null, springPreset="smooth";
function renderIcons(){
  var grid = document.getElementById("iconGrid"); if(!grid) return;
  var q = iconQuery.trim().toLowerCase();
  var h = "";
  ICONS.forEach(function(it, i){
    if(q){ var hay=(it.nm+" "+(it.id||"")).toLowerCase(); if(hay.indexOf(q)===-1) return; }
    var sel = (curIconNode && it.node===curIconNode) ? " sel" : "";
    h += '<div class="icon-card'+sel+'" data-i="'+i+'">'+iconSvg(it)
       + '<div class="nm">'+esc(it.nm)+'</div>'
       + '<button class="sm copy" data-i="'+i+'">复制 SVG</button></div>';
  });
  grid.innerHTML = h || '<div class="empty">没有匹配的图标，换个词试试～</div>';
}
function initMorph(){
  if(!window.createMorph || !window.canonicalD) return;
  var first=null;
  for(var i=0;i<ICONS.length;i++){ if(ICONS[i].node){ first=ICONS[i]; break; } }
  if(!first) return;
  curIconNode = first.node;
  morphInst = window.createMorph(document.getElementById("morphPath"), first.node);
  document.getElementById("morphName").textContent = first.id || first.nm;
}
function setMorph(i){
  var it = ICONS[i]; if(!it || !it.node || !window.createMorph) return;
  curIconNode = it.node;
  document.getElementById("morphName").textContent = it.id || it.nm;
  if(!morphInst){
    morphInst = window.createMorph(document.getElementById("morphPath"), it.node);
  } else {
    morphInst.morphTo(it.node, springPreset);
  }
  renderIcons();
}
function randomMorph(){
  var idx=[]; ICONS.forEach(function(it,i){ if(it.node) idx.push(i); });
  if(!idx.length) return;
  var r; do { r = idx[Math.floor(Math.random()*idx.length)]; } while(idx.length>1 && ICONS[r].node===curIconNode);
  setMorph(r);
}

/* ---------- 工坊控件初始化 ---------- */
function intentIds(k){
  for(var i=0;i<INTENTS.length;i++){ if(INTENTS[i].k===k) return INTENTS[i].ids; }
  return [];
}
function renderIntent(){
  var btns = document.querySelectorAll("#wkIntent button");
  btns.forEach(function(b){ b.classList.toggle("on", b.getAttribute("data-v")===state.intent); });
  var d = document.getElementById("intentDesc");
  if(d){ for(var i=0;i<INTENTS.length;i++){ if(INTENTS[i].k===state.intent){ d.textContent = INTENTS[i].desc; break; } } }
}
function initWkControls(){
  var sel = document.getElementById("wkTerm");
  var pool = (state.intent && state.intent!=="all") ? intentIds(state.intent) : null;
  var ids = pool ? pool.slice() : TERMS.map(function(t){ return t.id; });
  if(ids.indexOf(wkTerm)===-1) ids = ids.concat([wkTerm]); // 保证当前选中项始终在列表内
  var html=""; ids.forEach(function(id){ var t=termById(id); if(!t) return; html += '<option value="'+id+'">'+esc(t.cn)+'（'+esc(t.en)+'）</option>'; });
  sel.innerHTML = html; sel.value = wkTerm;
  var sh = document.getElementById("wkStyle"); html="";
  STYLES.forEach(function(s){ html += '<button class="chip'+(s===state.style?" on":"")+'" data-v="'+esc(s)+'">'+esc(s)+'</button>'; });
  sh.innerHTML = html;
  var ch = document.getElementById("wkColor"); html="";
  COLORS.forEach(function(c){ html += '<button class="sw'+(c[0]===state.color?" on":"")+'" data-v="'+c[0]+'" style="background:'+c[0]+'" title="'+esc(c[1])+'"></button>'; });
  ch.innerHTML = html;
  var ex = document.getElementById("wkExtra"); html="";
  EXTRAS.forEach(function(s){ html += '<button class="chip'+(state.extras.indexOf(s)>=0?" on":"")+'" data-v="'+esc(s)+'">'+esc(s)+'</button>'; });
  ex.innerHTML = html;
}

/* ---------- 事件绑定 ---------- */
function sv(el){ if(el && el.scrollIntoView){ try{ el.scrollIntoView({behavior:"smooth",block:"start"}); }catch(e){} } }
function on(id, ev, fn){ var e=document.getElementById(id); if(e){ e.addEventListener(ev, fn); } else { if(window.console) console.warn("bind: missing #"+id); } }
function onq(sel, ev, fn){ var e=document.querySelector(sel); if(e){ e.addEventListener(ev, fn); } else { if(window.console) console.warn("bind: missing "+sel); } }
function bind(){
  // Tab
  on("tabs", "click", function(e){
    var b = e.target.closest(".tab"); if(!b) return;
    var tab = b.getAttribute("data-tab");
    document.querySelectorAll(".tab").forEach(function(x){ x.classList.toggle("on", x===b); });
    document.getElementById("pgLib").classList.toggle("hide", tab!=="lib");
    document.getElementById("pgWk").classList.toggle("hide", tab!=="wk");
    document.getElementById("pgMy").classList.toggle("hide", tab!=="my");
    document.getElementById("pgAgent").classList.toggle("hide", tab!=="agent");
    document.getElementById("pgIcons").classList.toggle("hide", tab!=="icons");
    document.getElementById("pgColors").classList.toggle("hide", tab!=="colors");
    state.tab = tab; save();
  });
  // 翻译器：核心交互
  on("btnTranslate", "click", translate);
  on("trInput", "keydown", function(e){ if((e.ctrlKey||e.metaKey) && e.key==="Enter"){ e.preventDefault(); translate(); } });
  var EXMAP = {"点一下":"做一个主要按钮，点击后提交表单","填一下":"做一个下拉选择框让用户选城市","看一个东西":"展示一张带标题和说明的产品图片卡片","等个反馈":"操作成功后弹一个小提示告诉用户成功了","滑一下翻页":"可以左右滑动切换多张图片","鼠标放上去动一下":"卡片在鼠标放上去的时候微微抬起，加一点阴影"};
  on("trExamples", "click", function(e){ var b=e.target.closest("button[data-ex]"); if(!b) return; var k=b.getAttribute("data-ex"); document.getElementById("trInput").value = EXMAP[k] || ""; translate(); });
  on("trMic", "click", function(){ startVoice(); });
  on("btnAdvance", "click", function(){ var a=document.getElementById("trAdv"); var hid=a.classList.toggle("hide"); this.textContent = hid ? "手动精修 ▾" : "收起精修 ▴"; });
  // 展开 / 收起「为什么这么写（术语白话）」
  on("btnWhy", "click", function(){
    var bd = document.getElementById("wkWhy");
    var hid = bd.classList.toggle("hide");
    this.textContent = hid ? "展开解释" : "收起解释";
    if(!hid) renderWkWhy();
  });
  // 搜索
  on("q", "input", function(e){ state.q = e.target.value; renderCards(); renderNav(); });
  on("btnFavOnly", "click", function(){ state.favOnly=!state.favOnly; this.classList.toggle("on", state.favOnly); this.textContent = state.favOnly?"看全部":"只看收藏"; renderCards(); renderNav(); });
  on("btnClearQ", "click", function(){ document.getElementById("q").value=""; state.q=""; renderCards(); renderNav(); });
  // 章节导航点击滚动
  onq(".cnav-wrap", "click", function(e){ var a=e.target.closest(".cnav"); if(!a) return; var id="#chap-"+a.getAttribute("data-ch"); var el=document.querySelector(id); if(el) sv(el); });
  // 卡片星标 / 复制 / 去工坊 / 语义锚点跳转
  on("pgLib", "click", function(e){
    var dl=e.target.closest(".dv-link"); if(dl){ var s=dl.getAttribute("data-dv"); switchTab("agent"); var aq=document.getElementById("aq"); aq.value=s; agentQuery=s; agentCat="all"; renderAgentCats(); renderAgent(); sv(document.getElementById("pgAgent")); toast("已切到 AI 语义库：" + s); return; }
    var star=e.target.closest(".star"); if(star){ var id=star.getAttribute("data-id"); favs[id]=!favs[id]; if(!favs[id]) delete favs[id]; save(); refreshAll(); return; }
    var cp=e.target.closest(".copy"); if(cp){ var t=termById(cp.getAttribute("data-id")); if(t){ var p="你是一位资深前端工程师。我想实现【"+t.cn+"】（"+t.en+"）。\\n效果："+t.speak+"。\\n避免："+t.anti+"。\\n正确："+t.fix+"。\\n平台：网页Web（标准HTML/CSS/JS单文件零依赖）。\\n要点：\\n"; t.tip.forEach(function(x){p+="- "+x+"\\n";}); p+="\\n请输出完整可运行代码并写中文注释。"; copyText(p);} return; }
    var go=e.target.closest(".goto"); if(go){ var id=go.getAttribute("data-id"); wkTerm=id; switchTab("wk"); initWkControls(); document.getElementById("wkTerm").value=id; refreshAll(); return; }
    var tg=e.target.closest(".toggle"); if(tg){ var bd=tg.closest(".code").querySelector(".code-bd"); var hid=bd.classList.toggle("hide"); tg.textContent = hid?"展开":"收起"; }
  });
  // 收藏页
  on("pgMy", "click", function(e){
    var cp=e.target.closest(".copy"); if(cp){ var t=termById(cp.getAttribute("data-id")); if(t){ var p="实现【"+t.cn+"】（"+t.en+"）。效果："+t.speak+"。避免："+t.anti+"。正确："+t.fix+"。"; copyText(p);} return; }
    var un=e.target.closest("[data-un]"); if(un){ var id=un.getAttribute("data-un"); delete favs[id]; save(); refreshAll(); }
  });
  // Agent 语义库
  var aqEl = document.getElementById("aq");
  if(aqEl) aqEl.addEventListener("input", function(e){ agentQuery = e.target.value; renderAgent(); });
  on("agentCats", "click", function(e){ var b=e.target.closest(".chip"); if(!b) return; agentCat=b.getAttribute("data-cat"); renderAgentCats(); renderAgent(); });
  on("agentGrid", "click", function(e){
    var cp=e.target.closest(".aj-copy");
    if(cp){ var t=agentList[parseInt(cp.getAttribute("data-i"),10)]; if(t){ copyText(JSON.stringify(agContract(t),null,2)); toast("已复制语义名片 JSON"); } return; }
    var tg=e.target.closest(".aj-toggle");
    if(tg){ var card=tg.closest(".agent-card"); var pre=card && card.querySelector(".agent-json"); if(!pre) return; var hid=pre.classList.toggle("hide"); tg.textContent = hid ? "语义名片 ▾" : "收起名片 ▴"; }
  });
  on("btnCopyMcp", "click", function(){ var el=document.getElementById("mcpCode"); if(el){ copyText(el.textContent); toast("已复制 MCP 配置"); } });
  // AI 图标库：点图标 → 上方大图变形；点「复制 SVG」→ 复制
  on("iconGrid", "click", function(e){
    var cp=e.target.closest(".copy");
    if(cp){ var i=parseInt(cp.getAttribute("data-i"),10); var it=ICONS[i]; if(it){ copyText(iconSvg(it)); toast("已复制 SVG"); } return; }
    var card=e.target.closest(".icon-card");
    if(card){ setMorph(parseInt(card.getAttribute("data-i"),10)); }
  });
  on("btnCopyIcon", "click", function(){
    var it=null; for(var i=0;i<ICONS.length;i++){ if(ICONS[i].node===curIconNode){ it=ICONS[i]; break; } }
    if(it){ copyText(iconSvg(it)); toast("已复制 SVG"); }
  });
  on("btnRandomIcon", "click", randomMorph);
  on("morphPreview", "click", randomMorph);
  on("springRow", "click", function(e){
    var b=e.target.closest(".chip"); if(!b) return;
    springPreset=b.getAttribute("data-spring");
    this.querySelectorAll(".chip").forEach(function(x){ x.classList.toggle("on", x===b); });
  });
  var colorRow=document.getElementById("springColorRow");
  if(colorRow){ colorRow.addEventListener("click", function(e){
    var d=e.target.closest(".color-dot"); if(!d||d.classList.contains("custom")) return;
    var c=d.getAttribute("data-c"); var mp=document.getElementById("morphPreview");
    if(mp) mp.style.color = (c==="reset") ? "" : c;
    colorRow.querySelectorAll(".color-dot").forEach(function(x){ x.classList.toggle("on", x===d); });
  }); }
  var iqEl=document.getElementById("iconQ");
  if(iqEl) iqEl.addEventListener("input", function(e){ iconQuery=e.target.value; renderIcons(); });
  // 工坊
  on("wkPlat", "click", function(e){ var b=e.target.closest("button"); if(!b) return; state.plat=b.getAttribute("data-v"); this.querySelectorAll("button").forEach(function(x){x.classList.toggle("on",x===b);}); refreshAll(); });
  on("wkTerm", "change", function(e){ wkTerm=e.target.value; save(); refreshAll(); });
  on("wkStyle", "click", function(e){ var b=e.target.closest(".chip"); if(!b) return; state.style=b.getAttribute("data-v"); this.querySelectorAll(".chip").forEach(function(x){x.classList.toggle("on",x===b);}); save(); refreshAll(); });
  on("wkColor", "click", function(e){ var b=e.target.closest(".sw"); if(!b) return; state.color=b.getAttribute("data-v"); this.querySelectorAll(".sw").forEach(function(x){x.classList.toggle("on",x===b);}); save(); refreshAll(); });
  on("wkExtra", "click", function(e){ var b=e.target.closest(".chip"); if(!b) return; var v=b.getAttribute("data-v"); var i=state.extras.indexOf(v); if(i>=0) state.extras.splice(i,1); else state.extras.push(v); b.classList.toggle("on"); save(); refreshAll(); });
  on("btnCopy", "click", function(){ copyText(document.getElementById("wkOut").value); });
  on("btnSaveWk", "click", function(){ if(wkTerm && !favs[wkTerm]){ favs[wkTerm]=true; save(); refreshAll(); toast("已收藏到「我的收藏」"); } else toast("已经在收藏里了"); });
  // 导出/导入
  on("btnExport", "click", function(){ try { var data=JSON.stringify({favs:favs,state:state,wkTerm:wkTerm},null,2); var a=document.createElement("a"); a.href = (window.URL && URL.createObjectURL) ? URL.createObjectURL(new Blob([data],{type:"application/json"})) : "data:application/json;charset=utf-8,"+encodeURIComponent(data); a.download="vibecode-favs.json"; a.click(); toast("已导出收藏备份"); } catch(e){ toast("导出失败，请重试"); } });
  on("btnImport", "click", function(){ document.getElementById("fileIn").click(); });
  on("fileIn", "change", function(e){ var f=e.target.files[0]; if(!f) return; var r=new FileReader(); r.onload=function(){ try{ var o=JSON.parse(r.result); if(o.favs) favs=o.favs; if(o.state) state=Object.assign(state,o.state); if(o.wkTerm) wkTerm=o.wkTerm; save(); initWkControls(); refreshAll(); toast("导入成功"); }catch(err){ toast("文件格式不对"); } }; r.readAsText(f); });
  // 滚动更新章节高亮
  window.addEventListener("scroll", function(){ renderNav(); }, {passive:true});
}
function switchTab(tab){
  document.querySelectorAll(".tab").forEach(function(x){ x.classList.toggle("on", x.getAttribute("data-tab")===tab); });
  document.getElementById("pgLib").classList.toggle("hide", tab!=="lib");
  document.getElementById("pgWk").classList.toggle("hide", tab!=="wk");
  document.getElementById("pgMy").classList.toggle("hide", tab!=="my");
  document.getElementById("pgAgent").classList.toggle("hide", tab!=="agent");
  document.getElementById("pgIcons").classList.toggle("hide", tab!=="icons");
  document.getElementById("pgColors").classList.toggle("hide", tab!=="colors");
  state.tab=tab; save();
}

/* ---------- 交互增强：让前后效果对照区可点击 / 可滚动体验 ---------- */
function doTry(id, good){
  if(!good) return;
  var q = function(s){ return good.querySelector(s); };
  var all = function(s){ return good.querySelectorAll(s); };
  switch(id){
    case 'nav-hamburger': all('.v-ham').forEach(function(t){t.classList.toggle('on');}); break;
    case 'nav-overlay': all('.v-ovl').forEach(function(t){t.classList.toggle('on');}); break;
    case 'nav-dropdown': var d=q('.v-sub'); if(d) d.classList.toggle('on'); break;
    case 'nav-mega': var m=q('.v-mega'); if(m) m.classList.toggle('on'); break;
    case 'nav-sidebar': var s=q('.v-side'); if(s) s.classList.toggle('on'); break;
    case 'nav-crumb': var cr=q('.v-crumb'); if(cr){var its=cr.querySelectorAll('a,b');var on=cr.querySelector('.on');var nx=on?on.nextElementSibling:its[0];while(nx&&nx.tagName==='I'){nx=nx.nextElementSibling;}if(!nx)nx=its[0];its.forEach(function(x){x.classList.remove('on')});nx.classList.add('on');} break;
    case 'nav-anchor': var a=q('.v-anchor'); if(a){var ds=a.querySelectorAll('button');var on=a.querySelector('.on');var nx=on?(on.nextElementSibling||ds[0]):ds[0];ds.forEach(function(x){x.classList.remove('on')});nx.classList.add('on');} break;
    case 'nav-shrink': var b=q('.v-shrink'); if(b) b.classList.toggle('shrunk'); break;
    case 'nav-sticky': var ph=q('.nv-scroll'); if(ph) ph.scrollTop = ph.scrollTop>20?0:130; break;
    // 表单输入
    case 'form-input': var i=q('.demo-in'); if(i) i.focus(); break;
    case 'form-select': var fsx=q('.f-sel'); if(fsx) fsx.classList.toggle('on'); break;
    case 'form-switch': var sw=q('.f-sw'); if(sw) sw.classList.toggle('on'); break;
    case 'form-checkbox': all('.f-ck').forEach(function(x){x.classList.toggle('on')}); break;
    case 'form-radio': var r=q('.f-rd'); if(r){all('.f-rd').forEach(function(x){x.classList.remove('on')}); r.classList.add('on');} break;
    // 按钮操作
    case 'btn-primary': var p=q('.b-pri'); if(p){p.classList.add('pressed'); setTimeout(function(){p.classList.remove('pressed');},180);} break;
    case 'btn-loading': var l=q('.b-load'); if(l && !l.classList.contains('loading')){ l.classList.add('loading'); setTimeout(function(){l.classList.remove('loading');},1500);} break;
    case 'btn-disabled': var dis=q('.b-dis'); if(dis){dis.classList.remove('shake'); void dis.offsetWidth; dis.classList.add('shake');} break;
    case 'btn-group': var g=q('.b-grp'); if(g){var on=g.querySelector('.on'); var nx=on?on.nextElementSibling:g.firstElementChild; g.querySelectorAll('span').forEach(function(x){x.classList.remove('on')}); (nx||g.firstElementChild).classList.add('on');} break;
    case 'btn-icon': var ic=q('.b-ic'); if(ic) ic.classList.toggle('on'); break;
    // 补全组件
    case 'hover-lift': var hc=q('.hl-card'); if(hc) hc.classList.toggle('on'); break;
    case 'carousel': var tr=q('.cr-track'); if(tr){var w=tr.clientWidth||1;var max=tr.scrollWidth-w;var nx=tr.scrollLeft+w;if(nx>max)nx=0;tr.scrollLeft=nx;} break;
    // 弹窗遮罩
    case 'modal-dialog': var mo=q('.mo'); if(mo) mo.classList.toggle('on'); break;
    case 'modal-drawer': var dr=q('.dr'); if(dr) dr.classList.toggle('on'); break;
    case 'toast-msg': toast('已保存到本地 ✓'); break;
    case 'popconfirm': var pc=q('.pc'); if(pc) pc.classList.toggle('on'); break;
    case 'skeleton': var sk=q('.sk'); if(sk) sk.classList.toggle('on'); break;
    // 动效
    case 'anim-fade': var af=q('.an-fade'); if(af) af.classList.toggle('on'); break;
    case 'anim-flip': var fl=q('.an-flip'); if(fl) fl.classList.toggle('flipped'); break;
    case 'anim-list': all('.an-li .li').forEach(function(x){x.classList.toggle('on')}); break;
    case 'anim-progress': var pr=q('.an-bar'); if(pr){pr.classList.remove('run','half'); void pr.offsetWidth; pr.classList.add('run');} break;
    case 'anim-tab': var at=q('.an-tab'); if(at){var bs=at.querySelectorAll('.tabs2 button');var on=at.querySelector('.tabs2 button.on');var nx=on?on.nextElementSibling:bs[0]; var idx=nx?[].indexOf.call(bs,nx):0; bs.forEach(function(x){x.classList.remove('on')}); (nx||bs[0]).classList.add('on'); var ps=at.querySelectorAll('.panels .p'); ps.forEach(function(pp,i){pp.classList.toggle('on', i===idx)});} break;
    // 布局 / 交互 / 性能章（u-* 大幅对照）
    case 'sticky-top': var usc=q('.u-scroll'); if(usc) usc.scrollTop = usc.scrollTop>20?0:90; break;
    case 'overlay': var uov=q('.u-ovl'); if(uov) uov.classList.toggle('on'); break;
    case 'debounce': case 'throttle': var urp=q('.u-run'); if(urp){urp.classList.remove('u-run'); void urp.offsetWidth; urp.classList.add('u-run');} break;
    case 'darkmode': var udk=q('.u-dk'); if(udk) udk.classList.toggle('on'); break;
    case 'reduce-motion': var urm=q('.u-rm'); if(urm) urm.classList.toggle('on'); break;
    case 'lazy': var ulz=q('.u-lz'); if(ulz) ulz.classList.toggle('on'); break;
    case 'keyboard': var ukb=q('.u-kb-btn'); if(ukb) ukb.focus(); break;
    default:
      // 通用：点击试用 -> 高亮「平台提示词」正确做法一侧（before/after 对照的体验感；不引入新功能）
      good.classList.remove('try-pulse'); void good.offsetWidth; good.classList.add('try-pulse');
      break;
  }
}
function wireInteractions(){
  if(window.__wired) return; window.__wired = true;
  document.querySelectorAll('.vdemo[data-demo]').forEach(function(root){
    var good = root.querySelector('.vbx.good');
    var id = root.getAttribute('data-demo');
    if(!good) return;
    // 通用：data-toggle 切换目标 .on
    root.querySelectorAll('[data-toggle]').forEach(function(btn){
      btn.addEventListener('click', function(e){
        e.stopPropagation();
        var sel = '.'+btn.getAttribute('data-toggle');
        root.querySelectorAll(sel).forEach(function(tg){ tg.classList.toggle('on'); });
      });
    });
    // 通用：data-close 移除目标 .on
    root.querySelectorAll('[data-close]').forEach(function(btn){
      btn.addEventListener('click', function(e){
        e.stopPropagation();
        var sel = '.'+btn.getAttribute('data-close');
        root.querySelectorAll(sel).forEach(function(tg){ tg.classList.remove('on'); });
      });
    });
    // 单选互斥 data-pick（支持下拉回填、tab 面板联动）
    root.querySelectorAll('[data-pick]').forEach(function(el){
      el.addEventListener('click', function(e){
        e.stopPropagation();
        var grp = el.closest('[data-grp]') || el.parentElement;
        grp.querySelectorAll('[data-pick]').forEach(function(x){ x.classList.remove('on'); });
        el.classList.add('on');
        var fs = el.closest('.f-sel');
        if(fs){ fs.classList.remove('on'); var tx = el.getAttribute('data-txt'); var lb = fs.querySelector('.lbl'); if(tx && lb) lb.textContent = tx; }
        var at = el.closest('.an-tab');
        if(at){ var bs = at.querySelectorAll('.tabs2 button'); var idx = [].indexOf.call(bs, el); var ps = at.querySelectorAll('.panels .p'); ps.forEach(function(p,i){ p.classList.toggle('on', i===idx); }); }
      });
    });
    // 复选 data-check（toggle 自身）
    root.querySelectorAll('[data-check]').forEach(function(el){
      el.addEventListener('click', function(e){ e.stopPropagation(); el.classList.toggle('on'); });
    });
    // 加载按钮 data-load
    root.querySelectorAll('[data-load]').forEach(function(el){
      el.addEventListener('click', function(e){
        e.stopPropagation();
        if(el.classList.contains('loading')) return;
        el.classList.add('loading'); setTimeout(function(){ el.classList.remove('loading'); }, 1500);
      });
    });
    // 轻提示 data-toast
    root.querySelectorAll('[data-toast]').forEach(function(el){
      el.addEventListener('click', function(e){ e.stopPropagation(); toast(el.getAttribute('data-toast') || '完成'); });
    });
    // 禁用抖动 data-shake
    root.querySelectorAll('[data-shake]').forEach(function(el){
      el.addEventListener('click', function(e){
        e.stopPropagation();
        el.classList.remove('shake'); void el.offsetWidth; el.classList.add('shake');
      });
    });
    // 按下反馈 data-press
    root.querySelectorAll('[data-press]').forEach(function(el){
      el.addEventListener('click', function(e){
        e.stopPropagation();
        el.classList.add('pressed'); setTimeout(function(){ el.classList.remove('pressed'); }, 180);
      });
    });
    // 汉堡抽屉：点遮罩关闭
    if(id==='nav-hamburger'){
      var ov = good.querySelector('.nv-backdrop');
      if(ov) ov.addEventListener('click', function(){
        good.querySelectorAll('.v-ham').forEach(function(tg){ tg.classList.remove('on'); });
      });
    }
    // 全屏遮罩：点遮罩空白处关闭（stopPropagation 防止冒泡到整块又触发 doTry 重新打开）
    if(id==='nav-overlay'){
      var ov2 = good.querySelector('.nv-ovl');
      if(ov2) ov2.addEventListener('click', function(e){
        if(e.target === ov2){ e.stopPropagation(); good.querySelectorAll('.v-ovl').forEach(function(tg){ tg.classList.remove('on'); }); }
      });
    }
    // 滚动收缩：滚一点头部变小（rAF 节流，只 toggle class）
    if(id==='nav-shrink'){
      var ph = good.querySelector('.nv-shr');
      if(ph){
        var sTick=false;
        ph.addEventListener('scroll', function(){
          if(sTick) return; sTick=true;
          requestAnimationFrame(function(){
            var b = ph.querySelector('.v-shrink');
            if(b) b.classList.toggle('shrunk', ph.scrollTop>30);
            sTick=false;
          });
        }, {passive:true});
      }
    }
    // 锚点导航：rAF scrollspy 高亮 + 点圆点平滑跳转
    if(id==='nav-anchor'){
      var spy = good.querySelector('.nv-spy');
      var anc = good.querySelector('.v-anchor');
      if(spy && anc){
        var dots = anc.querySelectorAll('button');
        var secs = spy.querySelectorAll('section');
        var aTick=false;
        spy.addEventListener('scroll', function(){
          if(aTick) return; aTick=true;
          requestAnimationFrame(function(){
            var top = spy.scrollTop, idx = 0;
            for(var i=0;i<secs.length;i++){ if(secs[i].offsetTop - spy.offsetTop - 60 <= top) idx = i; }
            dots.forEach(function(d,j){ d.classList.toggle('on', j===idx); });
            aTick=false;
          });
        }, {passive:true});
        dots.forEach(function(dot, di){
          dot.addEventListener('click', function(e){
            e.stopPropagation();
            dots.forEach(function(x){ x.classList.remove('on'); });
            dot.classList.add('on');
            if(secs[di] && spy.scrollTo){ try{ spy.scrollTo({top: Math.max(secs[di].offsetTop - spy.offsetTop - 10, 0), behavior:'smooth'}); }catch(err){ spy.scrollTop = Math.max(secs[di].offsetTop - spy.offsetTop - 10, 0); } }
          });
        });
      }
    }
    // 面包屑：点任一段切换「当前」
    if(id==='nav-crumb'){
      var cr = good.querySelector('.v-crumb');
      if(cr) cr.querySelectorAll('a,b').forEach(function(s){
        s.addEventListener('click', function(e){
          e.stopPropagation();
          cr.querySelectorAll('a,b').forEach(function(x){ x.classList.remove('on'); });
          s.classList.add('on');
        });
      });
    }
    // 轮播图：左右按钮切换（stopPropagation，避免与整块点击冲突）
    if(id==='carousel'){
      var ctr = good.querySelector('.cr-track');
      if(ctr){
        var adv = function(dir){
          var w = ctr.clientWidth || 1;
          var max = ctr.scrollWidth - w;
          var nx = ctr.scrollLeft + dir * w;
          if(nx > max) nx = 0;
          if(nx < 0) nx = max;
          ctr.scrollLeft = nx;
        };
        var cp = good.querySelector('[data-cr-prev]');
        var cn = good.querySelector('[data-cr-next]');
        if(cp) cp.addEventListener('click', function(e){ e.stopPropagation(); adv(-1); });
        if(cn) cn.addEventListener('click', function(e){ e.stopPropagation(); adv(1); });
      }
    }
    // 显式「点击试用」按钮
    var vtry = root.querySelector('.vtry');
    if(vtry) vtry.addEventListener('click', function(e){ e.stopPropagation(); doTry(id, good); });
    // 整块正确效果也可点击体验（内部已 stopPropagation 的控件不会重复触发）
    good.addEventListener('click', function(){ doTry(id, good); });
    // 死按钮：点了抖一下（演示「没接事件就只是个装饰」）
    root.querySelectorAll('.m-dead').forEach(function(b){
      b.addEventListener('click', function(){
        b.classList.remove('shake'); void b.offsetWidth; b.classList.add('shake');
      });
    });
  });
}

/* 交互演示抽屉已移除：全站术语详情页统一采用 data-demo 版式（与导航术语一致），不再注入额外抽屉 */

/* ---------- 初始化（防御式：先数据后渲染） ---------- */
function init(){
  load();
  // 还原 tab（默认进入翻译器）
  switchTab(state.tab || "wk");
  initWkControls();
  bind();
  refreshAll();
  renderAgentCats(); renderAgent(); renderIcons(); initMorph();
  wireInteractions();
}
if(document.readyState==="loading"){ document.addEventListener("DOMContentLoaded", init); } else { init(); }
</script>
</body>
</html>
"""

# ============================================================================
# 多页静态导出：dist/（首页 + 每章节页 + 每术语页 + sitemap.xml + JSON-LD）
# 部署到阿里云 OSS 香港 / 腾讯云 COS 香港 + CDN 即可免备案上线，吃百度收录。
# 双语（/en/）路径结构已预留，本期先不做。
# ============================================================================
SITE_BASE = os.environ.get("VB_SITE_BASE", "https://mayi-vibecode.pages.dev").rstrip("/")

CHAPTER_SLUG = {
    0:"nav", 1:"layout", 2:"sizing", 3:"positioning", 4:"interaction",
    5:"responsive", 6:"performance", 7:"forms", 8:"buttons", 9:"overlays", 10:"motion",
}

DIST_CSS = """
.site-hd{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.site-hd .wrap{display:flex;align-items:center;justify-content:space-between;padding:12px 16px}
.brand{font-weight:800;color:var(--ink);text-decoration:none;font-size:16px}
.brand::before{content:"";display:inline-block;width:10px;height:10px;border-radius:3px;background:var(--accent);margin-right:8px;vertical-align:middle}
.topnav a{color:var(--ink-2);text-decoration:none;font-size:13px;font-weight:600}
.wrap{max-width:var(--max);margin:0 auto;padding:0 16px}
main.wrap{padding-top:22px;padding-bottom:48px}
.site-ft{border-top:1px solid var(--line);color:var(--ink-3);font-size:12.5px;padding:18px 16px;text-align:center;margin-top:24px}
.hero{background:linear-gradient(135deg,var(--accent-soft),var(--surface));border:1px solid var(--line);border-radius:var(--r);padding:26px 22px;margin-bottom:22px}
.hero h1{margin:0 0 8px;font-size:24px;color:var(--ink)}
.hero p{margin:0;color:var(--ink-2);font-size:14px;line-height:1.7;max-width:680px}
.cat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.cat{display:block;text-decoration:none;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px;transition:.15s}
.cat:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:var(--shadow)}
.cat-h{font-weight:800;color:var(--ink);font-size:15px;display:flex;align-items:center;gap:8px}
.cat .cnt{font-size:11px;background:var(--accent-soft);color:var(--accent);border-radius:20px;padding:1px 8px;font-weight:700}
.cat-sub{margin-top:6px;color:var(--ink-3);font-size:12.5px}
.crumb{font-size:13px;color:var(--ink-3);margin-bottom:10px}
.crumb a{color:var(--accent);text-decoration:none}
.termlist{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:8px}
.termlist li{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:12px 14px}
.termlist a{text-decoration:none;color:var(--ink);font-weight:700;font-size:15px}
.termlist .en{color:var(--ink-3);font-weight:500;font-size:12.5px;margin-left:8px}
.termlist .one{color:var(--ink-2);font-size:13px;margin-top:4px}
.pager{display:flex;justify-content:space-between;margin-top:22px;gap:10px}
.pager a{flex:1;text-decoration:none;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:10px 14px;font-size:13.5px;font-weight:600}
.pager a.next{text-align:right}
.pager a:hover{border-color:var(--accent)}
.cnt{color:var(--ink-3);font-weight:600;font-size:14px;margin-left:6px}
h1{color:var(--ink)}
/* 顶部导航：logo 后紧跟导航，留足间距，不挤右上角 */
.site-hd .wrap{display:flex;align-items:center;justify-content:flex-start;gap:26px;padding:12px 16px;flex-wrap:wrap}
.brand{font-weight:800;color:var(--ink);text-decoration:none;font-size:17px;letter-spacing:.2px}
.topnav{display:flex;align-items:center;gap:6px}
.topnav a{color:var(--ink-2);text-decoration:none;font-size:14px;font-weight:600;padding:7px 12px;border-radius:9px;transition:.15s}
.topnav a:hover{color:var(--accent);background:var(--accent-soft)}
/* 详情页：代码展开按钮放大 + 上色 */
.code-h{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px}
.code-h .toggle{height:36px;min-width:84px;padding:0 16px;border:1px solid var(--accent);color:var(--accent);background:#fff;font-weight:700;font-size:13.5px;border-radius:9px;cursor:pointer;transition:.15s}
.code-h .toggle:hover{background:var(--accent-soft)}
/* 详情页：提示词区块（三端都展示） */
.prompt{margin-top:18px;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px}
.prompt-h{font-size:14px;font-weight:800;color:var(--ink);margin-bottom:12px;display:flex;align-items:center;gap:6px}
.prompt-item{border:1px solid var(--line-2);border-radius:11px;padding:12px;margin-bottom:10px;background:#fcfbf9}
.prompt-item:last-child{margin-bottom:0}
.prompt-item-h{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px}
.prompt-item-h .pt{font-size:12px;font-weight:800;padding:3px 10px;border-radius:999px;color:#fff}
.prompt-item-h .pt.web{background:#3B6EA5}
.prompt-item-h .pt.app{background:#2E8B72}
.prompt-item-h .pt.mini{background:#C08A2E}
.copy-prompt{height:36px;font-size:13.5px;font-weight:700}
.prompt-bd{margin:0;max-height:360px;overflow:auto;background:#1f1d1a;color:#f3efe7;border-radius:9px;padding:12px;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12.5px;line-height:1.7;white-space:pre-wrap;word-break:break-word}
"""

PAGE_TMPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="/assets/logo.svg">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta name="keywords" content="%(kw)s">
<link rel="canonical" href="%(canon)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:image" content="%(ogimg)s">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">%(ld)s</script>
</head>
<body>
<header class="site-hd"><div class="wrap"><a class="brand" href="/">码译 · VibeCode</a><nav class="topnav"><a href="/">全部术语</a><a href="/colors/index.html">AI 配色</a><a href="/icons/index.html">AI 图标库</a></nav></div></header>
<main class="wrap">
%(body)s
</main>
<footer class="site-ft"><div class="wrap">© %(year)s 码译 · VibeCode · 用大白话找准前端组件术语</div></footer>
<div id="toast"></div>
<script src="/assets/site.js"></script>
</body>
</html>"""

def _extract_js_func(src, name):
    i = src.find("function %s(" % name)
    if i < 0: return ""
    j = src.find("{", i); depth = 0; k = j
    while k < len(src):
        c = src[k]
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return src[i:k+1]
        k += 1
    return ""

def _slug_unique(base, seen):
    s = base; n = 2
    while s in seen:
        s = "%s-%d" % (base, n); n += 1
    seen.add(s); return s

def _write_page(out, path, title, desc, body, ld, kw="", ogimg=""):
    loc = "/" if path == "" else "/%s/index.html" % path
    canon = SITE_BASE + loc
    html = PAGE_TMPL % {"title": esc(title), "desc": esc(desc), "canon": canon, "kw": esc(kw),
                        "ogimg": esc(ogimg),
                        "body": body, "ld": json.dumps(ld, ensure_ascii=False), "year": "2026"}
    fpath = os.path.join(out, path, "index.html")
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with io.open(fpath, "w", encoding="utf-8") as f:
        f.write(html)

def _index_body(by_ch, ch_slug, term_slug):
    out = ['<section class="hero"><h1>码译 · VibeCode</h1><p>把只会说白话的需求，翻译成 AI 编程工具听得懂的前端组件术语。每条配「大白话 vs 平台提示词」在线对比体验——左边看大白话生成什么样，右边看平台提示词一次到位的效果，点「点击试用」直接感受差距。</p></section>']
    out.append('<section class="cat-grid">')
    for ci in CH_DISPLAY:
        terms = by_ch.get(ci, [])
        sample = "、".join(t["cn"] for t in terms[:4])
        out.append('<a class="cat" href="/%s/index.html"><div class="cat-h">%s <span class="cnt">%d</span></div><div class="cat-sub">%s</div></a>' % (
            ch_slug[ci], esc(CHAPTERS[ci]), len(terms), esc(sample)))
    out.append('</section>')
    return "\n".join(out)

def _chapter_body(ci, terms, ch_slug, term_slug):
    out = ['<nav class="crumb"><a href="/">全部术语</a> / <span>%s</span></nav>' % esc(CHAPTERS[ci])]
    out.append('<h1>%s<span class="cnt">%d 条</span></h1>' % (esc(CHAPTERS[ci]), len(terms)))
    f = CHAPTER_FORMULA.get(ci)
    if f:
        ftitle, fchips = f
        chips_html = '<span class="plus">+</span>'.join(
            '<span class="chip">%s</span>' % esc(c) for c in fchips)
        out.append('<div class="chap-formula">')
        out.append('  <div class="cf-t">%s 本章口诀 · %s</div>' % (FORMULA_SVG, esc(ftitle)))
        out.append('  <div class="chips">%s</div>' % chips_html)
        out.append('</div>')
    out.append('<ul class="termlist">')
    for t in terms:
        out.append('<li><a href="/%s/index.html"><b>%s</b><span class="en">%s</span></a><div class="one">%s</div></li>' % (
            term_slug[t["id"]], esc(t["cn"]), esc(t["en"]), esc(t["speak"])))
    out.append('</ul>')
    return "\n".join(out)

def _term_body(t, ci, terms, idx, ch_slug, term_slug):
    out = []
    prev_t = terms[idx-1] if idx > 0 else None
    next_t = terms[idx+1] if idx < len(terms)-1 else None
    out.append('<nav class="crumb"><a href="/">全部术语</a> / <a href="/%s/index.html">%s</a> / <span>%s</span></nav>' % (
        ch_slug[ci], esc(CHAPTERS[ci]), esc(t["cn"])))
    out.append(term_card(t, interactive_footer=False))
    out.append('<nav class="pager">')
    if prev_t: out.append('<a class="prev" href="/%s/index.html">← %s</a>' % (term_slug[prev_t["id"]], esc(prev_t["cn"])))
    else: out.append('<span></span>')
    if next_t: out.append('<a class="next" href="/%s/index.html">%s →</a>' % (term_slug[next_t["id"]], esc(next_t["cn"])))
    else: out.append('<span></span>')
    out.append('</nav>')
    return "\n".join(out)

def _node_svg(node):
    """把 Lucide IconNode 渲染成内联 SVG 字符串。兼容两种导出格式：
    旧：[[tag, attrs], ...]（扁平）
    新：['svg', {svg属性}, [[tag, attrs], ...]]（外层包 svg + 第三元素是子元素列表）
    """
    if not node:
        return ""
    # 区分两种格式：若首元素是字符串 'svg' 且带子元素列表，则取 node[2] 为子元素
    children = node
    if (isinstance(node, list) and len(node) >= 1
            and isinstance(node[0], str) and node[0] == "svg"
            and len(node) > 2 and isinstance(node[2], list)):
        children = node[2]
    parts = ['<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">']
    for el in children:
        if not isinstance(el, (list, tuple)):
            continue
        tag = el[0]
        attrs = el[1] if len(el) > 1 and isinstance(el[1], dict) else {}
        a = "".join(' %s="%s"' % (k, esc(str(v))) for k, v in attrs.items())
        parts.append("<%s%s></%s>" % (tag, a, tag))
    parts.append("</svg>")
    return "".join(parts)

def _icons_body():
    items = load_icons()
    using_lucide = bool(items and "node" in items[0])
    cards, n_all = [], len(items)
    for it in items:
        if "node" in it:
            svg = _node_svg(it["node"])
            kw = esc("%s %s lucide" % (it["nm"], it["id"]))
        else:
            svg = it["svg"]
            kw = esc(it["nm"])
        if not svg:
            continue
        cards.append(
            '<div class="icon-card" data-kw="%s">'
            '<div class="icon-svg">%s</div>' % (kw, svg)
            + '<div class="nm">%s</div>' % esc(it["nm"])
            + '<button class="sm copy" type="button" data-svg="%s">复制 SVG</button>' % esc(svg)
            + '</div>'
        )
    grid = "".join(cards)
    sub = ("开源项目 <b>Lucide</b> 图标库精选 %d 枚 · 点「复制 SVG」即可拿走代码" % n_all) if using_lucide \
        else "为 AI / Agent 场景手绘的通用概念图标，全部内联 SVG、零依赖"
    return (
        '<section class="hero"><h1>AI 图标库</h1>'
        '<p>为 AI / Agent 场景挑选的通用概念图标，%s，自由用于你的产品原型或落地页。</p></section>' % sub
        + '<div class="icon-search"><input id="iconQ" class="inp" placeholder="搜索图标（中/英文，如 机器人 / bot）" /></div>'
        + _icon_color_bar()
        + '<div class="icon-grid" id="iconGrid">' + grid + '</div>'
        + '<div class="tip" id="iconEmpty" style="display:none">没有找到匹配的图标，换个关键词试试。</div>'
        + '<div class="tip">图标本体来自开源项目 Lucide（ISC 许可），均已内联进本页、离线可用。复制即代表你同意其开源许可。</div>'
        + '<style>.icon-card .copy.done{background:var(--accent);border-color:var(--accent);color:#fff}</style>'
        + '<script>(function(){'
        'var ICON_COLOR=null;'
        # 颜色选择
        'var grid=document.getElementById("iconGrid");var bar=document.getElementById("colorBar");'
        'if(bar){var dots=bar.querySelectorAll(".color-dot");'
        'dots.forEach(function(d){d.addEventListener("click",function(){'
        'var c=d.getAttribute("data-c");if(d.classList.contains("custom"))return;'
        'ICON_COLOR=(c==="reset")?null:c;if(grid)grid.style.setProperty("--icon-color",ICON_COLOR||"");'
        'dots.forEach(function(x){x.classList.remove("on")});d.classList.add("on");});});}'
        # 复制 SVG（若选了颜色则注入颜色，否则保留 currentColor）
        'document.querySelectorAll(".icon-card .copy").forEach(function(b){b.addEventListener("click",function(){'
        'var svg=b.getAttribute("data-svg");var cc=document.getElementById("colorCopy");'
        'if(ICON_COLOR&&cc&&cc.checked){svg=svg.replace(/currentColor/g,ICON_COLOR);}'
        'var ta=document.createElement("textarea");ta.value=svg;ta.style.position="fixed";ta.style.opacity="0";'
        'document.body.appendChild(ta);ta.select();try{document.execCommand("copy");}catch(e){}document.body.removeChild(ta);'
        'var o=b.textContent;b.textContent="已复制 ✓";b.classList.add("done");setTimeout(function(){b.textContent=o;b.classList.remove("done");},1400);});});'
        # 搜索过滤
        'var q=document.getElementById("iconQ");if(q){var cs=document.querySelectorAll("#iconGrid .icon-card");var empty=document.getElementById("iconEmpty");'
        'q.addEventListener("input",function(){var v=q.value.trim().toLowerCase();var shown=0;'
        'for(var i=0;i<cs.length;i++){var hit=!v||(cs[i].getAttribute("data-kw")||"").indexOf(v)>-1;cs[i].style.display=hit?"":"none";if(hit)shown++;}'
        'if(empty)empty.style.display=shown?"none":"";});}'
        '})();</script>'
    )

def _icon_color_bar():
    presets = [
        ("墨黑", "#1A1A1A"), ("朱红", "#C8442E"), ("琥珀", "#C08A2E"),
        ("青绿", "#2E8B72"), ("海蓝", "#3B6EA5"), ("紫", "#7A4FB0"),
        ("宝蓝", "#2B5FB3"), ("橙", "#E07B39"), ("粉", "#D46A9B"),
    ]
    dots = ['<span class="color-dot on" data-c="reset" style="background:#C8442E" title="默认色"></span>']
    for name, hexv in presets:
        dots.append('<span class="color-dot" data-c="%s" style="background:%s" title="%s"></span>' % (hexv, hexv, name))
    dots.append('<span class="color-dot custom" title="自定义颜色"><input type="color" value="#2E8B72"></span>')
    return ('<div class="color-bar" id="colorBar"><span class="cb-lab">图标颜色</span>'
            + "".join(dots)
            + '<label class="cb-lab" style="margin-left:6px;cursor:pointer"><input type="checkbox" id="colorCopy" checked> 复制到 SVG 时带颜色</label>'
            + '</div>')

# ============================================================================
# AI 配色方案库（100 套，SEO 友好：语义化 article + 可读 hex 文本 + JSON-LD）
# ============================================================================
def _hsl_to_hex(h, s, l):
    h = h % 360.0
    c = (1 - abs(2*l - 1)) * s
    x = c * (1 - abs((h/60.0) % 2 - 1))
    m = l - c/2.0
    if   h < 60:  r,g,b = c,x,0
    elif h < 120: r,g,b = x,c,0
    elif h < 180: r,g,b = 0,c,x
    elif h < 240: r,g,b = 0,x,c
    elif h < 300: r,g,b = x,0,c
    else:          r,g,b = c,0,x
    R=int(round((r+m)*255)); G=int(round((g+m)*255)); B=int(round((b+m)*255))
    return "#%02X%02X%02X" % (R,G,B)

_COLOR_THEMES = [
    ("科技蓝","科技互联网","SaaS 后台、数据看板、金融科技",212,200),
    ("深海蓝","企业后台","B 端管理台、CRM、ERP",222,205),
    ("湖心绿","环保健康","医疗健康、养生应用",168,150),
    ("薄荷绿","生活服务","生鲜电商、外卖平台",152,170),
    ("森野绿","自然户外","旅行攻略、园艺社区",135,95),
    ("暖阳橙","消费零售","电商大促、品牌商城",28,12),
    ("落日橘","美食餐饮","餐饮外卖、新式茶饮",18,350),
    ("蜜桃粉","女性时尚","美妆护肤、穿搭社区",340,320),
    ("樱花粉","社交社区","兴趣社区、UGC 平台",350,320),
    ("葡萄紫","文创娱乐","音乐播放、阅读应用",275,300),
    ("午夜紫","科技暗黑","游戏官网、电竞社区",262,210),
    ("石墨黑","极简高端","品牌官网、硬件产品",220,30),
    ("云灰白","工具效率","笔记协作、项目管理",210,200),
    ("赤陶红","国风文化","文博展览、非遗传承",8,24),
    ("帝王金","商务尊享","金融会员、尊享服务",42,30),
    ("苔藓褐","复古质感","精品咖啡、手作工坊",28,15),
    ("青瓷绿","东方禅意","茶道香道、东方美学",160,175),
    ("霓虹青","潮流酷玩","潮牌电商、夜店活动",185,320),
    ("宝蓝金","教育亲子","在线网课、早教启蒙",225,42),
    ("麦田黄","农业食品","农产直供、粮油品牌",48,95),
]
_COLOR_MODES = [
    ("标准",  dict(p_s=0.58,p_l=0.46,sec_l=0.55,acc_s=0.70,acc_l=0.50,dark=False,bg="#FFFFFF",surface="#F7F8FA",text="#1A1D21",muted="#6B7280",border="#E6E8EC")),
    ("浅色",  dict(p_s=0.45,p_l=0.62,sec_l=0.70,acc_s=0.62,acc_l=0.55,dark=False,bg="#FBFCFE",surface="#FFFFFF",text="#2A2F36",muted="#8A93A0",border="#EAEEF2")),
    ("暗色",  dict(p_s=0.60,p_l=0.58,sec_l=0.50,acc_s=0.72,acc_l=0.62,dark=True, bg="#0F1216",surface="#171B22",text="#E7EBF1",muted="#9AA4B2",border="#262C36")),
    ("高饱和",dict(p_s=0.78,p_l=0.50,sec_l=0.55,acc_s=0.85,acc_l=0.52,dark=False,bg="#FFFFFF",surface="#F6F7F9",text="#15181C",muted="#5E6672",border="#E2E4E8")),
    ("柔和",  dict(p_s=0.30,p_l=0.56,sec_l=0.64,acc_s=0.40,acc_l=0.58,dark=False,bg="#FCFCFA",surface="#FFFFFF",text="#33383F",muted="#8C929B",border="#ECEAE6")),
]

def gen_color_schemes():
    schemes = []
    idx = 0
    for tname, tcat, tscene, bh, ah in _COLOR_THEMES:
        for mname, mp in _COLOR_MODES:
            idx += 1
            p = _hsl_to_hex(bh, mp["p_s"], mp["p_l"])
            psoft = _hsl_to_hex(bh, mp["p_s"], min(mp["p_l"]+0.18, 0.92))
            sec = _hsl_to_hex((bh+18)%360, mp["p_s"]*0.85, mp["sec_l"])
            acc = _hsl_to_hex(ah, mp["acc_s"], mp["acc_l"])
            suc = _hsl_to_hex(145, 0.55, 0.42 if not mp["dark"] else 0.50)
            warn = _hsl_to_hex(38, 0.80, 0.48)
            dan = _hsl_to_hex(4, 0.72, 0.52)
            pal = {
                "主色": p, "主色浅": psoft, "辅色": sec, "强调色": acc,
                "背景": mp["bg"], "卡片": mp["surface"], "文字": mp["text"],
                "次要文字": mp["muted"], "边框": mp["border"],
                "成功": suc, "警告": warn, "危险": dan,
            }
            name = "%s·%s" % (tname, mname)
            tags = "%s %s %s" % (tname, tcat, tscene)
            schemes.append({
                "no": "no-%03d" % idx, "num": "%02d" % idx, "name": name,
                "cat": tcat, "scene": tscene, "tags": tags, "hue": bh,
                "palette": pal,
            })
    return schemes

_ROLE_ORDER = ["主色","主色浅","辅色","强调色","背景","卡片","文字","次要文字","边框","成功","警告","危险"]

def _hex_lum(hexv):
    hexv = hexv.lstrip("#")
    r, g, b = int(hexv[0:2], 16), int(hexv[2:4], 16), int(hexv[4:6], 16)
    return (0.299*r + 0.587*g + 0.114*b) / 255.0

def _hex_fg(hexv):
    """按亮度决定色块上的文字用深色还是白色。"""
    return "#1A1D21" if _hex_lum(hexv) > 0.62 else "#FFFFFF"

def _colors_body():
    schemes = gen_color_schemes()
    cats = []
    for s in schemes:
        if s["cat"] not in cats:
            cats.append(s["cat"])
    chip_html = '<button class="chip on" data-cat="">全部</button>' + "".join(
        '<button class="chip" data-cat="%s">%s</button>' % (esc(c), esc(c)) for c in cats)
    def art(s):
        p = s["palette"]["主色"]
        hfg = _hex_fg(p)
        hcls = "lt" if hfg == "#FFFFFF" else "dk"
        tiles = ""
        for role in _ROLE_ORDER:
            hexv = s["palette"][role]
            tf = _hex_fg(hexv)
            tiles += ('<div class="tile" style="background:%s;color:%s">'
                      '<span class="t-role">%s</span><span class="t-hex">%s</span></div>'
                      % (hexv, tf, role, hexv))
        pal_json = json.dumps(s["palette"], ensure_ascii=False)
        return (
            '<article class="scheme" id="%s" data-category="%s" data-name="%s" data-tags="%s" data-hue="%d">'
            '<div class="s-hero %s" style="background:%s;color:%s">'
            '<div class="s-word">COLOR<span class="s-sub">不一样的配色 · 绚丽多彩 —— 配色灵感</span></div>'
            '<h2 class="s-name"><span class="s-no">%s</span>%s</h2>'
            '<p class="s-main"><span class="s-main-nm">%s</span><span class="s-main-hex">%s</span></p>'
            '</div>'
            '<div class="s-tiles">%s</div>'
            '<div class="s-foot">'
            '<p class="s-scene">适合场景：%s</p>'
            '<div class="s-meta"><span>色相 %d°</span><span>分类 %s</span><span>共 %d 色</span>'
            '<button class="sm copy" type="button" data-pal="%s">复制配色 JSON</button></div>'
            '</div>'
            '</article>'
            % (s["no"], esc(s["cat"]), esc(s["name"]), esc(s["tags"]), s["hue"],
               hcls, p, hfg,
               s["num"], esc(s["name"]),
               esc(s["name"].split("·")[0]), p,
               tiles,
               esc(s["scene"]), s["hue"], esc(s["cat"]), len(s["palette"]),
               esc(pal_json))
        )
    first20 = "".join(art(s) for s in schemes[:20])
    rest = "".join(art(s) for s in schemes[20:])
    more = ('<details class="more"><summary>展开剩余 %d 套配色（共 100 套，全部可被搜索引擎收录）</summary><div class="scheme-grid more-grid">%s</div></details>'
            % (len(schemes)-20, rest))
    css = """<style>
.scheme-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}
@media(max-width:860px){.scheme-grid{grid-template-columns:minmax(0,1fr)}}
.scheme{background:var(--surface);border:1px solid var(--line);border-radius:18px;overflow:hidden;min-width:0;scroll-margin-top:80px;transition:box-shadow .18s,transform .18s}
.scheme:hover{box-shadow:0 12px 32px rgba(20,18,15,.12);transform:translateY(-2px)}
/* 海报 hero：大色块 + 超大 COLOR 字 */
.s-hero{padding:22px 22px 20px}
.s-word{font-size:48px;font-weight:900;letter-spacing:.04em;line-height:.95;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.s-word .s-sub{min-width:0}
.s-sub{font-size:10.5px;font-weight:700;letter-spacing:.14em;opacity:.72;white-space:nowrap}
.s-hero .s-name{color:inherit}
.scheme .s-name{font-size:25px;font-weight:900;margin:14px 0 0;letter-spacing:.02em;display:flex;align-items:center;gap:10px}
.scheme .s-no{font-size:11px;font-weight:800;padding:2px 8px;border-radius:7px;background:rgba(0,0,0,.14);letter-spacing:.06em}
.s-hero.lt .s-no{background:rgba(255,255,255,.2)}
.s-main{margin:12px 0 0;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.s-main-nm{font-size:16px;font-weight:800;letter-spacing:.06em}
.s-main-hex{font-size:12px;font-weight:700;font-family:ui-monospace,Menlo,Consolas,monospace;padding:4px 12px;border-radius:999px;letter-spacing:.05em}
.s-hero.lt .s-main-hex{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.45)}
.s-hero.dk .s-main-hex{background:rgba(0,0,0,.07);border:1px solid rgba(0,0,0,.22)}
/* 大色块区：每个颜色一张大圆角瓦片，色名+色值写在色块里 */
.s-tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;padding:14px 14px 4px}
.tile{border-radius:14px;min-width:0;min-height:104px;padding:12px 13px;display:flex;flex-direction:column;justify-content:flex-end;gap:2px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.06)}
.t-role{font-size:13.5px;font-weight:800;letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.t-hex{font-size:11px;font-weight:600;font-family:ui-monospace,Menlo,Consolas,monospace;opacity:.82;letter-spacing:.04em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
/* 底部信息 */
.s-foot{padding:10px 16px 16px}
.scheme .s-scene{font-size:12.5px;color:var(--ink-2);margin:0 0 10px;line-height:1.5}
.s-meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.s-meta span{background:var(--accent-soft);color:var(--accent);border-radius:6px;padding:2px 8px;font-size:11.5px;font-weight:600}
.s-meta .copy{margin-left:auto}
.scheme .copy.done{background:var(--accent);border-color:var(--accent);color:#fff}
.color-filter{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:4px 0 16px}
.color-filter .chip{padding:6px 12px;border-radius:999px;border:1px solid var(--line);background:var(--surface);font-size:12.5px;font-weight:600;color:var(--ink-2);cursor:pointer;transition:.12s}
.color-filter .chip:hover{border-color:var(--accent)}
.color-filter .chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
.color-search{margin-bottom:0}
.more{margin-top:14px;border:1px dashed var(--line);border-radius:12px;padding:10px 12px}
.more>summary{cursor:pointer;font-weight:700;color:var(--accent);font-size:13.5px;padding:6px 4px}
.more>.more-grid{margin-top:12px}
.more>.more-grid>.scheme{margin:0}
@media(max-width:640px){
  .s-word{font-size:36px}
  .s-sub{display:none}
  .scheme .s-name{font-size:21px}
  .s-tiles{grid-template-columns:repeat(2,minmax(0,1fr))}
  .tile{min-height:88px}
}
</style>"""
    js = """<script>(function(){
      var grid=document.getElementById('colorGrid'); if(!grid) return;
      var q=document.getElementById('colorQ'); var cats=document.getElementById('colorCats');
      var activeCat='';
      function apply(){ var v=(q?q.value:'').trim().toLowerCase();
        var cards=document.querySelectorAll('#colorGrid .scheme, .more-grid .scheme'); var shown=0;
        for(var i=0;i<cards.length;i++){ var c=cards[i];
          var hay=(c.getAttribute('data-name')+' '+c.getAttribute('data-tags')+' '+c.getAttribute('data-category')).toLowerCase();
          var ok=!v||hay.indexOf(v)>-1; var okc=!activeCat||c.getAttribute('data-category')===activeCat;
          var vis=ok&&okc; c.style.display=vis?'':'none'; if(vis)shown++; }
        var det=document.querySelector('details.more'); if(det && (v||activeCat)) det.open=true;
        var empty=document.getElementById('colorEmpty'); if(empty) empty.style.display=shown?'none':''; }
      if(q) q.addEventListener('input',apply);
      if(cats){ cats.addEventListener('click',function(e){ var b=e.target.closest('.chip'); if(!b) return;
        activeCat=b.getAttribute('data-cat')||''; cats.querySelectorAll('.chip').forEach(function(x){x.classList.toggle('on',x===b);}); apply(); }); }
      document.addEventListener('click',function(e){ var b=e.target.closest('.copy'); if(!b||!b.getAttribute('data-pal')) return;
        copyText(b.getAttribute('data-pal')); if(window.toast) toast('已复制配色 JSON'); });
      function openHash(){ var h=location.hash; if(h&&h.indexOf('#no-')===0){ var el=document.getElementById(h.slice(1)); if(el){ var d=el.closest('details.more'); if(d) d.open=true; } } }
      window.addEventListener('hashchange',openHash); openHash(); apply();
    })();</script>"""
    return (
        '<section class="hero"><h1>AI 配色方案库</h1>'
        '<p>100 套为网页 / App / 品牌精心调配的 AI 配色方案，每套都标注色值、色名与适用场景，点「复制配色 JSON」即可拿走。每套配色都是独立可索引的页面区块（带锚点 #no-xxx），方便搜索引擎收录与分享。</p></section>'
        + '<div class="color-search"><input id="colorQ" class="inp" placeholder="搜索配色：科技蓝 / 国风 / 电商 / 暗色 …"></div>'
        + '<div class="color-filter" id="colorCats">' + chip_html + '</div>'
        + '<div class="scheme-grid" id="colorGrid">' + first20 + '</div>'
        + more
        + '<div class="tip" id="colorEmpty" style="display:none">没有匹配的配色，换个关键词试试。</div>'
        + '<div class="tip">每套配色卡片里的 hex 色值、色名、适用场景都写成可读文本（不只藏在 CSS 里），并带 <code>data-category</code> / <code>data-tags</code> 结构化属性，便于筛选与搜索引擎理解。色值由 HSL 算法生成，可商用参考。</div>'
        + css + js
    )

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="码译 VibeCode">
  <rect width="64" height="64" rx="14" fill="#C8442E"/>
  <g fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M25 19 L13 32 L25 45"/>
    <path d="M39 19 L51 32 L39 45"/>
  </g>
  <g fill="none" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">
    <path d="M27 51 H37"/>
    <path d="M30.6 47.6 L27 51 L30.6 54.4"/>
    <path d="M33.4 47.6 L37 51 L33.4 54.4"/>
  </g>
</svg>"""

def export_static_dist(html):
    out = "dist"
    os.makedirs(os.path.join(out, "assets"), exist_ok=True)
    with io.open(os.path.join(out, "assets", "site.css"), "w", encoding="utf-8") as f:
        f.write(CSS + DIST_CSS)
    demo_js = "\n".join(_extract_js_func(html, fn) for fn in ("toast", "copyText", "fallbackCopy", "doTry", "wireInteractions"))
    demo_js += """
(function(){
  // dist 专用：代码块展开/收起 + 提示词复制（单文件版在 #pgLib 里绑定，dist 无该节点故这里补上）
  document.addEventListener('click', function(e){
    var tg = e.target.closest ? e.target.closest('.code .toggle') : null;
    if(tg){
      var code = tg.closest('.code');
      var bd = code && code.querySelector('.code-bd');
      if(bd){ var hid = bd.classList.toggle('hide'); tg.textContent = hid ? '展开' : '收起'; }
      return;
    }
    var cp = e.target.closest ? e.target.closest('.copy-prompt') : null;
    if(cp){
      var pk = cp.getAttribute('data-pk');
      var box = document.querySelector('.prompt-item[data-pk="'+pk+'"] .prompt-bd');
      if(box){ copyText(box.innerText || box.textContent); if(window.toast) toast('已复制 '+pk+' 提示词'); }
    }
  });
})();"""
    demo_js += "\nif(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',function(){wireInteractions();});}else{wireInteractions();}"
    with io.open(os.path.join(out, "assets", "site.js"), "w", encoding="utf-8") as f:
        f.write(demo_js)
    # 站点 Logo（内联 SVG，零依赖；作 favicon 与品牌标）
    with io.open(os.path.join(out, "assets", "logo.svg"), "w", encoding="utf-8") as f:
        f.write(LOGO_SVG)
    ch_slug = {ci: CHAPTER_SLUG.get(ci, "ch%d" % ci) for ci in range(len(CHAPTERS))}
    # 章节 slug 必须先占坑，避免某条 term 的英文 slug 与章节 slug 撞车导致互相覆盖
    seen = set(ch_slug.values()); term_slug = {}
    for t in T:
        term_slug[t["id"]] = _slug_unique(dv_slug(t["en"]), seen)
    by_ch = {}
    for t in T:
        by_ch.setdefault(t["ch"], []).append(t)
    written = 0
    _write_page(out, "", "码译 · VibeCode · 前端组件术语图鉴（%d 条）" % len(T),
                "用大白话找准前端组件术语，配前后效果对照与可复制提示词。", _index_body(by_ch, ch_slug, term_slug),
                {"@context":"https://schema.org","@type":"ItemList","name":"码译 · VibeCode · 全部术语",
                 "itemListElement":[{"@type":"ListItem","position":i+1,"url":"%s/%s/index.html"%(SITE_BASE,term_slug[t["id"]])} for i,t in enumerate(T)]})
    written += 1
    for ci in CH_DISPLAY:
        terms = by_ch.get(ci, [])
        _write_page(out, ch_slug[ci], "%s · 码译 · VibeCode" % CHAPTERS[ci],
                    "%s 分类下的前端术语与组件，共 %d 条。" % (CHAPTERS[ci], len(terms)),
                    _chapter_body(ci, terms, ch_slug, term_slug),
                    {"@context":"https://schema.org","@type":"CollectionPage","name":CHAPTERS[ci],
                     "hasPart":[{"@type":"WebPage","name":t["cn"],"url":"%s/%s/index.html"%(SITE_BASE,term_slug[t["id"]])} for t in terms]})
        written += 1
    for ci in CH_DISPLAY:
        terms = by_ch.get(ci, [])
        for idx, t in enumerate(terms):
            _write_page(out, term_slug[t["id"]], "%s（%s）· 码译 · VibeCode" % (t["cn"], t["en"]),
                        (t["speak"] or t["cn"]),
                        _term_body(t, ci, terms, idx, ch_slug, term_slug),
                        {"@context":"https://schema.org","@type":"DefinedTerm","name":t["cn"],"alternateName":t["en"],
                         "description":(t["speak"]+"。反模式："+t["anti"]),
                         "inDefinedTermSet":{"@type":"DefinedTermSet","name":"码译 · VibeCode"}})
            written += 1
    # AI 图标库（静态页）
    _write_page(out, "icons", "AI 图标库 · 码译 · VibeCode",
                "为 AI / Agent 场景手绘的内联 SVG 图标，零依赖，点一下复制即用。",
                _icons_body(),
                {"@context":"https://schema.org","@type":"CollectionPage","name":"AI 图标库",
                 "isPartOf":{"@type":"WebSite","name":"码译 · VibeCode"}})
    written += 1
    # AI 配色方案库（静态页，SEO 友好）
    _schemes = gen_color_schemes()
    _colors_ld = {"@context":"https://schema.org","@type":"ItemList",
                  "name":"AI 配色方案库（100 套）",
                  "itemListElement":[{"@type":"ListItem","position":i+1,
                                      "url":"%s/colors/#%s" % (SITE_BASE, s["no"]),
                                      "name":s["name"]} for i, s in enumerate(_schemes)]}
    _og = '%s/assets/og-colors.svg' % SITE_BASE
    _write_page(out, "colors", "AI 配色方案库 · 100 套网页配色 · 码译 · VibeCode",
                "100 套 AI 配色方案，每套标注色值、色名与适用场景，可一键复制 JSON，带锚点可被搜索引擎收录。",
                _colors_body(), _colors_ld,
                kw="AI配色,配色方案,网页配色,颜色搭配,UI配色,品牌色,设计灵感,渐变配色",
                ogimg=_og)
    written += 1
    # 生成 OG 分享封面（SVG，零依赖）
    _og_svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">'
               '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
               '<stop offset="0" stop-color="#1F6FB2"/><stop offset="1" stop-color="#2E8B72"/></linearGradient></defs>'
               '<rect width="1200" height="630" fill="#0F1216"/>'
               '<rect width="1200" height="630" fill="url(#g)" opacity="0.20"/>'
               '<text x="80" y="290" fill="#ffffff" font-size="78" font-family="sans-serif" font-weight="800">AI 配色方案库</text>'
               '<text x="80" y="360" fill="#cfd8e3" font-size="34" font-family="sans-serif">100 套网页 / App / 品牌配色 · 色值可一键复制</text>'
               '<g>')
    _sw = ["#1F6FB2","#2E8B72","#C8442E","#C08A2E","#7A4FB0","#E07B39","#3B6EA5","#D46A9B"]
    for i, c in enumerate(_sw):
        _og_svg += '<circle cx="%d" cy="500" r="34" fill="%s"/>' % (110 + i*130, c)
    _og_svg += '</g></svg>'
    with io.open(os.path.join(out, "assets", "og-colors.svg"), "w", encoding="utf-8") as f:
        f.write(_og_svg)
    sm_urls = [("/", 1.0)]
    for ci in CH_DISPLAY:
        sm_urls.append(("/%s/index.html" % ch_slug[ci], 0.6))
    for t in T:
        sm_urls.append(("/%s/index.html" % term_slug[t["id"]], 0.8))
    sm_urls.append(("/icons/index.html", 0.6))
    sm_urls.append(("/colors/index.html", 0.6))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, p in sm_urls:
        sm.append("  <url><loc>%s%s</loc><changefreq>weekly</changefreq><priority>%.1f</priority></url>" % (SITE_BASE, u, p))
    sm.append("</urlset>")
    with io.open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(sm))
    # robots.txt：放行所有蜘蛛（含百度），并声明 sitemap 位置
    robots = (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "# 百度蜘蛛放行（Cloudflare 切勿开启 Bot Fight Mode，否则会拦截 Baiduspider）\n"
        "User-agent: Baiduspider\n"
        "Allow: /\n"
        "\n"
        "Sitemap: %s/sitemap.xml\n" % SITE_BASE
    )
    with io.open(os.path.join(out, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)
    print("DIST: %d pages + sitemap.xml + robots.txt + assets -> %s/" % (written, out))

def _build_and_export():
    global html
    html = (html
            .replace("__JSONLD__", jsonld())
            .replace("__CSS__", CSS)
            .replace("__CNAV__", chapter_nav())
            .replace("__CHAPTERS__", chapter_sections())
            .replace("__ROADMAP__", roadmap_html())
            .replace("__MORPH_JS__", morph_js())
            .replace("__TERMS_JS__", terms_js())
            .replace("__PLAT__", json.dumps(PLAT, ensure_ascii=False))
            .replace("__NLIB__", str(len(T)))
            .replace("__NTERM__", str(len(T)))
            .replace("__COLORS__", _colors_body()))
    with io.open("vibecode-term-studio.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("OK terms=%d bytes=%d" % (len(T), len(html)))
    try:
        export_static_dist(html)
    except Exception as e:
        print("DIST export failed:", repr(e))

def _bootstrap_engine():
    """从编译快照加载渲染引擎（12 个函数 + 8 个 SVG 常量）并重绑到当前模块 globals。

    背景：2026-09-28 源文件局部损坏，term_card / chapter_sections / chapter_nav /
    roadmap_html / jsonld / prompt_for / card_prompt / apply_polish / naive_prompt_for /
    esc / dv_slug / load_icons 以及 STAR_SVG 等 8 个 SVG 常量只存在于损坏前的
    编译快照（_engine_snapshot.pyc）中。此函数把它们装回当前命名空间——
    函数经 types.FunctionType 重建后引用本模块的数据（VD / T / CHAPTERS 等），
    因此数据改动全部生效，快照内的旧数据不会被使用。
    """
    import importlib.util as _ilu
    import types as _types
    import os as _os
    _pyc = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "_engine_snapshot.pyc")
    if not _os.path.exists(_pyc):
        raise RuntimeError("缺少渲染引擎快照 _engine_snapshot.pyc（与 gen_vibecode.py 同目录）")
    _spec = _ilu.spec_from_file_location("_engine_snapshot", _pyc)
    _eng = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_eng)
    _ns = globals()
    _names = ["apply_polish", "card_prompt", "chapter_nav", "chapter_sections", "dv_slug",
              "esc", "jsonld", "load_icons", "naive_prompt_for", "prompt_for",
              "roadmap_html", "term_card",
              "STAR_SVG", "BAD_SVG", "GOOD_SVG", "COPY_SVG",
              "VHINT_SVG", "DV_SVG", "PLAT_SVG", "WK_SVG",
              "PLAT_PROMPT_LINE", "ICONS", "LUCIDE_ORDER", "LUCIDE_ZH", "PLAT"]
    _miss = [n for n in _names if not hasattr(_eng, n)]
    if _miss:
        raise RuntimeError("引擎快照缺少: %s" % ", ".join(_miss))
    for _n in _names:
        _obj = getattr(_eng, _n)
        if type(_obj).__name__ == "function":
            _obj = _types.FunctionType(_obj.__code__, _ns, _obj.__name__,
                                       _obj.__defaults__, _obj.__closure__)
        _ns[_n] = _obj

from polish_terms import POLISH_BAD, POLISH_PLAT  # noqa: E402  (apply_polish 依赖，定义于 polish_terms.py)

_bootstrap_engine()

def _load_terms_from_json():
    """若 data/terms.json 存在，则以它为内容源（覆盖 in-code 的 T/VD）。
    后台 CMS 改内容即写回该 JSON，构建时优先采用，便于版本化与自动部署。"""
    import json as _json
    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "terms.json")
    if not os.path.exists(_p):
        return
    _data = _json.load(open(_p, encoding="utf-8"))
    _terms = _data.get("terms", [])
    global T, VD
    T = [dict(t) for t in _terms]
    VD = {}
    for _t in _terms:
        _id = _t.get("id")
        if _id:
            VD[_id] = (_t.get("vd_bad", ""), _t.get("vd_good", ""))
    print("loaded %d terms from data/terms.json" % len(T))


if __name__ == "__main__":
    _load_terms_from_json()
    INTERACTIVE.clear()
    INTERACTIVE.update(t["id"] for t in T)
    _build_and_export()
