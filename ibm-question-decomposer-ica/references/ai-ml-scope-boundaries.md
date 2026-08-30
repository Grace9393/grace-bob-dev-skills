# AI and Machine Learning Scope-Limiting Bounding Statements

## Domain-Specific Boundaries for AI/ML Projects

### 1. ML Problem Type and Use Case Boundaries

**Bounding Statements:**
- "ML problem type: [classification / regression / clustering / recommendation / forecasting]"
- "Use cases: [specific use cases] only; additional use cases require separate assessment"
- "Model complexity: [simple / moderate / complex]; deep learning excluded unless explicitly scoped"
- "Business objective: [specific metric] improvement; multiple objectives require prioritization"
- "Success criteria: [specific threshold] (e.g., 85% accuracy, 0.15 RMSE)"

**Risk Mitigation:**
- Establishes clear ML problem definition
- Prevents scope creep to multiple use cases
- Limits model complexity expectations
- Clarifies success metrics upfront
- Protects against unrealistic accuracy targets

### 2. Data Availability and Quality Boundaries

**Bounding Statements:**
- "Training data: minimum [number] labeled examples required"
- "Data quality: client-provided clean, labeled data; data labeling excluded"
- "Historical data: [timeframe] required; insufficient data may limit model performance"
- "Data features: [number] features maximum; feature engineering limited to [scope]"
- "Data imbalance: class distribution [ratio]; severe imbalance requires separate handling"

**Risk Mitigation:**
- Establishes data requirements upfront
- Clarifies data labeling responsibilities
- Prevents insufficient data scenarios
- Limits feature engineering scope
- Protects against data quality issues

### 3. Model Development and Training Boundaries

**Bounding Statements:**
- "ML framework: [TensorFlow / PyTorch / scikit-learn / XGBoost]"
- "Model types: [specific algorithms] (e.g., Random Forest, Gradient Boosting, Neural Networks)"
- "Training iterations: [number] model experiments; hyperparameter tuning limited"
- "Training infrastructure: [specific compute] (CPU/GPU); distributed training excluded"
- "Training time: maximum [hours/days] per model; longer training requires approval"

**Risk Mitigation:**
- Establishes ML technology stack
- Limits algorithm exploration scope
- Prevents unlimited experimentation
- Clarifies compute resource boundaries
- Protects against excessive training costs

### 4. Model Performance and Accuracy Boundaries

**Bounding Statements:**
- "Target accuracy: [percentage]% on test set; higher accuracy may not be achievable"
- "Performance metrics: [specific metrics] (precision, recall, F1, AUC, RMSE)"
- "Baseline comparison: improvement over [baseline approach]"
- "Performance variance: ±[percentage]% acceptable across different data samples"
- "Edge cases: model may underperform on [specific scenarios]; requires separate handling"

**Risk Mitigation:**
- Sets realistic accuracy expectations
- Establishes clear evaluation metrics
- Provides baseline for comparison
- Manages performance variance expectations
- Clarifies model limitations upfront

### 5. Feature Engineering and Selection Boundaries

**Bounding Statements:**
- "Feature engineering: [number] derived features maximum"
- "Feature selection: automated methods only; manual feature crafting limited to [scope]"
- "Feature types: numerical and categorical; text/image features require separate scoping"
- "Feature scaling: standard normalization; custom scaling excluded"
- "Feature store: excluded; features computed on-demand"

**Risk Mitigation:**
- Limits feature engineering complexity
- Establishes feature selection approach
- Clarifies feature type support
- Protects against feature store implementation
- Defines feature computation strategy

### 6. Model Explainability and Interpretability Boundaries

**Bounding Statements:**
- "Model interpretability: [SHAP / LIME / feature importance] for [number] features"
- "Explainability reports: high-level feature importance only; detailed explanations excluded"
- "Regulatory compliance: [specific requirements] (e.g., GDPR right to explanation)"
- "Bias detection: basic fairness metrics; comprehensive bias audit excluded"
- "Model documentation: standard model card; extensive documentation excluded"

**Risk Mitigation:**
- Establishes explainability approach
- Limits interpretability scope
- Clarifies regulatory compliance boundaries
- Protects against comprehensive bias audits
- Defines documentation requirements

### 7. Model Deployment and Serving Boundaries

**Bounding Statements:**
- "Deployment platform: [specific platform] (AWS SageMaker, Azure ML, GCP Vertex AI, on-premise)"
- "Serving method: [batch / real-time / edge]; multi-modal serving excluded"
- "API endpoint: REST API only; GraphQL/gRPC excluded"
- "Latency requirement: [milliseconds] for [percentile]% of requests"
- "Throughput: [requests/second]; auto-scaling requires separate configuration"

**Risk Mitigation:**
- Clarifies deployment platform
- Establishes serving approach
- Limits API complexity
- Sets performance expectations
- Protects against unlimited scaling requirements

### 8. Model Monitoring and Maintenance Boundaries

**Bounding Statements:**
- "Model monitoring: prediction accuracy, data drift, model drift"
- "Monitoring frequency: [schedule] (daily, weekly); real-time monitoring excluded"
- "Alerting: threshold-based alerts for [specific conditions]"
- "Model retraining: [frequency] or when performance degrades by [percentage]%"
- "Retraining automation: excluded; manual retraining process"

**Risk Mitigation:**
- Establishes monitoring scope
- Clarifies monitoring frequency
- Limits alerting complexity
- Defines retraining triggers
- Protects against automated retraining complexity

### 9. MLOps and Pipeline Boundaries

**Bounding Statements:**
- "ML pipeline: [training / inference / both]; full MLOps excluded"
- "Pipeline orchestration: [specific tool] (Airflow, Kubeflow, Azure ML Pipelines)"
- "Version control: model versioning for [number] versions; full lineage excluded"
- "CI/CD integration: basic deployment pipeline; advanced CI/CD excluded"
- "Experiment tracking: [tool] (MLflow, Weights & Biases); custom tracking excluded"

**Risk Mitigation:**
- Clarifies MLOps scope
- Establishes pipeline boundaries
- Limits version control complexity
- Protects against full CI/CD implementation
- Defines experiment tracking approach

### 10. Natural Language Processing (NLP) Boundaries

**Bounding Statements:**
- "NLP task: [specific task] (sentiment analysis, named entity recognition, text classification)"
- "Language support: [specific languages] only; multilingual models excluded"
- "Text preprocessing: tokenization, lowercasing, stopword removal; advanced NLP excluded"
- "Model type: [transformer-based / traditional ML]; custom language models excluded"
- "Context length: maximum [tokens] per input; longer texts require chunking"

**Risk Mitigation:**
- Establishes NLP task scope
- Limits language support
- Clarifies preprocessing boundaries
- Protects against custom model development
- Defines input length constraints

### 11. Computer Vision Boundaries

**Bounding Statements:**
- "Vision task: [specific task] (image classification, object detection, segmentation)"
- "Image resolution: [dimensions]; higher resolution requires additional compute"
- "Image formats: [formats] (JPEG, PNG); other formats excluded"
- "Pre-trained models: [specific models] (ResNet, YOLO, EfficientNet); custom models excluded"
- "Video processing: excluded; image-only scope"

**Risk Mitigation:**
- Establishes vision task scope
- Limits image resolution complexity
- Clarifies format support
- Protects against custom model training
- Defines media type boundaries

### 12. Generative AI and LLM Boundaries

**Bounding Statements:**
- "LLM usage: [specific model] (GPT-4, Claude, Llama) via API; fine-tuning excluded"
- "Prompt engineering: [number] prompt templates; extensive prompt optimization excluded"
- "Context window: [tokens] maximum; longer contexts require chunking"
- "Generation parameters: temperature, max tokens; advanced parameters excluded"
- "Content moderation: basic filtering; comprehensive moderation excluded"

**Risk Mitigation:**
- Clarifies LLM platform and model
- Limits prompt engineering scope
- Establishes context boundaries
- Protects against fine-tuning complexity
- Defines content moderation approach

### 13. Recommendation System Boundaries

**Bounding Statements:**
- "Recommendation approach: [collaborative filtering / content-based / hybrid]"
- "Recommendation count: top [number] recommendations per user"
- "Update frequency: [schedule] (daily, weekly); real-time recommendations excluded"
- "Cold start handling: [approach] (popularity-based, content-based); advanced methods excluded"
- "Personalization level: user-level only; session-based personalization excluded"

**Risk Mitigation:**
- Establishes recommendation algorithm
- Limits recommendation complexity
- Clarifies update frequency
- Protects against cold start complexity
- Defines personalization scope

### 14. Time Series Forecasting Boundaries

**Bounding Statements:**
- "Forecasting horizon: [timeframe] (e.g., 7 days, 1 month)"
- "Forecasting frequency: [interval] (hourly, daily, weekly)"
- "Seasonality: [types] (daily, weekly, yearly); complex seasonality excluded"
- "External features: [number] exogenous variables maximum"
- "Forecast intervals: point estimates only; confidence intervals excluded"

**Risk Mitigation:**
- Establishes forecasting scope
- Clarifies temporal granularity
- Limits seasonality complexity
- Protects against unlimited external features
- Defines uncertainty quantification boundaries

### 15. Model Governance and Compliance Boundaries

**Bounding Statements:**
- "Model governance: basic model registry and approval process"
- "Compliance requirements: [specific regulations] (GDPR, CCPA, industry-specific)"
- "Bias and fairness: basic fairness metrics; comprehensive audit excluded"
- "Model risk management: [approach]; full MRM framework excluded"
- "Documentation: model card and basic technical documentation"

**Risk Mitigation:**
- Establishes governance approach
- Clarifies compliance scope
- Limits bias assessment complexity
- Protects against full MRM implementation
- Defines documentation requirements

---

## AI/ML Risk Scenarios

### Unrealistic Accuracy Expectations
**Scenario:** Client expects 99% accuracy on complex problem
**Bounded Response:** "Target accuracy: [realistic percentage]% based on: data quality, problem complexity, baseline performance. Achieving higher accuracy requires: more data, feature engineering, model complexity. Each 1% accuracy improvement beyond [threshold]% may require exponential effort."

### Insufficient Training Data
**Scenario:** Client has limited labeled data
**Bounded Response:** "Minimum [number] labeled examples required for [accuracy target]%. Current dataset: [number] examples. Options: (1) Reduce accuracy target, (2) Data augmentation (limited scope), (3) Transfer learning (if applicable), (4) Data labeling effort (separate SOW)."

### Real-Time Inference Requirements
**Scenario:** Client needs sub-millisecond predictions
**Bounded Response:** "Standard inference latency: [milliseconds] at [percentile]%. Sub-millisecond latency requires: model optimization, specialized hardware (GPU/TPU), edge deployment. Low-latency inference increases infrastructure costs by [percentage]% and requires separate performance engineering."

### Unlimited Model Experimentation
**Scenario:** Client wants to try all possible algorithms
**Bounded Response:** "Model development includes [number] algorithm experiments: [list algorithms]. Each additional algorithm requires: implementation, hyperparameter tuning, evaluation, comparison. Additional experiments: [effort estimate] per algorithm."

---

## AI/ML Estimation Impact

Proper AI/ML scope bounding reduces estimates by:
- **Data Preparation:** 30-40% reduction (clear data requirements)
- **Model Development:** 35-45% reduction (limited algorithm exploration)
- **Feature Engineering:** 25-35% reduction (defined feature scope)
- **Model Tuning:** 30-40% reduction (limited hyperparameter optimization)
- **Deployment:** 20-30% reduction (clear deployment approach)
- **Overall AI/ML Project:** 30-45% reduction in total estimate

---

## ML Problem Complexity Assessment

### Low Complexity (4-8 weeks)
- Well-defined problem (classification/regression)
- Clean, labeled data available (>10K examples)
- Standard algorithms (scikit-learn)
- Batch predictions acceptable
- Basic performance requirements

### Medium Complexity (8-16 weeks)
- Moderate problem complexity
- Some data preparation required
- Advanced algorithms (ensemble methods, neural networks)
- Near-real-time predictions
- Moderate performance requirements
- Basic explainability needed

### High Complexity (16-24 weeks)
- Complex problem (NLP, computer vision, multi-task)
- Significant data preparation/labeling
- Deep learning models
- Real-time predictions required
- High performance requirements
- Comprehensive explainability and monitoring

### Very High Complexity (6-12 months)
- Novel problem or research-level difficulty
- Limited or noisy data
- Custom model architecture
- Edge deployment
- Strict latency/accuracy requirements
- Full MLOps pipeline
- Regulatory compliance

---

## ML Model Selection Matrix

| Problem Type | Bounded Approach | Excluded Approach |
|-------------|------------------|-------------------|
| Classification | Logistic Regression, Random Forest, XGBoost | Deep learning (unless justified) |
| Regression | Linear Regression, Random Forest, Gradient Boosting | Neural networks (unless justified) |
| NLP | Pre-trained transformers (BERT, GPT) via API | Custom language model training |
| Computer Vision | Pre-trained CNNs (ResNet, EfficientNet) | Custom architecture, training from scratch |
| Time Series | ARIMA, Prophet, LSTM | Complex ensemble methods |
| Recommendation | Collaborative filtering, Matrix factorization | Deep learning recommenders |

---

## Data Requirements by ML Task

### Classification/Regression
- **Minimum:** 1,000 examples per class
- **Recommended:** 10,000+ examples per class
- **Features:** 10-100 features
- **Quality:** <5% missing values, labeled data

### NLP (Text Classification)
- **Minimum:** 1,000 documents per class
- **Recommended:** 10,000+ documents per class
- **Text length:** 10-500 words average
- **Quality:** Clean text, proper encoding

### Computer Vision
- **Minimum:** 1,000 images per class
- **Recommended:** 10,000+ images per class
- **Resolution:** 224x224 minimum
- **Quality:** Consistent lighting, clear objects

### Time Series Forecasting
- **Minimum:** 2 years historical data
- **Recommended:** 3-5 years historical data
- **Frequency:** Consistent intervals
- **Quality:** <10% missing values, no gaps

---

## ML Project Anti-Patterns to Avoid

1. **Accuracy at All Costs:** Don't sacrifice interpretability, speed, or maintainability for marginal accuracy gains
2. **Data Hoarding:** Don't collect unlimited data; focus on quality over quantity
3. **Model Complexity:** Don't use deep learning when simpler models suffice
4. **Premature Optimization:** Don't optimize before establishing baseline performance
5. **Ignoring Deployment:** Don't build models that can't be deployed to production
6. **Overfitting to Test Set:** Don't tune models based on test set performance
7. **Neglecting Monitoring:** Don't deploy without monitoring for drift and degradation
8. **Feature Engineering Rabbit Hole:** Don't spend unlimited time on feature engineering

---

## ML Success Criteria Template

**Business Metrics:**
- Primary: [metric] improvement of [percentage]%
- Secondary: [metric] maintained above [threshold]
- Constraint: [metric] not degraded by more than [percentage]%

**Technical Metrics:**
- Accuracy: [percentage]% on test set
- Latency: [milliseconds] at p95
- Throughput: [predictions/second]
- Model size: <[MB]

**Operational Metrics:**
- Training time: <[hours]
- Retraining frequency: [schedule]
- Monitoring: [metrics] tracked [frequency]
- Incident response: <[hours] to resolution