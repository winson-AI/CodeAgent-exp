---
name: compose-adapter-generator
description: 读取目标 Compose 库的文档、示例和 Shell 相关提示，在当前工作目录生成一份可草稿版 react-to-compose-ui 适配器打包文件，用于后续手动集成。
---

# Compose 适配器生成器

当目标 Compose 库需要全新适配器打包，或是现有打包内容过于简略、无法满足后续 `react-to-compose-ui` 运行需求时，使用该技能。

本技能**仅生成知识打包文件**，不会生成可执行插件逻辑，也不会为 `react-to-compose-ui` 新增自定义工作流钩子。

该技能属于前置预检或初始化接入工具，**不可**在页面翻译流程中作为同步子步骤运行。

禁止通过本技能直接写入固定的 `react-to-compose-ui` 技能目录。仅在当前工作目录生成可直接拷贝的草稿打包文件，并给出后续手动集成步骤说明。

典型用户场景：
- 在 Compose 翻译前，发现目标库暂无可用适配器
- 运行本技能，在当前目录生成适配器草稿
- 人工审核后，将该打包文件手动集成至 `react-to-compose-ui`
- 完成集成后，再执行 `react-to-compose-ui(adapterId=...)`

若翻译过程中发现所选适配器存在底层缺失，需终止本次翻译，使用本技能离线完善适配器后再重启翻译。切勿将本技能嵌入翻译流程循环中执行。

## 输入参数

- 必填：目标库名称
- 必填：`adapterId`
- 必填：Android 或 Compose 包前缀集合
- 必填：组件文档/示例的源文件集合
- 可选：Shell 专属依赖提示源文件集合
- 可选：已知降级规则或不支持区域列表

## 输出约定

将草稿打包文件输出至当前工作目录，示例：

- `./compose-adapter-<adapterId>/`

禁止直接修改内置运行时技能文件。

需准备以下内容：
- 一份可直接拷贝的适配器打包目录，后续放置路径：`skills/react-to-compose-ui/adapters/<adapterId>/`
- 一段注册表配置片段，后续手动插入至 `skills/react-to-compose-ui/adapters/registry.json`

打包文件必须包含：
- `manifest.json`
- `aliases.json`
- `component_knowledge.json`
- `prompt.md`

`component_knowledge.jsonl` 为可选文件，仅当库需要更丰富示例、避免 `component_knowledge.json` 臃肿时才添加。

## 强制工作流程

1. 读取 [references/adapter-generator.md](references/adapter-generator.md)
2. 读取 [references/generator-prompt-template.md](references/generator-prompt-template.md)
3. 读取 `skills/react-to-compose-ui/references/component-library-adapters.md`
4. 解析目标库源码：
   - 包前缀
   - 组件名称
   - 参数与事件
   - 主题或提供者约束
   - 图标与绘制资源规范
5. 若存在 Shell 提示文件，进行解析：
   - Shell 中已配置的导入依赖
   - 依赖声明配置
   - Shell 项目中的示例用法
6. 精简语义别名集合：
   - 仅保留主技能大概率会用到的高可信度语义
   - 禁止为凑数随意编造别名
7. 编写 `manifest.json`，包含核心必填字段：
   - `id`
   - `displayName`
   - `framework`
   - `selectionHints`
8. 编写 `aliases.json`
9. 编写 `component_knowledge.json` 作为核心知识源
10. 仅当额外示例能明显优化翻译效果时，才添加 `component_knowledge.jsonl`
11. 编写 `prompt.md` 规则说明文件：
    - 优先使用库内置组件的场景
    - 降级使用原生 Compose 的场景
    - 导入或主题约束条件
    - 避免重复定义与资源保真注意事项
12. 编写注册表配置片段，包含：
    - `id`
    - `path`
    - `displayName`
13. 执行校验脚本：`skills/compose-adapter-generator/scripts/validate_adapter_bundle.py --adapter-dir ./compose-adapter-<adapterId>/`
14. 清晰输出后续手动操作步骤：
    - 将打包目录拷贝至 `skills/react-to-compose-ui/adapters/<adapterId>/`
    - 将准备好的注册表片段写入 `skills/react-to-compose-ui/adapters/registry.json`
15. 仅在草稿打包校验通过，或明确输出阻塞问题后再结束流程

## 规则约束

- 输出产物为**知识打包文件**，而非运行时插件。
- 禁止新增可执行适配器脚本或自定义翻译钩子。
- `prompt.md` 保持精简，仅定义库级别通用规则。
- 复杂示例不要写在 `prompt.md` 中，深度示例统一放入 `component_knowledge.jsonl`。
- `component_knowledge.json` 以组件名作为键值索引。
- 不同组件允许配置不同详细程度的知识描述。
- 别名配置遵循实用精简原则，目标是提升检索效率，而非追求分类完整度。
- 若某区域无匹配的可靠库组件，需配置降级规则，而非强行生成错误映射关系。
- 草稿打包文件必须可通过生成器自带的 `--adapter-dir` 校验脚本检测。
- 禁止通过本技能直接编辑 `skills/react-to-compose-ui/adapters/` 目录及其 `registry.json` 文件。

## 参考文档

- [references/adapter-generator.md](references/adapter-generator.md)
- [references/generator-prompt-template.md](references/generator-prompt-template.md)
- [../react-to-compose-ui/references/component-library-adapters.md](/Users/bytedance/Code/d2c-plugin/skills/react-to-compose-ui/references/component-library-adapters.md)
- [scripts/validate_adapter_bundle.py](/Users/bytedance/Code/d2c-plugin/skills/compose-adapter-generator/scripts/validate_adapter_bundle.py)

## 退出标准

- 当前工作目录已生成 `./compose-adapter-<adapterId>/` 目录
- 输出内容包含注册表配置片段
- 所有必填配置文件齐全
- `component_knowledge.jsonl` 不存在或为合法 JSONL 格式
- 校验脚本通过 `--adapter-dir` 检测
- 标准输出简要展示：草稿打包路径、注册表片段、已选组件别名、现存阻塞问题