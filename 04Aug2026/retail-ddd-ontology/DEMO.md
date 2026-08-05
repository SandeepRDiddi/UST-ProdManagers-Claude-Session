# DEMO.md — Product Manager Walkthrough: Domain-Driven Design

**Audience:** Product managers. Nobody in the room writes or reads code. Everything happens by
clicking around a working app in a browser. Your job after this session isn't to build any of
this — it's to recognize **Domain-Driven Design (DDD)**'s actual building blocks when they show
up in a spec, a design review, or a conversation with your engineering team, and to know the
right question to ask.

**What you'll see:** a small online store (products, cart, checkout, order history) plus an
"Ontology" tab. `http://localhost:5173`. ~45 minutes.

---

## What "Domain-Driven Design" actually means

Before any demo — the one sentence to remember: **DDD is the discipline of building software
using the exact words the business already uses, and structuring the code around those words'
real-world rules — instead of translating your language into generic technical plumbing.**

DDD gives that discipline a specific vocabulary. By the end of this session you'll have met all
of it, live, in this app: **Ubiquitous Language, Entity, Value Object, Aggregate, Bounded
Context, Domain Event, Domain Service, Repository.** Every one of those words is something you'll
hear in an engineering design review. Right now they're probably noise to you. After this,
they're a checklist you can use to ask sharper questions.

---

## Part 1 — Domain-Driven Design, one building block at a time (30 min)

### 1.1 Ubiquitous Language — the #1 rule of DDD, and the most useful one for you

Open the app's **Catalog** tab. You see "Products" grouped by "Category." Go to **Checkout** —
you see an "Order" made of "Order Lines," placed by a "Customer."

Now ask your instructor to open the code file `backend/app/domain/entities.py`. Point at the
class names: `Category`, `Product`, `Customer`, `InventoryItem`. Then `aggregates.py`: `Order`,
`OrderLine`.

**The point:** these are not generic technical names like `Item`, `Record`, `Entity4`, or
`widget_qty`. The class in the code is *literally called* `Product`, because that's what you call
it in a planning meeting. When you say "Order" in a spec and an engineer says "Order" in a code
review, you are pointing at the exact same concept — same word, same file, same shape. This is
called the **Ubiquitous Language**: one shared vocabulary, used identically by the business and
the code, with zero translation layer in between.

**Why this is the most important idea in this whole session:** translation layers are where bugs
and miscommunication hide. If your team calls it a "Customer" and the database calls it a
`UserAccount`, and a third system calls it a `Party`, someone eventually builds a feature against
the wrong assumption, and nobody notices until it's expensive. A codebase with strong Ubiquitous
Language stays readable by *you*, years later, without an engineer as translator.

**The question to ask in your next design review:** "Does this design use our language, or did
we just invent a new technical name for something we already have a word for?" If engineering
starts introducing terms you've never heard in a product meeting, stop and ask why.

### 1.2 Entities vs. Value Objects — two different ways "sameness" works

Open `backend/app/domain/value_objects.py` — the `Money` class. Then `entities.py` —
the `Product` class.

**Demo:** in the app, add the *same* headphones to your cart in two separate orders, on two
separate checkouts. Look at the two Order confirmations.

**What happens:** two different Order IDs, even though the contents are identical.

**The point, in DDD's own words:** `Order`, `Product`, and `Customer` are **Entities** — DDD's
term for "a thing with its own identity that we track over time, even if every attribute about it
is temporarily identical to another one." Order #1 and Order #2 are different orders forever,
because each has its own ID and its own history, regardless of what's inside them.

`Money` is a **Value Object** — DDD's term for "a thing defined entirely by its value, with no
identity of its own." $10 is $10; there's no "which $10" question to ask. Value Objects are also
where business rules about *individual pieces of data* live — `Money` refuses to be negative, a
`SKU` refuses to be malformed, an `Email` refuses to be an invalid address — so those rules are
enforced once, at the source, not re-checked on every screen that happens to touch a price.

**Why this matters to you:** when you're deciding whether something in your spec is "a thing we
track over time" (Entity — needs an ID, a history, maybe a status) versus "just a value" (Value
Object — needs validation rules, not a lifecycle), you're doing real domain modeling. Get this
wrong in a spec and engineering either over-builds tracking for something that didn't need it, or
under-builds it for something that did.

### 1.3 Aggregates and the Aggregate Root — where the business rules actually live

Open `aggregates.py` — the `Order` class. Read the module comment at the top of the file: *"the
transactional consistency boundary for placing an order."*

**Demo:** in **Checkout**, try to place an order with zero items — you can't get there. Place a
real order, then go to **Order History** and try to add another item to it after the fact — you
can't.

**The point, in DDD's own words:** `Order` is the **Aggregate Root** for the Ordering
**Aggregate** — DDD's term for "the one object you're required to go through to safely change a
cluster of related data." `OrderLine`s cannot be created, added, or changed except through
`Order`'s own methods — and those methods are exactly where the business rules live: "an order
must have at least one line," "you cannot modify an order once it's placed." Nobody can add an
`OrderLine` from some other part of the codebase and accidentally bypass those rules, because the
`OrderLine` doesn't let you in except through the root.

**Why this matters to you:** "Aggregate" is DDD's answer to "where does this business rule live,
and can anyone accidentally get around it?" When you write an acceptance criterion like "an order
can't be placed empty," you're describing an Aggregate invariant. The right engineering answer is
"that rule lives in the `Order` aggregate — it's enforced everywhere, structurally, not checked
per-screen." If the answer is "we check that in the checkout button's onClick handler," that rule
is one bypass away from breaking somewhere else — a bulk import, an internal tool, a future
mobile app.

### 1.4 Bounded Contexts — why "just add a field to Product" isn't always simple

Open three files side by side and read their opening comments: `entities.py` (`InventoryItem`
is "Aggregate root of the **Inventory bounded context**"), `aggregates.py` (`Order` is "Aggregate
root for the **Ordering bounded context**"), and `application/order_service.py` (coordinates a use
case "across the **Ordering and Inventory bounded contexts**").

**The point:** this one small app already has three separate zones of ownership — **Catalog**
(what can be sold), **Inventory** (how much is in stock), **Ordering** (what a customer bought).
DDD calls each of these a **Bounded Context**: a boundary inside which a word means exactly one
precise thing, and outside of which that same word might mean something a little different. "A
Product" in the Catalog context is a name, description, and price for marketing and browsing. "A
Product" in a Shipping context (which this app doesn't have, but a real retailer would) might mean
a weight, dimensions, and a hazmat flag. Same English word, two different models — on purpose.

**Why this matters to you — this is the concept behind the friction you've already felt:** when
another team asks "can we just add a field to Product," and your engineering team pushes back
harder than the request seems to deserve, this is usually why. The `Product` *they* mean might
live in a different Bounded Context than the `Product` *you* mean, and DDD's advice is: don't
force one giant shared model to serve every team's needs — give each context its own model, and
translate deliberately at the boundary between them. A request that sounds like "just one field"
can actually be "please blur the boundary between two contexts that were kept separate on
purpose." That's worth understanding before you promise a date.

### 1.5 Domain Services — rules that don't belong to just one thing

Open `backend/app/domain/services.py` — the `InventoryService` class.

**Demo:** add the Espresso Machine (only 4 in stock) to your cart with quantity 500, and place the
order. Read the exact rejection message and where the "available" number comes from.

**The point:** "check whether there's enough stock, and reserve it" isn't really `Product`'s job
or `InventoryItem`'s job alone — it's coordination between the two, plus the outside world (the
requested quantity). DDD calls this a **Domain Service**: business logic that's real and
important, but doesn't naturally belong to one single Entity or Value Object, because it
coordinates across several.

**Why this matters to you:** when a rule genuinely spans two things you'd model separately (stock
level and a purchase request; a discount rule and an order total), that's a sign it belongs in its
own named piece, not awkwardly bolted onto one side. If you ever see business logic duplicated in
two different features because "it kind of belongs to both," that's usually a missing Domain
Service.

### 1.6 Domain Events — the system remembering what happened

Open `backend/app/domain/events.py`.

**The point:** every time something significant happens — an order gets placed, stock gets
reserved, an order gets cancelled — DDD says: don't just quietly update a status field. Record the
fact itself, named in past tense (`OrderPlaced`, `OrderCancelled`, `StockReserved`), as a
first-class thing the rest of the system can react to later.

**Why this matters to you:** every "send a confirmation email when X happens," "show me an
activity log," or "give me analytics on how often Y occurs" request you've ever made is, under the
hood, a request to *react to a Domain Event*. If your engineering team already models these
events, those features tend to be cheap add-ons. If they don't, each request becomes its own
mini rebuild of "how do we even know when this happened." Worth asking, during scoping: "are we
recording this as an event, so the notification/log/analytics feature is cheap to bolt on later?"

### 1.7 Repository — the business rules don't need to know where the data lives

Open `backend/app/domain/repositories.py` (just the interface, no implementation), then
`backend/app/infrastructure/` — point out there are *two* different real implementations sitting
there, one backed by a plain file, one that could be swapped for a production database, and the
`Order`/`Product` rules from 1.2-1.3 don't change one line either way.

**The point:** DDD calls this a **Repository** — a deliberately boring interface ("give me a
Product by ID," "save this Order") that hides *where and how* data is actually stored, so the
business rules never have to know or care.

**Why this matters to you:** this is why a "simple" infrastructure change — a new database, a new
cloud provider, adding a cache — sometimes takes a week, and sometimes takes a quarter, in ways
that seem to have nothing to do with the actual technical complexity. If the Repository pattern is
in place, swapping storage is close to mechanical. If it isn't, the business rules and the storage
code are tangled together, and *that* tangle — not the database migration itself — is what eats
the quarter. Fair question for a roadmap conversation: "is this actually a database problem, or
is it a 'the rules and the storage were never separated' problem?"

---

## Part 2 — The other half: what things mean, not just how they behave (15 min)

Everything in Part 1 was about **behavior** — rules, sequences, what's allowed. There's a second,
equally real question DDD deliberately does *not* try to answer on its own: **what do these
concepts mean, and how do they relate to each other, independent of any one feature's code?**
That's what the **Ontology** tab is for.

### 2.1 The problem Ubiquitous Language alone doesn't solve

Bounded Contexts (1.4) intentionally let each team have its *own* precise model. That's great for
avoiding one giant tangled `Product` object — but it creates a new problem: if Catalog, Inventory,
and a future Recommendations feature each have their own idea of what a "Category" is, how does
anyone answer a question that spans all of them — like "show me everything in Electronics,
including Laptops and Headphones, which are subcategories of it"?

**Demo:** click the **Ontology** tab. You'll see a graph — boxes (`Product`, `Category`,
`Customer`, `Order`...) connected by labeled arrows (`belongsToCategory`, `placedBy`,
`contains`...). Ask your instructor to run the "everything in Electronics, including
subcategories" query live.

**The point:** this graph is a single, explicit, shared map of how concepts relate — sitting
*alongside* the DDD model from Part 1, not replacing it. Each Bounded Context still owns its own
detailed rules; this is the lightweight shared vocabulary that lets you ask cross-cutting
questions without every feature re-guessing the relationships from scratch. This is the same idea
behind a **product taxonomy**, a **content tag hierarchy**, or a **knowledge graph** — words
you'll hear in search, recommendations, and "AI assistant that understands our catalog"
conversations.

**Why this matters to you:** if your roadmap includes smarter search, filters, recommendations, or
an AI feature over your own data, ask: "do we already have an explicit shared map like this, or
are we building it as part of this feature?" That answer changes the estimate a lot — and it's a
fair thing to want to know before you commit a date externally.

---

## Part 3 — The DDD glossary (keep this page)

| Term | Plain meaning | Where you saw it |
|---|---|---|
| **Ubiquitous Language** | One shared vocabulary, used identically by the business and the code — no translation layer. | Class names matching your spec's words exactly (1.1) |
| **Entity** | A thing with its own identity, tracked over time, even when its attributes are identical to another one. | `Order`, `Product`, `Customer` — two Orders are never "the same order" (1.2) |
| **Value Object** | A thing defined entirely by its value, no identity, validates itself so it can't exist in a broken state. | `Money` refuses to be negative (1.2) |
| **Aggregate / Aggregate Root** | The one object you must go through to safely change a cluster of related data — where the real business rules live. | `Order` won't let you add an item once placed (1.3) |
| **Bounded Context** | A boundary inside which a word means one precise thing — the same word can mean something different in another context, on purpose. | Catalog / Inventory / Ordering, each with its own model (1.4) |
| **Domain Service** | Business logic that coordinates across more than one Entity/Value Object, so it doesn't naturally belong to just one. | `InventoryService` checking and reserving stock (1.5) |
| **Domain Event** | A recorded fact that something happened, separate from just updating a status field. | `OrderPlaced`, `OrderCancelled` (1.6) |
| **Repository** | A deliberately boring interface that hides where/how data is stored, so business rules never depend on it. | Two swappable storage implementations, zero rule changes (1.7) |
| **Taxonomy / Ontology / Knowledge Graph** | An explicit, shared map of what things are and how they relate, usable across every feature instead of re-derived by each one. | The Ontology tab (2.1) |

---

## Closing discussion prompts (5 min)

Pick 2-3 for group discussion:

- Think of a bug or incident from a past project. Was it a missing **Aggregate rule** (something
  bypassed a check that should have been structural) or a missing **Bounded Context boundary**
  (two teams silently disagreed about what a shared word meant)? Which, and what would you have
  asked for differently in the spec?
- Has another team ever asked you to "just add a field" to something core to your product, and it
  turned into a much bigger conversation than expected? Revisit it through the **Bounded Context**
  lens (1.4) — does it look different now?
- If your roadmap has a search, filter, personalization, or AI feature on it: ask your engineering
  team whether an explicit shared map (**taxonomy/ontology**, Part 2) already exists for that data,
  or whether this feature is the first thing that will have to build one.
