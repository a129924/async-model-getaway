# Python library-architecture examples

Use these examples after `SKILL.md` narrows the task to reusable library/package architecture.

## Pure library example

### Prefer

```text
src/reporting_lib/
├── core/
│   ├── contracts.py
│   └── errors.py
├── query/
│   ├── builder.py
│   └── analyzer.py
├── render/
│   ├── html.py
│   └── pdf.py
└── client.py
```

```py
# reporting_lib/core/contracts.py
class QueryPlan:
    ...


# reporting_lib/query/builder.py
from reporting_lib.core.contracts import QueryPlan


def build_query(...) -> QueryPlan:
    ...


# reporting_lib/render/html.py
from reporting_lib.core.contracts import QueryPlan


def render_html(plan: QueryPlan) -> str:
    ...


# reporting_lib/client.py
from reporting_lib.query.builder import build_query
from reporting_lib.render.html import render_html


class ReportClient:
    def render_report(self, ...) -> str:
        plan = build_query(...)
        return render_html(plan)
```

- `query/` and `render/` collaborate through the shared `QueryPlan` contract in `core`.
- `client.py` is the composition root that coordinates both themes.
- `core` stays side-effect-free and does not decide how rendering or query execution is orchestrated.

### Avoid

```py
# reporting_lib/render/html.py
from reporting_lib.query.builder import build_query


def render_html(...) -> str:
    plan = build_query(...)
    ...
```

- `render/` now imports `query/` directly.
- The cross-theme import hides orchestration inside a theme instead of keeping it at the facade/client.

## SDK-style package example

### Prefer

```text
src/cloud_sdk/
├── core/
│   ├── credentials.py
│   ├── paging.py
│   └── errors.py
├── storage/
│   ├── operations.py
│   └── rest_adapter.py
├── queues/
│   ├── operations.py
│   └── rest_adapter.py
└── client.py
```

```py
# cloud_sdk/client.py
from cloud_sdk.core.credentials import Credential
from cloud_sdk.queues.operations import QueueOperations
from cloud_sdk.storage.operations import StorageOperations


class CloudClient:
    def __init__(self, credential: Credential, transport: object) -> None:
        self.storage = StorageOperations(credential, transport)
        self.queues = QueueOperations(credential, transport)
```

- SDK-style packages often have multiple service themes that share credentials, paging, or base errors.
- Those cross-service contracts belong in `core`.
- The public client composes service themes without making one service package depend on another.

## Anti-pattern: cross-theme import

### Avoid

```py
# shop_sdk/orders/operations.py
from shop_sdk.catalog.models import PageCursor


def list_orders(cursor: PageCursor | None) -> None:
    ...
```

- `orders/` is now coupled to `catalog/` for a shared contract.
- The rule allows zero exceptions, even for small DTOs or helper types.

### Prefer

```py
# shop_sdk/core/paging.py
class PageCursor:
    ...


# shop_sdk/orders/operations.py
from shop_sdk.core.paging import PageCursor


def list_orders(cursor: PageCursor | None) -> None:
    ...
```

- The shared contract moved into `core`.
- Each theme depends inward instead of sideways.

## Anti-pattern: orchestration in `core`

### Avoid

```py
# shop_sdk/core/bootstrap.py
from shop_sdk.orders.rest_adapter import OrdersAdapter
from shop_sdk.payments.rest_adapter import PaymentsAdapter


def build_client(api_key: str) -> object:
    orders = OrdersAdapter(api_key)
    payments = PaymentsAdapter(api_key)
    return {"orders": orders, "payments": payments}
```

- `core` is now doing package bootstrap and adapter wiring.
- This turns the shared contract center into an outward orchestrator.

### Prefer

```py
# shop_sdk/client.py
from shop_sdk.orders.rest_adapter import OrdersAdapter
from shop_sdk.payments.rest_adapter import PaymentsAdapter


class ShopClient:
    def __init__(self, api_key: str) -> None:
        self.orders = OrdersAdapter(api_key)
        self.payments = PaymentsAdapter(api_key)
```

- The facade/client is the composition root.
- `core` remains available for shared contracts such as credentials, paging, or base errors.

## Migration/refactor example

### Before

```text
src/commerce_sdk/
├── common/
│   ├── auth.py
│   └── helpers.py
├── users/
│   └── api.py
├── invoices/
│   └── api.py
└── client.py
```

```py
# commerce_sdk/invoices/api.py
from commerce_sdk.common.auth import refresh_token
from commerce_sdk.users.api import get_user_region


def create_invoice(...) -> None:
    token = refresh_token(...)
    region = get_user_region(...)
    ...
```

- `common/` is a grab bag, not a real shared contract center.
- `invoices/` imports `users/` directly, and orchestration leaks into a theme.

### After

```text
src/commerce_sdk/
├── core/
│   ├── auth_contracts.py
│   ├── region.py
│   └── errors.py
├── users/
│   ├── api.py
│   └── rest_adapter.py
├── invoices/
│   ├── api.py
│   └── rest_adapter.py
└── client.py
```

```py
# commerce_sdk/client.py
from commerce_sdk.invoices.api import InvoicesApi
from commerce_sdk.users.api import UsersApi


class CommerceClient:
    def __init__(self, auth_session: object) -> None:
        self.users = UsersApi(auth_session)
        self.invoices = InvoicesApi(auth_session)
```

Refactor steps:

1. List every peer import between themes.
2. Promote truly shared contracts, semantic primitives, and shared base errors into `core`.
3. Move transport setup, auth refresh, and cross-theme flow orchestration into the facade/client or a dedicated adapter owned by that flow.
4. Leave duplication local when it is still theme-specific instead of rebuilding `common/` under a new name.
5. Keep one primary facade/client; if a bounded secondary entry point remains, keep it orchestration-only.
