import asyncio
import json
import requests
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger

from app.agent.manus import Manus


class TestAgent:
    def __init__(self):
        self.agent = Manus()
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "requirements": "test-requirements",
            "frontend_updates": "frontend-updates",
            "backend_updates": "backend-updates",
            "frontend_bugs": "frontend-bugs",
            "backend_bugs": "backend-bugs",
            "test_results": "test-results"
        }
        self.current_requirement = None
        self.frontend_url = None
        self.backend_url = None

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            self.topics["requirements"],
            self.topics["frontend_updates"],
            self.topics["backend_updates"],
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="test-agent-group",
            max_poll_interval_ms=300000,  # 增加为 5 分钟
            max_poll_records=10  # 减少每次拉取的消息数量
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers
        )
        await self.consumer.start()
        await self.producer.start()

    async def process_updates(self):
        """Process updates from frontend and backend."""
        async for msg in self.consumer:
            try:
                data = json.loads(msg.value.decode())
                if msg.topic == self.topics["requirements"]:
                    # 处理新的测试需求
                    logger.info(f"Received new test requirement: {data}")
                    self.current_requirement = data
                    await self.generate_test_plan(data)
                elif msg.topic == self.topics["frontend_updates"]:
                    # 处理前端更新
                    logger.info(f"Received frontend update: {data}")
                    if "url" in data:
                        self.frontend_url = data["url"]
                    await self.run_tests()
                elif msg.topic == self.topics["backend_updates"]:
                    # 处理后端更新
                    logger.info(f"Received backend update: {data}")
                    if "url" in data:
                        self.backend_url = data["url"]
                    await self.run_tests()
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    async def generate_test_plan(self, requirement: dict):
        """Generate test plan based on requirements."""
        try:
            prompt = f"""
            As a test engineer, please help create a comprehensive test plan for the following requirement:
            {requirement['content']}

            Please:
            1. Analyze the requirements and identify test scenarios
            2. Design test cases for both frontend and backend
            3. Create automated test scripts
            4. Specify test data and expected results
            5. Document test environment requirements

            The test plan should include:
            - Functional tests
            - Integration tests
            - Error handling tests
            - Performance tests (if applicable)
            - Security tests (if applicable)
            """

            result = await self.agent.run(prompt)

            # 发送测试计划
            await self.producer.send_and_wait(
                self.topics["test_results"],
                json.dumps({
                    "type": "test_plan",
                    "content": result
                }).encode()
            )

        except Exception as e:
            logger.error(f"Error generating test plan: {e}")

    async def run_tests(self):
        """Run tests based on the current test plan."""
        try:
            if not self.current_requirement:
                logger.warning("No test requirement available")
                return

            prompt = f"""
            Based on the following requirement and test plan, please:
            1. Generate test code for both frontend and backend
            2. Implement automated tests
            3. Run the tests and collect results
            4. Report any issues found

            Requirement:
            {self.current_requirement['content']}

            Frontend URL: {self.frontend_url}
            Backend URL: {self.backend_url}
            """

            result = await self.agent.run(prompt)

            # 发送测试结果
            await self.producer.send_and_wait(
                self.topics["test_results"],
                json.dumps({
                    "type": "test_execution",
                    "content": result
                }).encode()
            )

        except Exception as e:
            logger.error(f"Error running tests: {e}")

    async def report_bug(self, bug_report: dict):
        """Report a bug to the appropriate team."""
        try:
            if bug_report["component"] == "backend":
                topic = self.topics["backend_bugs"]
            else:
                topic = self.topics["frontend_bugs"]

            await self.producer.send_and_wait(
                topic,
                json.dumps({
                    "type": "bug_report",
                    "content": bug_report
                }).encode()
            )

        except Exception as e:
            logger.error(f"Error reporting bug: {e}")

    async def cleanup(self):
        """Clean up resources."""
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        await self.agent.cleanup()


async def main():
    agent = TestAgent()
    try:
        await agent.initialize_kafka()
        logger.info("Test agent initialized and listening for requirements...")
        await agent.process_updates()
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
