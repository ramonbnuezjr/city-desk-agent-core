#!/usr/bin/env python3
"""
Data ingestion script for City Desk Knowledge Base.
Uploads NYC service documents and processes them for vector search.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock')

def upload_document_to_s3(file_path: str, bucket_name: str, s3_key: str) -> bool:
    """
    Upload a document to S3.
    
    Args:
        file_path: Local path to the document
        bucket_name: S3 bucket name
        s3_key: S3 object key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
        
        with open(file_path, 'rb') as file:
            s3.upload_fileobj(file, bucket_name, s3_key)
        
        logger.info(f"Successfully uploaded {s3_key}")
        return True
        
    except Exception as e:
        logger.error(f"Error uploading {file_path}: {e}")
        return False

def create_knowledge_base_data_source(knowledge_base_id: str, bucket_name: str, data_source_name: str) -> str:
    """
    Create a data source in the Bedrock Knowledge Base.
    
    Args:
        knowledge_base_id: Knowledge Base ID
        bucket_name: S3 bucket containing documents
        data_source_name: Name for the data source
        
    Returns:
        Data source ID
    """
    try:
        response = bedrock.create_data_source(
            knowledgeBaseId=knowledge_base_id,
            name=data_source_name,
            description=f"NYC service documents from {bucket_name}",
            dataSourceConfiguration={
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::{bucket_name}',
                    'inclusionPrefixes': ['documents/']
                }
            },
            roleArn=get_or_create_kb_role_arn()
        )
        
        data_source_id = response['dataSource']['dataSourceId']
        logger.info(f"Created data source: {data_source_id}")
        return data_source_id
        
    except ClientError as e:
        logger.error(f"Error creating data source: {e}")
        raise

def start_ingestion_job(knowledge_base_id: str, data_source_id: str) -> str:
    """
    Start an ingestion job to process documents.
    
    Args:
        knowledge_base_id: Knowledge Base ID
        data_source_id: Data Source ID
        
    Returns:
        Ingestion job ID
    """
    try:
        response = bedrock.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            description="Initial ingestion of NYC service documents"
        )
        
        job_id = response['ingestionJob']['ingestionJobId']
        logger.info(f"Started ingestion job: {job_id}")
        return job_id
        
    except ClientError as e:
        logger.error(f"Error starting ingestion job: {e}")
        raise

def wait_for_ingestion_completion(knowledge_base_id: str, job_id: str, timeout_minutes: int = 30) -> bool:
    """
    Wait for ingestion job to complete.
    
    Args:
        knowledge_base_id: Knowledge Base ID
        job_id: Ingestion Job ID
        timeout_minutes: Maximum time to wait
        
    Returns:
        True if successful, False if failed or timed out
    """
    import time
    
    start_time = time.time()
    timeout_seconds = timeout_minutes * 60
    
    while time.time() - start_time < timeout_seconds:
        try:
            response = bedrock.get_ingestion_job(
                knowledgeBaseId=knowledge_base_id,
                ingestionJobId=job_id
            )
            
            status = response['ingestionJob']['status']
            logger.info(f"Ingestion job status: {status}")
            
            if status == 'COMPLETED':
                logger.info("Ingestion job completed successfully!")
                return True
            elif status == 'FAILED':
                logger.error("Ingestion job failed!")
                return False
            elif status in ['IN_PROGRESS', 'STARTING']:
                logger.info("Ingestion job in progress, waiting...")
                time.sleep(30)  # Wait 30 seconds before checking again
            else:
                logger.warning(f"Unknown ingestion job status: {status}")
                time.sleep(30)
                
        except ClientError as e:
            logger.error(f"Error checking ingestion job status: {e}")
            time.sleep(30)
    
    logger.error(f"Ingestion job timed out after {timeout_minutes} minutes")
    return False

def get_or_create_kb_role_arn() -> str:
    """
    Get or create the IAM role ARN for Bedrock Knowledge Base.
    This is a simplified version - in production, you'd want to use CloudFormation/SAM.
    
    Returns:
        IAM role ARN
    """
    # For now, return a placeholder - this should be created via SAM template
    # In a real implementation, you'd check if the role exists and create it if needed
    return "arn:aws:iam::ACCOUNT_ID:role/city-desk-kb-role-dev"

def main():
    """Main function for data ingestion."""
    parser = argparse.ArgumentParser(description='Ingest NYC service documents into City Desk Knowledge Base')
    parser.add_argument('--knowledge-base-id', required=True, help='Knowledge Base ID')
    parser.add_argument('--bucket-name', required=True, help='S3 bucket name for documents')
    parser.add_argument('--documents-dir', required=True, help='Local directory containing documents')
    parser.add_argument('--data-source-name', default='nyc-service-documents', help='Name for the data source')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.documents_dir):
        logger.error(f"Documents directory does not exist: {args.documents_dir}")
        sys.exit(1)
    
    # Upload documents to S3
    documents_dir = Path(args.documents_dir)
    uploaded_count = 0
    
    for file_path in documents_dir.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.md', '.html']:
            s3_key = f"documents/{file_path.relative_to(documents_dir)}"
            
            if upload_document_to_s3(str(file_path), args.bucket_name, s3_key):
                uploaded_count += 1
    
    logger.info(f"Uploaded {uploaded_count} documents to S3")
    
    if uploaded_count == 0:
        logger.warning("No documents were uploaded. Check file extensions and directory contents.")
        return
    
    # Create data source
    try:
        data_source_id = create_knowledge_base_data_source(
            args.knowledge_base_id,
            args.bucket_name,
            args.data_source_name
        )
        
        # Start ingestion job
        job_id = start_ingestion_job(args.knowledge_base_id, data_source_id)
        
        # Wait for completion
        success = wait_for_ingestion_completion(args.knowledge_base_id, job_id)
        
        if success:
            logger.info("Data ingestion completed successfully!")
        else:
            logger.error("Data ingestion failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error during data ingestion: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
