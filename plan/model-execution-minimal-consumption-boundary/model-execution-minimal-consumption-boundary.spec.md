# model-execution-minimal-consumption-boundary Specification

## Acceptance Criteria

1. `async_model_gateway.model_runtime.model_execution` 只公開 `ModelExecution`；`model_runtime` umbrella與package root不re-export。
2. `ModelExecution`使用三個locked generic parameters、keyword-only async invoker constructor與exact async `execute()` signature。
3. 每次`execute()`只呼叫`_provider_runtime()`一次，並將相同runtime與invocation direct-await傳給invoker一次。
4. Invoker result、一般exception與`CancelledError`原樣傳播。
5. `ModelExecution`不建立provider adapter、dispatch、I/O、task、timeout、retry、cache或resource lifecycle。
6. `ModelExecution`是`_provider_runtime()`唯一production consumer；private handoff不改名、不公開。
7. Strict static fixture保留concrete`RuntimeT`、`InvocationT`與`ResultT`，且`ModelPool.acquire()`仍為`LoadedRuntimeModel[object]`。
8. Tests只使用static imports，不使用dynamic module loading。
9. Implement-plan不修改release-only paths；fresh RED、implementation review與code review在PR routing前完成。
10. Post-merge release docs只宣告最小`ModelExecution` boundary，並保留provider framework、loader I/O、orchestrator、remote execution、lifecycle、timeout與retry deferred。
11. Runtime version、`pyproject.toml`與`uv.lock`從`0.5.0`同步為`0.6.0`。
12. Release形成exact linear`M -> R -> E -> V`：`R.parent == M`、`E.parent == R`、`V.parent == E`，且`origin/dev == V`。
13. Lightweight`v0.6.0`從R建立，local/remote均解析到R，且E/V不得move、replace或retarget tag。
14. R只含Human release gate、README、四份declared docs及三個version/lock paths；E只含`release.yaml`；V只含`release-review.yaml`。
15. Reviewer只在`origin/dev == E`時author`release-review.yaml`及out-of-band blob OID；transport-only Implementer原樣commit/push形成V。
16. `released`只在V verdict為`approved`、remote review blob等於Reviewer OID、M/R/E/V topology成立且tag仍指R時成立。
17. `needs-rework` verdict仍須原樣transport形成V，之後停止且不得retag或標記released。
18. GitHub API確認`v0.6.0` GitHub Release為404，PyPI與TestPyPI`async-model-gateway/0.6.0` endpoints均為404，publication automation scan無match；不得延伸為其他registry的no-publication claim。

## Behavioral Scenarios

### Scenario 1: runtime與invocation原樣交給invoker

- **Given**: 一個`LoadedRuntimeModel[FakeRuntime]`、一個invocation object與相符typed async invoker。
- **When**: caller await `ModelExecution.execute(model, invocation)`。
- **Then**: invoker只被await一次，收到相同runtime與invocation object，result原樣回傳。

### Scenario 2: 一般失敗原樣傳播

- **Given**: injected invoker拋出sentinel exception。
- **When**: caller await `execute()`。
- **Then**: 相同exception object向caller傳播，沒有translation、wrapping或retry。

### Scenario 3: cancellation原樣傳播

- **Given**: injected invoker拋出`CancelledError` instance。
- **When**: caller await `execute()`。
- **Then**: 相同cancellation object向caller傳播，沒有shield、timeout translation或cleanup task。

### Scenario 4: execution seam保留靜態型別精度

- **Given**: `LoadedRuntimeModel[FakeRuntime]`、`FakeInvocation`、`FakeResult`與相符typed invoker。
- **When**: strict Pyright分析execution與pool acquisition。
- **Then**: execution保留三個concrete types，pool仍得到`LoadedRuntimeModel[object]`。

### Scenario 5: approved linear release

- **Given**: implementation已Human merge為M，fresh release-human-check已由Human author，且local/remote`v0.6.0`不存在。
- **When**: Release Implementer建立R、push lightweight tag、建立E；Reviewer在`origin/dev == E`author approved review及blob OID；transport-only Implementer原樣建立V。
- **Then**: `R.parent == M`、`E.parent == R`、`V.parent == E`、`origin/dev == V`、tag仍指R、remote review blob一致，topic可被triage為released。

### Scenario 6: release review需要回修

- **Given**: origin/dev已到E，但Reviewer發現docs、version、publication或chain blocker。
- **When**: Reviewer author verdict`needs-rework`與blob OID，transport-only Implementer原樣建立V。
- **Then**: repo-visible V保存verdict，release停止，不得retag、amend、force-push或標記released。

## Error / Edge Cases

- `ModelExecution`不新增runtime input validation；invocation接受與否由invoker決定。
- Invoker同步拋錯、awaitable執行時拋錯與`CancelledError`均不得被捕捉或轉譯。
- 不得使用`Any`、dynamic module loading、file-wide private suppression或未具名ignore。
- TypeVars不得由package root公開；umbrella/root不得新增`ModelExecution` export。
- `LoadedRuntimeModel`、`ModelPool`、model-artifact contracts與declared ReadOnly paths不得修改。
- Dedicated Pyright必須顯式分析fixture，避免zero-source false green。
- Tag collision、annotated tag、錯誤tag target、nonlinear parent、extra commit path或review blob mismatch均為blocking。
- Reviewer不得在`origin/dev != E`時author release review。
- Reviewer artifact不得自我內嵌blob OID；OID由Reviewer完成artifact後out-of-band提供，V trailer及remote tree必須驗證一致。
- Network failure或非404 response不得誤記為negative publication pass。
- Automation scan無match時的nonzero exit status必須記錄為預期語意，而非命令失敗。
- No-publication結論只限`v0.6.0` GitHub Release、PyPI及TestPyPI`0.6.0`。
