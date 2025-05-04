import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus


class IntegrationAgent:
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
        self.completion_status = {
            "frontend": False,
            "backend": False
        }
        self.code_content = {
            "frontend": None,
            "backend": None
        }

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        # Initialize consumer and producer
        self.consumer = AIOKafkaConsumer(
            self.topics["frontend_code"],
            self.topics["backend_code"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="integration-agent-group",
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
        """Handle frontend code integration."""
        if "content" not in message:
            return

        logger.info("Received frontend code...")
        self.code_content["frontend"] = message["content"]
        self.completion_status["frontend"] = True
        await self.check_completion()

    async def handle_backend_code(self, message):
        """Handle backend code integration."""
        if "content" not in message:
            return

        logger.info("Received backend code...")
        self.code_content["backend"] = message["content"]
        self.completion_status["backend"] = True
        await self.check_completion()

    async def check_completion(self):
        """Check if both frontend and backend code are received."""
        if all(self.completion_status.values()):
            logger.info("Both frontend and backend code received, generating documentation...")
            await self.generate_documentation()

    async def generate_documentation(self):
        """Generate comprehensive project documentation."""
        # Create docs directory if it doesn't exist
        docs_dir = os.path.join(os.getcwd(), "workspace", "docs")
        os.makedirs(docs_dir, exist_ok=True)

        prompt = f"""
        Please generate comprehensive project documentation based on the following code:

        Frontend Code:
        {self.code_content['frontend']}

        Backend Code:
        {self.code_content['backend']}

        The documentation should include:

        1. Project Overview
           - Project name and description
           - Features and functionality
           - Technology stack
           - Architecture overview

        2. Installation and Setup
           - Prerequisites
           - Installation steps
           - Configuration
           - Environment setup

        3. API Documentation
           - API endpoints
           - Request/response formats
           - Error handling
           - Example requests

        4. Frontend Documentation
           - Component structure
           - State management
           - API integration
           - User interface

        5. Backend Documentation
           - Server setup
           - Database schema
           - API implementation
           - Error handling

        6. Development Guide
           - Development environment setup
           - Code structure
           - Testing
           - Deployment

        7. Troubleshooting
           - Common issues
           - Error messages
           - Debugging tips
           - Performance optimization

        Save the documentation to docs/README.md.
        The documentation should be comprehensive and well-organized.
        """

        result = await self.agent.run(prompt)

        # Send completion notification
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "integration",
                "message": "Documentation generation completed"
            }).encode()
        )
        logger.info("Documentation generation completed")

    async def cleanup(self):
        """Clean up resources."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Integration agent stopped")


async def main():
    agent = IntegrationAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Integration agent initialized and listening for updates...")
        await agent.process_messages()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
