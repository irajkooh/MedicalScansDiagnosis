# AI Agent Tutorial Ideas

A comprehensive list of tutorial propositions showcasing multi-agent systems in real-world projects.

---

## Overview

Each tutorial is designed to teach specific multi-agent patterns while solving practical problems developers face. Tutorials are categorized by domain and tagged with the architectural patterns they demonstrate.

### Pattern Legend

| Pattern | Description |
|---------|-------------|
| **Hub-Spoke** | Central router distributes to specialists |
| **Sequential** | Linear pipeline, each agent hands to next |
| **Parallel** | Multiple agents work simultaneously, results merged |
| **Hierarchical** | Manager agents delegate to worker agents |
| **Loop** | Validation/retry cycles until condition met |
| **Escalation** | Severity-based routing with human fallback |

---

## Developer Tools (1-5)

### 1. Code Review Bot

**Pattern**: Parallel + Aggregator

**Architecture**:
```
                    ┌─────────────┐
                    │  Dispatcher │
                    └──────┬──────┘
           ┌───────────┬───┴───┬───────────┐
           ▼           ▼       ▼           ▼
      ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
      │Security│ │ Style  │ │  Perf  │ │ Tests  │
      └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘
           └───────────┴───┬───┴───────────┘
                           ▼
                    ┌─────────────┐
                    │ Aggregator  │
                    └─────────────┘
```

**Agents**:
- Dispatcher: Parses PR, routes files to specialists
- Security Agent: OWASP checks, secret detection, dependency vulnerabilities
- Style Agent: Linting, naming conventions, code formatting
- Performance Agent: Complexity analysis, N+1 queries, memory leaks
- Test Agent: Coverage analysis, test quality, missing edge cases
- Aggregator: Combines feedback, resolves conflicts, generates summary

**Learning Outcomes**:
- Parallel agent execution
- Merging conflicting outputs
- GitHub API integration
- Different models for different tasks (fast for style, smart for security)

**Tools**: GitHub API, AST parsers, linters, coverage tools

---

### 2. Git Commit Message Generator

**Pattern**: Sequential

**Architecture**:
```
Diff Analyzer → Intent Classifier → Message Drafter → Validator
```

**Agents**:
- Diff Analyzer: Parses git diff, identifies changed components
- Intent Classifier: Determines commit type (feat, fix, refactor, docs)
- Message Drafter: Generates conventional commit message
- Validator: Checks format, length, accuracy against diff

**Learning Outcomes**:
- Simple sequential pipelines
- Validation loops
- Git integration

**Tools**: Git CLI, diff parsers

---

### 3. Documentation Generator

**Pattern**: Hierarchical

**Architecture**:
```
         ┌─────────────┐
         │  Planner    │
         └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│API Docs│ │Guides  │ │Examples│
└────────┘ └────────┘ └────────┘
```

**Agents**:
- Planner: Analyzes codebase, creates documentation plan
- API Docs Agent: Generates function/class documentation
- Guides Agent: Creates how-to guides and tutorials
- Examples Agent: Generates code examples and snippets

**Learning Outcomes**:
- Codebase analysis
- Hierarchical delegation
- Template-based generation

**Tools**: AST parsers, docstring extractors, markdown generators

---

### 4. Dependency Update Bot

**Pattern**: Loop + Escalation

**Architecture**:
```
Scanner → Updater → Tester → [Pass: Committer | Fail: Rollback → Escalate]
```

**Agents**:
- Scanner: Identifies outdated dependencies
- Updater: Applies updates one at a time
- Tester: Runs test suite, checks for breaking changes
- Committer: Creates PR with changelog
- Escalator: Notifies human for manual review

**Learning Outcomes**:
- Retry/rollback patterns
- Human-in-the-loop escalation
- CI/CD integration

**Tools**: Package managers (npm, pip, cargo), test runners, GitHub API

---

### 5. Bug Reproducer

**Pattern**: Loop

**Architecture**:
```
Issue Parser → Environment Setup → Reproducer → [Success: Reporter | Fail: Retry with variations]
```

**Agents**:
- Issue Parser: Extracts reproduction steps from bug reports
- Environment Agent: Sets up isolated test environment
- Reproducer: Attempts to reproduce the bug
- Reporter: Documents reproduction steps, creates minimal example

**Learning Outcomes**:
- Iterative refinement
- Environment isolation
- Failure analysis

**Tools**: Docker, test frameworks, issue trackers

---

## Data & Analytics (6-10)

### 6. Natural Language to SQL

**Pattern**: Loop + Validation

**Architecture**:
```
┌──────────────────────────────────────┐
│                                      │
▼                                      │
Query Planner → SQL Generator → Validator → Executor → Formatter
                                   │
                                   └── [Invalid: retry]
```

**Agents**:
- Query Planner: Breaks complex questions into sub-queries
- SQL Generator: Converts natural language to SQL
- Validator: Checks syntax, permissions, query safety
- Executor: Runs query, handles errors
- Formatter: Presents results in readable format

**Learning Outcomes**:
- Schema-aware generation
- Query validation and safety
- Error recovery loops

**Tools**: Database connectors, SQL parsers, schema introspection

---

### 7. Data Quality Monitor

**Pattern**: Parallel + Aggregator

**Architecture**:
```
Scheduler → [Completeness, Consistency, Accuracy, Timeliness] → Reporter → Alerter
```

**Agents**:
- Scheduler: Triggers checks on schedule or data arrival
- Completeness Agent: Checks for missing values, required fields
- Consistency Agent: Cross-table validation, referential integrity
- Accuracy Agent: Range checks, format validation, outlier detection
- Timeliness Agent: Data freshness, SLA compliance
- Reporter: Generates quality scorecard
- Alerter: Routes issues by severity

**Learning Outcomes**:
- Scheduled agent execution
- Metric aggregation
- Alert routing

**Tools**: Database connectors, pandas, alerting systems (Slack, PagerDuty)

---

### 8. ETL Pipeline Builder

**Pattern**: Sequential + Branching

**Architecture**:
```
Source Analyzer → Schema Mapper → Transformer → Loader → Validator
```

**Agents**:
- Source Analyzer: Inspects source data structure
- Schema Mapper: Maps source to target schema
- Transformer: Applies data transformations
- Loader: Writes to destination
- Validator: Verifies data integrity post-load

**Learning Outcomes**:
- Data transformation patterns
- Schema evolution handling
- Idempotent operations

**Tools**: pandas, dbt, Airflow, database connectors

---

### 9. Report Generator

**Pattern**: Hierarchical

**Architecture**:
```
         ┌─────────────┐
         │  Planner    │
         └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Query  │ │ Chart  │ │Narrative│
└────────┘ └────────┘ └────────┘
         └──────┬──────┘
         ┌──────▼──────┐
         │  Assembler  │
         └─────────────┘
```

**Agents**:
- Planner: Determines report structure from request
- Query Agent: Fetches data from various sources
- Chart Agent: Generates visualizations
- Narrative Agent: Writes insights and summaries
- Assembler: Combines into final report

**Learning Outcomes**:
- Multi-modal output (text + charts)
- Template-based assembly
- Data storytelling

**Tools**: SQL, matplotlib/plotly, PDF generators

---

### 10. Anomaly Investigator

**Pattern**: Escalation

**Architecture**:
```
Detector → Classifier → [Low: Auto-resolve | Medium: Investigator | High: Human]
```

**Agents**:
- Detector: Identifies statistical anomalies
- Classifier: Determines severity and type
- Investigator: Performs root cause analysis
- Resolver: Applies automatic fixes for known patterns
- Escalator: Creates detailed report for human review

**Learning Outcomes**:
- Severity-based routing
- Automated remediation
- Human escalation patterns

**Tools**: Statistical libraries, time series analysis, alerting systems

---

## Document Processing (11-14)

### 11. Invoice Processing Pipeline

**Pattern**: Sequential + Validation

**Architecture**:
```
Ingester → Classifier → Extractor → Validator → [Valid: Processor | Invalid: Human Review]
```

**Agents**:
- Ingester: Receives documents from email/upload
- Classifier: Identifies document type (invoice, receipt, PO)
- Extractor: Pulls structured data (vendor, amount, line items)
- Validator: Cross-checks against PO, vendor database
- Processor: Creates accounting entries
- Review Agent: Queues ambiguous cases for human

**Learning Outcomes**:
- Document classification
- Structured extraction
- Validation workflows

**Tools**: OCR (Tesseract, cloud APIs), PDF parsers, accounting APIs

---

### 12. Contract Analyzer

**Pattern**: Parallel + Aggregator

**Architecture**:
```
Parser → [Risk, Obligations, Terms, Compliance] → Summarizer → Flagging
```

**Agents**:
- Parser: Extracts text, identifies sections
- Risk Agent: Identifies liability clauses, indemnification
- Obligations Agent: Extracts commitments, deadlines
- Terms Agent: Payment terms, renewal conditions
- Compliance Agent: Checks against company policies
- Summarizer: Creates executive summary
- Flagging Agent: Highlights items needing negotiation

**Learning Outcomes**:
- Legal document understanding
- Multi-perspective analysis
- Risk scoring

**Tools**: PDF parsers, legal NLP models, policy databases

---

### 13. Resume Screener

**Pattern**: Sequential + Scoring

**Architecture**:
```
Parser → Skills Extractor → Experience Scorer → Culture Matcher → Ranker
```

**Agents**:
- Parser: Extracts structured data from various formats
- Skills Extractor: Identifies and normalizes skills
- Experience Scorer: Evaluates relevance to job requirements
- Culture Matcher: Assesses soft skills, values alignment
- Ranker: Produces final candidate ranking with explanations

**Learning Outcomes**:
- Multi-criteria scoring
- Bias mitigation strategies
- Explainable rankings

**Tools**: Resume parsers, skills taxonomies, ATS integrations

---

### 14. Research Paper Analyzer

**Pattern**: Hierarchical

**Architecture**:
```
         ┌─────────────┐
         │  Ingester   │
         └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Abstract│ │Methods │ │Results │
└────────┘ └────────┘ └────────┘
         └──────┬──────┘
         ┌──────▼──────┐
         │ Synthesizer │
         └─────────────┘
```

**Agents**:
- Ingester: Parses PDF, identifies sections
- Abstract Agent: Extracts key claims, contributions
- Methods Agent: Analyzes methodology, identifies limitations
- Results Agent: Extracts findings, statistical significance
- Synthesizer: Creates structured summary, comparison with related work

**Learning Outcomes**:
- Section-aware processing
- Scientific reasoning
- Citation handling

**Tools**: PDF parsers, academic APIs (Semantic Scholar, arXiv)

---

## Customer-Facing (15-18)

### 15. E-commerce Support Bot

**Pattern**: Hub-Spoke + Escalation

**Architecture**:
```
         ┌─────────────┐
         │   Triage    │
         └──────┬──────┘
    ┌──────┬───┴───┬──────┐
    ▼      ▼       ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐
│Orders││Returns││Product││Human │
└──────┘└──────┘└──────┘└──────┘
```

**Agents**:
- Triage: Intent classification, routing
- Orders Agent: Tracking, modifications, cancellations
- Returns Agent: RMA process, refund status
- Product Agent: Recommendations, specifications, availability
- Escalation Agent: Complex cases, angry customers

**Learning Outcomes**:
- Customer service patterns
- Sentiment-based escalation
- Order management APIs

**Tools**: E-commerce APIs (Shopify, WooCommerce), shipping APIs

---

### 16. Appointment Scheduler

**Pattern**: Sequential + Loop

**Architecture**:
```
Intent Parser → Availability Checker → Slot Proposer → [Accepted: Booker | Rejected: Retry]
```

**Agents**:
- Intent Parser: Extracts date preferences, service type
- Availability Checker: Queries calendar systems
- Slot Proposer: Suggests available times
- Negotiator: Handles counter-proposals
- Booker: Confirms and sends notifications

**Learning Outcomes**:
- Calendar API integration
- Negotiation loops
- Confirmation workflows

**Tools**: Calendar APIs (Google, Outlook), notification systems

---

### 17. Travel Planner

**Pattern**: Hierarchical + Parallel

**Architecture**:
```
         ┌─────────────┐
         │  Planner    │
         └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Flights │ │ Hotels │ │Activities│
└────────┘ └────────┘ └────────┘
         └──────┬──────┘
         ┌──────▼──────┐
         │ Itinerary   │
         └─────────────┘
```

**Agents**:
- Planner: Parses travel requirements, creates search criteria
- Flights Agent: Searches and compares flights
- Hotels Agent: Finds accommodations matching preferences
- Activities Agent: Suggests attractions, restaurants, experiences
- Itinerary Agent: Assembles coherent day-by-day plan

**Learning Outcomes**:
- Multi-source aggregation
- Preference optimization
- Constraint satisfaction

**Tools**: Travel APIs (Amadeus, booking platforms), maps APIs

---

### 18. Healthcare Triage Bot

**Pattern**: Escalation + Safety

**Architecture**:
```
Symptom Collector → Risk Assessor → [Emergency: 911 | Urgent: Schedule | Routine: Self-care]
```

**Agents**:
- Symptom Collector: Gathers symptoms, duration, severity
- Risk Assessor: Evaluates urgency using clinical guidelines
- Emergency Agent: Immediate escalation for critical symptoms
- Scheduling Agent: Books appropriate appointment type
- Self-care Agent: Provides home care instructions

**Learning Outcomes**:
- Safety-critical routing
- Medical guidelines integration
- Liability considerations

**Tools**: Medical ontologies (SNOMED), scheduling systems, emergency protocols

---

## DevOps & Infrastructure (19-22)

### 19. Incident Response Bot

**Pattern**: Escalation + Loop

**Architecture**:
```
Alert Receiver → Diagnostician → [Auto-fix: Remediator | Manual: Escalate] → Post-mortem
```

**Agents**:
- Alert Receiver: Ingests alerts from monitoring systems
- Diagnostician: Correlates logs, metrics, traces
- Remediator: Applies automated fixes (restart, scale, rollback)
- Escalator: Pages on-call with context
- Post-mortem Agent: Generates incident report

**Learning Outcomes**:
- Alert correlation
- Automated remediation
- Runbook execution

**Tools**: Monitoring APIs (Datadog, PagerDuty), Kubernetes, cloud APIs

---

### 20. Infrastructure Cost Optimizer

**Pattern**: Parallel + Aggregator

**Architecture**:
```
Scanner → [Compute, Storage, Network, Reserved] → Recommender → Implementer
```

**Agents**:
- Scanner: Inventories cloud resources
- Compute Agent: Right-sizing, spot opportunities
- Storage Agent: Tiering, lifecycle policies
- Network Agent: Data transfer optimization
- Reserved Agent: Commitment recommendations
- Recommender: Prioritizes by ROI
- Implementer: Applies approved changes

**Learning Outcomes**:
- Cloud API integration
- Cost modeling
- Safe infrastructure changes

**Tools**: Cloud APIs (AWS, GCP, Azure), cost management APIs

---

### 21. Log Analyzer

**Pattern**: Sequential + Branching

**Architecture**:
```
Ingester → Parser → Classifier → [Error: Investigator | Pattern: Alerter | Normal: Archive]
```

**Agents**:
- Ingester: Collects logs from multiple sources
- Parser: Normalizes log formats
- Classifier: Categorizes log entries
- Investigator: Deep dives into errors
- Alerter: Identifies unusual patterns
- Archiver: Compresses and stores

**Learning Outcomes**:
- Log parsing at scale
- Pattern recognition
- Conditional routing

**Tools**: Log collectors (Fluentd), Elasticsearch, alerting systems

---

### 22. Deployment Pipeline

**Pattern**: Sequential + Validation Gates

**Architecture**:
```
Builder → Tester → Security Scanner → [Pass: Deployer | Fail: Notifier] → Validator
```

**Agents**:
- Builder: Compiles code, creates artifacts
- Tester: Runs test suites
- Security Scanner: Vulnerability scanning
- Deployer: Promotes to environments
- Notifier: Reports failures with context
- Validator: Post-deployment health checks

**Learning Outcomes**:
- CI/CD integration
- Quality gates
- Rollback strategies

**Tools**: CI systems (GitHub Actions), container registries, deployment tools

---

## Creative & Content (23-25)

### 23. Content Creation Pipeline

**Pattern**: Sequential

**Architecture**:
```
Researcher → Outliner → Drafter → Editor → SEO Optimizer → Publisher
```

**Agents**:
- Researcher: Gathers information on topic
- Outliner: Creates content structure
- Drafter: Writes initial content
- Editor: Improves clarity, fixes issues
- SEO Optimizer: Adds keywords, meta descriptions
- Publisher: Formats and publishes

**Learning Outcomes**:
- Content workflow automation
- Multi-stage refinement
- Publishing integrations

**Tools**: Search APIs, CMS APIs, SEO tools

---

### 24. Social Media Manager

**Pattern**: Parallel + Scheduler

**Architecture**:
```
         ┌─────────────┐
         │  Planner    │
         └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Twitter │ │LinkedIn│ │Instagram│
└────────┘ └────────┘ └────────┘
         └──────┬──────┘
         ┌──────▼──────┐
         │  Scheduler  │
         └─────────────┘
```

**Agents**:
- Planner: Creates content calendar from strategy
- Platform Agents: Adapts content for each platform
- Scheduler: Optimizes posting times
- Engagement Agent: Responds to comments
- Analytics Agent: Tracks performance

**Learning Outcomes**:
- Platform-specific adaptation
- Scheduling optimization
- Engagement automation

**Tools**: Social media APIs, scheduling tools, analytics platforms

---

### 25. Video Script Generator

**Pattern**: Hierarchical

**Architecture**:
```
         ┌─────────────┐
         │  Planner    │
         └──────┬──────┘
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│  Hook  │ │ Body   │ │  CTA   │
└────────┘ └────────┘ └────────┘
         └──────┬──────┘
         ┌──────▼──────┐
         │  Assembler  │
         └─────────────┘
```

**Agents**:
- Planner: Analyzes topic, determines structure
- Hook Agent: Creates attention-grabbing opening
- Body Agent: Develops main content sections
- CTA Agent: Crafts call-to-action
- Assembler: Combines with timing, transitions

**Learning Outcomes**:
- Content structure optimization
- Audience engagement patterns
- Multi-section assembly

**Tools**: Research APIs, content templates

---

## Comparison Matrix

| # | Tutorial | Patterns | Complexity | New Concepts |
|---|----------|----------|------------|--------------|
| 1 | Code Review Bot | Parallel, Aggregator | High | Parallel execution, output merging |
| 2 | Commit Message Generator | Sequential | Low | Simple pipelines |
| 3 | Documentation Generator | Hierarchical | Medium | Codebase analysis |
| 4 | Dependency Update Bot | Loop, Escalation | Medium | Retry patterns, human fallback |
| 5 | Bug Reproducer | Loop | Medium | Iterative refinement |
| 6 | NL to SQL | Loop, Validation | High | Query safety, error recovery |
| 7 | Data Quality Monitor | Parallel, Aggregator | Medium | Scheduled execution |
| 8 | ETL Pipeline Builder | Sequential, Branching | Medium | Data transformation |
| 9 | Report Generator | Hierarchical | Medium | Multi-modal output |
| 10 | Anomaly Investigator | Escalation | Medium | Severity routing |
| 11 | Invoice Processing | Sequential, Validation | Medium | Document extraction |
| 12 | Contract Analyzer | Parallel, Aggregator | High | Legal reasoning |
| 13 | Resume Screener | Sequential, Scoring | Medium | Bias mitigation |
| 14 | Research Paper Analyzer | Hierarchical | Medium | Academic processing |
| 15 | E-commerce Support | Hub-Spoke, Escalation | Medium | Customer service |
| 16 | Appointment Scheduler | Sequential, Loop | Low | Calendar integration |
| 17 | Travel Planner | Hierarchical, Parallel | High | Multi-source aggregation |
| 18 | Healthcare Triage | Escalation, Safety | High | Safety-critical systems |
| 19 | Incident Response | Escalation, Loop | High | Automated remediation |
| 20 | Cost Optimizer | Parallel, Aggregator | Medium | Cloud APIs |
| 21 | Log Analyzer | Sequential, Branching | Medium | Pattern recognition |
| 22 | Deployment Pipeline | Sequential, Validation | Medium | CI/CD integration |
| 23 | Content Creation | Sequential | Low | Content workflows |
| 24 | Social Media Manager | Parallel, Scheduler | Medium | Platform adaptation |
| 25 | Video Script Generator | Hierarchical | Low | Content structure |

---

## Recommended Tutorial Order

For a tutorial series, consider this progression:

### Beginner (Patterns 101)
1. **Commit Message Generator** - Simple sequential
2. **Appointment Scheduler** - Sequential + simple loop
3. **Content Creation Pipeline** - Longer sequential chain

### Intermediate (Complex Patterns)
4. **Customer Service Bot** (existing) - Hub-spoke
5. **Invoice Processing** - Sequential + validation gates
6. **Data Quality Monitor** - Parallel + aggregation
7. **Incident Response** - Escalation + human-in-loop

### Advanced (Production Patterns)
8. **Code Review Bot** - Full parallel + conflict resolution
9. **NL to SQL** - Complex loops + safety
10. **Travel Planner** - Hierarchical + parallel + optimization

---

## Template Applicability

All tutorials can use the same template structure from the customer service tutorial:

```markdown
## Project Overview
## Agents (name, role, handoff_description, tools, handoffs, routine)
## Shared Context
## Tools (name, purpose, inputs, outputs, side effects)
## UI Requirements
```

This consistency reinforces the pattern and makes the template more valuable as a reusable asset.
