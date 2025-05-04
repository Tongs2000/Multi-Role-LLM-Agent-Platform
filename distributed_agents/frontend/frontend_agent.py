import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus


class FrontendAgent:
    def __init__(self):
        self.agent = Manus(max_steps=5)
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "frontend_requirements": "frontend-requirements",
            "frontend_code": "frontend-code",
            "backend_api": "backend-api",
            "frontend_bugs": "frontend-bugs"
        }
        self.project_completed = False
        self.force_completed = False

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["frontend_requirements"],
            self.topics["backend_api"],
            self.topics["frontend_bugs"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="frontend-agent-group",
            max_poll_interval_ms=300000,  # Increased to 5 minutes
            max_poll_records=10  # Reduced number of messages per fetch
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
                            # Send final frontend code
                            await self.send_final_code()
                            break

                    if topic == self.topics["frontend_requirements"]:
                        await self.handle_requirements(message)
                    elif topic == self.topics["backend_api"]:
                        await self.handle_backend_api(message)
                    elif topic == self.topics["frontend_bugs"]:
                        await self.handle_bugs(message)

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Error in process_messages: {e}")

    async def send_final_code(self):
        """Send final frontend code before stopping."""
        if not self.force_completed:
            return

        logger.info("Sending final frontend code...")
        final_message = {
            "type": "code",
            "status": "force_completed",
            "message": "Frontend code completed due to time limit",
            "content": "Final frontend code sent before time limit reached."
        }

        await self.producer.send_and_wait(
            self.topics["frontend_code"],
            json.dumps(final_message).encode()
        )
        logger.info("Sent final frontend code")

    async def handle_requirements(self, message):
        """Handle frontend requirements."""
        if "content" not in message:
            return

        logger.info("Processing frontend requirements...")
        prompt = f"""
        Please implement the following frontend requirements:
        {message['content']}

        Consider:
        1. User interface design
        2. Component structure
        3. State management
        4. API integration
        5. Error handling

        Provide complete frontend code implementation.
        The code will be saved to the workspace directory.
        """

        result = await self.agent.run(prompt)

        # Send frontend code to Kafka for validation
        await self.producer.send_and_wait(
            self.topics["frontend_code"],
            json.dumps({
                "type": "code",
                "component": "frontend",
                "content": result,
                "status": "completed"
            }).encode()
        )
        logger.info("Frontend code completed and sent to Kafka for validation")

        # Send completion notification
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "frontend",
                "message": "Frontend agent completed its task"
            }).encode()
        )
        logger.info("Frontend agent task completed")

    async def handle_validation_feedback(self, message):
        """Handle validation feedback and fix issues."""
        if "content" not in message or "type" not in message or message["type"] != "validation_feedback":
            return

        logger.info("Processing validation feedback...")
        prompt = f"""
        Please fix the following issues in the frontend code:
        {message['content']}

        The code is in the workspace directory.
        Please update the files directly.
        """

        result = await self.agent.run(prompt)
        logger.info("Frontend code updated based on validation feedback")

    async def handle_backend_api(self, message):
        """Handle backend API specifications."""
        if "content" not in message:
            return

        logger.info("Processing backend API specifications...")
        prompt = f"""
        Please update frontend code based on the following backend API specifications:
        {message['content']}

        Consider:
        1. API endpoints
        2. Request/response formats
        3. Error handling
        4. Authentication

        Update frontend code accordingly.
        """

        result = await self.agent.run(prompt)

        # Send updated frontend code
        await self.producer.send_and_wait(
            self.topics["frontend_code"],
            json.dumps({
                "type": "code",
                "component": "frontend",
                "content": result,
                "status": "completed"
            }).encode()
        )
        logger.info("Sent updated frontend code")

    async def handle_bugs(self, message):
        """Handle frontend bug reports."""
        if "content" not in message:
            return

        logger.info("Processing frontend bug report...")
        prompt = f"""
        Please fix the following frontend bug:
        {message['content']}

        Consider:
        1. Bug description
        2. Root cause
        3. Impact
        4. Solution

        Provide fixed frontend code.
        """

        result = await self.agent.run(prompt)

        # Send fixed frontend code
        await self.producer.send_and_wait(
            self.topics["frontend_code"],
            json.dumps({
                "type": "code",
                "component": "frontend",
                "content": result,
                "status": "completed"
            }).encode()
        )
        logger.info("Sent fixed frontend code")

    async def cleanup(self):
        """Clean up resources."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Frontend agent stopped")


async def main():
    agent = FrontendAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Frontend agent initialized and listening for requirements...")
        await agent.process_messages()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
