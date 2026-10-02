# 内容精修补丁（2026-09-26）
# 依据 87 条质量体检结果，对以下两类短板做内容增强：
#   1) 37 条「不同平台注意」过短（<12 字，多为「RN 同逻辑 / wxss 同 web」这类无信息量提示）
#      -> 改写为三端差异化、可操作的真实指引（含各端组件名 / 约束 / rpx 等）
#   2) 14 条「反例代码 bad」过短（<25 字）
#      -> 改写为能直接看到问题、贴进 <pre> 就懂的反例片段
# 用法：apply_polish(T) 就地修改 gen_vibecode.T 中的对应条目，保证所有导出一致。

POLISH_PLAT = {
    "inline-gap": {
        "web": "用 display:flex 横排，间隙交给 gap，彻底消除空白符缝隙",
        "app": "RN 用 flexDirection:'row'+gap，无需处理空白符",
        "mini": "wxss 支持 flex+gap，横排用 flex 而非 inline-block",
    },
    "neg-margin": {
        "web": "负 margin 标准支持，注意会叠加到兄弟元素上",
        "app": "RN 不支持负 margin 直接重叠，改用绝对定位或 translate",
        "mini": "wxss 支持负 margin，rpx 下数值要换算清楚",
    },
    "two-col": {
        "web": "左固定 width + 右 flex:1 自适应，或 grid 两栏",
        "app": "RN 用 flexDirection:row，左固定 width 右 flex:1",
        "mini": "wxss 同思路：左固定 width 右 flex:1，注意 rpx",
    },
    "baseline": {
        "web": "vertical-align:baseline/middle 对齐行内元素基线",
        "app": "RN 用 alignItems 控制交叉轴，无 baseline 概念",
        "mini": "wxss 支持 vertical-align，行内基线对齐同 web",
    },
    "hairline": {
        "web": "用 transform:scaleY(.5) 伪元素画 0.5px 线，兼容各屏",
        "app": "RN 用 borderWidth 配合像素密度，或 hairline 样式",
        "mini": "wxss 用 transform:scale 伪元素，或 1rpx 已够细",
    },
    "line-height": {
        "web": "line-height:1.5~1.7 提升可读性，纯数字相对字号",
        "app": "RN lineHeight 用绝对 px，注意与 fontSize 比例",
        "mini": "wxss 同 web，正文 line-height 建议 1.6 左右",
    },
    "font-weight": {
        "web": "系统字体 400/500/700 齐全，别硬要没字重的 600",
        "app": "RN fontWeight 仅 normal/bold/100-900 离散值",
        "mini": "wxss 支持 font-weight，但小程序字体子集有限",
    },
    "letter-spacing": {
        "web": "letter-spacing 标准支持，标题可加 0.5-1px",
        "app": "RN letterSpacing 无单位（px），标题微调用",
        "mini": "wxss 同 web，letter-spacing 直接生效",
    },
    "stacking": {
        "web": "z-index 只在定位元素生效，配合 stacking context",
        "app": "RN 无全局层叠，用 flex 顺序或同容器 zIndex",
        "mini": "小程序 z-index 仅对定位元素生效，注意层叠上下文",
    },
    "relative": {
        "web": "position:relative 不脱离流，常作绝对定位锚点",
        "app": "RN 用 position:'relative' 配合 absolute 子元素",
        "mini": "wxss position:relative 同 web，作 absolute 父锚",
    },
    "absolute": {
        "web": "absolute 脱离流，需有定位父级否则相对视口",
        "app": "RN position:'absolute' 相对最近的 relative 父",
        "mini": "wxss absolute 同 web，记得父级 position:relative",
    },
    "pseudo": {
        "web": "::before/::after 装饰性强，content 属性必填",
        "app": "RN 无伪元素，用额外 View+绝对定位模拟",
        "mini": "wxss 支持 ::before/::after，但 content 必填",
    },
    "scroll-lock": {
        "web": "弹窗时给 body 加 overflow:hidden 锁背景滚动",
        "app": "Modal 蒙层覆盖，内容区 ScrollView 独立滚动",
        "mini": "弹窗时 catchtouchmove 阻止底层滚动穿透",
    },
    "hover": {
        "web": "hover 只在鼠标设备有效，触屏用 :active 替代",
        "app": "RN 无 hover，用 Pressable 的 pressed 态模拟",
        "mini": "小程序 hover-class 仅部分组件支持，触屏慎用",
    },
    "easing": {
        "web": "cubic-bezier 自定义缓动，ease/linear 内置",
        "app": "RN Animated 用 easing 库（Easing.inOut 等）",
        "mini": "wxss transition-timing-function 同 web，支持 cubic-bezier",
    },
    "throttle": {
        "web": "手写或 lodash.throttle，间隔触发最后一次",
        "app": "RN 同逻辑，组件卸载时清理定时器",
        "mini": "小程序同 web，页面 onUnload 清理定时器",
    },
    "media": {
        "web": "用 @media 按 min/max-width 切断点布局",
        "app": "RN 用 Dimensions/useWindowDimensions 取宽高分流",
        "mini": "wxss 支持 @media，按屏宽切 rpx 断点",
    },
    "orientation": {
        "web": "用 @media (orientation:landscape/portrait) 适配",
        "app": "监听 useWindowDimensions 变化重排布局",
        "mini": "wxss @media (orientation:) 横竖屏切布局",
    },
    "tablet": {
        "web": "手机/平板/桌面三套断点，grid 自动换行",
        "app": "按 width 判断 phone/tablet 加载不同布局",
        "mini": "wxss 三断点+rpx，平板单独调列数",
    },
    "reflow": {
        "web": "只动 transform/opacity 走合成层，避开重排",
        "app": "RN 用原生驱动动画（useNativeDriver）更顺",
        "mini": "小程序动画走 WXS 避免通信卡顿",
    },
    "semantic": {
        "web": "header/nav/main/article 提升结构与 SEO",
        "app": "RN 无语义标签，用组件名与无障碍 role 体现",
        "mini": "小程序用 view/text 居多，结构靠类名语义化",
    },
    "contrast": {
        "web": "正文与背景对比度≥4.5:1，满足 WCAG AA",
        "app": "RN 同样遵循对比度，深色模式别压太低",
        "mini": "小程序同 web，文字/背景对比度达标才可读",
    },
    "reduce-motion": {
        "web": "用 @media (prefers-reduced-motion) 关掉大动画",
        "app": "RN 读系统设置，提供 reduceMotion 配置",
        "mini": "小程序同 web，尊重系统减弱动效开关",
    },
    "form-switch": {
        "web": "input[type=checkbox] 自定义成开关样式",
        "app": "RN 直接用 Switch 组件，受控 value/onValueChange",
        "mini": "小程序 switch 组件，bindchange 拿勾选状态",
    },
    "form-checkbox": {
        "web": "input[type=checkbox]+label，CSS 自定义勾选样式",
        "app": "RN 用 Checkbox 或第三方，受控 checked/onChange",
        "mini": "小程序 checkbox 组件，bindchange 拿选中值数组",
    },
    "form-radio": {
        "web": "input[type=radio] name 分组，CSS 自定义圆点",
        "app": "RN Radio 组件或自定义，单选靠状态管理",
        "mini": "小程序 radio 组件，同 name 自动互斥",
    },
    "btn-disabled": {
        "web": "button[disabled] 禁用交互，CSS 调灰减透明度",
        "app": "RN disabled 属性+样式区分，禁止点击逻辑",
        "mini": "小程序 button disabled 属性，禁用态样式单独写",
    },
    "btn-icon": {
        "web": "button 内嵌 svg/图标，给 aria-label 说明用途",
        "app": "RN 用 TouchableOpacity 包 Icon 做成 IconButton",
        "mini": "小程序用 icon 组件或 image，bindtap 触发",
    },
    "modal-drawer": {
        "web": "transform+transition 从侧边滑出，蒙层点击关闭",
        "app": "RN Drawer/Modal 组件，自带手势与蒙层",
        "mini": "小程序用 drawer 或自定义 view+transform 滑出",
    },
    "toast-msg": {
        "web": "fixed 居中提示，2-3s 自动消失",
        "app": "RN 用 Toast 库（如 react-native-toast-message）",
        "mini": "小程序 wx.showToast，注意 icon 与 duration",
    },
    "popconfirm": {
        "web": "用 Popover/气泡组件，点确认才执行危险操作",
        "app": "RN 用 Alert/dialog 或自定义气泡确认",
        "mini": "小程序无原生 popconfirm，用弹窗或自定义气泡替代",
    },
    "skeleton": {
        "web": "CSS 渐变+shimmer 动画模拟灰条占位",
        "app": "RN 用 Skeleton 组件或 view+动画占位",
        "mini": "小程序用 view 灰条+动画模拟骨架屏",
    },
    "anim-fade": {
        "web": "opacity 过渡实现淡入淡出，transition 控制时长",
        "app": "RN 用 Animated/Reanimated 做 opacity 动画",
        "mini": "wxss transition opacity 或 WXS 做淡入淡出",
    },
    "anim-flip": {
        "web": "transform:rotateY(180deg)+transform-style:preserve-3d",
        "app": "RN 用 rotateY 动画或 react-native-flip-card",
        "mini": "小程序用 transform:rotateY+preserve-3d 翻牌",
    },
    "anim-progress": {
        "web": "用 width 百分比或 progress 元素做进度条",
        "app": "RN 用 ProgressView/自定义 view width 动画",
        "mini": "小程序 progress 组件，percent 控制进度",
    },
    "hover-lift": {
        "web": "hover 时 translateY(-4px)+阴影，给出浮起感",
        "app": "RN 用 Pressable pressed 态模拟悬停高亮",
        "mini": "小程序 hover-class 加 translateY+阴影",
    },
    "carousel": {
        "web": "flex 轨道+transform 位移，手势+指示点",
        "app": "RN 用横向 ScrollView/第三方 Swiper",
        "mini": "小程序 swiper 组件，autoplay+指示点开箱即用",
    },
}

POLISH_BAD = {
    "nav-hamburger": '''<!-- 桌面菜单原样平铺，窄屏 8 项挤成两行还溢出 -->
<nav class="menu"><a>首页</a><a>分类</a><a>搜索</a><a>消息</a><a>我的</a>...（共 8 项一行排开）</nav>''',
    "nav-anchor": '''<!-- 一整页长文没有任何锚点，用户只能拼命往下滚 -->
<div class="long">第1章...第8章...（全文无目录无跳转）</div>''',
    "scroll-lock": '''/* 只盖了蒙层，没锁 body 滚动，背景还在偷偷滚 */
.overlay{position:fixed;inset:0} /* 漏了 body{overflow:hidden} */
// 滚动穿透，蒙层下面照样滚''',
    "focus-visible": '''/* 没写 :focus-visible，键盘 Tab 切过去完全没焦点提示 */
a{outline:none} /* 键盘用户不知道当前在哪 */
button:focus{outline:none}''',
    "active": '''/* 没 :active 态，点击瞬间毫无反馈，用户怀疑没点到 */
.btn{background:#C8442E} /* 按下没有任何视觉变化 */''',
    "media": '''/* 只有一套固定宽度布局，手机和 4K 屏都硬套 */
.container{width:1200px} /* 手机直接横向溢出，得手动缩放 */''',
    "orientation": '''/* 横竖屏用同一套固定布局，横屏时元素被拉变形 */
.wrap{width:100vw} /* 没处理 orientation，横屏比例全乱 */''',
    "reduce-motion": '''/* 所有动画强制播放，无视系统“减弱动效”偏好 */
.spin{animation:spin 2s infinite} /* 眩晕/前庭用户直接遭殃 */''',
    "toast-msg": '''/* 保存成功后页面静默无任何提示，用户怀疑没保存 */
function save(){api.save(data)} /* 没弹 toast，也没 loading */''',
    "anim-flip": '''/* 点正面直接跳转到另一个页面看背面，割裂感强 */
.front{onclick:go('/back')} /* 离开当前卡片上下文 */''',
    "anim-progress": '''/* 一直转圈 spinner，没有真实进度，用户不知还要等多久 */
.loading{animation:spin 1s infinite} /* 永远 100% 不明 */''',
    "anim-tab": '''/* 多块内容全堆在一屏，或点一下跳一个页面 */
<div class="all">区块A 区块B 区块C...（全平铺无切换）</div>''',
    "card": '''/* 所有内容平铺一屏无分组，信息密度高到看不懂 */
<div class="wall">标题 图 文字 按钮 标题 图 文字...（无卡片边界）</div>''',
    "carousel": '''/* 多张图直接堆在一起重叠，只能手动一张张翻 */
<div><img src="a.jpg"><img src="b.jpg"><img src="c.jpg">（全叠一起）</div>''',
}


def apply_polish(T):
    for t in T:
        iid = t.get("id")
        if iid in POLISH_PLAT:
            t["plat"].update(POLISH_PLAT[iid])
        if iid in POLISH_BAD:
            t["bad"] = POLISH_BAD[iid]
    return T
