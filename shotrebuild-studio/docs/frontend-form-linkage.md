# 前端联动、失败回退与重试说明

## Provider / Model / Workflow 联动
- 选择 provider 后，自动加载对应 model 与 workflow。
- 不允许手动输入 provider_id，仅通过下拉框选择。

## 表单校验
- Provider 未选中：提示“请先选择 Provider”。
- Model/Workflow 未选中：提示“请先选择模型和工作流”。
- Prompt 非法 JSON：提示“Prompt JSON 格式错误”。
- Workflow 创建字段为空：提示 `workflow_key`/`name` 不能为空。

## 任务失败与重试交互
- 提交时支持设置：`fallback_provider`、`fallback_model_key`、`max_retries`。
- 页面会轮询任务状态并展示失败原因。
- 提供“重试任务”按钮触发 `/provider_jobs/{job_id}/retry`。

## Provider/Model/Workflow 管理
- Provider 页：新增、启停更新、删除。
- Model 页：新增、删除。
- Workflow 页：新增、删除。
