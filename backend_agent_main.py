import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger

from app.agent.manus import Manus


class BackendAgent:
    def __init__(self):
        self.agent = Manus()
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "requirements": "backend-requirements",
            "updates": "backend-updates",
            "frontend_updates": "frontend-updates",
            "bugs": "backend-bugs"
        }

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["requirements"],
            self.topics["bugs"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="backend-agent-group",
            max_poll_interval_ms=300000,  # 增加为 5 分钟
            max_poll_records=10  # 减少每次拉取的消息数量
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
                    # 处理新的需求
                    logger.info(f"Received new requirement: {data}")
                    await self.handle_requirement(data)
                elif msg.topic == self.topics["frontend_updates"]:
                    # 处理前端更新
                    logger.info(f"Received frontend update: {data}")
                    await self.handle_frontend_update(data)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def handle_requirement(self, requirement: dict):
        """Handle a new requirement using the agent."""
        try:
            # 使用 agent 处理需求
            prompt = f"""
            As a backend developer, please help implement the following requirement:
            {requirement['content']}

            Please:
            1. Analyze the requirements
            2. Design the API endpoints
            3. Implement the backend code
            4. Share your progress and API specifications with the frontend team
            """

            result = await self.agent.run(prompt)

            # 发送进度更新
            await self.producer.send_and_wait(
                self.topics["updates"],
                json.dumps({
                    "type": "progress",
                    "content": result
                }).encode()
            )

        except Exception as e:
            logger.error(f"Error handling requirement: {e}")

    async def handle_frontend_update(self, update: dict):
        """Handle updates from frontend."""
        try:
            if update["type"] == "api_requirements":
                # 处理前端API需求
                prompt = f"""
                The frontend team has requested the following API:
                {update['content']}

                Please implement these API endpoints and share the specifications.
                """

                result = await self.agent.run(prompt)

                # 发送API规范
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
