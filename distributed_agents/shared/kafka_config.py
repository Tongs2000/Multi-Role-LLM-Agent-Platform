"""Shared Kafka configuration for all agents"""

KAFKA_CONFIG = {
    'bootstrap_servers': 'localhost:9092',
    'auto_offset_reset': 'latest',
    'security_protocol': 'PLAINTEXT',
    'client_id': 'openmanus-agent',
    'request_timeout_ms': 30000,
    'retry_backoff_ms': 1000
}

# Kafka topics
TOPICS = {
    'user_queries': 'user-queries',
    'search_requests': 'search-requests',
    'search_results': 'search-results',
    'frontend_requirements': 'frontend-requirements',
    'backend_requirements': 'backend-requirements',
    'backend_api_spec': 'backend-api-spec',
    'frontend_bugs': 'frontend-bugs',
    'backend_bugs': 'backend-bugs',
    'test_results': 'test-results',
    'project_updates': 'project-updates',
    'code_updates': 'code-updates'
}
