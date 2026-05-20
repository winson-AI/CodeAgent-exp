---
name: flow_figma_compose_wf
description: "当用户要把一个或多个 Figma section/node 设计稿转换为 Android Jetpack Compose，或要把 Figma 对应业务模块接入存量 KMP/CMP Compose 仓库时使用。按 Figma -> React 中间表示 -> 优化后的 API-ready React flow -> Compose 的顺序执行；React 阶段遵循 Figma 设计稿、交互和 mock API 数据边界，Compose 阶段先判断目标是默认壳工程还是存量 KMP/CMP 仓库，再启动 sub-agent review task、理解仓库并尽量复用现有导航、主题、组件、状态和数据层。"
---

# 从 Figma 启动 React 到 Compose 工作流

## Overview

工作目标分成四个阶段：

1. 输入与能力判断：确认 Figma section/node 链接、access token、可用 MCP 或环境内 Figma-to-React 工具
2. Figma -> React 中间表示：逐张设计稿生成 React 和截图，再按交互顺序拼接为 flow 跳转版本
3. React -> optimized React：启动新的 sub-agent，使用 `mobile-react-refactor` skill 产出遵循 Figma 视觉、交互和 mock API 数据边界的 React flow
4. final React -> Compose：启动新的 sub-agent，先 review 当前 Figma 转码任务并理解目标 Compose 仓库；使用 `react-to-compose-ui` skill 生成或接入 Compose 代码。若目标是存量 KMP/CMP 仓库，按尽量复用原则接入对应业务模块，而不是生成孤立 demo

## 执行约束

- 在开始实现前，创建四步 todo，并与本 skill 的四个阶段完全一致。
- 严格按顺序执行。Step 1 未完成时，不要开始 Step 2；Step 2 未完成时，不要开始 Step 3；Step 3 未完成时，不要开始 Step 4。
- Step 3 和 Step 4 必须启动新的 sub-agent 完成，不要由当前 agent 直接完成。
- 启动 sub-agent 时，传递给模型的核心指令使用本 skill 中写明的固定话术；包含 `${ANDROID_PROJECT_DIR}` 和 `${COMPOSE_CODE_DIR}` 的话术必须先替换为 Step 1 解析出的绝对路径。
- Figma 到 React 阶段只负责生成、整理和串联中间表示；响应式重构、数据接口抽象和 Compose 映射分别交给后续 skill。
- React 优化阶段必须把 React 视为面向 Compose 的中间实现：视觉遵循 Figma 设计稿，交互遵循 Figma/用户指定 flow，展示数据通过 mock API、local service 或等价 adapter 暴露，方便后续映射到 KMP/CMP 的真实数据层。
- Compose 阶段如果目标是存量 KMP/CMP 仓库，必须保留当前 Figma 转码任务的上下文和产物，不要改写成全新迁移任务；先 review React flow、截图、交互和 mock API 边界，再理解目标仓库，最后按复用优先原则接入既有业务模块。
- 多张设计稿输入时，不要并行混写同一个 React 文件。先逐张生成独立产物，再统一拼接成 flow。

## 工作流

### Step 1：输入与能力判断

#### 1. 解析 Figma 输入

- 接受一个或多个包含 `node-id` 的 Figma section/node URL。
- 将输入规范化为有序屏幕清单，建议结构为：

```text
screenId: screen-01
figmaUrl: https://www.figma.com/design/...?...node-id=...
route: /screen-01
title: 可选，来自用户说明或 Figma section 名称
next: 可选，下一屏 screenId
```

- 如果用户明确给出交互顺序，按用户顺序执行。
- 如果用户只给出多个链接但没有交互顺序，按用户提供的链接顺序作为默认 flow，并在执行前简短提醒用户将按该顺序串联。
- 如果任一 Figma URL 不包含 `node-id`，停止并要求用户补充正确链接。

#### 2. 判断 React 生成路径

按以下优先级选择 Figma -> React 生成方式：

1. **Figma 链接 + access token 可用**
   - 使用 MCP 工具：`flow_d2c/tools/anchor-d2c-mcp`。
   - 调用 `figma_to_code_convert` 生成 React，参数使用：

```text
framework: Tailwind
generationMode: jsx
workspaceRoot: 当前工作目录或当前屏幕独立工作目录
figmaUrl: 当前屏幕的 Figma URL
useCache: 可按重试需要设置
```

   - 调用 `figma_to_code_fetch_screenshot` 获取当前屏幕截图。
   - 不要自己实现 HTTP、SSE、stdio 客户端或 Figma 转代码协议逻辑。

2. **有 Figma 链接但没有 access token**
   - 检查当前执行环境是否已暴露可直接使用的 Figma-to-React 工具，例如已配置的 MCP、IDE 工具、脚本或用户提供的本地生成命令。
   - 如果可以直接生成 React，先显示提醒：当前未收到 access token，将使用环境中可用的 Figma-to-React 工具生成 React 中间表示。
   - 如果环境工具可以同时导出截图，也必须导出每个屏幕的截图；如果不能导出截图，停止并要求用户提供截图或 token。

3. **没有 Figma 链接、没有 token、也没有可直接使用的 Figma-to-React 工具**
   - 停止并向用户提问，等待用户补充以下任一输入：
     - 包含 `node-id` 的 Figma 链接和 access token
     - 可直接执行的环境生成工具或命令
     - 已生成的 React 文件和对应截图

#### 3. 解析 Android 工程目录和 Compose 实现目录

如果用户没有指定代码实现目录，先通过本 skill 的脚本读取 Android 工程目录和 Compose 实现目录，然后根据返回结果执行：

```bash
python3 ${skill dir}/scripts/resolve_android_project.py getdata --workdir "$PWD"
```

如果用户已指定 Android 工程目录和 Compose 代码生成目录，直接调用 `setdata` 保存。

如果用户只指定了 Compose 代码生成目录，先从该目录向上查找 Android 工程根目录，再调用 `setdata` 保存：

```bash
python3 ${skill dir}/scripts/resolve_android_project.py setdata --workdir "$PWD" --android-project-dir "$ANDROID_PROJECT_DIR" --compose-code-dir "$COMPOSE_CODE_DIR"
```

如果用户选择使用默认 Android 壳工程，调用：

```bash
python3 ${skill dir}/scripts/resolve_android_project.py getdata --workdir "$PWD" --use-default-shell
```

默认 Android 壳工程的 Compose 代码写入目录是：

```text
app/src/main/java/com/example/myapplication/
```

要求：

- 必须解析脚本 stdout 的 JSON 结果
- 必须执行脚本返回的 `agentInstruction`
- 当 `nextAction` 是 `continue` 时，记录 `androidProjectDir` 为 `ANDROID_PROJECT_DIR`，记录 `composeCodeDir` 为 `COMPOSE_CODE_DIR`
- 当 `nextAction` 是 `ask_user` 时，使用脚本返回的 `userPrompt` 和 `choices` 询问用户，并按用户选择的 `commandTemplate` 重新运行脚本
- 当 `nextAction` 是 `stop` 时，停止并报告脚本返回的英文 `message`
- 如果用户已指定 Compose 代码生成目录，必须通过 `setdata` 将该目录作为 `--compose-code-dir` 保存
- Step 4 的 Android 工程根目录必须来自 `ANDROID_PROJECT_DIR`
- Step 4 的 Compose 代码写入目录必须来自 `COMPOSE_CODE_DIR`

#### 4. 判断 Compose 目标工程类型

根据 `ANDROID_PROJECT_DIR`、`COMPOSE_CODE_DIR`、用户描述和仓库文件结构，记录 Compose 目标类型：

```text
composeTargetType: shell-compose | existing-android-compose | existing-kmp-cmp
```

判断建议：

- 如果用户选择默认 Android 壳工程，记录为 `shell-compose`。
- 如果目标仓库是 Android Compose App，但没有 KMP/CMP 模块结构，记录为 `existing-android-compose`。
- 如果目标仓库包含 `composeApp`、`shared`、`commonMain`、`androidMain`、`iosMain`、`kotlin-multiplatform`、`org.jetbrains.compose`、`compose.multiplatform` 等明显 KMP/CMP 线索，记录为 `existing-kmp-cmp`。
- 如果无法判断，但用户明确说是存量 KMP、CMP、Compose Multiplatform 或 Kotlin Multiplatform 仓库，按 `existing-kmp-cmp` 处理。
- 如果仍无法判断，先按 `existing-android-compose` 处理，并在 Step 4 指令中要求 sub-agent review 仓库后纠正目标类型。

当目标类型是 `existing-kmp-cmp` 时，Step 4 不是“把 React 翻译成一个新 demo 页面”，而是“把当前 Figma 对应业务模块接入存量 KMP/CMP 仓库”。必须保留 Figma 转码任务上下文，包括：

- 有序屏幕清单和 Figma URL
- `Preview-screen-**.png` 或 `Preview.png`
- `ValidatedComponent.jsx`
- `RefactoredComponent.jsx`
- React flow 中的交互顺序、触发点和 mock API 数据边界

Step 1 到此结束时，至少要满足：

- 已得到有序屏幕清单，且每个 Figma URL 都包含 `node-id`，或已得到等价的本地 React + 截图输入
- 已确定 Figma -> React 生成路径
- 已解析并记录 `ANDROID_PROJECT_DIR`
- 已解析并记录 `COMPOSE_CODE_DIR`
- 已记录 `composeTargetType`
- `ANDROID_PROJECT_DIR` 不是空值

如果以上任一项不成立，不要进入 Step 2。

### Step 2：生成 React 中间表示并拼接 flow

#### 1. 准备 React 壳

在当前工作目录准备 React 壳：

```bash
git clone https://github.com/BubblePtr/react-dome.git ./react
```

#### 2. 逐屏生成 React 和截图

对屏幕清单逐项执行，不要跳过失败项：

- 使用 Step 1 选择的生成方式生成该屏 React。
- 如果使用 `anchor-d2c-mcp`，每个 Figma URL 单独调用一次 `figma_to_code_convert`。
- 为每个屏幕保存独立 React 源文件，例如：

```text
react/src/generated/Screen01Raw.jsx
react/src/generated/Screen02Raw.jsx
```

- 为每个屏幕保存独立截图，例如：

```text
Preview-screen-01.png
Preview-screen-02.png
```

- 复制资源文件到 React 工程合理目录，同时修改代码内的引用路径。
- 如果只有一个屏幕，保存唯一基础截图为 `Preview.png`，以兼容后续单屏 skill。
- 如果有多个屏幕，不要创建、复制或依赖 `Preview.png`；每个 screen 都必须保存为 `Preview-screen-**.png`，包括初始 screen。

#### 3. 拼接 flow 跳转交互版本

在 `./react` 中创建 `react/src/ValidatedComponent.jsx`，作为 Figma -> React 中间表示层的 flow 入口。

要求：

- 引入每个独立生成的 Raw screen 组件。
- 按 Step 1 的有序屏幕清单建立 screen registry。
- 提供真实 React flow 跳转交互，例如 `currentScreenId` 状态、上一页/下一页/指定 screen 切换函数和组件级 `onClick` 事件。
- 不改变单屏原始视觉结构；flow 容器只负责切屏和路由，不在此阶段重构布局。
- 如果 Figma 或用户提供了明确交互关系，按该关系设置跳转；否则按输入顺序设置线性 flow。
- 不能把多张截图、静态图或 Figma 预览图纵向滚动展示来冒充 flow。截图只能作为视觉参考，不能作为最终 UI 节点。
- flow 中显示的每个 screen 必须来自该屏生成的 React 组件，而不是 `<img src="Preview-screen-**.png">` 或背景图截图。
- 使用 VLM/视觉理解能力检查每张设计稿截图和生成的 React 结构，识别可能触发跳转的组件：
  - 主要按钮、底部 CTA、文字按钮
  - 返回箭头、下一步箭头、关闭按钮
  - tab、卡片、列表项、图标按钮和底部导航项
  - 视觉上表达继续、进入详情、返回、完成、取消或切换状态的控件
- 将高置信度触发点接入 React 事件，例如 `onClick={() => navigateTo("screen-02")}`、`onClick={goBack}` 或 `onClick={goNext}`。
- 当触发关系不确定时，保留可运行的默认跳转控件，并在代码注释或执行报告中说明低置信度触发点；不要因此退化为静态图片流。
- 在 `./react` 中配置对应页面或入口，让 `ValidatedComponent.jsx` 通过路由 `/validated` 被渲染。

#### 4. 跑通 React 壳

Step 2 的完成标准不只是“拿到代码”，还包括把生成的 React flow 挂到 `./react` 壳中并实际运行。

不要把“代码已经生成”误判成“React 壳已经可运行”。

Step 2 到此结束时，至少要满足：

- 当前工作目录中已有 `./react`
- 每个 Figma 屏幕或本地输入都有独立 React 源
- 单屏输入时，当前工作目录中已有唯一 `Preview.png`
- 多屏输入时，当前工作目录中没有被用于验证的 `Preview.png`，并且每个可达 screen 都有对应 `Preview-screen-**.png`
- `react/src/ValidatedComponent.jsx` 是 flow 入口，而不是单个散落组件
- 路由 `/validated` 已经指向该 flow 入口
- 多屏输入时，`ValidatedComponent.jsx` 通过 React 状态和事件实现屏幕切换，而不是滚动展示截图或静态图
- 已使用 VLM/视觉理解能力检查按钮、箭头、tab、卡片、列表项和底部导航等潜在触发组件，并将高置信度触发点接入 React 跳转事件
- 资源文件保存在 React 工程中，且被正常引用
- 该 React flow 已经能在 React 壳中运行

如果以上任一项不成立，不要进入 Step 3。

### Step 3：启动新的 sub-agent 重写 React flow

启动一个新的 sub-agent 完成这一步。

传递给该 sub-agent 的模型指令就是：

`使用 mobile-react-refactor skill 转换 ./react/src/ValidatedComponent.jsx 到 ./react/src/RefactoredComponent.jsx。严格遵守该 skill 中的要求和原则，不要跳过任何步骤。输入可能是由多张 Figma 设计稿拼接出的 flow 跳转交互版本；必须同时遵循 Figma 设计稿视觉、Figma/用户指定交互和数据 mock API 边界。保留 React 状态和事件驱动的 flow 交互顺序，重点检查按钮、箭头、tab、卡片、列表项、底部导航等触发组件，使用 VLM/视觉理解能力判断可点击区域并在 React 中加入或保留事件触发跳转。禁止把多屏 UI 退化为截图、静态图或滚动图片预览。将静态展示数据抽象成 mock API、local service、adapter 或等价接口化输出模式，为后续映射 KMP/CMP 的 repository/use case/view model 或线上接口做准备。所有资源文件已保存在本地，无需再使用脚本获取。`

同时明确输入输出：

- 输入是 Step 2 产出的 React flow 源 `./react`
- 保留 Step 2 产出的原始代码，不要直接覆盖 `ValidatedComponent.jsx`
- 输出文件是 `./react/src/RefactoredComponent.jsx`
- 在 `./react` 中新增或更新对应路由，使 `RefactoredComponent.jsx` 通过 `/refactored` 被渲染
- 输出必须仍是 flow 跳转交互式版本；不要退化成单屏静态页面
- 输出必须通过 React 组件、状态和事件处理实现跳转；不要用截图、静态图片或滚动图片预览表达多屏 UI
- 输出必须保留或补强高置信度触发组件的事件绑定，例如按钮、箭头、tab、卡片、列表项和底部导航项
- 输出必须包含可替换的数据加载边界，例如 mock API、local service、mock API adapter 或等价的接口化数据源
- 输出的数据结构命名应尽量贴近业务语义，方便 Compose 阶段映射到存量 KMP/CMP 的 repository、use case、ViewModel、UiState 或 equivalent store

### Step 4：启动新的 sub-agent 实现 Compose

启动一个新的 sub-agent 完成这一步。

传递给该 sub-agent 的模型指令就是：

`使用 react-to-compose-ui skill 转换 ./react/src/RefactoredComponent.jsx 到 Android/KMP/CMP 工程 ${ANDROID_PROJECT_DIR} 中的 Compose 实现目录 ${COMPOSE_CODE_DIR}。严格遵守该 skill 中的要求和原则，不要跳过任何步骤。React 输入是已经验证的 optimized flow 版本，包含 Figma 视觉、交互 flow 和可替换的数据加载边界；Compose 翻译时保留已验证布局和 flow 层级，不要回到原始 Figma 导出重新设计。开始写代码前，先 review 当前 Figma 转码任务上下文，包括 Figma URL、截图、ValidatedComponent.jsx、RefactoredComponent.jsx、交互触发点和 mock API 数据边界；再理解目标 Compose 仓库的导航、主题、组件、资源、状态管理、ViewModel/repository/use case 和模块边界。如果目标是存量 KMP/CMP 仓库，按尽量复用原则把 Figma 对应业务模块接入现有仓库：优先复用现有 navigation graph、theme/design system、commonMain 组件、平台资源、UiState、ViewModel/store、repository/use case 和 DI 入口；只有缺口明确时才新增最小必要代码。不要把结果写成孤立 demo、独立壳 App 或与现有业务流脱节的新页面。`

同时明确输入输出：

- 输入是 Step 3 验证后的 `RefactoredComponent.jsx`、Step 1 解析出的 `ANDROID_PROJECT_DIR` 和 `COMPOSE_CODE_DIR`
- 目标是把 UI 翻译到 Android Jetpack Compose 或 Compose Multiplatform（Kotlin），并根据 `composeTargetType` 决定是写入默认壳工程、既有 Android Compose App，还是接入存量 KMP/CMP 仓库
- 保持基准视口下尽量像素级一致
- 保留可映射到线上接口的数据边界意图；在存量 KMP/CMP 仓库中，优先映射到已有 repository/use case/ViewModel/store/UiState，不要在 Compose 阶段发明不存在的真实线上接口
- 如果 React flow 中存在多个 screen，Compose 输出也必须保留可导航的 flow 结构或明确映射到目标仓库现有导航
- 当目标是 `existing-kmp-cmp` 时，sub-agent 必须先输出简短 review 结论，说明将复用哪些现有模块、哪些新文件是必要的、Figma 业务模块接入到哪条现有入口或导航路径
- 当目标是 `existing-kmp-cmp` 时，新增代码优先放在仓库既有 feature/module 结构内；不要默认写入 `app/src/main/java/com/example/myapplication/`

## 停止条件

- Figma URL 不包含 `node-id`
- 没有 Figma 链接、没有 access token、没有可用环境工具，也没有已生成 React + 截图输入
- 已选择 `anchor-d2c-mcp`，但 `figma_to_code_convert` 不可用或没有产出可用 React 代码
- 已选择 `anchor-d2c-mcp`，但 `figma_to_code_fetch_screenshot` 不可用或截图获取失败
- 已选择环境工具，但无法生成可运行 React 或无法提供截图
- React 壳 clone 失败
- Android 工程解析脚本返回 `nextAction: ask_user`，且用户未指定 Compose 代码生成目录或未选择默认 Android 壳工程
- Android 工程解析脚本返回 `nextAction: stop`
- `ANDROID_PROJECT_DIR` 是空值
- 无法确定 Compose 目标工程类型，且 Step 4 sub-agent 也无法通过仓库 review 纠正
- 任一屏幕的 React 中间表示生成失败
- 多屏输入时没有形成明确 flow 顺序
- `ValidatedComponent.jsx` 还不是可运行的 flow 入口
- 多屏 UI 被实现为截图、静态图或滚动图片预览，而不是 React 组件之间的事件跳转
- 未检查或未处理明显的按钮、箭头、tab、卡片、列表项和底部导航跳转触发点
- 生成的 React flow 还不能在 React 壳中运行
- 存量 KMP/CMP 接入时，Step 4 没有先 review Figma 转码任务上下文和目标仓库结构
- 存量 KMP/CMP 接入时，Step 4 输出是孤立 demo、独立壳 App 或脱离现有业务模块的页面

出现以上任一情况时，停止并先修复初始化问题，不要继续后续步骤。

## 常见错误

- 在没有 `node-id` 的情况下就开始调用 React 生成或截图工具
- 把 `figma_to_code_convert` 和 `figma_to_code_fetch_screenshot` 写成旧的或不存在的工具名
- 有 Figma 链接但没有 access token 时，没有检查环境是否已有可用生成工具
- 没有 Figma 链接、token 或工具时，擅自编造 React 中间表示
- 多张 Figma 设计稿输入时，把所有输出覆盖到同一个文件
- 多张 Figma 设计稿输入时，跳过逐屏生成，直接手写合并结果
- 多张 Figma 设计稿输入时，把 `Preview-screen-**.png` 当作 UI 主体，做成滚动截图墙或静态图片预览
- 只添加全局上一页/下一页按钮，却没有检查设计稿自身的按钮、箭头、tab、卡片、列表项和底部导航触发点
- 没有使用 VLM/视觉理解能力判断可点击组件和跳转意图
- 单屏没有获取 `Preview.png`，或多屏没有获取每个 screen 对应的 `Preview-screen-**.png` 就继续后续步骤
- 没有解析 Android 工程目录和 Compose 实现目录就继续 Step 4
- 没有判断目标是默认壳工程、既有 Android Compose App 还是存量 KMP/CMP 仓库
- 用户只指定 Compose 代码生成目录时，没有先查找 Android 工程根目录并调用 `setdata`
- 在 Step 4 使用固定相对路径作为 Android 工程目录或 Compose 代码写入目录
- 只获取了 React 代码，却没有把产出的 React flow 挂到 `./react/src/ValidatedComponent.jsx` 并通过 `/validated` 验证运行
- 在 Step 3 直接覆盖 `ValidatedComponent.jsx`，没有保留原始代码
- 没有产出 `RefactoredComponent.jsx` 或没有提供 `/refactored` 路由
- `RefactoredComponent.jsx` 退化成单屏静态页面，丢失 flow 跳转
- React 优化阶段没有遵循 Figma 设计稿、交互和 mock API 数据边界
- React 优化阶段没有把 Figma 展示数据抽象成 API-ready/mock API 数据加载边界
- 存量 KMP/CMP 场景下，把当前 Figma 转码任务改写成全新迁移任务，丢失 Figma URL、截图、React flow、交互和 mock API 上下文
- 存量 KMP/CMP 场景下，调用 `react-to-compose-ui` 前没有 review task 或理解 Compose 仓库
- 存量 KMP/CMP 场景下，直接生成孤立 demo 页面，没有复用现有 navigation、theme、component、resource、UiState、ViewModel/store、repository/use case 或 DI 入口
- Step 3 或 Step 4 没有真正启动新的 sub-agent，而是当前 agent 直接做了实现
- 启动 sub-agent 时没有使用本 skill 指定的固定指令
- Step 1 还没完成就提前进入 Step 2
- Step 2 还没完成就提前进入 Step 3
- Step 3 还没完成就提前进入 Step 4
