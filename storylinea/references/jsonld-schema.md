# Context Studio JSON-LD Schema (01_context_studio/schema.jsonld)

The domain entity model uploaded as **Schema** into Context Studio (always
before the source documents). Same family as the `jsonld-ontology-generator`
skill — Entity / Operation / State members under `@graph` with a custom
namespace layered on schema.org — plus storylinEA-specific conventions below.

## Sizing rules

- **Entities per process:** complex → 4, moderate → 3, simple → 2.
- Entity names globally unique across processes.
- Prefer vendor-native entity names when a vendor was selected
  (e.g. SAP: `AP_VendorInvoice`, `MM_GoodsReceipt`, `FI_PaymentRun`;
  Workday: `EC_EmploymentRecord`, `PY_PayrollResult`; Coupa: `CoupaSupplier`;
  Ariba: `AribaPurchaseOrder`; ServiceNow: `Incident`, `ServiceRequest`,
  `Change`; Salesforce: `Opportunity`, `Quote`, `Case`; Guidewire: `Claim`,
  `ClaimExposure`). Otherwise derive domain-appropriate PascalCase names;
  generic fallback: `ProcessRecord`, `ApprovalRequest`, `ExceptionTicket`.
- `relatesTo` per entity: cap 4 (multi-process: prefer 2 cross-process + 2
  same-process) or 3 (single process).
- One `CrossProcessLink` node per adjacent process pair (multi-process only).

## @context shape

```json
{
  "@context": {
    "{prefix}": "{namespaceUri}",
    "schema": "http://schema.org/",
    "id": "@id",
    "type": "@type",
    "name": "schema:name",
    "description": "schema:description",
    "attributes": "{prefix}:attributes",
    "identityKey": "{prefix}:identityKey",
    "humanRef": "{prefix}:humanRef",
    "invariant": "{prefix}:invariant",
    "precondition": "{prefix}:precondition",
    "postcondition": "{prefix}:postcondition",
    "sourceProcess": "{prefix}:sourceProcess",
    "targetProcess": "{prefix}:targetProcess",
    "emitsEvent": "{prefix}:emitsEvent",
    "hasState": { "@id": "{prefix}:hasState", "@type": "@id" },
    "initialState": { "@id": "{prefix}:initialState", "@type": "@id" },
    "terminalStates": { "@id": "{prefix}:terminalStates", "@type": "@id" },
    "relatesTo": { "@id": "{prefix}:relatesTo", "@type": "@id" },
    "from": { "@id": "{prefix}:from", "@type": "@id" },
    "to": { "@id": "{prefix}:to", "@type": "@id" },
    "Entity": "{prefix}:Entity",
    "Operation": "{prefix}:Operation",
    "State": "{prefix}:State",
    "CrossProcessLink": "{prefix}:CrossProcessLink"
  },
  "@graph": [ ... ]
}
```

Pick a short industry namespace prefix (e.g. `fin`, `ins`, `mfg`) and a URI like
`https://{company-slug}.example.com/ontology#`.

Two things to get right here:
- **Keep the colon.** Context values are CURIEs — `"rwk:attributes"`, not
  `"rwkattributes"`. (The original app emitted them without the colon, which
  does not resolve against the namespace; don't reproduce that bug.)
- **`emitsEvent` is a plain string term, not a link.** Event names like
  `ClaimApproved` are labels describing what the transition publishes; they are
  not nodes in the graph. Only `hasState`, `initialState`, `terminalStates`,
  `relatesTo`, `from` and `to` are `@id`-typed, and every value of those six
  must resolve to a node.

## Node types in @graph

**Entity** (one per entity):
```json
{
  "id": "{prefix}:AP_VendorInvoice",
  "type": "Entity",
  "name": "AP_VendorInvoice",
  "description": "A vendor invoice record managed within the Accounts payable process. Tracks the full lifecycle from initiation through completion, including all state transitions, approvals, exceptions, and audit trail.",
  "identityKey": "apVendorInvoiceId: UUID",
  "humanRef": "APV-XXXXXX",
  "attributes": { "referenceCode": "string", "status": "string",
    "createdDate": "date", "lastModifiedDate": "date", "createdBy": "string",
    "version": "number", "invoiceNumber": "string", "vendorId": "string",
    "invoiceDate": "date", "dueDate": "date", "totalAmount": "number",
    "currency": "string",
    "paymentStatus": "UNPAID|PARTIALLY_PAID|PAID|DISPUTED|OVERDUE" },
  "invariant": [
    "AP_VendorInvoice must have a valid reference code before any state transition",
    "AP_VendorInvoice must be in a valid state at all times",
    "AP_VendorInvoice status must align with the current lifecycle state",
    "Completed or rejected vendor invoice records must not be modified"
  ],
  "hasState": ["{prefix}:AP_VendorInvoiceReceived", "..."],
  "initialState": "{prefix}:AP_VendorInvoiceReceived",
  "terminalStates": ["{prefix}:AP_VendorInvoicePaid"],
  "relatesTo": ["{prefix}:MM_GoodsReceipt", "..."],
  "emitsEvent": ["{prefix}:AP_VendorInvoiceCreated", "{prefix}:AP_VendorInvoiceSubmitted",
    "{prefix}:AP_VendorInvoiceApproved", "{prefix}:AP_VendorInvoiceRejected",
    "{prefix}:AP_VendorInvoiceCompleted"]
}
```

Attribute rules: always include the 6 base attributes (`referenceCode, status,
createdDate, lastModifiedDate, createdBy, version`), then 5–8 domain-specific
ones. Permitted types are `string`, `number`, `boolean`, `date`, pipe-delimited
enums (`"HIGH|MEDIUM|LOW"`), nullable variants (`"date|null"`), and arrays
(`"string[]"`, `"LineItem[]"`).

State machine: model a **linear chain** — `[initial, 3–5 middle states, one
terminal]` in `hasState`, giving one Operation per consecutive pair. Because
Operations are built from adjacency, `terminalStates` lists exactly the
terminal state(s) you actually created as nodes; if you want alternative
outcomes such as Rejected or Cancelled, add them as State nodes *and* give each
its own Operation from the state it branches off, otherwise leave them out.
Domain-plausible examples —
invoice: Received → Validated → MatchedToPO → PendingApproval → Approved →
ScheduledForPayment → Paid/Rejected/Cancelled; vendor: Pending → UnderReview →
DocumentsVerified → BankDetailsConfirmed → Active/Rejected/Suspended; claim:
Filed → UnderAssessment → PendingDocuments → Approved → Settled/Declined/Withdrawn;
generic: Draft → UnderReview → Approved → Processing → Completed/Rejected/Cancelled.

**State** (one per state per entity):
```json
{ "id": "{prefix}:AP_VendorInvoiceReceived", "type": "State",
  "name": "AP_VendorInvoice — Received",
  "description": "The vendor invoice is in the received state" }
```
State IDs concatenate entity+state with **no separator** (`…InvoiceReceived`,
not `…Invoice_Received`).

**Operation** (one per consecutive state pair — `states.length - 1` per entity):
```json
{ "id": "{prefix}:AP_VendorInvoiceReceivedToValidated", "type": "Operation",
  "name": "AP_VendorInvoice: Received → Validated",
  "description": "Transition the vendor invoice from received to validated",
  "from": "{prefix}:AP_VendorInvoiceReceived",
  "to": "{prefix}:AP_VendorInvoiceValidated",
  "precondition": [
    "AP_VendorInvoice must be in the Received state",
    "Performing user must have the required role and authority",
    "All required fields must be populated" ],
  "postcondition": [
    "AP_VendorInvoice is now in the Validated state",
    "Transition is recorded in the audit log with timestamp and user identity",
    "Relevant parties are notified of the state change" ],
  "emitsEvent": ["{prefix}:AP_VendorInvoiceValidated"] }
```

**CrossProcessLink** (multi-process only, one per adjacent pair):
```json
{ "id": "{prefix}:CrossProcess_1", "type": "CrossProcessLink",
  "name": "Accounts payable → Payment run execution",
  "description": "Handoff between Accounts payable and Payment run execution at {Company}.",
  "sourceProcess": "Accounts payable", "targetProcess": "Payment run execution" }
```

## Formatting

Serialize with 2-space indent, UTF-8 without BOM. Order `@graph` by entity —
each Entity followed by its own States then its Operations — with any
CrossProcessLink nodes last.

`identityKey` = `{camelName}Id: UUID`. `humanRef` = an **exactly 3-character**
uppercase stem + `-XXXXXX`: take the name's capitals (`AP_VendorInvoice` →
`APV`), and when there are fewer than three, pad from the following letters
(`Claim` → `CLM`, `PolicyRecord` → `PLR`). Stems must be unique across
entities — bump a letter if two collide.

Before writing, check that the file parses as JSON and that every value of the
six `@id`-typed fields resolves to a node in the graph. Write a throwaway
script for this rather than eyeballing it; a dangling reference is the failure
mode this format hides best.
