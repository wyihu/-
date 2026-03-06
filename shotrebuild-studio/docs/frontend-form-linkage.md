# 前端联动、任务回退与重试说明

## 联动规则
- 先选择 Provider，再动态加载对应 Model / Workflow。
- 不允许手动输入 provider_id。

## 校验规则
- Provider 未选：提示“请先选择 Provider”。
- Model/Workflow 未选：提示“请先选择模型和工作流”。
- Prompt 非法 JSON：提示“Prompt JSON 格式错误”。

## 任务回退与重试
- 提交任务时可配置：
  - `fallback_provider`
  - `fallback_model_key`
  - `max_retries`
- 若主 provider/model 失败，后端自动按重试策略尝试并回退到备用方案。

## 页面展示
- 实时轮询任务状态（2s）并显示 `PENDING/RUNNING/SUCCEEDED/FAILED/RETRYING`。
- 失败时展示失败原因（error_message）。
- 提供“重试任务”按钮，触发 `/provider_jobs/{job_id}/retry`。
- 提供任务历史状态显示（`status_history_json`）与任务列表展示（含重试次数）。
