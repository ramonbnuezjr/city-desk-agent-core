import json
import logging
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Environment variables
API_KEY = os.environ['API_KEY']

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda authorizer for API Gateway HTTP API.
    
    Args:
        event: API Gateway authorizer event
        context: Lambda context
        
    Returns:
        IAM policy document for authorization
    """
    try:
        # Extract API key from headers
        headers = event.get('headers', {})
        api_key = headers.get('x-api-key', '')
        
        logger.info(f"Authorizing request with API key: {api_key[:8]}...")
        
        # Validate API key
        if api_key == API_KEY:
            logger.info("API key validation successful")
            return generate_policy('Allow', event['methodArn'])
        else:
            logger.warning("API key validation failed")
            return generate_policy('Deny', event['methodArn'])
            
    except Exception as e:
        logger.error(f"Error in authorizer: {str(e)}", exc_info=True)
        return generate_policy('Deny', event['methodArn'])

def generate_policy(effect: str, resource: str) -> Dict[str, Any]:
    """
    Generate IAM policy document for API Gateway authorization.
    
    Args:
        effect: 'Allow' or 'Deny'
        resource: API Gateway resource ARN
        
    Returns:
        IAM policy document
    """
    return {
        'principalId': 'user',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
