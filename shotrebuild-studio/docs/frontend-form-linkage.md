# 前端联动与校验说明

## Provider / Model / Workflow 联动
- 页面：`apps/desktop/src/pages/WorkflowsPage.tsx`
- 逻辑：
  1. 先拉取 provider 列表；
  2. 选择 provider 后，动态请求对应的 models 与 workflows；
  3. 任务提交时从下拉框选择 provider/model/workflow，不允许手动输入 provider_id。

## 表单校验
- Provider 未选中：提示“请先选择 Provider”。
- 模型/工作流未选中：提示“请先选择模型和工作流”。
- Prompt 非法 JSON：提示“Prompt JSON 格式错误”。
- Workflow 创建字段为空：提示 `workflow_key` / `name` 不能为空。
- Model 创建字段为空：提示 `model_key` / `display_name` 不能为空。

## 错误展示
- API 请求错误会展示在页面红色错误提示区域。
