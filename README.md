# 12-ladderbill（阶梯电费）

Ladderbill — 居民阶梯电价分段累进（含尖峰系数）

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4100 |
| API | http://localhost:9100 |

## 主链

抄表录入 → 阶梯分段计费 → 账单明细

## 尖峰对比与钉选

- `POST /api/compare` 入库时把输入参数与当时所用 `peak_factor` 一并快照到对比运行记录。
- `GET /api/compare/runs?page=&page_size=` 分页列表（软删除默认不可见，钉选置前）；`GET /api/compare/runs/{id}` 读详情，软删除记录按 id 仍可读完整快照。
- `POST/DELETE /api/compare/runs/{id}/pin` 钉选/取消；`DELETE /api/compare/runs/{id}` 软删除。
- 钉选后在设置页修改全局系数（`PUT /api/settings/peak_factor`），只影响之后的新对比；已钉选运行的系数与合计保持钉选当时的值不变。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
