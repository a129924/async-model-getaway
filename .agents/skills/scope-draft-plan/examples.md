# Scope Draft Plan examples

Use these examples after `SKILL.md` has identified scope convergence as the
task. They illustrate the decision boundary, not a required domain model.

## Positive: merge technical slices into one Mission

**Starting request**

> 先建立 `OrderRepository`，再做 DTO、資料表、service、API 和 tests。

**Recommended Mission**

> 支援登入使用者建立基本訂單，保存建立當下必要的訂單快照，並取得可供後續流程使用的訂單識別碼。

**Why this is correct**

- The user can observe a completed order-creation outcome.
- Repository, schema, service, API, and tests are necessary technical tasks in
  one Mission, not five SDD projects.
- Payment, cancellation, refund, shipment, returns, and notifications remain
  follow-up capabilities.

## Positive: reduce an oversized lifecycle

**Starting request**

> 完成訂單系統：建立、付款、取消、退款、出貨、退貨和通知。

**Recommended first Mission**

> 支援登入使用者建立基本訂單並取得訂單識別碼。

**Why this is correct**

- It provides a full primary flow with an observable persistent result.
- Each later lifecycle result has independent business value and can be a
  follow-up Mission.
- The Draft Plan should include only the essential failure path for creation,
  not a disguised implementation of later stages.

## Positive: respect cross-BC ownership

**Starting request**

> 讓客服取消已付款訂單，並立即退款和通知倉庫停止出貨。

**Recommended boundary**

> 支援客服在符合條件時取消已付款訂單，並記錄取消決定與需要對外發出的處理請求。

**Why this is correct**

- Order management is the primary BC for the cancellation decision.
- Payment refund and warehouse stop-shipment are named cross-BC contracts or
  dependent Missions unless their ownership and contract are already locked.
- If the cancellation policy or external contract changes the outcome, it is a
  risk gate rather than an unexamined inclusion.

## Blocking ambiguity: ask, do not guess

**Starting request**

> 做一個訂單取消功能。

**Material questions**

1. 哪一種訂單狀態可取消，且誰擁有此規則？
2. 取消是否必須同步觸發退款，或只建立退款請求？
3. 取消決定是否會改變對外已承諾的 public contract？

These questions are justified only because their answers may change the
primary BC, ownership, or public contract. Do not ask for class names, table
names, or internal implementation preferences at this stage.

## Negative: technical task is not a Mission

**Wrong output**

> Mission：新增 `POST /orders`。

**Why it fails**

An endpoint is a delivery choice. It does not say which actor gains what
business capability, what result persists, or what acceptance behavior proves
completion.

## Negative: low-impact unknown should not block

**Starting request**

> 讓使用者查詢自己的訂單列表。

**Wrong response**

> 在確認 controller 名稱、pagination library 和 table index 前無法切 scope。

**Why it fails**

Those details usually do not change the core capability. State a bounded
assumption if needed and keep them for later planning; ask only if an answer
would change ownership, public contract, or the observable outcome.
