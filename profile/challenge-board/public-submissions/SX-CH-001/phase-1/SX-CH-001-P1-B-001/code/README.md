# SX-CH-001: Multi-Hop Causal Chain Uncertainty Quantification

## 因果链多跳推理的不确定性量化

本仓库实现了一套用于量化因果链多跳推理不确定性的方法，包含非朴素置信度聚合模型和原则性停止准则。

## 项目结构

```
SX-CH-001-causal-chain-uncertainty/
├── src/
│   ├── __init__.py
│   ├── aggregator.py        # 置信度聚合模型（朴素连乘 / 贝叶斯更新 / Noisy-OR）
│   ├── stopping.py         # 停止准则（置信区间宽度 / 信息增益 / 最大跳数）
│   ├── calibrator.py       # 校准验证（Brier Score / 可靠性图 / 分桶校准）
│   └── evaluator.py       # 端到端评估器
├── data/
│   ├── annotated_chains.csv   # 标注因果链数据（50 条）
│   └── results/               # 评估结果输出目录
├── configs/
│   └── default.yaml          # 默认配置
├── tests/
│   └── test_core.py          # 核心测试用例
├── annotation/
│   └── ANNOTATION_TASK.md   # 标注任务说明（帮手使用）
└── README.md
```

## 快速开始

```bash
pip install -r requirements.txt
python -m src.evaluator --input data/annotated_chains.csv --output data/results
```

## 输入格式

数据文件 `data/annotated_chains.csv` 的列定义如下：

| 列名 | 类型 | 说明 |
|------|------|------|
| `chain_id` | string | 链编号 |
| `hops` | JSON 字符串 | 事件描述字符串列表，如 `["事件A", "事件B"]` |
| `confidence_per_hop` | JSON 字符串 | 每跳置信度浮点数列表，如 `[0.95, 0.90, 0.85]` |
| `label` | boolean | 因果链最终是否成立（true/false） |
| `domain` | string | 所属金融领域（macro/commodity/equity/forex/crypto/credit） |
| `notes` | string | 标注备注 |

示例 CSV 行：

```csv
chain_id,hops,domain,label,confidence_per_hop,notes
CH001,"[""美联储宣布加息50bp"",""美元指数走强"",""新兴市场资本外流""]",macro,True,"[0.95, 0.90, 0.85]","标准宽松周期"
```

程序接受以下两种调用方式：

**方式 1：命令行指定 CSV 文件（批量评估）**

```bash
python run.py --input data/annotated_chains.csv --output data/results
```

**方式 2：单条链 JSON 字符串（快速测试）**

```bash
python run.py --chain '{"chain_id":"TEST","hops":["事件A","事件B"],"label":true,"confidence_per_hop":[0.95, 0.90]}'
```

**方式 3：模块调用**

```python
from src.evaluator import CausalChainEvaluator

chain = {
    "chain_id": "TEST",
    "hops": ["美联储加息", "美元走强"],
    "label": True,
    "confidence_per_hop": [0.95, 0.90],
}

evaluator = CausalChainEvaluator(aggregator_name="DampedMultiplier")
result = evaluator.evaluate(chain)
print(f"置信度: {result.end_to_end_confidence:.4f}")
print(f"CI: [{result.ci_lower:.4f}, {result.ci_upper:.4f}]")
print(f"停止: {result.should_stop} ({result.stop_reason})")
```

## 输出格式

端到端输出包含：

- `end_to_end_confidence`: 端到端置信度
- `end_to_end_ci`: 置信区间 [lower, upper]
- `should_stop`: 是否应停止推理
- `stop_reason`: 停止原因
- `brier_score`: Brier Score
- `calibration_plot.png`: 可靠性图

## 方法说明

详见 [ANNOTATION_TASK.md](annotation/ANNOTATION_TASK.md) 中的理论背景部分。

## 奖金档位目标

- S 档（7,200 元）：Brier Score < 0.15，50 条标注链校准验证
- A 档（5,100 元）：Brier Score 0.15–0.20，可运行 + 校准框架
- B 档（2,700 元）：至少 2 种聚合方案 + 停止准则雏形 + 合成案例
- C 档（900 元）：清晰分析 + 替代公式说明
