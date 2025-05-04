import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus


class RetrievalAgent:
    def __init__(self):
        self.agent = Manus(max_steps=3)
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "search_requests": "search-requests",
            "search_results": "search-results",
            "user_queries": "user-queries"
        }
        self.project_completed = False
        self.force_completed = False

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["search_requests"],
            self.topics["user_queries"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="retrieval-agent-group",
            max_poll_interval_ms=300000,
            max_poll_records=10,
            auto_offset_reset='latest'
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers
        )
        await self.consumer.start()
        await self.producer.start()

    async def process_messages(self):
        """Process messages from Kafka topics."""
        try:
            async for msg in self.consumer:
                try:
                    message = json.loads(msg.value.decode())
                    topic = msg.topic

                    # Check for completion notifications
                    if "type" in message:
                        if message["type"] == "completion":
                            self.project_completed = True
                            logger.info("Received project completion notification")
                            break
                        elif message["type"] == "force_completion":
                            self.force_completed = True
                            logger.info("Received force completion notification")
                            break

                    if topic == self.topics["search_requests"]:
                        await self.handle_search_request(message)
                    elif topic == self.topics["user_queries"]:
                        await self.handle_user_query(message)

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Error in process_messages: {e}")

    async def handle_search_request(self, message):
        """Handle search request."""
        if "content" not in message:
            return

        logger.info("Processing search request...")
        prompt = f"""
        Please search for information about:
        {message['content']}

        Focus on:
        1. Game mechanics
        2. Implementation details
        3. Best practices
        4. Common issues
        5. Performance considerations

        Provide relevant code examples and documentation.
        """

        result = await self.agent.run(prompt)

        # Send search results
        await self.producer.send_and_wait(
            self.topics["search_results"],
            json.dumps({
                "type": "search",
                "content": result
            }).encode()
        )
        logger.info("Sent search results")

    async def handle_user_query(self, message):
        """Handle user query."""
        if "content" not in message:
            return

        logger.info("Processing user query...")
        # 直接转发到 search_requests
        await self.producer.send_and_wait(
            self.topics["search_requests"],
            json.dumps({
                "type": "search",
                "content": message["content"]
            }).encode()
        )
        logger.info("Forwarded user query to search request")

    async def cleanup(self):
        """Clean up resources."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Retrieval agent stopped")


async def main():
    agent = RetrievalAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Retrieval agent initialized and listening for updates...")
        await agent.process_messages()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
