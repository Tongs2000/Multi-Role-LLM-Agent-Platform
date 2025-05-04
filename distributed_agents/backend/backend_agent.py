import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus


class BackendAgent:
    def __init__(self):
        self.agent = Manus(max_steps=5)
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "requirements": "backend-requirements",
            "updates": "backend-updates",
            "frontend_updates": "frontend-updates",
            "bugs": "backend-bugs",
            "backend_code": "backend-code"
        }

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["requirements"],
            self.topics["bugs"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="backend-agent-group",
            max_poll_interval_ms=300000,  # Increased to 5 minutes
            max_poll_records=10,  # Reduced number of messages per fetch
            auto_offset_reset='latest'  # Only read latest messages
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers
        )
        await self.consumer.start()
        await self.producer.start()

    async def process_requirements(self):
        """Process requirements from Kafka."""
        async for msg in self.consumer:
            try:
                data = json.loads(msg.value.decode())
                if msg.topic == self.topics["requirements"]:
                    # Process new requirements
                    logger.info(f"Received new requirement: {data}")
                    await self.handle_requirements(data)
                elif msg.topic == self.topics["frontend_updates"]:
                    # Process frontend updates
                    logger.info(f"Received frontend update: {data}")
                    await self.handle_frontend_update(data)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def handle_requirements(self, message):
        """Handle backend requirements."""
        if "content" not in message:
            return

        logger.info("Processing backend requirements...")
        prompt = f"""
        Please implement the following backend requirements:
        {message['content']}

        Consider:
        1. API endpoints
        2. Database schema
        3. Business logic
        4. Error handling
        5. Security

        Provide complete backend code implementation.
        The code will be saved to the workspace directory.
        """

        result = await self.agent.run(prompt)

        # Send backend code to Kafka for validation
        await self.producer.send_and_wait(
            self.topics["backend_code"],
            json.dumps({
                "type": "code",
                "component": "backend",
                "content": result,
                "status": "completed"
            }).encode()
        )
        logger.info("Backend code completed and sent to Kafka for validation")

        # Send completion notification
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "backend",
                "message": "Backend agent completed its task"
            }).encode()
        )
        logger.info("Backend agent task completed")

    async def handle_validation_feedback(self, message):
        """Handle validation feedback and fix issues."""
        if "content" not in message or "type" not in message or message["type"] != "validation_feedback":
            return

        logger.info("Processing validation feedback...")
        prompt = f"""
        Please fix the following issues in the backend code:
        {message['content']}

        The code is in the workspace directory.
        Please update the files directly.
        """

        result = await self.agent.run(prompt)
        logger.info("Backend code updated based on validation feedback")

    async def handle_frontend_update(self, update: dict):
        """Handle updates from frontend."""
        try:
            if update["type"] == "api_requirements":
                # Process frontend API requirements
                prompt = f"""
                The frontend team has requested the following API:
                {update['content']}

                Please implement these API endpoints and share the specifications.
                """

                result = await self.agent.run(prompt)

                # Send API specifications
                await self.producer.send_and_wait(
                    "frontend-api-spec",
                    json.dumps({
                        "type": "api_spec",
                        "content": result
                    }).encode()
                )

        except Exception as e:
            logger.error(f"Error handling frontend update: {e}")

    async def cleanup(self):
        """Clean up resources."""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        await self.agent.cleanup()


async def main():
    agent = BackendAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Backend agent initialized and listening for requirements...")
        await agent.process_requirements()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
