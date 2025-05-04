import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agent.manus import Manus


class PlanningAgent:
    def __init__(self):
        self.agent = Manus(max_steps=1)
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "user_queries": "user-queries",
            "search_results": "search-results",
            "search_requests": "search-requests",
            "frontend_requirements": "frontend-requirements",
            "backend_requirements": "backend-requirements"
        }
        self.project_completed = False
        self.force_completed = False

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["user_queries"],
            self.topics["search_results"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="planning-agent-group",
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

                    if topic == self.topics["user_queries"]:
                        await self.handle_user_query(message)
                    elif topic == self.topics["search_results"]:
                        await self.handle_search_results(message)

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Error in process_messages: {e}")

    async def handle_user_query(self, message):
        """Handle user query and generate requirements."""
        if "content" not in message:
            return

        logger.info("Received user query, sending to retrieval agent...")
        # Send search request to retrieval agent
        await self.producer.send_and_wait(
            self.topics["search_requests"],
            json.dumps({
                "type": "search",
                "content": message["content"]
            }).encode()
        )
        logger.info("Sent search request to retrieval agent")

        # Start generating initial requirements immediately
        logger.info("Generating initial requirements...")
        await self.generate_requirements(message["content"])

        # Send completion notification
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "planning",
                "message": "Initial requirements generation completed"
            }).encode()
        )
        logger.info("Planning agent completed initial requirements generation")

    async def generate_requirements(self, content):
        """Generate requirements based on content."""
        try:
            prompt = f"""
            Based on the following task, generate detailed requirements:

            Task:
            {content}

            Please provide:

            1. Frontend Requirements:
               - User interface components
               - User interactions
               - Visual elements
               - State management
               - API integration points

            2. Backend Requirements:
               - API endpoints
               - Data models
               - Business logic
               - Data storage
               - Configuration management

            The requirements should be clear, implementable, and directly related to the task at hand.
            """

            result = await self.agent.run(prompt)

            # Send to frontend and backend agents
            await self.producer.send_and_wait(
                self.topics["frontend_requirements"],
                json.dumps({
                    "type": "requirements",
                    "content": result,
                    "component": "frontend"
                }).encode()
            )
            logger.info("Sent frontend requirements")

            await self.producer.send_and_wait(
                self.topics["backend_requirements"],
                json.dumps({
                    "type": "requirements",
                    "content": result,
                    "component": "backend"
                }).encode()
            )
            logger.info("Sent backend requirements")

        except Exception as e:
            logger.error(f"Error generating requirements: {e}")
            # Send error update
            await self.producer.send_and_wait(
                "updates",
                json.dumps({
                    "type": "error",
                    "content": str(e),
                    "component": "planning"
                }).encode()
            )

    async def handle_search_results(self, message):
        """Handle search results and generate requirements."""
        if "content" not in message:
            return

        logger.info("Evaluating search results for potential requirement updates...")

        prompt = f"""
        Based on the following search results, evaluate if they provide valuable insights that would improve our initial requirements:

        Search Results:
        {message['content']}

        Please:
        1. Review the search results
        2. Compare with initial requirements
        3. Only if the search results provide significant new insights or improvements, generate updated requirements

        If the search results are valuable, provide:

        1. Frontend Requirements Updates:
           - New or modified UI components
           - Enhanced user interactions
           - Additional visual elements
           - Updated state management
           - New API integration points

        2. Backend Requirements Updates:
           - New or modified API endpoints
           - Updated data models
           - Enhanced business logic
           - Additional data storage needs
           - New configuration requirements

        If the search results don't provide significant value, simply respond with "No significant updates needed."
        """

        result = await self.agent.run(prompt)

        # Only send updates if search results are valuable
        if "no significant updates needed" not in result.lower():
            # Send frontend and backend requirement updates
            await self.producer.send_and_wait(
                self.topics["frontend_requirements"],
                json.dumps({
                    "type": "requirements_update",
                    "content": result,
                    "component": "frontend"
                }).encode()
            )
            logger.info("Sent frontend requirements update")

            await self.producer.send_and_wait(
                self.topics["backend_requirements"],
                json.dumps({
                    "type": "requirements_update",
                    "content": result,
                    "component": "backend"
                }).encode()
            )
            logger.info("Sent backend requirements update")
        else:
            logger.info("Search results don't provide significant value, no updates needed")

        # Send completion notification
        await self.producer.send_and_wait(
            "updates",
            json.dumps({
                "type": "completion",
                "component": "planning",
                "message": "Requirements evaluation completed"
            }).encode()
        )
        logger.info("Planning agent completed requirements evaluation")

    async def cleanup(self):
        """Clean up resources."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Planning agent stopped")


async def main():
    agent = PlanningAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Planning agent initialized and listening for updates...")
        await agent.process_messages()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
