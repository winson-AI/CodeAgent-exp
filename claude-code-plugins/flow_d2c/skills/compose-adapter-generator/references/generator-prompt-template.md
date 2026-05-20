# 生成器提示词模板

当需要智能代理新建适配器配置包时，可使用以下提示词：

```text
为以下 Compose 库创建一个全新的 `react-to-compose-ui` 适配器包。

库名称：<display name>
适配器 ID：<adapterId>
包前缀：<逗号分隔的前缀列表>
文档与示例：<路径或 URL 地址>
外壳判定依据：<路径、依赖项或导入语句（如可用）>
已知降级规则：<可选备注>

输出要求：
- 将草稿包写入 ./compose-adapter-<adapterId>/
- 请勿直接修改 skills/react-to-compose-ui/adapters/ 目录或其注册表
- 输出一段注册表条目片段，用于后续手动插入到 skills/react-to-compose-ui/adapters/registry.json
- 必需文件：manifest.json、aliases.json、component_knowledge.json、prompt.md
- 可选文件：component_knowledge.jsonl
- framework 必须为 android-compose
- manifest 必须包含 id、displayName、framework、selectionHints
- 别名应保持精简且基于语义
- component_knowledge.json 必须以组件名称作为键
- prompt.md 应保持简洁且为库级别说明
- 请勿添加可执行插件逻辑或自定义工作流钩子
- 完成前运行 skills/compose-adapter-generator/scripts/validate_adapter_bundle.py --adapter-dir ./compose-adapter-<adapterId>/

专注于生成可复用的知识库包，而非页面实现。
```
