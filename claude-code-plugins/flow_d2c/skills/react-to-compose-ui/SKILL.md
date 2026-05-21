---
name: react-to-compose-ui
description: 使用已验证的 optimized React 壳作为真实来源执行 Compose 翻译阶段。支持单 Figma 输入沿用当前转码流程，也支持多 Figma -> React -> optimized React flow 转换为 Compose 导航、交互逻辑和数据流。先区分目标代码库是默认壳工程还是存量 Android/KMP/CMP 工程；默认壳工程直接转码验证，存量工程先理解仓库、明确 Figma/React 业务在目标代码中的位置，查找 mock API 对应的真实线上数据和可复用 UI/逻辑/数据流组件，再按复用原则增量接入或扩展新业务模块。若存在第三方参考代码库，先分析其 UI/逻辑/数据控制/API/网络实现，将 Mock API 替换为参考代码实际使用的线上数据 API，并将 Figma 业务能力和 React 中间表现无缝嵌入目标 KMP/CMP 仓库。保留 overlay 映射、资源保真、adapter 注册表解析、目标仓库验证门控和构建验证。
---

# React To Compose UI

仅在 React 阶段已通过验证后使用此 skill。

已验证的 React 壳是布局、交互和数据边界的真实来源。不要重新设计层级或将翻译压缩为快速的 Box 和 Column 重写。单 Figma 输入沿用当前单屏翻译流程；多 Figma 输入必须保留 optimized React 中已经验证的 screen registry、页面跳转、交互触发点、mock API 数据边界和跨屏状态。

在翻译之前解析 adapter 使用。读取 `${skill dir}/adapters/registry.json`。如果注册表可读且其 `adapters` 数组包含带 `id` 值的条目，按注册表顺序选择第一个有效的 adapter id 并启用 adapter 模式。如果注册表缺失、不可读或其 `adapters` 数组不包含 adapter id，翻译为原始 Compose 并复用目标工程原生资源。

当 adapter 模式启用时，此 skill 假定所选 adapter 在翻译开始之前已准备就绪。Adapter 创建或重大 adapter 修复不在此工作流范围内。如果所选 adapter 缺失或根本性不完整，停止，在此运行之外修复 adapter，然后重新开始翻译。

Adapter 包仅提供知识。它们不拥有工作流，也不注入自定义执行步骤。此 skill 仍然是翻译、资源保真、目标工程集成和构建验证的工作流所有者。

## 输入

- 一个已验证的 optimized React 实现，通常是 `./react/src/RefactoredComponent.jsx`
- 单 Figma 输入：一张参考截图，通常为 `Preview.png` 或 Figma 导出的屏幕截图
- 多 Figma 输入：多个参考截图 `Preview-screen-**.png`，例如 `Preview-screen-01.png`、`Preview-screen-02.png`
- 一个已解析的 React 资源清单，默认为 `parsed_resources/resources.json`
- 一个预准备的 Android 项目路径
- 一个 Compose 输出目录或目标模块路径
- 当调用方提供时的可选 KMP 上下文目录
- 当调用方提供时的可选第三方参考代码库路径，用于对齐已有业务实现
- 来自上次重试的可选验证失败摘要

## 输入模式和目标类型

在编辑前先记录两个分类，并在执行报告中说明依据：

```text
reactInputMode: single-figma | multi-figma-flow
targetRepoType: shell-compose | existing-android-compose | existing-kmp-cmp
```

### `reactInputMode`

- `single-figma`：React 只表达一个 screen 或一个页面状态，参考截图是 `Preview.png`，没有 screen registry、跨 screen route、回退栈或多组 screen data。
- `multi-figma-flow`：React 来自多张 Figma 设计稿，存在 `Preview-screen-**.png`、screen registry、`currentScreenId`、导航/回退函数、跨屏状态、mock API flow data 或多个可达 screen。

单 Figma 输入直接遵循当前转码流程。多 Figma 输入必须扩展为 Compose 中的多 screen 结构、导航/状态切换、交互事件和数据流，不能压缩为一个静态页面或截图墙。

### `targetRepoType`

- `shell-compose`：默认 Android 壳工程，通常只有基础 `app`、`MainActivity`、`setContent` 和简单 Compose 入口。直接开展转码，把产物挂载到壳入口并用 Gradle 验证。
- `existing-android-compose`：存量 Android Compose 工程。先理解仓库结构、主题、导航、资源、已有 feature/module、ViewModel/state/repository 约定，再判断 Figma 对应业务是否已有模块。优先增量接入已有模块；没有对应模块时，依赖当前仓库基础能力扩展新的业务模块。
- `existing-kmp-cmp`：存量 KMP/CMP 或 Compose Multiplatform 工程。先理解 `commonMain`/平台 source set、`composeApp`/`shared`/feature module、导航、主题、DI、resource API 和状态管理，再按复用原则接入或扩展业务模块。

存量工程场景下，目标不是生成孤立 demo，而是把 Figma 对应业务接入当前代码仓。

## 内置工作区约定

首先读取 [config.json](config.json) 并将其视为默认壳工程的本地约定：

- 必需的构建命令：`./gradlew :app:assembleDebug`
- 可选的 adapter 注册表：`${skill dir}/adapters/registry.json`

如果已验证的 React 文件、截图或 Android 项目路径缺失，停止并报告缺失的产物。如果存在 KMP 上下文目录，在编辑之前读取它。如果不存在，从已验证的 React 源树、截图、已解析资源清单和 Android 项目继续。

构建验证规则：

- `shell-compose`：默认使用 [config.json](config.json) 中的 `./gradlew :app:assembleDebug`。
- `existing-android-compose` 或 `existing-kmp-cmp`：先全局搜索仓库已有构建脚本、Gradle task、README/CI 命令、Makefile、justfile、package scripts 或 IDE 配置；优先使用仓库自己的验证入口。如果无法确定验证命令，先询问用户，不要擅自编造。

## 强制工作流

按顺序执行以下步骤。不要跳过、重排或并行跳过强制步骤。

1. 读取必需的运行时输入：
   - 已验证的 React 文件
   - 单屏：`Preview.png`
   - 多屏：`Preview-screen-**.png` 映射
   - 已解析资源清单（如存在），默认为 `parsed_resources/resources.json`
   - Android 项目路径
   - Compose 输出目录或目标模块路径
   - KMP 上下文目录（如存在）
   - 第三方参考代码库路径（如存在）
   - 重试失败摘要（如存在）
2. 判定并记录 `reactInputMode`：
   - 单 Figma 输入直接使用当前单屏转码路径
   - 多 Figma 输入建立 `screenId -> preview -> React screen/component -> route/event -> data` 映射
3. 判定并记录 `targetRepoType`：
   - 默认壳工程直接转码
   - 存量工程先理解仓库，再决定接入已有业务模块还是扩展新业务模块
4. 读取 [config.json](config.json)
5. 解析所选 adapter 包：
   - 尝试读取 `${skill dir}/adapters/registry.json`
   - 如果注册表可读且其 `adapters` 数组包含带 `id` 值的条目，按注册表顺序选择第一个有效的 adapter id
   - 如果注册表缺失、不可读或其 `adapters` 数组不包含 adapter id，继续使用原始 Compose 翻译并复用目标工程原生资源
   - 如果 adapter id 解析但其包缺失或不明确，停止并报告 adapter 阻塞
   - 如果 adapter id 解析成功，继续启用 adapter 模式
6. 确保 Android 项目路径存在并就地检查
7. 读取 [references/compose-mapping.md](references/compose-mapping.md)
8. 如果 adapter 模式启用，读取 [references/component-library-adapters.md](references/component-library-adapters.md)
9. 在编辑之前理解目标代码库：
   - `MainActivity`
   - `setContent`
   - 现有导航或 scaffold 归属
   - 主题和图片加载依赖
   - 现有库导入和依赖提示
   - 存量工程中的 feature/module 结构、业务入口、ViewModel/state/repository/use case/DI 约定
   - Figma 对应业务在当前仓库是否已有模块；有则增量接入，无则依赖仓库基础能力扩展新模块
10. 如果存在第三方参考代码库，先运行第 7.5 轮理解参考代码库并抽取 Figma 对应业务实现
11. 对存量目标工程运行第 7.8 轮，明确 Figma/React 业务落点、真实数据/API 映射和可复用组件/逻辑/数据流
12. 在大型翻译编辑之前，将已解析的 React 资源物化到目标资源目录：
   - 从 `parsed_resources/resources.json` 读取已解析资源清单，除非调用方显式覆盖清单路径
   - Android 壳/Android Compose 工程：运行 `scripts/convert_svg_to_android_vector.py`，使已解析的 SVG 资源成为 Android `VectorDrawable` XML 文件，已解析的位图资源被复制到目标 drawable 目录
   - KMP/CMP 工程：优先复用现有 multiplatform resource 方案；如果仓库使用 Android drawable 资源，则按现有 source set/模块约定写入
   - 在翻译依赖这些资源的 UI 区域之前，停止并修复资源同步失败
13. 在大型翻译编辑之前，盘点已验证 React 屏幕的真实视觉资源：
   - 当 adapter 模式启用时，目标工程或所选 adapter 资源已提供的图标
   - 从 React 资源清单物化的已解析 drawable 资源
   - 必须保留的 SVG 或内联矢量形状
   - 属于最终 UI 的本地或远程图片资源
   - 当前有被占位符替换风险的任何区域
14. 如果重试摘要存在，先修复该阻塞问题，再扩展翻译
15. 运行第 8 轮以确保每个剩余 overlay 是 Compose 安全的
16. 如果 adapter 模式启用，运行第 8.5 轮以加载所选 adapter 知识并仅检索与当前屏幕或当前 flow 相关的组件条目
17. 运行第 9 轮将已验证的壳层级翻译到目标 Compose 工程
18. 如果 `reactInputMode` 是 `multi-figma-flow`，运行第 9.5 轮生成 Compose 多屏导航、交互逻辑和数据流
19. 显式分类从 React 携带过来的任何仿状态栏、home indicator 或其他 `device-chrome`，并在布局基线正确后从最终 Compose UI 中移除该仿 chrome
20. 移除仿 `device-chrome` 后，保持实际应用内容和背景填满全屏；不要在模拟器应提供真实系统 chrome 的位置留下顶部或底部空白条带
21. 虽然仿 `device-chrome` 必须移除，但锚定内容（如工具栏、底部操作、浮动按钮和底部导航）须保持与真实模拟器系统栏的安全距离；背景可以保持全屏无边距，但内容不得与导航栏或底部手势指示器冲突
22. 先添加专用 screen/feature composable，然后按 `targetRepoType` 挂载：
   - `shell-compose`：挂载到壳入口点
   - 存量工程：挂载到现有导航、feature 入口或业务模块入口，避免孤立 demo
23. 自行负责 build -> fix -> build 循环：
   - `shell-compose` 使用 [config.json](config.json) 中的构建命令，默认为 `./gradlew :app:assembleDebug`
   - 存量工程使用仓库已有验证命令；无法确定时询问用户
24. 仅在 Compose 文件存在且验证健康，或报告了实际阻塞后退出

## 停止条件

- 如果 React 阶段未经验证，停止并报告 Compose 尚无法开始
- 如果已验证的 React 文件缺失，停止，而非从过时内存或原始 D2C 导出翻译
- 如果 adapter 模式启用且所选 adapter id 未解析到 `${skill dir}/adapters/` 下的包，停止并报告缺失的 adapter
- 如果 adapter 模式启用且翻译因所选 adapter 缺少核心库规则或基本组件知识而受阻，停止并报告 adapter 必须在重新运行前修复
- 如果 Android 项目路径缺失，停止并报告缺失项目阻塞
- 如果 `scripts/convert_svg_to_android_vector.py` 在物化已解析资源时失败，停止并报告资源物化阻塞，再继续 Compose 翻译
- 如果多 Figma 输入没有 `Preview-screen-**.png` 映射、screen registry、可达 screen 或基本跳转关系，停止并报告 flow 输入阻塞
- 如果存量工程无法确定目标业务模块、导航入口或扩展位置，先完成仓库理解；仍无法判断时询问用户，不要写孤立 demo
- 如果存量工程中无法确认 React mock API 对应的真实数据/API/repository/use case，先报告候选和缺口；不要擅自发明线上接口
- 如果第三方参考代码库存在但无法定位 Figma 对应业务场景，先报告已搜索范围和缺口；不要把整个参考仓库照搬到目标工程
- 如果验证命令失败，持续修复项目直到通过或遇到实际阻塞；不要在未明确说明阻塞内容的情况下将控制权交还作为部分成功

如果构建因环境配置而非布局代码失败，先修复本地前置条件：

- 无效的 `org.gradle.java.home`
- 缺少 `sdk.dir` 或 `ANDROID_HOME`
- 缺少壳本地配置文件如 `local.properties`

不要将这些视为布局失败。修复壳环境，然后继续验证。

## 轮次

### 第 7.5 轮：第三方参考代码库理解和业务抽取

仅当调用方提供第三方参考代码库时运行。

目标：如果 Figma 设计稿在第三方参考代码库中已有实现，先理解参考仓库整体架构，再抽取与当前 Figma 业务场景直接相关的实现细节，作为目标 Android/KMP/CMP 工程的映射参考。

执行：

1. 识别参考仓库技术栈、模块结构、入口、路由/导航、UI 层、状态管理、数据控制、API/network 层和资源组织。
2. 定位 Figma 对应业务场景在参考仓库中的实现：
   - 页面/screen/component
   - 交互逻辑和状态流转
   - 数据模型、repository/service/API 调用
   - 网络请求、参数、响应模型、错误/空态/加载态
   - 资源、主题、组件和设计系统使用
3. 输出可映射清单：
   - 可直接借鉴的 UI 结构和组件语义
   - 可映射到目标工程的逻辑、状态和数据控制
   - 可映射到目标工程真实 API 或 repository/use case 的数据模型
   - React mock API 应替换为参考仓库实际线上数据 API 的位置，包括 endpoint/service、请求参数、响应模型、错误处理、鉴权/session、分页/搜索/筛选语义
   - 需要新增到目标工程的必要依赖
   - 不能直接复用、只能作为语义参考的实现
4. 不要照搬参考仓库结构。参考仓库用于理解业务实现，最终代码必须遵循目标工程结构、依赖、编码规范、架构边界和验证门控。

如果目标是 `shell-compose`，仍应复用参考代码库中与 Figma 业务对应的 UI/逻辑/数据控制/API/network 设计；同时补充最小必要依赖和 mock/real API 边界，使壳工程可编译运行。

如果目标是 `existing-kmp-cmp`，参考代码库提取结果必须被映射到目标 KMP/CMP 仓库的既有 source set、feature/module、navigation、DI、repository/use case、ViewModel/store、UiState、resource 和 networking 约定中。不要创建与目标仓库割裂的独立实现。

### 第 7.8 轮：存量目标工程业务落点和复用分析

仅当 `targetRepoType` 是 `existing-android-compose` 或 `existing-kmp-cmp` 时运行。

目标：在写 Compose 代码之前，明确 Figma/React 业务在存量代码中的位置，并找到可复用的 UI、逻辑和真实数据能力。

执行：

1. 明确业务落点：
   - Figma/React 对应的是哪个业务域、feature、route、tab、入口或用户流程
   - 目标仓库是否已有对应模块；如果已有，作为增量开发无缝融合
   - 如果没有对应模块，选择最贴近的父模块、导航入口、主题和数据层能力扩展新业务模块
2. 对齐 React mock API 到真实数据：
   - 读取 React mock API/local service/adapter 的字段、数据结构、状态和调用方式
   - 在目标仓库搜索对应的 API service、repository、use case、DAO/cache、DTO/domain model、ViewModel/store 和 UiState
   - 建立 `reactMockField -> targetRealField/API/model` 映射
   - 找不到真实接口时，只保留最小 mock 或 adapter 边界并明确缺口；不要发明线上接口
3. 查找可复用 UI/逻辑/数据流组件：
   - UI：design system、theme、button、card、list item、toolbar、bottom nav、input/search/filter、dialog、loading/empty/error 组件
   - 逻辑：navigation、selection、pagination/search/filter/form validation、back handling、permission/session 等已有机制
   - 数据流控制：ViewModel/store、UiState、Flow/StateFlow、repository/use case、DI、error handling、loading/empty 状态
4. 输出接入决策：
   - 复用哪些已有模块/组件/API/状态流
   - 新增哪些最小文件
   - Figma 业务接入到哪条 navigation/feature 入口
   - React mock 数据如何替换为真实数据或保留为临时 adapter

已有模块增量开发时，优先修改或扩展现有模块内的 screen/component/ViewModel/state/repository 接入点，避免创建平行的新 feature。

### 第 8 轮：将剩余 Overlay 映射到 Compose

目标：确保每个剩余 `absolute` 可以翻译为 Compose `Box` 对齐。

如果剩余 `absolute` 仍依赖任意页面坐标，返回上一步。如果它可以表达为顶部边缘、底部边缘、全覆盖或居中 overlay，则是 Compose 安全的。

使用 [references/compose-mapping.md](references/compose-mapping.md)。

### 第 8.5 轮：加载 Adapter 知识并检索组件

目标：当 adapter 模式启用时，在翻译之前加载所选 adapter 包并仅检索与当前 screen 或当前 flow 相关的组件。

仅在注册表解析出 adapter id 时运行此轮。

工作流：

1. 检查已验证 React 文件中的语义提示：
   - 组件名称
   - 可复用 UI 原语
   - 点击目标
   - 列表、面板、标签、按钮、工具栏和对话框模式
2. 检查截图以进行视觉消歧：
   - 填充与描边操作
   - 药丸形、chip、badge 和 tag 形状
   - 标题栏和面板样式
   - 分隔线和卡片处理
3. 检查目标工程的库可用性：
   - 现有导入
   - 现有主题归属
   - 已接入目标工程的依赖提示
4. 从 `${skill dir}/adapters/<selected adapter id>/` 读取所选 adapter 包的 `manifest.json`；当 `${skill dir}/adapters/registry.json` 元数据可用时使用它
5. 确认目标工程暴露了所选 adapter 声明的包前缀、导入或依赖提示
6. 读取所选 adapter 的 `aliases.json`
7. 使用 `aliases.json` 加上目标工程和 React 证据缩小可能的组件名称范围
8. 使用 `component_knowledge.json` 作为所选组件名称的默认完整查找源
9. 仅当 `component_knowledge.jsonl` 文件存在且你需要更丰富的示例或参数/事件细节时才打开它
10. 读取 `prompt.md`
11. 仅检索与屏幕相关的组件条目，而非加载整个库或完整示例包
12. 将所选 adapter 规则、候选映射和检索到的组件知识带入第 9 轮

React 是结构和语义的主要真实来源。截图是视觉消歧的次要来源。

如果所选 adapter 存在但目标工程证据薄弱或缺失，不要自动切换到另一个 adapter。首先保持整体布局正确，仅对不支持或低置信度的区域回退到原始 Compose。

如果 adapter 差距是局部的且小的，在该区域继续使用原始 Compose。如果 adapter 差距是结构性的、重复的，或使库无法作为所选真实来源使用，停止并在重新运行前在工作流外修复 adapter。

### 第 9 轮：翻译到目标 Compose 工程

目标：将已验证的移动端布局移入目标 Compose 工程，不丢失壳层级、重叠语义、运行时稳定性，或在 adapter 模式启用时所选 adapter 意图。

仅在 React 壳视觉上足够稳定后使用此轮。

工作流：

1. 在编辑之前检查目标工程入口点
   - 如果 Android 项目路径缺失，停止并报告缺失项目阻塞
   - 如果是存量工程，先定位现有导航、feature/module、主题、资源和状态管理约定
2. 先添加专用屏幕或 feature composable，然后将其挂载到目标入口点
3. 将已验证的 React 壳翻译为 Compose 结构：
   - `Box` 用于真正的 overlay
   - `Column` 和 `Row` 用于流式区域
   - `LazyColumn` 用于重复列表
   - `align(...)` 用于顶部、底部和居中 overlay
4. 在翻译期间保留以下语义：
   - hero 背景与支撑层
   - 工具栏锚点
   - 头像重叠深度
   - 内容壳归属
   - 底部导航归属
5. 默认使用原始 Compose 和目标工程原生资源；如果 adapter 模式启用，当匹配置信度高时优先使用所选 adapter 组件，对不明确或不支持的区域回退到原始 Compose
6. 在发明回退方案之前保留真实图标和图稿：
   - 如果目标工程或所选 adapter 已暴露正确的图标资源，直接复用该资源
   - 如果源使用必须在 Android 中保留的 SVG 或内联矢量图，通过已解析资源同步流程将其物化，使其成为 Android 兼容的 `VectorDrawable` `.xml` 资源，而非留下原始 `.svg` 供 Android 运行时加载
   - 不要仅为了让屏幕编译就用占位符框、占位符图片或无关素材替换真实图标或插图
7. 如果视觉徽章已嵌入 SVG 或图片资源中，不要在其上再添加 Compose 徽章
8. 如果远程 hero 资源或背景拼贴在运行时加载失败，仅用本地 drawable 替换不稳定的支撑层，再判断整体翻译
9. 将仿状态栏、home indicator 和其他 `device-chrome` 视为临时验证产物，而非最终应用 UI
10. 一旦布局基线正确，从 Compose 输出中移除仿 `device-chrome`
11. 移除仿 `device-chrome` 后，确保真实屏幕仍视觉上填满整个设备视口：
    - hero 背景和支撑层在适当时须继续延伸到系统栏之后
    - 内容容器仍须拥有全屏高度，而非缩小到旧的模拟框架
    - 不要在移除的仿状态栏或 home indicator 原位置留下空白 padding 条带
    - 锚定内容仍须通过 Compose inset 处理（如 `WindowInsets`、`statusBarsPadding()`、`navigationBarsPadding()` 或 safe-drawing padding）尊重真实系统栏和底部手势区域
12. 按目标工程类型验证：

默认壳工程：

```bash
./gradlew :app:assembleDebug
```

存量工程：

- 全局搜索仓库已有编译脚本/工具，例如 Gradle task、README/CI 命令、Makefile、justfile、脚本目录或 IDE 配置。
- 优先使用仓库自己的验证命令。
- 如果找不到明确命令，询问用户选择验证方式。

Compose 翻译检查清单：

- 屏幕或业务入口已挂载到目标工程中，可从应用启动路径、导航路径或目标 feature 入口访问
- 编译时错误已解决
- 关键背景在运行时可见
- 翻译期间未引入重复 overlay
- 工具栏、头像和面板仍占据与已验证 React 版本相同的视觉条带
- 当 adapter 模式启用时，在证据充分处使用了所选 adapter 组件
- 多屏 flow 的每个可达 screen 都有 Compose 表达，并能通过导航/状态切换到达
- 存量工程中没有生成脱离现有入口和业务模块的孤立 demo

### 第 9.5 轮：多 Figma Flow 的 Compose 导航和数据流

仅当 `reactInputMode` 是 `multi-figma-flow` 时运行。

目标：把 optimized React 中已验证的页面跳转、交互逻辑和 mock API 数据边界映射为 Compose/KMP/CMP 可维护结构。

执行：

1. 建立 `screenId -> preview -> composable -> route/state -> data` 映射。
2. 将 React 的 `currentScreenId`、screen registry、回退栈、route 参数或选中项映射到目标仓库已有导航或状态机制：
   - 默认壳工程可使用最小可运行的 Compose state/navigation shell。
   - 存量工程优先复用现有 navigation graph、route 类型、ViewModel/store、UiState、repository/use case 和 DI。
3. 将 React 事件映射为 Compose 事件：
   - button/CTA/card/list item -> navigate/select/submit
   - back icon/close -> popBack/goBack
   - tab/segmented/filter -> update state/filter
   - input/search/input bar -> controlled state、query update、submit/search action
4. 将 React mock API/local service 数据边界映射到 Compose 数据层：
   - 默认壳工程可创建最小 mock repository 或 in-memory provider。
   - 存量工程优先接入已有 repository/use case/ViewModel/store/UiState；没有对应能力时新增最小必要模块，并遵循仓库命名、分层和 DI 约定。
   - 如果存在第三方参考代码库，并且参考库中已实现该 Figma 业务的线上数据 API，必须优先用参考代码中的真实 API/service/repository/network 模型替换 React mock API；不要继续保留 mock 作为最终数据源。
   - 将参考 API 的请求参数、响应模型、错误处理、鉴权/session、分页、搜索、筛选和缓存语义映射到目标 KMP/CMP 仓库已有网络层和数据层。
5. 每个可达 screen 必须能展示对应数据，并且跳转时携带必要状态，例如 selected id、query、filter、form draft 或 back target。
6. 不要把多张 `Preview-screen-**.png` 作为图片拼接进 Compose；截图只作为验证参考。

## 规则

- 此 skill 从已验证的 React 壳开始，而非从原始 D2C 画布开始。
- 强制工作流步骤必须按顺序执行。不要因为翻译路径看似明显就跳过它们。
- 在翻译之前读取 `${skill dir}/adapters/registry.json`。
- 所选 adapter 包仅提供知识。不要让它接管工作流。
- 不要在运行中途暂停以创建新 adapter。Adapter 生成是预检活动，而非翻译子步骤。
- 如果存在 KMP 上下文目录，在编辑之前读取它。其缺失不是阻塞。
- 如果 Android 项目路径缺失，在翻译之前停止。
- 在编辑前必须判定 `reactInputMode` 和 `targetRepoType`。单屏走当前单屏流程；多屏必须保留 flow、交互和数据边界。
- 存量工程必须先理解仓库，再写代码。优先复用现有 navigation、theme、component、resource、ViewModel/store、repository/use case、DI 和 module 结构。
- 存量工程中如果存在 Figma 对应业务模块，直接增量接入；如果不存在，依赖当前仓库基础能力扩展新的业务模块。两种情况都遵循复用原则。
- 存量工程必须明确 Figma/React 在目标代码中的业务落点。已有模块增量开发时，应与现有模块无缝融合，不要创建平行模块绕过原业务。
- React mock API 必须尝试映射到目标工程真实线上数据能力，包括 API service、repository、use case、DTO/domain model、ViewModel/store 和 UiState。找不到真实能力时保留 adapter 边界并报告缺口，不要发明线上接口。
- React 中使用的 UI 组件、交互逻辑和数据流控制必须在目标 Android/KMP/CMP 工程中查找可复用实现；优先复用已有设计系统、组件、状态管理、导航、数据层和 DI。
- 如果提供第三方参考代码库，必须先理解其架构和 Figma 对应业务实现，再只抽取可映射的 UI/逻辑/数据控制/API/network 设计对齐到目标工程。目标为壳工程时，也要复用参考实现的业务设计并补充必要依赖。
- 如果第三方参考代码库中存在该 Figma 业务实际使用的线上数据 API，最终目标实现必须用该真实 API/service/repository/network 模型替换 React mock API。Mock 只能作为无法接入真实 API 时的临时 adapter，并且必须在报告中说明缺口。
- 生成到 `existing-kmp-cmp` 时，Figma 业务能力和 optimized React 中间表现必须无缝嵌入目标 KMP/CMP 仓库：遵循既有 source set、feature/module、navigation、DI、resource、network、repository/use case、ViewModel/store、UiState 和编码规范。
- 融合过程必须符合目标 KMP/CMP 仓库已有架构要求和代码风格；不得孤立于目标仓库，不得引入与目标仓库约定冲突的平行架构、平行网络层、平行状态管理或平行资源体系。
- 必须沿用目标 KMP/CMP 仓库已有评估和验证门控，例如 build、unit test、KMP/CMP target 编译、detekt/ktlint/lint、preview/screenshot、CI 脚本或仓库自定义校验。发现问题时先修复，再声明完成。
- 不要在存量工程中生成孤立 demo、独立壳 App 或绕过现有导航入口的新页面。
- 除非重试摘要证明存在直接翻译 bug，否则不要重新设计已验证的 React 层级。
- 使用 `Box` 用于真正的 overlay 和对齐层。
- 使用 `Column` 和 `Row` 用于流式内容。
- 仅对真正重复的垂直内容使用 `LazyColumn`。
- 将 absolute 风格的定位限制在真正的 overlay，而非整个页面。
- 优先使用父级相对尺寸和对齐，而非硬编码 dp 宽度。
- 仿状态栏、home indicator 或其他设备模拟元素不是最终 Compose UI 的一部分。
- 如果 `device-chrome` 在 React 参考中仅用于截图匹配，在布局基线正确后于 Compose 中移除它。
- 移除仿 `device-chrome` 不意味着将相应屏幕区域留空；应用背景和内容壳仍需填满模拟器在系统 chrome 后面显示的真实全屏视口。
- 模拟器的真实系统 chrome 应替换仿 chrome，而你的 Compose 背景在产品设计期望的位置仍须全屏无边距。
- 全屏无边距背景不意味着全屏无边距内容。工具栏、底部栏、固定 CTA 和其他锚定控件必须通过使用适当的 Compose inset API 而非仿间隔 chrome，与真实系统栏和底部手势指示器保持足够距离。
- 保留真实资源保真。不要仅因为 Android 无法直接渲染原始 `.svg` 就用占位符替换源图标、SVG 衍生矢量或有意义的插图。
- 为 Android 运行时兼容性，将需要在应用中发布的本地 SVG 设计资源转换为 `VectorDrawable` `.xml` 资源后再从 Compose 引用。不要依赖原始 `.svg` 文件作为 Android drawable 输入。
- 优先通过 `scripts/convert_svg_to_android_vector.py` 将 `parse_resources.py` 清单物化到目标工程资源目录，而非手动创建资源回退；KMP/CMP 工程按现有 multiplatform resource 方案处理。
- 当 React 阶段已产出 `parsed_resources/resources.json` 时，优先使用内置辅助脚本 `scripts/convert_svg_to_android_vector.py` 作为默认 Android 资源物化路径；它应在 Compose 代码开始引用这些资源之前，将已解析的 SVG 和已解析的位图资源转换/复制到目标 `res/drawable/` 或仓库约定的资源目录。
- 当现有目标工程资源或 adapter 提供的 drawable 指导匹配时优先使用。当必须添加新的本地矢量资源时，添加真实的转换后 drawable 资源而非临时占位符。
- 优先将已验证的 React 层级翻译为真实的目标工程 Compose 入口，而非编写隔离的伪 Compose 代码片段。
- 先添加屏幕 composable 并将其挂载到目标工程现有的 activity、导航层或 feature 入口，而非重写无关的应用结构。
- 多 Figma flow 必须翻译为 Compose 中真实可达的多个 screen/状态；不要压缩为单 screen 静态页面。
- 多 Figma flow 的交互组件和数据流必须保留：页面跳转、按钮/卡片/列表点击、tab/filter、input/search/input bar、selected item、query/filter/form state 和 mock API 数据边界。
- 一旦 adapter id 解析，不要在库选择上花时间。此 skill 必须在该次运行中保持使用该 adapter。
- 当无 adapter id 解析时优先使用原始 Compose。仅当 adapter 模式启用且 adapter 匹配置信度高时，优先使用所选 adapter 组件而非原始 Compose。
- 当 React 语义和截图证据强烈不一致时，不要强制使用 adapter 组件。
- 使用 `component_knowledge.json` 作为默认完整查找源，仅当 `component_knowledge.jsonl` 文件存在时将其保留用于针对性深度示例。
- 在声称翻译就绪之前，运行目标工程适用的构建命令。默认壳工程使用 [config.json](config.json)；存量工程优先使用仓库已有验证命令，找不到时询问用户。
- 对目标 KMP/CMP 仓库，验证不应只停留在单个 Android assemble。优先执行仓库已有的 KMP/CMP 验证门控；如果门控失败，修复由本次融合引入的问题，直到通过或明确报告外部阻塞。
- 如果运行时网络图片使 Compose 屏幕看起来空白或不稳定，仅先本地化关键支撑层资源，以便布局验证可以继续。

## 脚本

### `scripts/convert_svg_to_android_vector.py`

将此作为 Android drawable 资源物化入口。它读取 `parsed_resources/resources.json`，将已解析的 SVG 文件转换为 Android `VectorDrawable` XML 资源，并将已解析的位图资源复制到目标 drawable 目录。KMP/CMP 工程如果使用其他 multiplatform resource 方案，应遵循仓库现有资源入口。

首选命令：

```bash
python3 scripts/convert_svg_to_android_vector.py \
  --manifest parsed_resources/resources.json \
  --output-dir <android-project>/app/src/main/res/drawable \
  --overwrite
```

## 参考

- [config.json](config.json)
- [references/compose-mapping.md](references/compose-mapping.md)
- [references/component-library-adapters.md](references/component-library-adapters.md)

## 退出条件

- 在所提供 Android 项目的 Compose 输出根目录下至少存在一个 Compose 文件
- Compose 层级反映已验证的 React 结构而非原始 D2C 画布
- 已记录 `reactInputMode` 和 `targetRepoType`
- 单 Figma 输入沿用单屏转码流程；多 Figma 输入保留了多 preview、页面跳转、交互逻辑和数据流
- 存量工程中 Figma 对应业务已接入现有模块，或按仓库基础能力扩展为新业务模块；没有孤立 demo
- 存量工程中已记录 Figma/React 业务落点、真实数据/API 映射、可复用 UI 组件、可复用逻辑和可复用数据流控制；缺口已明确说明
- 如果存在第三方参考代码库，已记录其 Figma 对应业务场景的 UI/逻辑/数据控制/API/network 映射结果，并说明哪些被复用、哪些只作为语义参考
- 如果参考代码库提供真实线上数据 API，React mock API 已被目标实现中的真实 API/service/repository/network 模型替换，或已明确说明无法替换的外部阻塞
- 如果目标是 KMP/CMP 存量仓库，Figma 业务能力和 optimized React 中间表现已按目标仓库架构无缝嵌入，未引入平行架构或与仓库约定冲突的实现
- 来自验证壳的仿 `device-chrome` 已从最终 Compose UI 中移除
- Compose 屏幕在仿 `device-chrome` 移除后仍填满真实设备视口；没有留下空白顶部或底部条带
- 锚定内容在仿 `device-chrome` 移除后仍与真实模拟器系统栏和底部手势指示器保持距离
- 真实图标和矢量/图片资源已保留或正确转换；最终 Compose 屏幕中未留下占位符图稿
- 当 adapter 模式启用时，所选 adapter 包已被解析、验证并用于组件检索
- Android 项目路径存在并已就地检查
- 目标工程适用的验证命令已通过：默认壳工程使用 [config.json](config.json)，存量工程使用仓库已有命令；KMP/CMP 仓库沿用了已有评估和验证门控并修复本次引入的问题；若无法确定命令，已询问用户并报告阻塞
- stdout 简要列出已更改的文件、adapter 模式启用时的所选 adapter id、构建状态和任何仍存在的实际障碍
