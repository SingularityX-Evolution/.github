# SX-CH-002｜提升 Tardis 历史数据与 Binance 实时采集数据在四个永续合约上的一致性，并定位剩余行情与因子差异原因

[← Back to Challenge Board](../README.md) ｜ [返回挑战列表](../README.zh-CN.md)

| 项目 | 内容 |
|---|---|
| 规则版本 | V2.0.0（第二版） |
| 发布日期 | 2026-06-12 |
| 规则解释主体 | 零界演化 |
| 挑战编号 | SX-CH-002 |
| 难度等级 | Hard |
| 人民币赏金上限 | 8,800 元 |
| 认定关闭规则 | 不设置固定时间限制；S、A 任一等级认证成功后，该等级即关闭 |
| 提交方式 | 默认私密邮箱提交；公开 PR 可选 |

> 本页面为公开展示版，展示背景、核心问题、公开任务范围、交付标准、认定标准以及赏金分档。赏金为上限，不是保证付款；实际支付以隐藏评测、复现结果、评审结论、合规要求和最终接收规则为准。


## 背景

我们在一个量化交易项目中使用 Binance USD-M Futures 行情数据，当前重点品种为：

- BTCUSDT
- ETHUSDT
- BNBUSDT
- DOTUSDT

系统同时使用两类数据源：

| 数据源 | 用途 |
|---|---|
| Tardis 历史数据 | 用于离线因子计算、回测、模型训练和历史验证。 |
| Binance 实时采集数据 | 通过 Binance Futures WebSocket 和 REST API 实时采集，用于线上因子计算和实盘推理。 |

理论上，这两类数据描述的是同一交易所、同一合约、同一市场事件。但实际使用中发现：即使尽量对齐数据字段、时间窗口和计算逻辑，Tardis 历史数据与实时采集数据仍然存在差异，并且这种差异会传导到 10 秒级因子计算结果中。

本问题不是策略优化，也不是模型优化，而是行情数据一致性与差异归因问题。

## 涉及数据通道

本问题主要涉及 Binance Futures 的以下数据通道：

| 数据侧 | 通道 / 接口 | 说明 |
|---|---|---|
| Tardis 历史数据 | trades | 成交数据，用于计算成交价格、成交量、买卖方向、VWAP、TWAP、成交次数、买卖方向分组因子等。 |
| Tardis 历史数据 | quotes | 最优买卖价数据，用于计算 spread、mid price、best bid / ask 变化次数、盘口一档量价变化等。 |
| Tardis 历史数据 | book_snapshot_25 | 25 档盘口快照，用于构建 order book 状态并生成盘口相关特征。 |
| Tardis 历史数据 | derivative_ticker | 衍生品行情信息，用于 mark price、index price、funding rate、open interest 等因子或辅助字段。 |
| Binance 实时采集 | WebSocket `@depth` | 用于接收增量盘口更新，并结合 REST snapshot 重建 order book。 |
| Binance 实时采集 | REST `/fapi/v1/depth` | 用于初始化或重同步 order book。 |
| Binance 实时采集 | WebSocket `@trade` | 用于实时成交数据，并与 Tardis trades 通道对齐。 |
| Binance 实时采集 | REST `/fapi/v1/premiumIndex` | 用于获取 mark price、index price、funding rate、next funding time 等信息。 |
| Binance 实时采集 | REST `/fapi/v1/openInterest` | 用于获取 open interest。 |
| Binance 实时采集 | REST `/fapi/v1/ticker/24hr` | 用于补充 last price 等 ticker 信息。 |

## 核心问题

如何在 BTCUSDT、ETHUSDT、BNBUSDT、DOTUSDT 四个 Binance 永续合约上，尽可能提高 Tardis 历史数据和 Binance 实时采集数据的一致性，并在仍然不一致时定位剩余差异来自哪里。

需要关注两个层面的差异：

1. **原始行情数据不一致**：例如时间戳口径、depth update 事件顺序、丢包、重连、REST snapshot 衔接、quotes 与实时 top-of-book 口径、book_snapshot_25 与实时重建盘口快照、derivative_ticker 与实时 REST 拼接字段、trades 成交方向、成交时间、成交 id、重复、缺失、乱序等。
2. **10 秒级因子计算结果不一致**：例如 quote 类因子、trade 类因子、derivative ticker 字段、rolling window、标准化因子和模型输入在两类数据源上的差异。

最终目标是判断因子差异到底来自原始数据差异，还是来自采样窗口、事件排序、时间戳对齐、盘口重建、字段定义、缺失填充、rolling warmup、标准化参数等环节，并区分哪些差异可修复，哪些差异可能是数据源天然差异。

## 公开任务范围

请设计一套可落地方案，用于解决以下问题：

- 在 BTCUSDT、ETHUSDT、BNBUSDT、DOTUSDT 四个 Binance 永续合约上，尽可能提高 Tardis 历史数据和 Binance 实时采集数据的一致性。
- 明确说明每个数据通道应如何对齐：`trades`、`quotes`、`book_snapshot_25`、`derivative_ticker`、实时 `@depth`、实时 `@trade`、实时 REST depth、premiumIndex、openInterest、ticker/24hr。
- 明确说明如何比较和提升 10 秒级因子计算结果的一致性。
- 对仍然无法消除的差异进行分类归因，并说明哪些差异可修复，哪些差异可能是数据源天然差异。

## 预期提交内容

提交内容应覆盖以下公开交付方向：

- 数据通道级对齐方案，包括 Tardis trades / quotes / book_snapshot_25 / derivative_ticker 与 Binance 实时 WebSocket、REST 数据之间的对应关系。
- 时间戳与事件顺序处理方案，包括主对齐时间、depth update 连续性判断、乱序、丢包、重连、REST snapshot 重同步，以及 Tardis `timestamp` 与 `local_timestamp` 的差异处理。
- 原始数据一致性指标，包括 trade、quote、book snapshot、derivative ticker 等通道的价格、数量、方向、更新时间和误差指标。
- 因子一致性分析方案，包括原始数据、标准化行情数据、10 秒聚合结果、最终因子结果、rolling / 标准化模型输入的逐层比较。
- 剩余差异归因框架，包括数据源定义差异、实时采集延迟或丢包、depth 重建、quote 生成、derivative ticker 拼接、窗口边界、ffill / bfill、warmup、rolling window、标准化参数等原因。
- 验证实验设计，覆盖四个目标合约以及多个交易日或多个实时采样时段，并能对一致性提升前后的原始行情层面和因子层面误差进行比较。

## 悬赏金额、等级认定与最终接收规则

本题悬赏总金额最高为人民币 **8,800 元**。

本题采用“S / A 等级认证、单档关闭、按完成度分档支付”机制：

1. 主办方收到提交后进行评测；提交内容一经提交不得更改。
2. 提交或上传后五个自然日内，主办方会给出答复。答复可能包括：确认进入评审、要求补充非实质性材料、初筛未通过、继续复现评测、通过某档认证或未通过等级认证。
3. S、A 两个等级分别独立认定；当某一等级已有认证成功者并由主办方公告关闭后，该等级即关闭，不再接受该等级新的认定申请。
4. 同一档位以完整提交送达主办方指定邮箱或指定上传渠道的时间戳为准进入评审队列；关闭公告前已经收到的提交，主办方仍会给出答复，但不保证该档位仍有奖金名额或继续进入该档奖金评审。
5. 认证成功者不自动获得全额，实际支付金额将根据隐藏评测集中的数据一致性、因子一致性、工程可运行性、差异归因完整度和报告完整度分档确定。
6. 未通过等级认证、未被采纳且未进入结算流程的方案原则上不支付奖金；除评审、复核、反作弊、安全审计、争议处理和合规留存所需的必要查看、测试和保存外，主办方不得直接将该方案的代码、模型、参数、策略逻辑、接口定义、测试样例、验证集或核心实现细节用于生产、商业化、再许可或对外发布。
7. 等级认证成功后，主办方仅会在不披露敏感信息、私有代码、账户信息、未公开策略细节和受限数据的前提下，公示认证成功者的脱敏作品摘要、认证档位、挑战编号或经审核可公开材料，公示期为一周。

## 交付标准

有效提交应至少包含以下内容：

1. **完整工程仓库**
   - README.md、Dockerfile 或等价环境配置、依赖文件、配置文件和测试脚本；
   - 能在隔离环境中运行公开样例或提交者自备样例；
   - 能生成标准化行情数据、10 秒级聚合数据、最终因子结果、逐日 IC 评测结果和差异归因报告。

2. **四类 Tardis 数据与 Binance 实时数据对齐方案**
   - 覆盖 Tardis `trades`、`quotes`、`book_snapshot_25`、`derivative_ticker`；
   - 覆盖 Binance `@depth`、`@trade`、REST depth、premiumIndex、openInterest、ticker/24hr；
   - 明确字段映射、时间戳选择、缺失处理、重复处理、排序规则和异常处理。

3. **Order Book 重建与连续性检测**
   - 正确处理 Binance depth update 中的 `E`、`T`、`U`、`u`、`pu`；
   - 支持 REST snapshot 初始化、增量更新衔接、sequence continuity 检测、断线恢复和 REST snapshot 重同步；
   - 稳定生成 25 档盘口状态；
   - 不得使用未来数据、未来 sequence 或 hindsight 方式修复历史盘口。

4. **因子层一致性与逐层归因**
   - 逐层比较 raw data、标准化行情数据、10 秒聚合数据、最终因子数据、rolling / 标准化模型输入；
   - 当某个因子 IC 下降或误差扩大时，能够追溯到上游字段、时间窗口、事件排序、盘口重建、缺失填充、rolling warmup 或标准化参数。

5. **评估报告**
   - 输出逐日、逐合约、逐通道、逐特征 IC correlation；
   - 展示一致性提升前后对比；
   - 明确区分可修复差异与不可修复差异；
   - 对声称“天然不可对齐”的差异提供实验依据和误差量级。

## 奖金分档与认定标准

本题最终评测以“连续五日、多品种、多通道、多特征一致性”为核心。主办方将使用隐藏测试集，对提交方案生成的数据与 Tardis 源数据进行逐日逐特征对齐评测。

核心量化口径如下：

1. 对 BTCUSDT、ETHUSDT、BNBUSDT、DOTUSDT 四个合约分别评测。
2. 对 `trades`、`quotes`、`book_snapshot_25`、`derivative_ticker` 四类数据及其派生的 10 秒级因子分别评测。
3. 每日对每个合约、每类数据、每个特征计算 IC correlation，即 `corr(feature_realtime, feature_tardis)`。
4. 重点统计“连续五日 IC ≥ 0.99 的特征比例”。该比例越高，说明方案的一致性越好。
5. 若某特征在任意一天缺失、无法生成、时间索引无法对齐或样本数不足，则该特征默认计为未达标。
6. 除 IC 外，主办方可辅助参考 MAE、RMSE、方向一致率、缺失率、重复率、KS Statistic、Wasserstein Distance 等指标。

| 档位 | 支付金额 | 量化判定标准 |
|---|---:|---|
| S 档：完全解出 | 8,800 元 | 连续五日 IC ≥ 0.99 的特征比例 ≥ 90%；Mean IC ≥ 0.995；Median IC ≥ 0.997；四个合约、四类数据全部覆盖；核心 10 秒级因子一致性显著提升；order book reconstruction 正确且可复现；差异归因完整。 |
| A 档：基本解出 | 5,200 元 | 连续五日 IC ≥ 0.99 的特征比例 ≥ 75%；Mean IC ≥ 0.990；Median IC ≥ 0.992；完成主要数据通道对齐；核心 quote / trade / orderbook 因子一致性明显提升；工程可运行；能定位大部分差异来源。 |

说明：

1. 若提交未达到 A 档最低有效标准，主办方可判定该提交未通过等级认证，不支付奖金。
2. 若方案达到 A 档但未达到 S 档，则只支付 A 档金额，不因其提交较早或排名靠前而自动支付更高等级金额。
3. 若某方案在 IC 指标上达到高档位，但存在不可复现、使用未来数据、隐藏样本失效或差异归因严重缺失，主办方可下调档位或判定未通过等级认证。
4. 若某方案未达到 S 档基础奖金，但发现经验证的重要结构性差异，例如 Tardis 与 Binance 某接口字段定义差异、采样触发逻辑差异、timestamp 口径差异或 Binance 实时接口不可恢复缺陷，主办方可在 S、A 对应档位内酌情上调认定。

## “完全解出”的明确标准

获得全额 8,800 元，必须同时满足以下条件：

1. **工程可运行**
   - 提交完整代码仓库；
   - 包含 README.md、Dockerfile 或等价环境配置文件、依赖文件、配置文件和测试脚本；
   - 主办方在隔离环境中可一键复现；
   - 能生成标准化后的行情数据、10 秒级聚合数据、最终因子结果、逐日 IC 评测结果和差异归因报告。

2. **四类数据均完成对齐**
   - 必须覆盖 `trades`、`quotes`、`book_snapshot_25`、`derivative_ticker` 四类 Tardis 数据；
   - 必须覆盖 Binance `@depth`、`@trade`、REST depth、premiumIndex、openInterest、ticker/24hr 等实时或 REST 数据来源；
   - 必须说明每类数据的字段映射、时间戳选择、缺失处理、重复处理和排序规则。

3. **连续五日 IC 达标**
   - 隐藏测试集中，连续五个自然日或交易日内，四个合约整体统计的 IC ≥ 0.99 特征比例不得低于 90%；
   - Mean IC 不得低于 0.995；Median IC 不得低于 0.997；
   - 若某一天任一核心通道无法生成有效数据，则该日相关特征计为未达标；
   - 不得只针对 BTCUSDT 或单一高流动性时段优化，四个合约均需稳定。

4. **因子层一致性必须可解释**
   - 必须逐层比较 raw data、标准化行情数据、10 秒聚合数据、最终因子数据、rolling / 标准化模型输入；
   - 当某个因子 IC 下降或误差扩大时，必须能够追溯到上游字段、时间窗口、事件排序、盘口重建、缺失填充、rolling warmup 或标准化参数。

5. **Order Book 重建正确**
   - 必须正确处理 Binance depth update 中的 `E`、`T`、`U`、`u`、`pu`；
   - 必须支持 REST snapshot 初始化、增量更新衔接、sequence continuity 检测、断线恢复和 REST snapshot 重同步；
   - 必须稳定生成 25 档盘口状态；
   - 不得使用未来数据对历史盘口进行 hindsight 修复。

6. **差异归因完整**
   - 必须明确区分可修复差异与不可修复差异；
   - 必须说明差异是否来自数据源定义、实时采集延迟、丢包、depth 重建错误、quote 生成逻辑、derivative ticker 拼接逻辑、10 秒窗口边界、ffill / bfill、rolling warmup 或标准化参数；
   - 对声称“天然不可对齐”的差异，必须提供实验依据和误差量级，不接受仅凭主观判断。

## 原始行情与因子一致性评测指标

| 数据/因子层 | 评测对象 | 主要指标 |
|---|---|---|
| trades | trade price、amount、side、trade count、VWAP、volume | IC、缺失率、重复率、方向一致率、成交量误差、VWAP 误差 |
| quotes | bid、ask、bidsize、asksize、spread、mid、top-of-book update count | IC、MAE、RMSE、spread error、更新次数差异 |
| book_snapshot_25 | 前 25 档 bid / ask price、amount、depth imbalance、weighted price | IC、档位价格误差、档位数量误差、imbalance error |
| derivative_ticker | mark price、index price、funding rate、funding timestamp、open interest、last price | IC、更新时间差异、数值误差、缺失率 |
| 10 秒级因子 | OHLC、TWAP、VWAP、AWAP、rolling mean / sum / std、zscore / rank / minmax | IC、MAE、RMSE、方向一致率、分布差异、连续五日达标比例 |

## 无效提交认定

以下情况可判定为无效提交或未通过等级认证：

- 无法运行、无法复现或缺少核心代码；
- 仅提交文字方案、PPT、截图或无法验证的结论；
- 未覆盖 BTCUSDT、ETHUSDT、BNBUSDT、DOTUSDT 四个合约；
- 未覆盖 `trades`、`quotes`、`book_snapshot_25`、`derivative_ticker` 四类核心数据；
- 未展示一致性提升前后对比；
- 使用未来数据、未来 sequence 或 hindsight 方式修复历史结果；
- 未能输出逐日、逐合约、逐特征 IC correlation 结果；
- 无法解释主要剩余差异来源。

---

[← Back to Challenge Board](../README.md) ｜ [返回挑战列表](../README.zh-CN.md)
