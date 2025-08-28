# City Desk - Serverless AWS RAG Agent

A serverless Retrieval-Augmented Generation (RAG) agent built on AWS that answers NYC resident questions using trusted public datasets. Built with AWS SAM, Bedrock Knowledge Bases, and S3 Vectors for cost-effective, scalable question answering.

## 🎯 Business Goal

- **Primary KPI:** ≥90% of questions answered with cited sources within <2s p95 latency
- **Cost ceiling:** ≤$25/month under test traffic (≤50 daily users)
- **Operations:** Mean time to detect misconfigurations <24h via budgets/alerts

## 🏗️ Architecture

```
Client → API Gateway (HTTP API) → Lambda (Python) → Bedrock Knowledge Base
                                    ↓
                              S3 (raw docs) + S3 Vectors (embeddings)
```

### Core Components

- **API Gateway HTTP API**: Low-cost, stateless API endpoint
- **Lambda Functions**: Python 3.12 runtime for RAG processing and API key auth
- **Bedrock Knowledge Base**: Managed RAG with S3 Vectors for embeddings
- **Titan Text Express**: Fast, cost-effective text generation model
- **S3 Storage**: Raw documents + vector indexes with lifecycle policies
- **CloudWatch**: Logging, metrics, and monitoring
- **AWS Budgets**: Cost alerts at 50%, 80%, and 100% thresholds
- **CloudTrail**: Account-wide API call auditing

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** installed and configured
2. **AWS SAM CLI** installed
3. **Python 3.12+** for local development
4. **AWS Account** with appropriate permissions

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd city-desk-agent-core

# Install Python dependencies
pip install -r requirements.txt

# Deploy to AWS (dev environment)
./deploy.sh dev us-east-1
```

### Deployment

The deployment script will:
1. Build the SAM application
2. Deploy all AWS resources
3. Generate a random API key
4. Test the API endpoint
5. Save configuration details

```bash
# Deploy with custom parameters
./deploy.sh dev us-east-1 my-custom-api-key

# Deploy to different environments
./deploy.sh staging us-west-2
./deploy.sh prod us-east-1
```

## 📚 Data Ingestion

### Supported Formats

- PDF documents
- Text files (.txt)
- Markdown files (.md)
- HTML files (.html)

### Ingest Documents

```bash
# Upload and process documents
python scripts/ingest_data.py \
    --knowledge-base-id <kb-id> \
    --bucket-name <documents-bucket> \
    --documents-dir ./sample-documents \
    --data-source-name nyc-service-documents
```

### Sample Documents

Create a `sample-documents/` directory with NYC service information:

```
sample-documents/
├── snap-benefits/
│   ├── how-to-apply.md
│   ├── eligibility-requirements.pdf
│   └── renewal-process.txt
├── housing/
│   ├── affordable-housing-guide.pdf
│   └── rent-control-faq.md
└── transportation/
    ├── metrocard-guide.pdf
    └── reduced-fare-program.md
```

## 🔌 API Usage

### Authentication

Include your API key in the `x-api-key` header:

```bash
curl -X POST "https://your-api-endpoint/query" \
    -H "Content-Type: application/json" \
    -H "x-api-key: your-api-key" \
    -d '{"q": "How do I apply for a SNAP card?", "top_k": 6}'
```

### Request Format

```json
{
    "q": "Your question here",
    "top_k": 6
}
```

### Response Format

```json
{
    "answer": "Detailed answer with citations...",
    "citations": [
        {
            "text": "Relevant text excerpt...",
            "source_url": "https://nyc.gov/...",
            "title": "Document Title",
            "section": "Section Name",
            "relevance_score": 0.95
        }
    ],
    "retrieval_time_ms": 1250,
    "query": "Original question"
}
```

## 💰 Cost Optimization

### Current Estimates (us-east-1)

- **Lambda**: ~$0.20 per 1M requests (512MB, 1s avg)
- **API Gateway**: ~$1.00 per 1M requests
- **Bedrock**: ~$0.15 per 1K input tokens + $0.60 per 1K output tokens
- **S3**: ~$0.023 per GB/month
- **CloudWatch**: ~$0.50 per GB ingested

### Budget Alerts

- **50% threshold**: $12.50 (early warning)
- **80% threshold**: $20.00 (escalation)
- **100% threshold**: $25.00 (immediate action)

## 📊 Monitoring & Observability

### CloudWatch Metrics

- Request count and duration
- Error rates and types
- Retrieval performance
- Token usage and costs

### Logs

- Structured JSON logging
- Request/response tracing
- Error details and stack traces
- Performance metrics

### Alerts

- Cost threshold notifications
- Error rate spikes
- Performance degradation
- Service availability

## 🔒 Security

### Authentication

- API key-based authentication
- Secure key rotation via SSM Parameter Store
- Rate limiting capabilities

### Data Protection

- S3 buckets with public access blocked
- IAM roles with least privilege
- CloudTrail for audit logging
- Encryption at rest and in transit

## 🧪 Testing

### Local Testing

```bash
# Test Lambda functions locally
sam local invoke RAGAgentFunction --event events/test-event.json

# Start local API
sam local start-api
```

### Load Testing

```bash
# Stress test with 5-10 RPS for 10 minutes
# Monitor costs and performance metrics
```

## 🚧 Development

### Project Structure

```
city-desk-agent-core/
├── template.yaml          # SAM template
├── src/                   # Lambda function source
│   ├── lambda_function.py # Main RAG agent
│   └── authorizer.py      # API key validation
├── scripts/               # Utility scripts
│   └── ingest_data.py     # Data ingestion
├── deploy.sh              # Deployment script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Adding Features

1. **New Lambda Functions**: Add to `template.yaml` and create in `src/`
2. **Additional Services**: Extend SAM template with new resources
3. **Enhanced Monitoring**: Add CloudWatch metrics and alarms
4. **Cost Controls**: Implement additional budget alerts

## 🔄 CI/CD

### GitHub Actions (Recommended)

```yaml
name: Deploy City Desk
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: sam build
      - run: sam deploy --no-confirm-changeset
```

## 📈 Performance Tuning

### Cold Start Optimization

- Python 3.12 runtime
- Minimal dependencies
- Provisioned concurrency (if needed)
- Memory optimization (512MB baseline)

### Retrieval Enhancement

- Chunk size: 800-1200 tokens
- Overlap: 150-200 tokens
- Top-k retrieval: 6 documents
- Relevance scoring thresholds

## 🆘 Troubleshooting

### Common Issues

1. **Knowledge Base not responding**: Check IAM permissions and region support
2. **High latency**: Monitor Lambda memory and duration settings
3. **Cost overruns**: Review Bedrock usage and implement stricter limits
4. **Auth failures**: Verify API key and authorizer configuration

### Debug Commands

```bash
# Check CloudFormation stack status
aws cloudformation describe-stacks --stack-name city-desk-dev

# View Lambda logs
sam logs -n RAGAgentFunction --stack-name city-desk-dev

# Test API endpoint
curl -v -X POST "your-endpoint/query" -H "x-api-key: your-key"
```

## 📚 Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [S3 Vectors Preview](https://docs.aws.amazon.com/bedrock/latest/userguide/vectors.html)
- [API Gateway HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Create a GitHub issue
- Check CloudWatch logs for debugging
- Review AWS CloudFormation events
- Monitor AWS Budgets for cost issues

---

**Built with ❤️ for NYC residents and AWS enthusiasts**
