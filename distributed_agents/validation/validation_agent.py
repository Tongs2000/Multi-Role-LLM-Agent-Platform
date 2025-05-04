import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus


class ValidationAgent:
    def __init__(self):
        self.agent = Manus(max_steps=3)
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "frontend_code": "frontend-code",
            "backend_code": "backend-code"
        }
        self.project_completed = False
        self.force_completed = False

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["frontend_code"],
            self.topics["backend_code"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="validation-agent-group",
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

                    if topic == self.topics["frontend_code"]:
                        await self.handle_frontend_code(message)
                    elif topic == self.topics["backend_code"]:
                        await self.handle_backend_code(message)

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Error in process_messages: {e}")

    async def handle_frontend_code(self, message):
        """Handle frontend code validation."""
        if "content" not in message:
            return

        logger.info("Validating frontend code...")
        prompt = f"""
        Please validate the following frontend code:
        {message['content']}

        Consider:
        1. Code quality
        2. Performance
        3. Security
        4. Best practices
        5. Compatibility

        Provide validation results and recommendations.
        """

        result = await self.agent.run(prompt)

        # Send validation results
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "validation",
                "message": "Frontend validation completed"
            }).encode()
        )
        logger.info("Frontend validation completed and results sent")

    async def handle_backend_code(self, message):
        """Handle backend code validation."""
        if "content" not in message:
            return

        logger.info("Validating backend code...")
        prompt = f"""
        Please validate the following backend code:
        {message['content']}

        Consider:
        1. Code quality
        2. Performance
        3. Security
        4. Best practices
        5. Error handling

        Provide validation results and recommendations.
        """

        result = await self.agent.run(prompt)

        # Send validation results
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "validation",
                "message": "Backend validation completed"
            }).encode()
        )
        logger.info("Backend validation completed and results sent")

    async def cleanup(self):
        """Clean up resources."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Validation agent stopped")


async def main():
    agent = ValidationAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Validation agent initialized and listening for updates...")
        await agent.process_messages()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
