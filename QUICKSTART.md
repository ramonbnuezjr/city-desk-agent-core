# 🚀 City Desk Quick Start Guide

Get City Desk running in under 10 minutes!

## Prerequisites Check

```bash
# Check if you have the required tools
aws --version
sam --version
python3 --version
```

## 1. Setup Project

```bash
# Clone and setup
git clone <your-repo>
cd city-desk-agent-core

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure AWS

```bash
# Set up AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

## 3. Deploy to AWS

```bash
# Deploy to dev environment
./deploy.sh dev us-east-1

# Or use SAM directly
sam build
sam deploy --guided
```

## 4. Test the API

```bash
# Get your API endpoint from deployment output
curl -X POST "YOUR_API_ENDPOINT/query" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"q": "How do I apply for SNAP?", "top_k": 3}'
```

## 5. Add Your Documents

```bash
# Upload documents to S3
python scripts/ingest_data.py \
  --knowledge-base-id YOUR_KB_ID \
  --bucket-name YOUR_DOCUMENTS_BUCKET \
  --documents-dir ./your-documents
```

## 🎯 What You Get

- ✅ Serverless RAG API with <2s latency
- ✅ Cost-controlled ($25/month budget)
- ✅ Secure API key authentication
- ✅ Full monitoring and logging
- ✅ Scalable architecture

## 🔧 Local Development

```bash
# Test Lambda functions locally
sam local invoke RAGAgentFunction --event events/test-event.json

# Start local API
sam local start-api

# View logs
sam logs -n RAGAgentFunction --stack-name city-desk-dev
```

## 📊 Monitor & Debug

- **CloudWatch Logs**: Lambda function logs
- **AWS Budgets**: Cost alerts at 50%, 80%, 100%
- **CloudTrail**: API call auditing
- **CloudFormation**: Resource status

## 🆘 Need Help?

- Run `python test_setup.py` to verify setup
- Check CloudWatch logs for errors
- Review AWS CloudFormation events
- Monitor AWS Budgets for cost issues

---

**Ready to serve NYC residents! 🗽**
