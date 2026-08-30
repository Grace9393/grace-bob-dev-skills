# Data Scope-Limiting Bounding Statements

## Domain-Specific Boundaries for Data Projects

### 1. Data Volume and Scale Boundaries

**Bounding Statements:**
- "Data volume: maximum [TB/GB] total storage"
- "Record count: up to [number] records per table/entity"
- "Transaction volume: [number] transactions per second/minute/hour"
- "Historical data: [timeframe] only; older data archived or excluded"
- "Growth projection: [percentage]% annual growth; re-architecture required beyond"

**Risk Mitigation:**
- Prevents infrastructure under-sizing
- Establishes clear capacity planning boundaries
- Protects against performance degradation
- Creates scaling triggers
- Limits storage costs

### 2. Data Source and System Boundaries

**Bounding Statements:**
- "Data sources: [number] systems: [list specific sources]"
- "Database types: [specific databases] (e.g., PostgreSQL, MySQL, Oracle, SQL Server)"
- "File sources: [formats] only (CSV, JSON, XML, Parquet)"
- "Streaming sources: [specific platforms] (Kafka, Kinesis, Event Hub)"
- "Legacy systems: [specific systems] only; additional sources require assessment"

**Risk Mitigation:**
- Prevents unlimited data source integration
- Establishes clear source system scope
- Clarifies database platform support
- Limits file format complexity
- Protects against legacy system complexity

### 3. Data Quality and Cleansing Boundaries

**Bounding Statements:**
- "Data quality checks: completeness, format validation, type checking"
- "Deduplication: based on [specific fields] only"
- "Data cleansing: standardization and format correction only"
- "Business rule validation: client responsibility"
- "Data enrichment: excluded; source data used as-is"

**Risk Mitigation:**
- Limits data quality scope
- Establishes cleansing boundaries
- Prevents unlimited data transformation
- Clarifies validation responsibilities
- Protects against enrichment complexity

### 4. Data Model and Schema Boundaries

**Bounding Statements:**
- "Data model: [specific approach] (star schema, snowflake, data vault, normalized)"
- "Tables/entities: maximum [number]"
- "Columns/attributes: maximum [number] per table"
- "Relationships: maximum [number] foreign keys per table"
- "Schema changes: require impact assessment and change request"

**Risk Mitigation:**
- Establishes data modeling approach
- Prevents model complexity explosion
- Clarifies schema design boundaries
- Protects against unlimited schema changes
- Creates change control process

### 5. Data Migration and Loading Boundaries

**Bounding Statements:**
- "Migration approach: [full load / incremental / CDC]"
- "Migration window: [timeframe] for initial load"
- "Cutover strategy: [big bang / phased / parallel run]"
- "Data validation: [percentage]% sample verification"
- "Rollback plan: [approach]; full rollback excluded beyond [timeframe]"

**Risk Mitigation:**
- Clarifies migration strategy
- Establishes migration timeline
- Limits validation scope
- Protects against unlimited rollback obligations
- Defines cutover approach

### 6. Data Transformation and ETL Boundaries

**Bounding Statements:**
- "ETL tool: [specific tool] (Informatica, Talend, Azure Data Factory, AWS Glue)"
- "Transformation complexity: simple mappings and aggregations only"
- "Complex transformations: maximum [number] per pipeline"
- "Custom code: excluded; tool-native transformations only"
- "Pipeline orchestration: [number] pipelines maximum"

**Risk Mitigation:**
- Establishes ETL platform
- Limits transformation complexity
- Prevents custom code proliferation
- Clarifies pipeline scope
- Protects against orchestration complexity

### 7. Data Warehouse/Lake Architecture Boundaries

**Bounding Statements:**
- "Architecture: [data warehouse / data lake / lakehouse]"
- "Platform: [specific platform] (Snowflake, Redshift, BigQuery, Databricks, Synapse)"
- "Storage layers: [raw / curated / consumption] only"
- "Compute resources: [specific sizing]; scaling requires review"
- "Data retention: [period] in active storage; archival client responsibility"

**Risk Mitigation:**
- Clarifies architectural approach
- Establishes platform boundaries
- Limits storage layer complexity
- Protects against compute cost overruns
- Defines retention policies

### 8. Data Security and Governance Boundaries

**Bounding Statements:**
- "Data classification: [levels] (public, internal, confidential, restricted)"
- "Encryption: at-rest and in-transit; key management client responsibility"
- "Access control: role-based access control (RBAC) with [number] roles"
- "Data masking: [specific fields/columns]; dynamic masking excluded"
- "Audit logging: access logs retained for [period]"

**Risk Mitigation:**
- Establishes security classification
- Clarifies encryption approach
- Limits access control complexity
- Protects against unlimited masking requirements
- Defines audit retention

### 9. Data Analytics and Reporting Boundaries

**Bounding Statements:**
- "Reporting tool: [specific tool] (Power BI, Tableau, Looker, Qlik)"
- "Reports/dashboards: maximum [number] included"
- "Data refresh frequency: [schedule] (real-time excluded)"
- "User concurrency: designed for [number] concurrent users"
- "Ad-hoc query capability: excluded; predefined reports only"

**Risk Mitigation:**
- Establishes reporting platform
- Prevents unlimited report creation
- Clarifies refresh frequency
- Protects against concurrency issues
- Limits ad-hoc query complexity

### 10. Data Lineage and Metadata Management

**Bounding Statements:**
- "Data lineage: source-to-target mapping documentation"
- "Metadata management: technical metadata only; business metadata excluded"
- "Lineage tool: [specific tool] or documentation-based"
- "Lineage scope: [specific pipelines/tables]"
- "Metadata updates: manual; automated metadata harvesting excluded"

**Risk Mitigation:**
- Clarifies lineage documentation approach
- Limits metadata management scope
- Establishes lineage tool boundaries
- Protects against comprehensive lineage requirements
- Defines metadata maintenance approach

### 11. Master Data Management (MDM) Boundaries

**Bounding Statements:**
- "MDM domains: [specific domains] (customer, product, location)"
- "MDM approach: [registry / consolidation / coexistence]"
- "Golden record rules: [number] matching/merging rules"
- "Data stewardship: client responsibility"
- "MDM tool: [specific tool] or custom solution excluded"

**Risk Mitigation:**
- Establishes MDM domain scope
- Clarifies MDM architectural approach
- Limits matching rule complexity
- Protects against data stewardship burden
- Defines MDM platform boundaries

### 12. Real-Time and Streaming Data Boundaries

**Bounding Statements:**
- "Streaming platform: [Kafka / Kinesis / Event Hub / Pub/Sub]"
- "Stream processing: [specific framework] (Spark Streaming, Flink, Kafka Streams)"
- "Event throughput: maximum [events/second]"
- "Processing latency: [seconds/minutes]; sub-second excluded"
- "Stream retention: [period]; longer retention requires additional storage"

**Risk Mitigation:**
- Clarifies streaming platform
- Establishes processing framework
- Limits throughput expectations
- Protects against ultra-low latency requirements
- Defines retention boundaries

### 13. Data Science and ML Data Preparation

**Bounding Statements:**
- "Feature engineering: [number] features maximum"
- "Training data: [volume/timeframe] of historical data"
- "Data labeling: client-provided labeled data"
- "Feature store: excluded unless explicitly scoped"
- "Data versioning: [approach]; full versioning excluded"

**Risk Mitigation:**
- Limits feature complexity
- Establishes training data scope
- Clarifies labeling responsibilities
- Protects against feature store complexity
- Defines versioning approach

### 14. Data Backup and Recovery Boundaries

**Bounding Statements:**
- "Backup frequency: [schedule] (daily, weekly)"
- "Backup retention: [period]; longer retention requires additional storage"
- "Recovery time objective (RTO): [timeframe]"
- "Recovery point objective (RPO): [timeframe]"
- "Disaster recovery: [approach]; full DR site excluded"

**Risk Mitigation:**
- Establishes backup schedule
- Clarifies retention policies
- Sets recovery expectations
- Protects against unlimited DR requirements
- Defines business continuity approach

### 15. Data Performance and Optimization Boundaries

**Bounding Statements:**
- "Query performance: [seconds] for [percentage]% of queries"
- "Indexing strategy: [approach]; custom indexes limited to [number]"
- "Partitioning: [strategy] (date-based, hash, range)"
- "Caching: [approach]; distributed caching excluded"
- "Performance tuning: [number] optimization iterations included"

**Risk Mitigation:**
- Establishes performance targets
- Limits indexing complexity
- Clarifies partitioning approach
- Protects against unlimited optimization
- Defines tuning scope

---

## Data Project Risk Scenarios

### Unlimited Data Sources
**Scenario:** Client wants to integrate data from all systems
**Bounded Response:** "Scope includes [number] data sources: [list]. Each additional source requires: source system analysis, data profiling, mapping definition, quality assessment, testing. Additional sources: [effort estimate] per source."

### Complex Data Transformation
**Scenario:** Client needs extensive business logic in ETL
**Bounded Response:** "ETL handles: extraction, simple transformations (mapping, aggregation, filtering), loading. Complex business logic should remain in source/target systems. Complex transformations in ETL increase effort by 50-70% and create maintenance burden."

### Real-Time Data Expectations
**Scenario:** Client expects all data to be real-time
**Bounded Response:** "Real-time streaming limited to [use cases]. Batch processing (hourly/daily) recommended for: reporting, analytics, historical analysis. Real-time requires: streaming infrastructure, monitoring, higher costs. Each real-time pipeline: [effort estimate]."

### Unlimited Data Quality
**Scenario:** Client wants perfect data quality
**Bounded Response:** "Data quality includes: format validation, completeness checks, deduplication on [fields]. Advanced quality (business rule validation, enrichment, complex matching) requires: rule definition, testing, ongoing maintenance. Target data quality: [percentage]% accuracy."

---

## Data Project Estimation Impact

Proper data scope bounding reduces estimates by:
- **Data Source Integration:** 30-40% reduction (defined source list)
- **Data Quality/Cleansing:** 35-45% reduction (clear quality boundaries)
- **ETL Development:** 25-35% reduction (limited transformation complexity)
- **Testing Effort:** 20-30% reduction (defined validation scope)
- **Performance Tuning:** 25-35% reduction (clear performance targets)
- **Overall Data Project:** 25-40% reduction in total estimate

---

## Data Architecture Decision Matrix

| Requirement | Bounded Approach | Excluded Approach |
|-------------|------------------|-------------------|
| Architecture | Data Warehouse (structured), Data Lake (raw), Lakehouse (hybrid) | Custom architecture, multiple platforms |
| ETL Pattern | Batch (non-critical), Micro-batch (important), Streaming (critical) | All real-time |
| Data Quality | Format validation, deduplication, standardization | Business rule validation, enrichment, ML-based quality |
| Storage | Hot (active queries), Warm (occasional), Cold (archive) | All hot storage, unlimited retention |
| Processing | SQL-based (simple), Spark (complex), Custom code (excluded) | Custom processing frameworks |
| Security | RBAC, encryption, basic masking | Fine-grained access, dynamic masking, tokenization |

---

## Data Volume Complexity Assessment

### Small Scale (2-4 weeks)
- Data volume: <100GB
- Sources: 1-3 systems
- Tables: <20
- Simple transformations
- Batch processing (daily)

### Medium Scale (6-12 weeks)
- Data volume: 100GB-1TB
- Sources: 4-8 systems
- Tables: 20-50
- Moderate transformations
- Batch/micro-batch processing

### Large Scale (3-6 months)
- Data volume: 1TB-10TB
- Sources: 8-15 systems
- Tables: 50-100+
- Complex transformations
- Streaming + batch processing

### Enterprise Scale (6-12 months)
- Data volume: >10TB
- Sources: 15+ systems
- Tables: 100+
- Very complex transformations
- Multi-region, high availability

---

## Data Quality Tiers

### Tier 1: Basic Quality (Included)
- Format validation (data types, lengths)
- Completeness checks (required fields)
- Deduplication (exact match on key fields)
- Standardization (case, whitespace, formats)

### Tier 2: Enhanced Quality (Additional Effort)
- Fuzzy matching and deduplication
- Cross-field validation
- Reference data validation
- Statistical outlier detection

### Tier 3: Advanced Quality (Separate SOW)
- Business rule validation
- Data enrichment from external sources
- ML-based anomaly detection
- Complex matching algorithms
- Data profiling and discovery

---

## Data Migration Complexity Factors

**Low Complexity:**
- Single source system
- Simple data model (<20 tables)
- Minimal transformations
- Good source data quality
- Batch migration acceptable

**Medium Complexity:**
- Multiple source systems (3-5)
- Moderate data model (20-50 tables)
- Standard transformations
- Average source data quality
- Phased migration required

**High Complexity:**
- Many source systems (5+)
- Complex data model (50+ tables)
- Complex transformations
- Poor source data quality
- Zero-downtime migration required
- Data reconciliation critical