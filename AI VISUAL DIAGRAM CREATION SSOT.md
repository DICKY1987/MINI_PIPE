

# **AI VISUAL DIAGRAM CREATION SSOT**

**Deterministic Diagram Standards for draw.io**

---

## **Document Metadata**

doc\_id: DOC-SSOT-DIAGRAM-STANDARDS-001  
title: AI Visual Diagram Creation SSOT  
version: 1.0.0  
status: active  
doc\_type: visualization\_ssot  
target\_tool: draw.io (diagrams.net)  
preferred\_flow\_direction: LEFT\_TO\_RIGHT  
authoritative\_scope: ALL AI-GENERATED VISUAL DIAGRAMS

---

## **Table of Contents**

1. [Purpose & Authority](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#1-purpose--authority)  
2. [Core Principles](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#2-core-principles)  
3. [Flow Direction Standard (Horizontal)](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#3-flow-direction-standard-horizontal)  
4. [Diagram Structure & Logic Rules](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#4-diagram-structure--logic-rules)  
5. [Shape Ontology (Semantic Meaning)](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#5-shape-ontology-semantic-meaning)  
6. [Text & Labeling Standards](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#6-text--labeling-standards)  
7. [Data Transfer & I/O Contracts](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#7-data-transfer--io-contracts)  
8. [Stable ID System & Registry Usage](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#8-stable-id-system--registry-usage)  
9. [Layer Model (Mandatory)](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#9-layer-model-mandatory)  
10. [Layout & Geometry Rules](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#10-layout--geometry-rules)  
11. [Containers, Pages, and Hierarchy](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#11-containers-pages-and-hierarchy)  
12. [Metadata, Links, and Traceability](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#12-metadata-links-and-traceability)  
13. [Legend, Header, and Diagram Grammar](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#13-legend-header-and-diagram-grammar)  
14. [Validation Checklist (AI-Enforced)](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#14-validation-checklist-ai-enforced)  
15. [End-to-End Correct Example](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#15-end-to-end-correct-example)  
16. [Non-Goals](https://chatgpt.com/c/693d17cf-f6a0-8329-a4c0-5ba6d947065b#16-non-goals)

---

## **1\. Purpose & Authority**

This document defines the **only approved structure, rules, and standards** for AI-generated diagrams.

If any other instruction, prompt, or diagram conflicts with this document, **this document wins**.

---

## **2\. Core Principles**

1. **Determinism over aesthetics**  
2. **No implied logic**  
3. **Everything must be explicit**  
4. **One meaning per construct**  
5. **Machine-recoverable structure**  
6. **Stable IDs everywhere**  
7. **Horizontal flow by default**

---

## **3\. Flow Direction Standard (Horizontal)**

### **3.1 Global Rule**

All diagrams MUST flow:

LEFT → RIGHT

Vertical or mixed flows are forbidden unless explicitly overridden (rare).

### **3.2 Why**

* Improves AI traversal  
* Matches execution pipelines  
* Reduces ambiguous “top/bottom” interpretation  
* Aligns with system orchestration mental models

---

## **4\. Diagram Structure & Logic Rules**

### **4.1 Start & End**

* Exactly **one START**  
* One or more **END**  
* Shape: **Oval**  
* Labels: `START`, `END`

### **4.2 Connectivity**

* Every node MUST be connected  
* No proximity-based meaning  
* Directional arrows required

### **4.3 Decisions**

* Shape: **Diamond**  
* Text: **Question**  
* Outgoing edges:  
  * Labeled  
  * Mutually exclusive

✅ Correct:

Is User Authenticated?  
 ├─ Yes  
 └─ No

---

## **5\. Shape Ontology (Semantic Meaning)**

| Shape | Meaning | Forbidden Usage |
| ----- | ----- | ----- |
| Oval | START / END | Status, notes |
| Rectangle | Action / Process | Decisions |
| Diamond | Decision | Actions |
| Parallelogram | Input / Output | Logic |
| Document | File / Artifact | Flow |
| Cylinder | Persistent State | Temp data |

**Never overload shapes.**

---

## **6\. Text & Labeling Standards**

### **6.1 Actions**

* Verb \+ Noun  
* One action per node

✅ `Validate Credentials`  
❌ `Credential Validation`

### **6.2 Decisions**

* Question form only

✅ `Is Order Approved?`  
❌ `Order Approved`

### **6.3 Edges**

* All decision edges labeled  
* No blank arrows

---

## **7\. Data Transfer & I/O Contracts**

### **7.1 Terminology**

* Arrow \= **Control Flow**  
* Edge label \= **Data Flow**  
* Data flow is treated as an **I/O Contract**

### **7.2 Labeling Standard (Mandatory)**

IO:\<IO\_ID\> | \<PayloadType\>

### **7.3 Example**

Validate Credentials ──▶ Create Session  
Edge Label:  
IO:IO-AUTH-001 | Credentials

### **7.4 Decision \+ Contract**

Yes | IO:IO-AUTH-OK-001 | SessionToken  
No  | IO:IO-AUTH-FAIL-001 | AuthError

---

## **8\. Stable ID System & Registry Usage**

### **8.1 Single Registry Rule**

There MUST be **one global ID registry**, extended via namespaces.

### **8.2 Required Namespaces**

| Prefix | Used For |
| ----- | ----- |
| DIAG-\* | Diagram artifact |
| NODE-\* | Diagram node |
| EDGE-\* | Diagram edge |
| IO-\* | I/O contract |
| LANE-\* | Swimlane |
| COMP-\* | Real system component |

### **8.3 Dual-ID Pattern (Recommended)**

* **Semantic ID** (what it represents)  
* **Diagram Object ID** (diagram instance)

Example (node):

COMP-AUTH-001 | Validate Credentials  
Metadata:  
node\_id \= NODE-DIAG-AUTHFLOW-004

---

## **9\. Layer Model (Mandatory)**

Layers are **semantic dimensions**, not decoration.

### **9.1 Canonical Layer Stack**

L0\_FRAME\_METADATA  
L1\_CONTROL\_FLOW  
L2\_DATA\_FLOW\_IO  
L3\_STATE\_PERSISTENCE  
L4\_ERROR\_PATHS  
L5\_ANNOTATIONS

### **9.2 Rules**

* Every object belongs to exactly one layer  
* Control logic exists ONLY in L1  
* Layers must be toggle-safe

---

## **10\. Layout & Geometry Rules**

* Grid ON  
* Snap ON  
* Uniform spacing  
* Orthogonal edges only (90°)  
* No diagonals  
* Ports used consistently (left \= input, right \= output)

---

## **11\. Containers, Pages, and Hierarchy**

### **11.1 Containers**

Use containers for:

* Phases  
* Subsystems  
* Bounded scopes

Rules:

* Container \= one semantic boundary  
* Collapsible allowed  
* Cross-container edges must be explicit

### **11.2 Pages**

Use multiple pages when:

* \~30 nodes  
* Multiple abstraction levels

Recommended pages:

* Overview  
* Control Flow  
* Data / Contracts  
* Error Handling

---

## **12\. Metadata, Links, and Traceability**

### **12.1 Custom Properties (Strongly Recommended)**

{  
  "node\_id": "NODE-...",  
  "ref\_id": "COMP-...",  
  "io\_contract": "IO-...",  
  "deterministic": true,  
  "tests": \["TST-001"\]  
}

### **12.2 Links**

Shapes SHOULD link to:

* Source code  
* Spec docs  
* Schema files

---

## **13\. Legend, Header, and Diagram Grammar**

### **13.1 Header Block (Required)**

Diagram Name:  
Diagram ID:  
Version:  
Flow Direction: LEFT\_TO\_RIGHT  
Generated By:

### **13.2 Legend (Required)**

Oval          \= Start / End  
Rectangle     \= Action  
Diamond       \= Decision  
Parallelogram \= Input / Output  
Cylinder      \= Database

---

## **14\. Validation Checklist (AI-Enforced)**

AI MUST verify:

* One START  
* All nodes connected  
* Horizontal flow only  
* All decisions labeled  
* One action per node  
* All nodes have IDs  
* All data flows labeled  
* Layers correctly used  
* No implied logic

---

## **15\. End-to-End Correct Example**

### **Nodes (L1\_CONTROL\_FLOW)**

START  
  ↓  
COMP-AUTH-001 | Validate Credentials  
  ↓  
DEC-AUTH-001 | Is Authentication Successful?

### **Edges (L2\_DATA\_FLOW\_IO)**

EDGE-001:  
Yes | IO:IO-AUTH-OK-001 | SessionToken

EDGE-002:  
No | IO:IO-AUTH-FAIL-001 | AuthError

### **State (L3\_STATE\_PERSISTENCE)**

STATE-SESSION-001 | Session Store

---

## **16\. Non-Goals**

This SSOT does NOT optimize for:

* Artistic layout  
* Minimal node count  
* Informal sketches  
* Human intuition shortcuts

---

### **END OF SSOT**

---

