# Improvements Backlog (Prioritized)

## P0 – Must do next
- **Deploy to AWS dev environment** — Test SAM template and Lambda functions with real AWS services
- **Test Bedrock Knowledge Base integration** — Verify S3 Vectors and document ingestion work correctly
- **Validate Titan performance** — Benchmark response times and costs against <2s p95 target
- **Test Titan integration** — Verify RAG agent works correctly with Titan Text Express

## P1 – Near‑term
- **Add zero‑spend & free‑tier guard alerts** in AWS Budgets (email + SNS). :contentReference[oaicite:16]{index:16}
- **Cold‑start control:** package Lambda slim, Python 3.12, minimal deps; only add Provisioned Concurrency if p95 > target after traffic.
- **Citations UX:** include URL + section titles; add "Can't verify → refuse" branch.
- **CI/CD pipeline** — Set up GitHub Actions for automated testing and deployment
- **Integration tests** — Test full RAG pipeline with sample documents
- **Performance benchmarking** — Compare Titan vs Claude performance and costs

## P2 – Later
- **Cost stress test:** 5–10 RPS for 10 minutes; record $/1k req estimates for Lambda+API GW using current region prices. (Use official pricing tables.) :contentReference[oaicite:17]{index:17}
- **Lambda cost hygiene:** measure memory vs duration; consider Graviton; note INIT billing change effective Aug 1, 2025. :contentReference[oaicite:18]{index:18}
- **Observability:** structured JSON logs; add CloudWatch metrics (retrieval ms, tokens, answer length).
- **Auth hardening:** swap API key for Cognito (user pools), rate limiting by user.
- **Data freshness:** nightly re‑ingest S3 objects; add `updated_at` checks.
- **A/B prompts:** safe vs terse modes; log win rate.

## ✅ Completed
- **Infrastructure as Code** — Full SAM template with all AWS resources
- **Lambda Functions** — RAG agent and API key authorizer
- **Data Ingestion** — Automated document processing and upload
- **Deployment Automation** — One-click deployment script
- **Documentation** — Comprehensive README and quick start guide
- **Testing Framework** — Local testing and validation scripts
- **Titan Integration** — Amazon Titan Text G1 - Express fully integrated

---

## Open Questions
- Which Bedrock model family best balances quality/latency on your corpus? (Run A/B at top‑k=6.) **RESOLVED: Titan Text Express selected for speed/cost balance**
- Any REST‑only features required? If yes, revisit API type (accept higher cost). :contentReference[oaicite:19]{index:19}
- What's the optimal chunk size for NYC service documents? (Currently set to 800-1200 tokens)
- Should we implement rate limiting per API key or per user?
- How does Titan performance compare to Claude for civic service questions?

## Next Sprint Goals
1. **Week 1**: Deploy to AWS, test Titan integration, validate performance
2. **Week 2**: Load test and optimize Titan performance, benchmark costs
3. **Week 3**: Add monitoring and alerting, document Titan vs Claude comparison
4. **Week 4**: Plan v2 features based on real-world performance data
