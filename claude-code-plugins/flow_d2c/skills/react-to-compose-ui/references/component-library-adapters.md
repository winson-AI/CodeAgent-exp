# Compose Adapter 包

仅当调用方显式启用 adapter 模式并希望 Compose 翻译将 React 语义和截图证据映射到一个所选 adapter 包时，使用此参考。

## 目的

一个 adapter 包告诉 skill：

- 所选 adapter 有哪些 Compose 库组件可用
- 如何将屏幕语义映射到这些组件
- 哪些导入、包前缀和壳信号应指导翻译
- 哪些组件示例可以安全复用

Skill 仍然是工作流所有者。Adapter 包仅提供知识。

## 注册表约定

内置 adapter 位于 `adapters/<adapterId>/` 下，由 `adapters/registry.json` 索引。

`registry.json` 必须保持最小化：

- `version`
- `adapters`
- 每个 adapter 条目：
  - `id`
  - `path`
  - `displayName`

主 skill 使用调用方提供的 `adapterId` 在 adapter 模式显式启用时解析恰好一个注册表条目。如果所选 adapter 不可用，它不得自动切换到另一个 adapter。

## 包文件集

每个 adapter 包必须包含：

- `manifest.json`
- `aliases.json`
- `component_knowledge.json`
- `prompt.md`

`component_knowledge.jsonl` 是可选的。仅当需要更深入的示例或更丰富的参数和事件细节时使用它。

允许为编写便利添加额外文件，但主 skill v1 仅消费上面列出的文件。

## 证据划分

对不同输入区别对待：

- React 代码：
  - 结构和语义的主要来源
  - 识别按钮、标签、卡片、工具栏、列表、对话框和归属边界
- 截图：
  - 视觉消歧的次要来源
  - 澄清填充与描边、chip 与 tag、标题栏样式、分隔线处理、elevation 和间距强调
- Android 壳：
  - 实际库可用性的来源
  - 确认导入、主题、导航归属和依赖配置
- 所选 adapter 包：
  - 组件候选、库规则和组件级知识的来源

不要让截图样式单独覆盖强 React 或壳证据。

## 资源保真

当所选 adapter 或原始 Compose 区域需要图标或本地图稿时：

- 当真实壳或 adapter 指导的 drawable 资源已与已验证的 React 源匹配时优先使用
- 保留源中的真实图标和插图，而非替换为占位符或无关素材
- 如果本地矢量资源源自 `.svg` 且须在 Android 上运行，在接入 Compose 之前将其转换为 Android `VectorDrawable` `.xml`
- 如果 React 阶段已产出 `parsed_resources/resources.json`，优先先将该清单物化到 Android drawable 目录，使 SVG 和位图资源通过一个稳定步骤进入壳
- 优先使用 `scripts/convert_svg_to_android_vector.py` 作为该步骤的唯一仓库本地物化封装；当你已有 React 阶段的已解析资源清单时，使用该清单作为唯一输入约定
- 不要依赖原始 `.svg` 文件作为 Android 运行时 drawable 输入

对于接受 `iconRes` 或其他 drawable 资源参数的组件，传递真实 drawable 资源而非占位符。

## 检索流程

在 adapter 启用的运行中接收到 `adapterId` 后：

1. 读取 `adapters/registry.json`
2. 解析该 `adapterId` 的确切包路径
3. 假定包已在运行时消费之前生成并验证
4. 读取 `manifest.json`
5. 确认壳暴露了 adapter 描述的包前缀、导入或依赖提示
6. 读取 `aliases.json`
7. 使用 `aliases.json` 从屏幕语义缩小候选组件名称范围
8. 为你实际计划使用的候选组件打开 `component_knowledge.json`
9. 仅当文件存在且你需要更丰富的示例、事件约定或参数形状时才打开 `component_knowledge.jsonl`
10. 读取 `prompt.md`
11. 将紧凑的翻译上下文带入第 9 轮：
    - adapter id
    - 库规则
    - 组件映射
    - 导入或包提示
    - 一小组示例

默认不要将完整组件库或完整示例包加载到上下文中。

## 推荐检索结构

使用紧凑的中间结果，如：

```json
{
  "library": "dux",
  "confidence": 0.86,
  "mappings": [
    {
      "semantic": "button",
      "component": "DuxButton",
      "confidence": 0.93
    },
    {
      "semantic": "title_bar",
      "component": "DuxTitleBar",
      "confidence": 0.88
    }
  ]
}
```

如果置信度低，首先保持布局正确，对不明确区域回退到原始 Compose 而非强制使用 adapter 组件。原始 Compose 仍是此 skill 的默认路径。

## 包文件约定

### `manifest.json`

必需核心字段：

- `id`
- `displayName`
- `framework`
- `selectionHints`

允许的可选字段：

- `packagePrefixes`
- `fallback`
- `notes`
- 其他不冲突的元数据，有助于编写或调试

`framework` 必须为 `android-compose`。

### `aliases.json`

将屏幕语义映射到可能的 adapter 组件，例如：

```json
{
  "button": ["DuxButton"],
  "title_bar": ["DuxTitleBar"],
  "panel": ["DuxBasicPanel"]
}
```

此文件有意保持宽松。它不需要覆盖每个语义。它应仅提供当前库的最强候选。

### `component_knowledge.json`

在缩小到候选组件后用作主要知识查找源。此文件应按组件名称索引，可包含以下任意组合：

- 描述
- 接口签名
- 属性
- 事件
- 少量示例

并非每个组件都需要相同的深度。保持文件有用且紧凑，而非人为统一。

### `component_knowledge.jsonl`

可选的深度示例源。仅当所选组件仍需要更丰富的实现细节时使用。优先按组件名称针对性查找，而非打开整个文件。

### `prompt.md`

包含简短的库特定翻译规则：

- 何时优先使用库组件
- 何时回退
- 导入和主题约束
- 反重复规则
- 资源注意事项

保持 `prompt.md` 简短。详细示例属于 `component_knowledge.jsonl`（当该文件存在时）。

## 验证规则

包验证完全属于 adapter 生成阶段。`react-to-compose-ui` 假定所选 adapter 已准备就绪并符合约定的包约定。

## 参考示例

`adapters/dux/` 是此仓库中的第一个参考 adapter 包。将其用作以下方面的基线示例：

- 注册表条目形状
- manifest 形状
- alias 风格
- prompt 简洁性
- 组件知识粒度
