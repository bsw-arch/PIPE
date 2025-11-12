"""
Domain Router - Routes queries to appropriate domain services via Kafka
"""

from typing import List, Dict, Any
from aiokafka import AIOKafkaProducer
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DomainRouter:
    """Routes queries to appropriate domain services"""

    def __init__(self, kafka_brokers: List[str]):
        self.kafka_brokers = kafka_brokers
        self.producer: AIOKafkaProducer = None

    async def initialise(self):
        """Initialise Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip',
            acks='all'
        )

        await self.producer.start()
        logger.info("Domain Router initialised with Kafka")

    async def route_query(self,
                         query: str,
                         target_domains: List[str],
                         context: 'UserContext') -> Dict[str, Any]:
        """
        Route query to target domains via Kafka topics

        Returns routing information
        """
        routing_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'domains': target_domains,
            'status': {}
        }

        for domain in target_domains:
            try:
                # Prepare message
                message = {
                    'query': query,
                    'context': {
                        'user_id': context.user_id,
                        'session_id': context.session_id,
                        'preferences': context.domain_preferences,
                        'metadata': context.metadata
                    },
                    'domain': domain,
                    'timestamp': datetime.utcnow().isoformat()
                }

                # Send to domain-specific topic
                topic = f"cag.{domain.lower()}.queries"

                await self.producer.send(
                    topic,
                    value=message,
                    key=context.session_id.encode('utf-8')
                )

                routing_info['status'][domain] = 'routed'

                logger.debug(f"Routed query to {domain} via topic {topic}")

            except Exception as e:
                logger.error(f"Failed to route to {domain}: {e}")
                routing_info['status'][domain] = f'failed: {str(e)}'

        return routing_info

    async def close(self):
        """Close Kafka producer"""
        if self.producer:
            await self.producer.stop()
        logger.info("Domain Router closed")
