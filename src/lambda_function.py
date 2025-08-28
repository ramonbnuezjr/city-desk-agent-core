import json
import logging
import os
import time
from typing import Dict, List, Any
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime')
bedrock_agent = boto3.client('bedrock-agent-runtime')
s3 = boto3.client('s3')

# Environment variables
KNOWLEDGE_BASE_ID = os.environ['KNOWLEDGE_BASE_ID']
BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for RAG queries.
    
    Args:
        event: API Gateway event containing the query
        context: Lambda context
        
    Returns:
        Response with answer and citations
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        query = body.get('q', '')
        top_k = body.get('top_k', 6)
        
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: q (query)'
                })
            }
        
        logger.info(f"Processing query: {query[:100]}...")
        start_time = time.time()
        
        # Retrieve relevant documents from Knowledge Base
        retrieval_response = retrieve_documents(query, top_k)
        
        if not retrieval_response.get('retrievalResults'):
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'answer': 'I cannot find specific information to answer your question. Please try rephrasing or contact NYC 311 for assistance.',
                    'citations': [],
                    'retrieval_time_ms': int((time.time() - start_time) * 1000)
                })
            }
        
        # Generate answer using retrieved context
        answer, citations = generate_answer(query, retrieval_response)
        
        total_time = int((time.time() - start_time) * 1000)
        
        # Log metrics
        logger.info(f"Query processed in {total_time}ms", extra={
            'query_length': len(query),
            'retrieval_time_ms': total_time,
            'citations_count': len(citations),
            'answer_length': len(answer)
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'answer': answer,
                'citations': citations,
                'retrieval_time_ms': total_time,
                'query': query
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

def retrieve_documents(query: str, top_k: int) -> Dict[str, Any]:
    """
    Retrieve relevant documents from Bedrock Knowledge Base.
    
    Args:
        query: User's question
        top_k: Number of documents to retrieve
        
    Returns:
        Retrieval response from Bedrock
    """
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': top_k
                }
            }
        )
        
        logger.info(f"Retrieved {len(response.get('retrievalResults', []))} documents")
        return response
        
    except ClientError as e:
        logger.error(f"Error retrieving documents: {e}")
        raise

def generate_answer(query: str, retrieval_response: Dict[str, Any]) -> tuple[str, List[Dict[str, str]]]:
    """
    Generate answer using retrieved context and Bedrock model.
    
    Args:
        query: User's question
        retrieval_response: Retrieved documents from Knowledge Base
        
    Returns:
        Tuple of (answer, citations)
    """
    # Prepare context from retrieved documents
    context_parts = []
    citations = []
    
    for result in retrieval_response.get('retrievalResults', []):
        content = result.get('content', {})
        text = content.get('text', '')
        metadata = content.get('metadata', {})
        
        if text:
            context_parts.append(text)
            
            # Extract citation information
            citation = {
                'text': text[:200] + '...' if len(text) > 200 else text,
                'source_url': metadata.get('source_url', ''),
                'title': metadata.get('title', ''),
                'section': metadata.get('section', ''),
                'relevance_score': result.get('score', 0)
            }
            citations.append(citation)
    
    if not context_parts:
        return "I cannot find specific information to answer your question.", []
    
    # Combine context
    context = "\n\n".join(context_parts)
    
    # Prepare prompt for Bedrock
    prompt = f"""You are a helpful assistant for NYC residents. Answer the user's question based on the provided context. 

Context:
{context}

Question: {query}

Instructions:
1. Answer the question using only the information provided in the context
2. Be specific and helpful
3. If the context doesn't contain enough information to answer the question, say so
4. Keep your answer concise but informative
5. Focus on practical steps and information NYC residents need

Answer:"""

    try:
        # Invoke Bedrock model (Titan Text Express)
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({
                "inputText": prompt,
                "textGenerationConfig": {
                    "temperature": 0.7,
                    "maxTokenCount": 1000,
                    "topP": 0.9,
                    "stopSequences": []
                }
            })
        )
        
        response_body = json.loads(response['body'].read())
        answer = response_body['results'][0]['outputText'].strip()
        
        # Clean up answer
        if answer.startswith("Answer:"):
            answer = answer[7:].strip()
        
        return answer, citations
        
    except ClientError as e:
        logger.error(f"Error generating answer: {e}")
        raise

def format_citations(citations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format citations for better readability.
    
    Args:
        citations: Raw citations from retrieval
        
    Returns:
        Formatted citations
    """
    formatted = []
    
    for citation in citations:
        formatted_citation = {
            'text': citation['text'],
            'source': citation['source_url'] or 'Unknown source',
            'title': citation['title'] or 'No title',
            'section': citation['section'] or 'No section',
            'relevance': round(citation['relevance_score'], 3) if citation['relevance_score'] else 0
        }
        formatted.append(formatted_citation)
    
    return formatted
