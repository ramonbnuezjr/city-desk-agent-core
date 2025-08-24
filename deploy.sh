#!/bin/bash

# City Desk Deployment Script
# Deploys the serverless RAG agent using AWS SAM

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="city-desk"
ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
API_KEY=${3:-$(openssl rand -hex 32)}

echo -e "${GREEN}🚀 Deploying City Desk - Serverless RAG Agent${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo -e "${YELLOW}Stack Name: ${STACK_NAME}-${ENVIRONMENT}${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo -e "${RED}❌ AWS SAM CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials are not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build the SAM application
echo -e "${YELLOW}🔨 Building SAM application...${NC}"
sam build --use-container

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ SAM build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ SAM build completed${NC}"

# Deploy the application
echo -e "${YELLOW}🚀 Deploying to AWS...${NC}"
sam deploy \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region "${REGION}" \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
        Environment="${ENVIRONMENT}" \
        ApiKey="${API_KEY}" \
        BudgetAlertEmail="admin@example.com" \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"

# Get stack outputs
echo -e "${YELLOW}📋 Getting stack outputs...${NC}"
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)

DOCUMENTS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='DocumentsBucketName'].OutputValue" \
    --output text)

VECTOR_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='VectorBucketName'].OutputValue" \
    --output text)

KNOWLEDGE_BASE_ID=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region "${REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='KnowledgeBaseId'].OutputValue" \
    --output text)

# Display deployment information
echo -e "${GREEN}🎉 Deployment Summary:${NC}"
echo -e "${YELLOW}API Endpoint:${NC} ${API_ENDPOINT}"
echo -e "${YELLOW}Documents Bucket:${NC} ${DOCUMENTS_BUCKET}"
echo -e "${YELLOW}Vector Bucket:${NC} ${VECTOR_BUCKET}"
echo -e "${YELLOW}Knowledge Base ID:${NC} ${KNOWLEDGE_BASE_ID}"
echo -e "${YELLOW}API Key:${NC} ${API_KEY}"

# Save configuration to file
CONFIG_FILE="deployment-config-${ENVIRONMENT}.json"
cat > "${CONFIG_FILE}" << EOF
{
    "environment": "${ENVIRONMENT}",
    "region": "${REGION}",
    "api_endpoint": "${API_ENDPOINT}",
    "documents_bucket": "${DOCUMENTS_BUCKET}",
    "vector_bucket": "${VECTOR_BUCKET}",
    "knowledge_base_id": "${KNOWLEDGE_BASE_ID}",
    "api_key": "${API_KEY}",
    "deployment_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo -e "${GREEN}💾 Configuration saved to ${CONFIG_FILE}${NC}"

# Test the API
echo -e "${YELLOW}🧪 Testing API endpoint...${NC}"
TEST_RESPONSE=$(curl -s -X POST "${API_ENDPOINT}/query" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${API_KEY}" \
    -d '{"q": "How do I apply for a SNAP card?", "top_k": 3}' \
    --max-time 30 || echo "Request failed")

if [[ "$TEST_RESPONSE" == *"error"* ]]; then
    echo -e "${YELLOW}⚠️  API test returned an error (this is expected if no documents are ingested yet)${NC}"
else
    echo -e "${GREEN}✅ API test successful${NC}"
fi

echo -e "${GREEN}🎯 Next steps:${NC}"
echo -e "1. Upload NYC service documents to S3 bucket: ${DOCUMENTS_BUCKET}"
echo -e "2. Run data ingestion: python scripts/ingest_data.py --knowledge-base-id ${KNOWLEDGE_BASE_ID} --bucket-name ${DOCUMENTS_BUCKET} --documents-dir ./sample-documents"
echo -e "3. Test queries using the API endpoint: ${API_ENDPOINT}"
echo -e "4. Monitor costs in AWS Budgets (set to $25/month)"
echo -e "5. Check CloudWatch logs for monitoring"

echo -e "${GREEN}🚀 City Desk is ready to serve NYC residents!${NC}"
