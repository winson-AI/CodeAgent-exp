# Compose 映射

将剩余 overlay 映射到 `Box` 分层语义。

当仿 `device-chrome` 被移除后，保持两层区分：

- 背景层可以在真实系统栏之后保持全屏无边距
- 锚定内容层必须通过 Compose inset 处理尊重真实安全区域和底部手势区域，而非仿间隔 chrome

## 常见映射

### 全背景

React / Tailwind：

```jsx
<div className="absolute inset-0 ..." />
```

Compose：

```kotlin
Box(modifier = Modifier.matchParentSize())
```

如果这是背景或支撑层，它可以保持全屏无边距。不要仅因为 React 验证壳包含模拟 device chrome 就添加仿顶部或底部间隔条带。

### 底部 overlay

React / Tailwind：

```jsx
<div className="absolute inset-x-0 bottom-0 ..." />
```

Compose：

```kotlin
Box(
    modifier = Modifier
        .align(Alignment.BottomCenter)
        .fillMaxWidth()
        .navigationBarsPadding()
)
```

用于必须远离模拟器真实导航栏或底部手势指示器的锚定内容。如果元素仅是背景填充，保持背景全屏无边距，并将 inset padding 应用到前景内容层。

### 顶部浮动工具栏

React / Tailwind：

```jsx
<div className="absolute inset-x-0 top-0 ..." />
```

Compose：

```kotlin
Row(
    modifier = Modifier
        .align(Alignment.TopCenter)
        .fillMaxWidth()
        .statusBarsPadding()
)
```

用于真实顶部内容如工具栏或操作。不要在其上方重建仿状态栏块；依赖真实系统 inset。

### 标签页下划线

React / Tailwind：

```jsx
<div className="absolute bottom-0 left-0 w-full h-[2px]" />
```

Compose：

```kotlin
Box(
    modifier = Modifier
        .align(Alignment.BottomCenter)
        .fillMaxWidth()
        .height(2.dp)
)
```

### 卡片底部 overlay

React / Tailwind：

```jsx
<div className="absolute inset-x-0 bottom-0 ..." />
```

Compose：

```kotlin
Row(
    modifier = Modifier
        .align(Alignment.BottomStart)
        .fillMaxWidth()
        .navigationBarsPadding()
)
```

## 决策规则

如果剩余 `absolute` 可以表达为：

- 全覆盖
- 顶部边缘
- 底部边缘
- 居中 overlay

则可以安全保留通过 React 重构并稍后翻译为 `Box` 对齐。

如果它仍需要任意页面坐标，则 React 重构尚未完成。

## Inset 规则

仿 `device-chrome` 移除后：

- 当产品设计期望全屏无边距渲染时，保持背景和支撑层视觉上全屏
- 将 `statusBarsPadding()`、`navigationBarsPadding()`、`WindowInsets.safeDrawing` 或等效 inset 处理添加到锚定内容，而非默认添加到整个屏幕
- 不要通过恢复仿 chrome 块或永久空白间隔条带来解决模拟器 chrome 重叠问题

## 高度约束（heightIn vs height）

将 React 中的固定高度（如 `h-[54px]`）翻译到 Compose 时：
- **对于包含文本或动态内容的容器**，始终使用 `.heightIn(min = 54.dp)` 而非 `.height(54.dp)`。这可防止在不同字体大小和屏幕密度下出现文本截断和内容挤压。
- **对于纯装饰元素或固定图标**，`.height(X.dp)` 是可接受的。
- **绝对不要**对消息卡片、列表项或任何包含可能多行文本的块使用刚性 `.height(...)`，除非明确要求。
