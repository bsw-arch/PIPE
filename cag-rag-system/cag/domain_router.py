#!/usr/bin/env python3
"""
BSW-Arch CAG Layer - Domain Router
Routes queries to appropriate domain services and aggregates responses
"""

from typing import Dict, List, Any, Optional
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)


class DomainRouter:
    """
    Routes queries to appropriate bot domain services

    Responsibilities:
    - Parallel routing to multiple domains
    - Response aggregation
    - Error handling and retries
    - Load balancing
    """

    def __init__(self, domain_config: Dict[str, Any]):
        """
        Initialize Domain Router

        Args:
            domain_config: Dictionary mapping domain names to config:
                {
                    'AXIS': {
                        'endpoint': 'http://axis-orchestrator:8000',
                        'auth_token': 'token',
                        'timeout': 30
                    },
                    ...
                }
        """
        self.domain_config = domain_config
        self.clients = {}

        # Initialize HTTP clients for each domain
        for domain, config in domain_config.items():
            timeout = config.get('timeout', 30)
            self.clients[domain] = httpx.AsyncClient(
                timeout=timeout,
                headers=self._build_headers(config)
            )

        logger.info(f"Domain Router initialized for {len(domain_config)} domains")

    def _build_headers(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Build HTTP headers for domain requests"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'BSW-Arch-CAG-Router/1.0'
        }

        auth_token = config.get('auth_token')
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'

        return headers

    async def route_query(self,
                         query: str,
                         target_domains: List[str],
                         context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Route query to target domains and collect responses

        Args:
            query: User query
            target_domains: List of domain names to query
            context: Optional user context

        Returns:
            Dictionary mapping domain names to responses
        """
        logger.info(f"Routing query to domains: {target_domains}")

        # Prepare routing tasks
        routing_tasks = []
        for domain in target_domains:
            if domain in self.clients:
                task = self._route_to_domain(
                    domain=domain,
                    query=query,
                    context=context
                )
                routing_tasks.append(task)
            else:
                logger.warning(f"Domain {domain} not configured, skipping")

        # Execute routing in parallel
        results = await asyncio.gather(*routing_tasks, return_exceptions=True)

        # Aggregate results
        aggregated_results = {}
        for domain, result in zip(target_domains, results):
            if isinstance(result, Exception):
                logger.error(f"Domain {domain} failed: {result}")
                aggregated_results[domain] = {
                    'error': str(result),
                    'status': 'failed',
                    'domain': domain
                }
            else:
                aggregated_results[domain] = result

        logger.info(
            f"Routing complete: {len(aggregated_results)} domains, "
            f"{sum(1 for r in aggregated_results.values() if r.get('status') != 'failed')} successful"
        )

        return aggregated_results

    async def _route_to_domain(self,
                              domain: str,
                              query: str,
                              context: Optional[Any]) -> Dict[str, Any]:
        """
        Route query to specific domain

        Args:
            domain: Domain name
            query: User query
            context: User context

        Returns:
            Domain response dictionary
        """
        config = self.domain_config[domain]
        endpoint = config['endpoint']
        client = self.clients[domain]

        # Prepare request payload
        request_payload = {
            'query': query,
            'domain': domain,
        }

        # Add context if provided
        if context:
            request_payload['context'] = {
                'user_id': getattr(context, 'user_id', None),
                'session_id': getattr(context, 'session_id', None),
                'preferences': getattr(context, 'domain_preferences', []),
                'metadata': getattr(context, 'metadata', {})
            }

        try:
            # Send request to domain service
            logger.debug(f"Sending request to {domain} at {endpoint}")

            response = await client.post(
                f"{endpoint}/api/v1/process",
                json=request_payload
            )

            response.raise_for_status()

            result = response.json()
            result['status'] = 'success'
            result['domain'] = domain

            logger.debug(f"Received response from {domain}")

            return result

        except httpx.TimeoutException as e:
            logger.error(f"Timeout routing to {domain}: {e}")
            return {
                'error': f'Timeout: {str(e)}',
                'status': 'timeout',
                'domain': domain
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error routing to {domain}: {e}")
            return {
                'error': f'HTTP {e.response.status_code}: {str(e)}',
                'status': 'http_error',
                'domain': domain,
                'status_code': e.response.status_code
            }

        except Exception as e:
            logger.error(f"Error routing to {domain}: {e}", exc_info=True)
            return {
                'error': str(e),
                'status': 'error',
                'domain': domain
            }

    async def route_to_single_domain(self,
                                    domain: str,
                                    query: str,
                                    context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Route query to a single domain (convenience method)

        Args:
            domain: Domain name
            query: User query
            context: User context

        Returns:
            Domain response
        """
        results = await self.route_query(query, [domain], context)
        return results.get(domain, {})

    def get_available_domains(self) -> List[str]:
        """Get list of configured domains"""
        return list(self.domain_config.keys())

    def get_domain_info(self, domain: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration info for a domain

        Args:
            domain: Domain name

        Returns:
            Domain configuration or None
        """
        return self.domain_config.get(domain)

    async def health_check(self) -> Dict[str, bool]:
        """
        Check health of all configured domains

        Returns:
            Dictionary mapping domain names to health status
        """
        logger.info("Performing health check on all domains")

        health_tasks = []
        for domain in self.domain_config.keys():
            health_tasks.append(self._check_domain_health(domain))

        results = await asyncio.gather(*health_tasks, return_exceptions=True)

        health_status = {}
        for domain, result in zip(self.domain_config.keys(), results):
            if isinstance(result, Exception):
                health_status[domain] = False
            else:
                health_status[domain] = result

        logger.info(f"Health check complete: {health_status}")

        return health_status

    async def _check_domain_health(self, domain: str) -> bool:
        """Check health of a single domain"""
        config = self.domain_config[domain]
        endpoint = config['endpoint']
        client = self.clients[domain]

        try:
            response = await client.get(
                f"{endpoint}/health",
                timeout=5.0
            )
            return response.status_code == 200

        except Exception as e:
            logger.debug(f"Health check failed for {domain}: {e}")
            return False

    async def close(self):
        """Close all HTTP clients"""
        logger.info("Closing domain router clients")
        for client in self.clients.values():
            await client.aclose()
