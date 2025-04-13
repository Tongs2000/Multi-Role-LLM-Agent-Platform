import asyncio
import json
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger

from app.agent.manus import Manus


class FrontendAgent:
    def __init__(self):
        self.agent = Manus()
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "requirements": "frontend-requirements",
            "backend_updates": "backend-updates",
            "frontend_bugs": "frontend-bugs",
            "backend_api_spec": "backend-api-spec"
        }
        self.current_requirement = None
        self.api_spec = None
        self.requirement_event = asyncio.Event()
        self.api_spec_event = asyncio.Event()

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["requirements"],
            self.topics["backend_api_spec"],
            self.topics["frontend_bugs"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="frontend-agent-group",
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
                    self.current_requirement = data
                    self.requirement_event.set()
                    await self.handle_requirement(data)
                elif msg.topic == self.topics["backend_api_spec"]:
                    # 处理后端API规范
                    logger.info(f"Received API spec: {data}")
                    self.api_spec = data
                    self.api_spec_event.set()
                    await self.handle_api_spec(data)
                elif msg.topic == self.topics["frontend_bugs"]:
                    # 处理 bug 报告
                    logger.info(f"Received bug report: {data}")
                    await self.handle_bug(data)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def handle_requirement(self, requirement: dict):
        """Handle a new requirement using the agent."""
        try:
            # 等待API规范
            logger.info("Waiting for API specification from backend...")
            await self.api_spec_event.wait()

            # 使用 agent 处理需求
            prompt = f"""
            As a frontend developer, please help implement the following requirement:
            {requirement['content']}

            The backend team has provided the following API specification:
            {self.api_spec}

            Please:
            1. Analyze the requirements and API specification
            2. Design the UI/UX
            3. Implement the frontend code that uses the provided API
            4. Make sure to properly integrate with the backend API

            Important: Use GET requests for the API calls:
            - Example: fetch('http://localhost:5001/api/random?min=1&max=100')
            - The response will be in JSON format: {{"result": number}}
            """

            result = await self.agent.run(prompt)

            # 发送进度更新
            await self.producer.send_and_wait(
                self.topics["backend_updates"],
                json.dumps({
                    "type": "progress",
                    "content": result
                }).encode()
            )

        except Exception as e:
            logger.error(f"Error handling requirement: {e}")

    async def handle_api_spec(self, api_spec: dict):
        """Handle API specification from backend."""
        try:
            if self.current_requirement:
                # 如果已经有需求在等待，重新处理需求
                await self.handle_requirement(self.current_requirement)
        except Exception as e:
            logger.error(f"Error handling API spec: {e}")

    async def handle_bug(self, bug_report: dict):
        """Handle bug report from test agent."""
        try:
            prompt = f"""
            The test team has reported the following bug in the frontend:
            {bug_report['content']}

            Please:
            1. Analyze the bug report
            2. Fix the issue
            3. Share your progress with the test team
            """

            result = await self.agent.run(prompt)

            # 发送修复更新
            await self.producer.send_and_wait(
                self.topics["backend_updates"],
                json.dumps({
                    "type": "bug_fix",
                    "content": result
                }).encode()
            )

        except Exception as e:
            logger.error(f"Error handling bug: {e}")

    async def cleanup(self):
        """Clean up resources."""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        await self.agent.cleanup()


async def main():
    agent = FrontendAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Frontend agent initialized and listening for requirements...")
        await agent.process_requirements()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
