# docs 入口

## 文件目的與範圍

這份文件是 `docs/` 的入口與導覽層。

目前目標是提供最小可行的 docs information architecture，讓讀者知道：

- 先讀哪一份文件
- 不同主題應該去哪裡找
- 哪份文件對哪個主題具有 authority
- 既有文件彼此是什麼層次與關係

這份文件不負責重述各主題正文，也不重開已經固定的核心語意。

## 建議讀序

建議先讀：

1. `README.md`
2. `docs/architecture.md`

之後依需求往下讀：

- 若要確認 settings 的 phase-bound policy，讀 `docs/settings-policy.md`
- 若要確認 core abstractions 的 boundary contract，讀 `docs/specs/core-abstractions-boundary.md`
- 若要確認特定狹義邊界，從 `docs/specs/core-abstractions-boundary.md` 再進到對應 spec

## Authoritative Map

- `README.md`
  authoritative for repo entry summary、目前 phase、核心詞彙摘要與文件入口。
- `docs/architecture.md`
  authoritative for shared vocabulary、canonical input、高層責任邊界與 initialization 階段的概念 flow。
- `docs/settings-policy.md`
  authoritative for settings policy boundary 與其 deferred items。
- `docs/specs/core-abstractions-boundary.md`
  authoritative for 目前 core boundary specs 的入口、閱讀順序與依賴方向摘要。
- `docs/specs/*.md`
  authoritative for 各自命名的 narrow boundary contract，例如 canonical input、orchestrator、model side、response cache。

## 文件層次與關係

- `README.md` 是 repo 第一讀，負責專案級摘要。
- `docs/README.md` 是 docs 導覽層，負責讀序、地圖、authority map 與關係說明。
- `docs/architecture.md` 是共享語彙與高層邊界層。
- `docs/settings-policy.md` 是特定主題的 policy / decision note。
- `docs/specs/` 是 boundary-specific contract 區。

`docs/specs/*.md` 的角色是細化 `docs/architecture.md` 已固定的高層語意與依賴方向，不是另起一套語意，也不是覆寫 architecture 的核心定義。

`docs/settings-policy.md` 與 `docs/specs/` 是平行主題：前者固定 settings 邊界，後者固定各狹義 boundary contract，兩者不互相吞併。

## 目前 Coverage 與刻意不納入的類型

目前這組最小可行 docs 結構已涵蓋：

- repo overview
- architecture overview
- settings policy boundary
- core boundary specs

目前刻意不引入以下文件類型：

- `interfaces/`
- `flows/`
- `state-machines/`
- `implementation-notes/`

這代表目前 docs 結構是刻意收斂在 initialization 階段需要的資訊架構，而不是遺漏這些類型。

## 新增或修改文件時的放置規則

- 共享語彙、跨邊界責任與高層概念 flow，放在 `docs/architecture.md`
- settings policy 與其 deferred boundary，放在 `docs/settings-policy.md`
- 狹義 boundary 的細部 contract，放在 `docs/specs/`
- `docs/README.md` 只在 docs 拓樸、讀序、authority map 或文件層次關係改變時更新

目前 `docs/` 的實際結構仍可視為暫時參考，但已足以承接最小可行的 docs information architecture。

這一輪不需要新增 `docs/specs/README.md`；`docs/README.md` 已承擔整體入口，而 `docs/specs/core-abstractions-boundary.md` 已足夠作為 specs 內部入口。
