---
name: mobile-react-refactor
description: 将 React 验证壳从 ./react/src/ValidatedComponent.jsx 重构为 ./react/src/RefactoredComponent.jsx，并严格区分截图输入：单张 Figma 只使用 Preview.png；多张 Figma flow 只使用 Preview-screen-**.png，不应出现或依赖 Preview.png。用于把 Figma 导出的静态 React 或交互 flow 重构为移动端自适应、跨 Figma 渲染环境稳定、优先复用本地 Figma resource（layer/icon/image/section/json/component 等），并在检测到缺失资源时从 Figma 资源库补齐以保障还原度；识别并实现 input/search/input bar 等交互组件、保留 React 页面跳转事件、且通过 mock API 数据加载接口支撑多屏展示数据的 optimized React。如果 Figma 设计稿在第三方参考代码库中已有实现，先理解参考库的 UI/逻辑/数据控制/API/网络架构并抽取对应业务场景，再将可映射能力对齐到 optimized React。
---

# Mobile React Refactor

在 React 验证阶段使用此 skill。

此工作流使用预准备的本地 React 产物和本地 Figma resource，聚焦于重构、验证、像素校验、动态适配、交互恢复和数据接口抽象。输入可能是单屏静态 Figma React，也可能是由多个 Figma section 拼接出的 flow 跳转版本。先判定输入模式，再选择验证粒度：单屏沿用单张 Figma 重构逻辑；多屏在逐屏重构能力之上保留 React 事件驱动的前后跳转行为，并通过 mock API 数据支撑页面展示与跨屏状态。当存在第三方参考代码库时，参考库是业务语义和交互/数据控制的重要证据；optimized React 仍以 Figma 截图和已验证 React 为视觉真实来源，但应对齐参考库中对应业务的 UI 结构、交互逻辑、数据控制和 API/network 语义。

## 输入

- 预准备的 React 壳位于 `./react`
- 源组件位于 `./react/src/ValidatedComponent.jsx`
- 单屏输入的唯一参考截图位于 `./Preview.png`
- 多屏 flow 的参考截图位于 `./Preview-screen-**.png`，例如 `Preview-screen-01.png`、`Preview-screen-02.png`
- 单屏和多屏截图约定互斥：多屏 flow 不应创建、读取或依赖 `Preview.png`
- 本地 Figma resource 通常已预准备；可选资源清单位于 `./parsed_resources/resources.json` 或导出产物中的等价 manifest。如果本轮 React 优化检测到资源缺失，应从 Figma 资源库补齐缺失项以优先保障还原度
- Figma resource 可能包括 layer、icon、image、section、json、component、SVG、字体、样式 token、导出图片和资源引用映射
- 可选第三方参考代码库路径：当 Figma 设计稿在参考库中已有实现时，用于提取对应业务场景的 UI、逻辑、数据控制、API 和网络实现
- 来自上次重试的可选验证失败摘要

## 输入模式和完成度判断

在进入审计、重构和像素循环前，先将输入归类为以下之一，并在执行报告中说明依据。

### 单屏 Figma React

判定依据：

- `ValidatedComponent.jsx` 只表达一个 screen 或一个页面状态
- 没有 screen registry、`currentScreenId`、路由切换、状态机或多组 Raw screen 组件
- 只有 `Preview.png`

处理方式：

- 直接沿用本 skill 原有单屏重构逻辑：审计布局、恢复语义壳、抽象数据、移动端适配、截图验证。
- 保留单屏内已有交互，例如 tab、展开、选择、输入、按钮状态；但不要凭空发明跨 screen flow。
- 完成度以 `RefactoredComponent.jsx` 在 `/refactored` 中稳定渲染该 screen，且构建、移动端适配和必要像素循环通过为准。

### 多屏 Figma React Flow

判定依据：

- 用户明确给出多张 Figma 设计稿或多节点转码结果
- `ValidatedComponent.jsx` 已经包含多个 screen 组件、screen registry、`currentScreenId`、flow 状态、路由切换或上一页/下一页逻辑
- 本地存在多个截图，如 `Preview-screen-01.png`、`Preview-screen-02.png`，或存在多个 Raw screen 源文件

处理方式：

- 将每个 screen 当作一次单屏重构对象，分别恢复布局语义、数据模型和移动端适配。
- 将 flow shell 当作独立结构保留和优化：screen registry、当前 screen 状态、跳转函数、回退栈、路由参数和跨 screen 状态都必须有明确归属。
- 保留或补强设计稿内部的高置信度触发点，例如 recent item、CTA、filter chip、apply button、back icon、tab、卡片、input text、search bar、input bar、筛选框、表单控件和底部导航。调试用上一页/下一页控件只能作为 fallback，不能替代设计内触发点。
- 多屏展示数据必须来自 mock API、local service 或 adapter：列表、详情、搜索结果、选中态、筛选条件和跨屏参数不能继续散落在硬编码 JSX 中。
- 多屏不使用 `Preview.png` 代表初始 screen；初始 screen 也必须有自己的 `Preview-screen-**.png` 截图。
- 多屏完成度必须覆盖每个可达 screen 的截图、布局检查、交互跳转和构建验证。

### 完成度关系

- 单屏完成 = 一个 screen 的视觉、数据边界、响应式和构建健康。
- 多屏完成 = 每个 screen 均满足单屏完成要求，并且 screen 之间的 React 事件跳转前后行为与输入 flow 一致。
- 如果某个 screen 的 `Preview-screen-**.png` 截图缺失、路由不可达或触发目标不确定，先补齐证据或在报告中标注低置信度 fallback；不要把多屏 flow 简化为静态截图墙。

## 准备

在继续之前确认以下本地产物：

1. `react/src/ValidatedComponent.jsx` 存在
2. 截图输入符合模式：单屏必须存在 `Preview.png`；多屏必须存在每个可达 screen 对应的 `Preview-screen-**.png`，且不依赖 `Preview.png`
3. React 壳可以通过 `/validated` 路由渲染已验证组件
4. 已完成输入模式判定：单屏 Figma React 或多屏 Figma React flow
5. 确认 Figma resource 是否在本地完备可用。若 `parsed_resources/resources.json` 缺失，先从本地工作文件和本地资源目录生成索引清单；如果检测到 layer/icon/image/section/json/component 等资源缺失，允许从 Figma 资源库下载缺失项并更新清单，优先保障视觉还原度
6. 如果存在多屏 flow，确认每个可达 screen 都有对应的 `Preview-screen-**.png`，并记录 screenId 到截图文件的映射
7. 如果调用方提供第三方参考代码库路径，确认路径存在并记录为 referenceRepo；如果路径缺失但用户明确要求参考库对齐，先要求补充路径

## 如何阅读此 Skill

- `Mandatory Workflow` 是必须遵守的外层执行顺序。
- `Rounds` 将强制工作流步骤 5-15 展开为详细的分析与重构循环。
- 当工作流步骤说 `read` 某个文件时，意思是：
  - 为特定决策目的而读取
  - 在下一个相关动作中立即使用
  - 不要将其视为可选的背景阅读

## 强制工作流

按顺序执行以下步骤。不要跳过、重排或并行跳过强制步骤。

1. 确认预准备的本地产物：
   - `react/src/ValidatedComponent.jsx`
   - 单屏：`Preview.png`
   - 多屏：`Preview-screen-**.png` 映射；不要要求或读取 `Preview.png`
   - React 壳路由 `/validated`
   - 输入模式：单屏 Figma React 或多屏 Figma React flow
   - 多屏 flow 的 screen 清单、初始 screen、可达 screen、跳转入口和 `Preview-screen-**.png` 映射
   - Figma resource 优先使用本地已有资产，包括 layer/icon/image/section/json/component 等可用资源
   - 已解析资源清单位于 `parsed_resources/resources.json`；缺失时先从本地文件创建索引清单
   - 如果发现 JSX、manifest 或截图验证证明资源缺失，允许从 Figma 资源库下载缺失资源并更新 `parsed_resources/resources.json`
   - 下载只用于补齐缺失的 Figma resource；不要用通用占位图、公共图标包、emoji 或重绘替代真实资源
   - 第三方参考代码库路径（如存在）

   - 在继续之前确保以下产物在本地存在：
     - React 工作文件
     - 单屏：`Preview.png`
     - 多屏：每个可达 screen 对应的 `Preview-screen-**.png`
     - Figma resource 本地文件或本地 manifest；如果缺失项已检测到，已有下载计划或已完成补齐
     - 已解析资源清单位于 `parsed_resources/resources.json`
     - 第三方参考代码库路径存在（如调用方提供）
2. 读取预准备的输入：
   - React 工作文件
   - 单屏：`Preview.png`
   - 多屏：`Preview-screen-**.png` 映射
   - 已解析资源清单，默认为 `parsed_resources/resources.json`
   - 第三方参考代码库的入口、模块结构和与 Figma 业务相关文件（如存在）
   - 重试失败摘要（如存在）
   - 目的：
     - 在做出布局决策之前，确立原始导出结构、可编辑壳目标、输入模式、视觉参考、flow 边界、跳转表、交互组件清单、具体资源清单和参考库业务证据
3. 在做出锚点决策之前打开对应参考截图：单屏打开 `Preview.png`；多屏只打开每个 `Preview-screen-**.png`
   - 不要使用 `cat`、`head`、`grep` 或 `sed` 等面向文本的命令读取 `Preview.png` 或其他截图文件
   - 需要尺寸或元数据时，使用 `sips` 或 `file` 等图像安全检查命令
   - 目的：
     - 使用截图判断视觉条带位置、重叠深度，以及节点是真正贴边还是自由浮动
     - 对多屏 flow，建立每个 screen 的视觉边界、可点击区域和目标 screen 关系
4. 读取 [config.json](config.json)
   - 目的：
     - 了解像素验证默认值，如浏览器和等待时间
5. 如果运行时暴露了专用工具 `run_layout_audit`、`capture_preview` 和 `run_pixel_diff`，优先使用这些工具，而非手动用 shell 重建脚本命令
   - 目的：
     - 保持审计、截图和 diff 行为与 skill 默认值一致，而非临时拼凑命令
6. 自行对工作文件运行布局审计，并将其输出作为第一轮风险图
   - 目的：
     - 识别 absolute 节点、固定尺寸和锚点密集区域，后续轮次必须优先检查这些区域
     - 对多屏 flow，同时识别 flow shell、每个 screen 子树和跨 screen 共享组件中的布局风险
7. 读取 [references/heuristics.md](references/heuristics.md) 并对节点分类
   - 目的：
     - 将导出节点分类为 background、support-layer、overlay、floating-content、flow-content 和 device-chrome
     - 决定哪些节点应保留分层含义，哪些应转换为父级相对的流式结构
8. 为实现像素一致性，在编辑 JSX 之前读取 [references/pixel-validation.md](references/pixel-validation.md)
   - 目的：
     - 在进行后续将以 `Preview.png`（单屏）或对应 `Preview-screen-**.png`（多屏）为评判标准的编辑之前，先了解截图循环规则
8.5. 在重构 JSX 之前识别 Figma 渲染环境假设
   - 目的：
     - 判断导出代码是否依赖固定画布宽高、Figma preview 外壳、设备 chrome、缩放比例、根级居中夹具或不可迁移的 viewport 假设
     - 为后续移动端动态适配建立约束：根页面必须填满真实视口，内部区域按父级和内容语义适配
8.7. 如果存在第三方参考代码库，在重构 JSX 之前理解参考库并抽取 Figma 对应业务场景
   - 目的：
     - 理解参考代码库整体架构，包括 UI 层、逻辑层、状态/数据控制、API/network、路由/导航、资源和设计系统
     - 定位 Figma 设计稿对应业务在参考库中的实现，并抽取 UI 结构、交互逻辑、数据模型、API 调用、网络请求、错误/空态/加载态和控制流
     - 明确哪些能力可以在 optimized React 中对齐实现，哪些只能作为语义参考
9. 在重构 class 之前，根据代码、截图和审计视图编写意图伪代码
   - 目的：
     - 产出语义布局方案，用于指导第 2.5 至 6 轮
9.5. 在重构 JSX 之前抽象展示数据
   - 目的：
     - 从 Figma 静态展示内容中恢复数据模型，识别重复卡片、列表、tab、指标、标签、徽章、按钮文案、空态和加载态线索
     - 定义 mock API/local service/adapter 数据加载边界，使输出能够从本地 mock 数据平滑映射到线上接口
     - 对多屏 flow，明确哪些数据属于单个 screen，哪些是跨 screen 共享状态或由上一个 screen 传入
     - 覆盖搜索词、输入文本、筛选条件、选中项、表单值、列表查询结果和详情页 id 等交互数据
9.6. 在重构 JSX 之前恢复 flow 交互触发
   - 目的：
     - 对单屏输入，保留 screen 内原有交互，不强行创造跨屏跳转
     - 对多屏 flow 使用 VLM/视觉理解能力检查每个 `Preview-screen-**.png`，结合 JSX 结构识别按钮、箭头、tab、卡片、列表项、图标按钮、input text、search bar、input bar、筛选控件、表单控件和底部导航等可交互触发点
     - 将可交互触发点映射到 React 状态切换、screen route 切换、回退事件、输入更新、搜索提交、筛选更新或 mock API 查询，确保 UI 预览之间是 React 交互跳转和数据更新，而不是截图或静态图片滚动
10. 在预准备的 React 壳内执行移动端重构
    - 目的：
      - 将第 3-6 轮做出的决策应用到实际验证目标中，而非隔离副本
      - 将重构后的组件写入 `react/src/RefactoredComponent.jsx`，不覆盖 `react/src/ValidatedComponent.jsx`
      - 添加或更新 `/refactored` 路由，使重构组件可直接验证
      - 保留输入中的 flow 跳转关系；如果输入是多屏 flow，输出也必须是可交互 flow
      - 保留或补强按钮、箭头、tab、卡片、列表项、图标按钮和底部导航项的 `onClick` 跳转事件
      - 将 input text、search bar、input bar、textarea、select、filter chip、segmented control 等表单/查询控件实现为受控 React 状态，并接入 mock API 查询、筛选或提交行为
      - 禁止把多屏 flow 改成截图、静态图、背景图或滚动图片预览
      - 将展示数据迁移到本地 mock API service、adapter 函数或等价数据源文件中，组件通过数据渲染而非硬编码重复 JSX
11. 在认为重构稳定之前，在 React 壳内验证移动端适配
    - 目的：
      - 在进行截图级别的清理之前，确认页面结构在不同 Figma 渲染环境和真实移动视口中都是响应式的
12. 为实现像素一致性，在任何 Compose 翻译之前自行负责 compare -> fix -> compare 循环，并保持截图尺寸与对应参考截图匹配
    - 目的：
      - 在结构稳定后，使用截图 diff 作为最终的几何反馈循环
      - 单屏输入默认对比 `Preview.png`
      - 多屏 flow 必须逐个可达 screen 对比对应 `Preview-screen-**.png`，不要只验证初始 screen
13. 当当前参考截图中出现 `device-chrome` 时，在截图匹配期间保留它
14. 保持最外层页面壳全屏且自适应；不要在根页面容器上放置 `max-width`、`max-height`、`maxWidth`、`maxHeight`、`max-w-*` 或 `max-h-*` 约束
15. 仅在 `react/src/RefactoredComponent.jsx` 和 `/refactored` 路由稳定、React 构建健康、数据加载边界清晰、且你已将单屏或多屏的对应像素循环推进到无法突破的实际障碍时才退出

## 停止条件

- 如果 `react/src/ValidatedComponent.jsx` 缺失，停止并报告缺少 React 工作文件
- 如果判定为单屏，但 `Preview.png` 缺失，停止并报告缺少单屏参考截图
- 如果判定为多屏 flow，但任一可达 screen 没有对应 `Preview-screen-**.png`，停止并报告缺少多屏截图证据
- 如果判定为多屏 flow，但流程仍要求或读取 `Preview.png`，停止并修正截图约定；多屏不应出现 `Preview.png`
- 如果判定为多屏 flow，但无法从 `ValidatedComponent.jsx` 确认初始 screen、可达 screen 或基本跳转关系，停止并先修复 flow 输入，不要退化为单屏重构
- 不要仅凭内存中的 JSX 继续；使用 React 壳中预准备的文件
- 如果本地 Figma resource 缺失或资源 manifest 与 JSX 引用无法对应，先尝试从 Figma 资源库下载缺失项并更新引用/manifest；只有在无法定位或下载真实资源时才停止并报告缺失项
- 如果 `parsed_resources/resources.json` 缺失，优先使用导出产物中的本地 manifest 或从本地 JSX/资源目录创建索引；如果需要补齐缺失资源，可以使用已有资源解析/下载脚本或等价工具。解析或下载失败则停止
- 不要通过将原始字节流式输出到 stdout 来检查截图二进制文件；如果需要截图尺寸或文件元数据，使用图像安全工具而非文本读取器
- 如果运行时暴露了 `run_layout_audit`，使用该工具而非手动重建布局审计命令；如果审计失败，停止并修复，不要仅凭代码猜测有风险的布局意图
- 如果 React 壳尚未稳定，不要当作阶段已完成而继续
- 如果多屏 flow 的重构版本无法通过设计内事件到达每个目标 screen，不要当作阶段已完成
- 如果 input/search/input bar 等明显交互控件只是静态 div 或图片，没有 React 状态、输入事件或提交/筛选行为，不要当作阶段已完成
- 如果多屏展示数据仍散落在重复 JSX 中，或没有 mock API/local service/adapter 边界，不要当作阶段已完成
- 如果提供了第三方参考代码库但没有完成参考库架构理解、Figma 对应业务定位和可映射能力清单，不要开始 JSX 重构
- 如果参考库中能定位 Figma 对应业务实现，但 optimized React 的 UI/交互/数据/控制逻辑未对齐该业务语义，不要当作阶段已完成

截图命名必须先按输入模式分流：

- 单屏 Figma React：只使用 `Preview.png` 作为参考截图。
- 多屏 Figma React flow：只使用 `Preview-screen-**.png` 作为参考截图，例如 `Preview-screen-01.png`、`Preview-screen-02.png`；不要创建、复制、读取或要求 `Preview.png`。
- 如果多屏中的某个 screen 有状态变体，在 screen 名称后追加状态，例如 `Preview-screen-01-loading.png`，不要回退到 `Preview.png`。

## 轮次

这些轮次展开工作流步骤 5-15。在上述准备和初始读取完成后按顺序执行。

- 第 1-2 轮展开工作流步骤 5-7
- 第 2.2 轮展开工作流步骤 8.7
- 第 2.5-2.75 轮展开工作流步骤 9
- 第 2.8 轮展开工作流步骤 9.5
- 第 2.9 轮展开工作流步骤 9.6
- 第 3-6 轮展开工作流步骤 10
- 第 7 轮展开工作流步骤 11，并覆盖动态适配检查
- 第 7.5 轮展开工作流步骤 12-13

### 第 1 轮：审计风险样式

目标：找出在不同手机尺寸下会破坏或偏移的样式。

捕获：

- 所有 `absolute` 节点
- 固定 `w/h` 节点
- 锚点 class 如 `left/top/right/bottom`
- 重复块
- 可能的 device chrome，如状态栏或 home indicator
- 输入模式证据：
  - 单屏：唯一 screen 根节点、主要状态和单一截图
  - 多屏：screen registry、Raw screen 组件、状态变量、跳转函数、路由入口、截图映射
- 来自当前模式参考截图的观察：
  - 可见的视觉条带
  - 明显的分组元素
  - 区域重叠深度
  - 看似贴边与自由浮动的节点
- 如果是多屏 flow，分别记录每个 `Preview-screen-**.png` 的 screen 名称、主要视觉区域和疑似触发点

暂不编辑。此轮仅构建问题清单。

### 第 2 轮：分类布局含义

目标：决定哪些 absolute 节点在语义上是合理的，哪些是设计工具残留。

将每个 absolute 节点分类为以下之一：

- `background`
- `support-layer`
- `overlay`
- `floating-content`
- `flow-content`
- `device-chrome`

使用 [references/heuristics.md](references/heuristics.md) 中的规则。这是工作流中价值最高的决策步骤。

重要：分类 `device-chrome`，但当用户要求与当前参考截图的像素级一致性时，不要删除它。在截图匹配足够好之前，将其保留在验证壳中。

如果参考截图可用，使用它来打破僵局：

- 代码回答父子结构
- 截图回答视觉意图

如果截图显示节点位于中间视觉条带，不要仅凭代码将其分类为底部锚定或顶部锚定。

### 第 2.2 轮：第三方参考代码库业务抽取

仅当调用方提供第三方参考代码库路径时运行。

目标：当 Figma 设计稿在第三方参考代码库中已有实现时，先理解参考库整体架构，再抽取当前 Figma 业务场景的 UI、逻辑、数据控制、API 和网络实现细节，作为 optimized React 的业务对齐依据。

在编辑 JSX 之前完成以下工作：

1. 理解参考代码库整体架构：
   - 技术栈、入口、路由/导航、页面/screen/module 组织
   - UI 层、组件库、设计系统、资源和样式组织
   - 状态管理、业务逻辑、表单/搜索/筛选/分页等控制逻辑
   - 数据模型、service/repository/API client、网络请求、参数和响应模型
   - loading、empty、error、权限、会话或缓存等运行时状态
2. 定位 Figma 对应业务场景：
   - 与截图视觉结构匹配的页面、组件或 flow
   - 与 React mock data 字段匹配的数据模型、API、列表、详情和状态
   - 与设计内可交互组件匹配的点击、输入、搜索、筛选、提交和导航逻辑
3. 输出可对齐清单：
   - 可在 optimized React 中实现对齐的 UI 结构和组件语义
   - 可在 optimized React 中实现对齐的交互逻辑、状态机和控制流
   - 可映射为 mock API/local service 的数据结构、API 参数、响应模型和状态
   - 只能作为语义参考、不能直接迁移到 React 的实现细节
4. 明确优先级：
   - Figma 截图和已验证 React 仍决定视觉还原度
   - 第三方参考库决定业务语义、交互行为、数据控制和 API/network 形态
   - 如果二者冲突，保留 Figma 视觉，同时在 optimized React 的状态、事件和 mock API 中对齐参考库业务语义

不要照搬整个参考仓库或把参考库依赖引入 React 验证壳。只抽取当前 Figma 业务所需的 UI/逻辑/数据/API/network 语义，并用 React state、事件处理和 mock API adapter 表达。

### 第 2.5 轮：编写意图伪代码

目标：在重构 class 之前，将截图和导出代码翻译为布局意图。

编写 5 到 15 行伪代码，描述：

- 顶层壳，如 `hero`、`content shell`、`list shell`
- 背景和支撑层，如背景图、渐变或实色支撑条带
- 浮动内容组，如头像、标题、工具栏和徽章
- 重叠归属：
  - 哪个壳重叠哪个前一个壳
  - 哪些节点属于同一个白色内容壳
- 流式归属：
  - 哪些组在重叠之后应继续正常流式排列

在编辑之前用伪代码回答这些问题：

- 这个白色区域是一个内容壳还是多个不相关的区域？
- 这个深色条带只是颜色填充，还是下一个壳重叠的支撑层？
- 标签页和网格是否与统计和操作属于同一个壳？
- 下一个块是相对于页面定位，还是相对于前一个壳边界定位？

暂不编辑。此轮的目的是在 CSS 修改之前恢复业务和布局语义。

### 第 2.75 轮：冻结关键几何

目标：在重构将其从视野中移除之前，保留原始构图数值。

在触碰 class 之前记录关键的导出几何：

- 根宽度和高度
- hero 高度
- 面板重叠深度
- 工具栏顶部偏移
- 头像尺寸和偏移
- 标题或元信息块偏移
- 标签页高度和下划线粗细
- 重复卡片宽高比和卡片间距

如果用户要求像素级一致性，此轮是必须的。在记录这些数值之前，不要用通用间距猜测替换测量值。

### 第 2.8 轮：恢复数据模型和 API 边界

目标：把 Figma 导出的静态展示内容恢复为可替换的数据结构，为后续映射线上接口做准备。

在编辑 JSX 之前记录：

- 重复列表、网格、卡片、tab、菜单、指标和徽章的字段集合
- 单个 screen 或多个 screen 共享的数据结构
- 文案、图片、图标、状态、数量、价格、时间、标签等字段的命名
- 交互 flow 中 screen 之间传递的最小状态，例如当前 tab、选中项、输入文本、搜索词、筛选条件或详情页 id
- 多屏 flow 中每个 screen 的输入数据、输出事件和共享状态，例如 query、inputValue、selected filter、selected item、form draft、search results、back target
- 如果存在第三方参考代码库，将参考库中的 API 参数、响应字段、domain model、状态字段和错误/空态/加载态映射到 React mock API 数据结构
- 可能来自接口的 loading、empty、error 状态；如果截图没有体现，不要强行展示，但要在数据边界中留出可扩展位置

实现要求：

- 将重复 JSX 改为由数组、对象和 `map` 渲染。
- 将静态展示数据放入本地 mock API service、mock API adapter 或等价模块，例如 `react/src/services/mockApi.js`、`react/src/services/mockData.js`、`react/src/data/screens.js` 或与项目风格一致的文件。
- 组件通过函数如 `loadHomeScreenData()`、`getScreenData(screenId)` 或等价接口读取数据，不直接散落硬编码业务数据。
- 数据接口返回结构应接近线上 API 可替换形态：包含稳定字段名、列表数组、资源引用和状态字段。
- 多屏 flow 的 service 应能按 screen 或 flow 聚合返回数据，例如 `loadFlowData()`、`getScreenData(screenId)`、`getTransitionMap()`、`searchItems(query)`、`filterItems(filters)` 或等价接口，避免让跳转逻辑和展示数据从硬编码 JSX 反推。
- 搜索、输入、筛选和表单提交可以调用同步 mock API 函数或 Promise-like mock adapter；不要引入真实网络请求。
- 如果第三方参考库提供了对应 API/network 语义，mock API 函数命名、参数、响应结构和状态字段应尽量对齐参考实现，例如查询参数、分页字段、筛选条件、详情 id、错误码或加载态。
- 不要为了接口化引入真实网络请求、后端依赖或复杂状态库；此阶段只建立可替换边界。
- 不要把纯布局常量误抽象为业务 API 数据。间距、颜色和响应式断点仍属于布局实现。

### 第 2.9 轮：恢复 flow 交互触发

目标：确保多屏 UI 预览之间是 React 交互代码跳转，而不是截图、静态图或滚动图片预览。

如果输入是多屏 flow，在编辑 JSX 之前完成以下判断：

- 使用 VLM/视觉理解能力检查每个 `Preview-screen-**.png`，识别视觉上可点击或表达导航意图的组件。
- 将视觉判断与生成 JSX 的 DOM 结构对应起来，找到可绑定事件的真实 React 节点或包装节点。
- 优先关注：
  - 主要按钮、底部 CTA、文字按钮
  - 返回箭头、下一步箭头、关闭按钮
  - tab、segmented control、底部导航项
  - input text、search bar、input bar、textarea、select、filter chip、表单控件
  - 卡片、列表项、图片宫格、详情入口
  - 表达继续、完成、进入详情、返回、取消、切换状态、搜索、提交、发送、筛选的图标或文案
- 为高置信度触发点建立交互表，例如 `triggerId -> targetScreenId`、`triggerId -> goBack`、`triggerId -> updateState`、`inputId -> updateQuery`、`searchBar -> searchItems(query)` 或 `formSubmit -> submitMockData(formState)`。
- 如果目标 screen 不确定，使用输入顺序作为低置信度 fallback，并在代码注释或执行报告中标注原因。

如果输入是单屏 Figma React：

- 不要求建立跨 screen 跳转表。
- 仍需检查单屏内可点击和可输入元素，保留或恢复 tab、展开折叠、选中态、输入提交、搜索、筛选等局部交互。
- 如果用户只给了一张 Figma，但 JSX 中已有弹层、抽屉或状态切换，按单屏多状态处理；参考截图仍以唯一的 `Preview.png` 为基准。

实现要求：

- 在 React 中使用真实事件处理，如 `onClick`, `onChange`, `onInput`, `onSubmit`, `onKeyDown`, `role="button"` 和必要的可访问键盘触发。
- input text、search bar 和 input bar 必须使用受控值、placeholder、提交/清空/搜索行为，并根据交互意图更新 mock API 查询结果或本地 UI 状态。
- 通过 React 状态、screen registry、route 参数或等价机制切换当前 screen。
- 对多屏 flow，保持输入顺序和明确交互关系一致；如果重构拆分组件，不要丢失原有 `screenId`、回退目标或跨 screen 状态。
- 对多屏 flow，页面跳转和展示数据必须联动：列表项点击应携带 selected id，搜索/筛选应影响结果或状态，详情页应读取对应 mock 数据。
- 如果第三方参考库提供了对应交互或控制逻辑，optimized React 应对齐其行为语义，例如 tab 切换规则、搜索提交时机、筛选组合方式、列表项进入详情、表单校验、返回路径、loading/empty/error 展示和重试逻辑。
- 不要把 `Preview-screen-**.png` 作为 `<img>`、背景图或 scroll view 的主要 UI 实现。
- 截图只允许作为验证参考，不允许成为 flow 的可见 UI 主体。
- 不要只添加外部上一页/下一页调试按钮就结束；必须检查设计稿自身的按钮、箭头、tab、卡片、列表项和底部导航。
- 如果某些触发点低置信度，保留最小可用默认跳转控件，但不能删除高置信度的设计内触发事件。

### 第 3 轮：将页面坐标转换为父级约束

目标：停止使用全画布坐标推理。

仅对分类为以下类型的节点操作：

- `floating-content`
- `flow-content`

对每个节点：

- 计算其相对于直接父级的位置，而非页面
- 在编辑之前记录关键比率：
  - `top / parentHeight`
  - `bottom / parentHeight`
  - `left / parentWidth`
  - `right / parentWidth`
  - 与下一个区域的重叠深度
- 在更改任何锚点之前，决定节点实际锚定到哪条边
- 仅当节点是普通内容且语义锚点不变时，才将 `right/bottom` 转换为 `left/top`
- 尽可能用边约束替换固定宽度约束
- 优先使用 `left + right` 或水平 padding 而非 `left + width`

暂不重构整个区域。此轮唯一的问题是："此节点能否相对于其父级表达？"

重要：

- 除非原始节点实际上是底部锚定的，否则不要用 `mt-auto`、`justify-end` 或通用底部锚定替换测量的顶部偏移
- 如果 hero 内容块原本位于中下部条带，首先使用父级相对的顶部比率保留该条带
- 不要将每个节点都标准化为 `left/top`；首先回答该节点在语义上锚定到哪个父级和哪条边

### 第 4 轮：恢复区域壳

目标：将页面恢复为一系列区域的堆叠，而非单一固定画布。

仅恢复外壳：

- 根页面容器
- hero 壳
- 面板壳
- 列表壳

如果意图伪代码表明统计、简介、操作、标签页和网格属于一个白色内容壳，首先恢复该壳，并保持这些组在一起，直到壳关系稳定。

使用正常流加上受控重叠。暂不优化内部内容。

### 第 5 轮：逐区域重构

目标：在不破坏页面其余部分的情况下，移除一个区域内的非语义布局。

典型顺序：

1. hero
2. 信息面板
3. 标签页
4. 卡片或网格

在选定区域内：

- 普通内容使用 `flex`、`grid` 或流式布局
- 重复标记使用数组和 map
- 仅当 overlay 仍需堆叠含义时才保持分层

除非用户明确要求更大批次，否则不要在一轮中混合多个区域。

### 第 6 轮：释放刚性尺寸

目标：在保留位置语义的同时，移除宽度和高度刚性。

聚焦于：

- 固定根宽度
- 固定文本块宽度
- 应变为 `aspect-*` 的固定卡片尺寸
- 应变为相对重叠的固定重叠

对于移动端适配，当有意义的偏移表达真实的 UI 意图时保留它们。当刚性尺寸表达的是设计画布假设时移除它们。

重要：

- 不要通过将整个页面包裹在居中的 `max-width` 或 `max-height` 壳中来解决响应式问题
- 最外层页面容器必须保持全屏并填满真实移动视口
- 如果某个区域需要内部边界，在页面结构内表达，而非作为根级页面夹具

此轮内的顺序：

1. 释放固定宽度
2. 释放固定高度或转换为宽高比
3. 仅在验证区域仍位于相同相对视觉条带后才释放重叠

永远不要用看起来更整洁的流式代码换取正确的相对位置。如果结构变得更简单但 hero 构图偏移了，此轮失败。

### 第 7 轮：验证移动端适配

目标：确保布局在不同手机和不同 Figma 渲染环境下稳定，再考虑桌面或平板优化。

检查：

- 窄手机宽度
- 常见手机宽度
- 较大手机宽度
- Figma 导出根节点宽高与真实浏览器 viewport 不一致的情况
- 设计稿截图中包含或不包含模拟状态栏、home indicator、设备边框时的布局稳定性
- flow 中每个 screen 的切换后布局稳定性
- 多屏 flow 中连续交互路径，例如 screen-01 -> screen-02 -> screen-03 -> apply/back -> screen-02
- 状态栏或安全区域冲突
- 文本截断和溢出
- API-like 数据源替换一两条文本或列表长度变化后，布局仍能合理适配

此轮关注移动端稳定性，而非最大化桌面宽度。

动态适配要求：

- 不要用根级固定宽高、根级居中 `max-width` 或缩放容器模拟 Figma 画布。
- 根页面填满真实 viewport，内部 screen 根据父级宽度、safe area 和内容流适配。
- 需要保持 Figma 视觉比例时，优先在具体区域使用相对尺寸、`aspect-ratio`、受控重叠和父级 padding，而不是锁死整页。
- 对多屏 flow，逐个验证 screen；不要只验证初始屏。
- 对单屏输入，只需验证该 screen 及其已有状态变体；不要为了满足 flow 检查而引入无来源的新 screen。

### 第 7.5 轮：验证像素一致性

目标：通过可复现的截图循环，缩小重构与参考截图之间的差距。

如果用户要求像素级匹配，或重试摘要提到截图偏移：

1. 如需要则构建 React 壳，通过内置的 `scripts/capture_preview.py` 辅助脚本截图
2. 让该辅助脚本启动临时预览服务器，并将视口匹配到当前参考截图；单屏使用 `Preview.png`，多屏按 screen 使用对应 `Preview-screen-**.png`
3. 等待资源加载
4. 截取新截图
5. 运行 `scripts/pixel_diff.py <reference-preview> current-preview.png`
6. 先检查 diff 图像，再使用不匹配比率作为辅助量化提示
7. 在编辑之前命名主要不匹配集群：
   - 如果 `mismatch_ratio > 0.2`，优先检查整体布局偏移（例如内容被状态栏 padding 推得太靠下或靠上，缺少边距）或 overlay 定位错误（例如绝对定位元素、固定头部或模态框偏移），再进行微调
   - 哪个视觉区域有误
   - 最可能的布局原因
   - 下一步要修复的几何集群
8. 每次修正一个几何集群
9. 如果当前参考截图中出现 `device-chrome`，在此循环中保留它
10. 当 `mismatch_ratio < 0.1` 时停止循环，前提是剩余 diff 不隐藏明显的结构性布局错误
11. 否则将此循环上限设为 5 轮聚焦 diff 修复；仅在连续两轮未产生有意义的视觉改善时提前停止
12. 当剩余 diff 已仅限于微调细节（如 font-weight 微调、微小 letter-spacing 变化或个位数间距调整）时，不要在这些轮次上花费时间
13. **强制执行：** 你绝对不能仅因为代码结构看起来更整洁就提前退出此循环。你必须严格重复 compare -> fix -> compare 循环，直到 `mismatch_ratio < 0.1` 或你已完成恰好 `5` 轮修复。如果比率仍高于 0.1，不要主观判断布局是否"足够好"。
13.1. **禁止回退：** 绝对不要为了通过像素 diff 测试而将代码回退到固定 width/height（如 `w-[129px]`）和绝对定位。你必须保持响应式 flex/grid 布局（`flex-1`、`aspect-square`、`w-full`）。如果布局在结构上是健全且响应式的，但在 5 轮后仍因渲染差异未达到 0.1 阈值，接受该 diff 并停止。永远不要用结构语义和响应性换取更低的不匹配比率。
14. **显式状态日志：** 每次运行 `pixel_diff.py` 后，你必须在做出下一个决策之前以以下精确格式将当前状态打印到 stdout：
    - 当前轮次：[1 到 5]
    - 不匹配比率：[值]
    - 动作：[将继续下一轮 | 因比率 < 0.1 停止 | 因达到最大 5 轮停止 | 因连续 2 轮无改善停止]
15. 如果剩余不匹配主要是排版细节或微小间距微调而非结构性布局错误，停止循环并明确报告这些残留差异

多屏 flow 的截图循环：

- 为每个可达 screen 建立 `screenId -> route/state setup -> reference screenshot -> current screenshot -> diff output` 映射。
- 先验证初始 screen，再沿高置信度交互路径逐个切换并截图。
- 每个 screen 独立记录 mismatch ratio、主要 diff 集群和停止原因。
- 每个 screen 的 reference screenshot 必须是 `Preview-screen-**.png`。
- 不允许用 `Preview.png` 作为多屏 flow 的初始 screen 或任一 screen 的复用截图；如果缺少 `Preview-screen-**.png`，不要声称该 screen 已完成像素验证。

单屏首选截图命令：

```bash
python3 scripts/capture_preview.py \
  --react-root react \
  --reference Preview.png \
  --output current-preview.png
```

此辅助脚本是截图捕获的默认路径。它启动临时本地预览服务器，绑定唯一端口，从 `config.json` 读取 `waitMs`，并以匹配当前参考截图的视口进行截图。多屏 flow 时，将 `--reference` 替换为当前 screen 对应的 `Preview-screen-**.png`，并为输出和 diff 文件使用 screen 专属文件名。

典型 diff 命令：

```bash
python3 scripts/pixel_diff.py <reference-preview> current-preview.png --channel-threshold 96 --diff-out pixel-diff.png
```

## 规则

- 此 skill 使用预准备的本地 React 产物。
- 此 skill 优先使用预准备的本地 Figma resource；如果本轮 React 优化检测到 layer/icon/image/section/json/component 等资源缺失，允许从 Figma 资源库补齐真实缺失资源以保障还原度。
- 输入可能是单屏组件，也可能是多屏 flow；如果输入是 flow，输出必须保留 flow 跳转能力。
- 在任何审计或重构前先判定输入模式。单屏不要强行扩展成多屏；多屏不要压缩成单屏。
- 截图约定必须互斥：单屏只使用 `Preview.png`；多屏只使用 `Preview-screen-**.png`。多屏时不要创建、复制、读取或依赖 `Preview.png`。
- 强制工作流步骤必须按顺序执行。不要因为后续工作看似明显就跳过它们。
- 仅在资源清单缺失时从本地 JSX、导出资源目录或等价本地 manifest 创建索引清单；如果索引发现资源缺失，应补齐缺失资源并更新清单。
- 当需要资源清单时，优先使用等价本地 manifest；如果 manifest 缺失或显示资源缺失，可以使用 `scripts/parse_resources.py` 或等价工具从 Figma 资源库补齐真实资源。此 skill 在资源保留和回退决策之前需要本地已解析资源清单。
- 将所有重构编辑保留在预准备的 React 壳副本内。
- 不要覆盖 `react/src/ValidatedComponent.jsx`；使用 `react/src/RefactoredComponent.jsx` 作为重写组件。
- 在任何 Compose 翻译之前先验证 React 壳。
- 多屏 flow 必须由 React 组件、状态和事件处理实现跳转；不要用截图、静态图、背景图或滚动图片预览表达多屏 UI。
- 多屏 flow 的逐屏重构可以复用单屏方法，但最终验收必须同时覆盖每个 screen 的视觉质量和 screen 间事件行为。
- 必须使用 VLM/视觉理解能力结合 JSX 结构判断设计内可交互触发点，并为高置信度触发点接入 `onClick`、`onChange`、`onSubmit`、`onKeyDown` 或等价事件。
- 重点检查按钮、箭头、tab、卡片、列表项、图标按钮、input text、search bar、input bar、筛选控件、表单控件和底部导航项；这些组件通常比额外添加的调试按钮更接近真实产品交互。
- 在重构前先恢复数据模型和接口边界；不要把 Figma 展示数据继续散落在重复 JSX 中。
- 对重复内容使用数组和 `map`，对 screen 数据、搜索结果、筛选结果、详情数据和表单状态使用本地 mock API service、mock API adapter 或等价模块。
- 数据接口应是后续线上 API 可替换的形态，但本阶段不要引入真实网络请求或后端依赖。
- 如果存在第三方参考代码库，必须先理解参考库整体架构并定位 Figma 对应业务实现，再将可映射的 UI、交互、数据控制、API/network 语义对齐到 optimized React。
- 第三方参考库用于业务语义对齐，不用于替代 Figma 视觉还原。Figma 截图和已验证 React 决定视觉，参考库决定业务行为、数据控制和 API/network 形态。
- 基于第三方参考库实现优化 React 时，应保持 UI、交互、数据以及控制逻辑一致：组件语义、状态流转、输入/搜索/筛选/提交行为、列表/详情数据流、loading/empty/error 和导航路径都应有对应表达。
- 不要照搬参考仓库依赖或整体架构到 React 验证壳；只把当前 Figma 业务所需的能力表达为 React state、组件拆分、事件处理和 mock API adapter。
- 区分业务展示数据与布局参数。业务文案、列表项、标签、图片和状态可以接口化；像素间距、锚点、颜色和响应式断点仍由布局负责。
- 当用户后续要映射线上接口时，保留清晰的字段命名和 adapter 函数，避免让 Compose 阶段从硬编码 JSX 中反推数据。
- 仅当 `absolute` 明确表达 overlay 或边缘锚定时才保留它。
- 尽早分类 `device-chrome`，但当它出现在参考截图中时，保留到像素验证之后。
- 在重构 class 之前编写意图伪代码。不要直接从审计输出跳到 JSX 编辑。
- 在优化间距之前恢复壳归属。如果多个视觉组共享一个背景、一个重叠边界和一个圆角容器，在证明它们应分离之前将它们视为一个内容壳。
- 不要批量将 `right/bottom` 锚点转换为 `left/top`；除非更改明显安全，否则保留原始语义锚点。
- 当有意义的位置语义在移动端很重要时，保留它们。
- 区分支撑层和可丢弃背景。一个在视觉上支撑下一个壳的实色条带或深色底层是布局线索，而不仅仅是装饰。
- 在移除所有偏移之前先移除刚性宽度和高度。
- 在简化结构之前冻结父级相对位置语义。
- 对于面向截图的工作，在第一次 JSX 编辑之前冻结原始几何。
- 优先使用 `w-full`、`flex-1`、`min-w-0` 和 `aspect-ratio` 而非固定宽度。
- 首先保留视觉顺序；在结构正确后再优化比率和间距。
- 当下一个区域在视觉上覆盖前一个区域时，优先使用壳之间的受控重叠而非页面级绝对定位。
- 对于 hero 或媒体构图，在编辑前后验证三个数值：
  - 顶部内容条带
  - 面板重叠深度
  - 工具栏距顶部安全区域的距离
- 如果预览资源加载失败，在判断布局之前用本地回退颜色稳定预览。
- 使用 `config.json` 作为像素验证默认值的真实来源。
- 优先保留原始 JSX 资源引用、SVG、图片 URL、layer/icon/image/section/json/component 引用和内部图标资源；缺失时从 Figma 资源库补齐真实资源，而非替换为新建的占位符。
- 不要仅为了让壳能构建就用通用公共图标包、emoji 或手绘替代品替换源图标或图片资源。
- 如果私有依赖缺失，修复依赖或创建保留原始资源或 SVG 语义的最小本地 shim，而非重新设计图标。
- 不要使用根级 `max-width`、`max-height`、`maxWidth`、`maxHeight`、`max-w-*` 或 `max-h-*` 来整理页面。顶层页面壳必须保持全屏且移动端自适应。
- 不要用根级固定 Figma 画布、缩放容器或居中模拟框解决不同渲染环境差异。真实页面根容器必须适配当前 viewport。
- 如果 Figma 截图和浏览器 viewport 的 chrome、safe area 或根尺寸不同，优先调整区域归属、父级约束和 safe-area padding，而不是锁死整页尺寸。
- 多屏 flow 中每个 screen 都必须经过移动端适配检查；不要只让首屏通过验证。
- 多屏 flow 中每个可达 screen 都必须有对应 `Preview-screen-**.png` 截图验证；缺少截图是阻塞项，不要用 `Preview.png` 作为复用截图。
- 优先在预准备的壳内验证组件，而非维护单独的预览产物。
- 当像素一致性重要时，优先使用 Playwright 截图而非临时浏览器截图。
- 使用截图 diff 输出来指导几何修复，而非仅凭主观视觉判断。
- 使用 `mismatch_ratio < 0.1` 作为像素循环的数值早停条件，但如果 diff 仍显示有意义的结构性布局错误，不要将其视为自动成功。
- 在像素循环中，分析 diff 集群的位置及其含义，再决定工作是否完成。
- 如果不匹配比率很低但仍存在明显的布局或构图错误，继续修复布局。
- 如果剩余 diff 仅是微小的 font-weight、letter-spacing 或微小间距微调，不要为了追求更整洁的不匹配指标而继续迭代。
- 在截图一致性足够好之前，不要移除可见的状态栏或 home indicator，否则 diff 基线会偏移。
- 不要在内层像素循环中硬编码预览端口如 `4173`。当验证壳启动时，读取该次运行的实际 localhost 端口，并在该循环中一致使用。

## 脚本

### `scripts/layout_audit.py`

用于快速静态检查。它输出一份简洁报告，涵盖可能的 absolute 类别、锚点使用、固定尺寸和重复布局风险。

### `scripts/pixel_diff.py`

用于组件在验证壳中挂载后的截图级验证。单屏将捕获的预览与 `Preview.png` 比较；多屏 flow 应按 screen 将捕获预览与对应 `Preview-screen-**.png` 比较。脚本会打印不匹配比率，并写入高亮 diff 图像。将不匹配比率视为辅助指标而非决策本身；diff 图像和不匹配集群应驱动下一次几何修复。

### `scripts/parse_resources.py`

在确认 `react/src/ValidatedComponent.jsx` 存在后使用。它应从工作 JSX 和本地资源目录中解析资源引用，必要时从 Figma 资源库补齐缺失资源，并写入一个清单。后续资源清单步骤在做出资源保留或回退决策之前必须读取该清单。

重要：Figma resource 优先由上游 Figma -> React 阶段预准备。本 skill 中的资源解析先复用本地资源；如果发现 layer/icon/image/section/json/component 等资源缺失，可以从 Figma 资源库下载真实缺失项以保障还原度。下载失败或无法定位真实资源时，停止并报告缺失项；不要替换成占位符或重新设计资源。

默认约定：

- 源 JSX：`react/src/ValidatedComponent.jsx`
- 输出根目录：`parsed_resources/`
- 清单：`parsed_resources/resources.json`

首选命令：

```bash
python3 scripts/parse_resources.py \
  --source react/src/ValidatedComponent.jsx \
  --output-root parsed_resources \
  --manifest parsed_resources/resources.json
```

在准备完成后立即读取 `parsed_resources/resources.json`，并将其作为此 skill 其余部分的默认资源清单输入，除非调用方显式覆盖路径。

## 参考

- [config.json](config.json)
- [references/heuristics.md](references/heuristics.md)
- [references/pixel-validation.md](references/pixel-validation.md)

## 退出条件
- `react/src/RefactoredComponent.jsx` 存在
- `/refactored` 渲染 `react/src/RefactoredComponent.jsx`
- React 壳仍反映已验证的移动端层级，而非全新设计
- 已记录输入模式：单屏 Figma React 或多屏 Figma React flow
- 如果输入是多屏 flow，`RefactoredComponent.jsx` 仍保留可操作的 screen 跳转关系
- 多屏跳转由 React 状态和事件触发实现，不是截图、静态图或滚动图片预览
- 如果输入是多屏 flow，每个可达 screen 均已通过移动端适配检查，并且有对应 `Preview-screen-**.png` 截图验证；没有使用 `Preview.png` 作为多屏参考
- 如果输入是单屏 Figma React，未强行新增无来源 screen，且已有单屏状态交互仍可操作
- 高置信度的按钮、箭头、tab、卡片、列表项和底部导航触发点已经接入跳转事件，低置信度触发点已说明 fallback
- input text、search bar、input bar、筛选控件和表单控件已经实现为真实 React 受控交互，并能更新 UI 状态或 mock API 查询结果
- Figma 静态展示数据已抽象为本地 mock API service、mock adapter 或等价数据源，重复 UI 通过数据渲染
- 多屏 flow 的页面跳转、selected item、query/filter/form state 和展示数据之间有明确的数据流
- 数据加载边界具备后续映射线上接口的稳定字段名和 adapter 位置
- 如果存在第三方参考代码库，已记录参考库整体架构、Figma 对应业务场景、UI/逻辑/数据控制/API/network 可映射清单，并已在 optimized React 中对齐可实现部分
- 基于第三方参考库的 UI、交互、数据和控制逻辑一致性已体现在 React 组件、状态、事件和 mock API adapter 中；不可直接对齐的部分已说明
- 原始 JSX 和本地 Figma resource 使用已保留；若检测到资源缺失，已从 Figma 资源库补齐真实资源或报告无法补齐的缺失项；没有占位替换或重新设计 layer/icon/image/section/json/component
- 顶层页面壳仍保持全屏无边距，没有根级 max width 或 max height 夹具
- 页面在窄手机、常见手机和较大手机 viewport 下没有明显结构性偏移
- React 构建通过
- 如果要求了面向像素的工作，剩余 diff 区域是小的且已理解的，而非仅仅低于阈值
- 如果要求了面向像素的工作，你必须仅在 `mismatch_ratio < 0.1` 或修复轮次超过 5 时停止。报告任何残留的结构或排版差异。
- **隔离要求：** 不要急于开始下一个 skill 或阶段。你必须完全穷尽像素一致性循环，并确保所有当前 React 验证规则满足后，才能认为此 skill 成功完成。
- stdout 简要列出已更改的文件、构建状态和任何仍存在的实际障碍
