import asyncio
import json
from aiokafka import AIOKafkaProducer
from loguru import logger


class TaskLauncher:
    def __init__(self):
        self.kafka_bootstrap_servers = "localhost:9092"
        self.producer = None
        self.topics = {
            "frontend_requirements": "frontend-requirements",
            "backend_requirements": "backend-requirements",
            "test_requirements": "test-requirements"
        }

    async def initialize_kafka(self):
        """Initialize Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers
        )
        await self.producer.start()

    async def send_task(self, task_description: str):
        """Send task description to all agents."""
        try:
            # 发送任务到前端 Agent
            await self.producer.send_and_wait(
                self.topics["frontend_requirements"],
                json.dumps({
                    "type": "task",
                    "content": task_description
                }).encode()
            )
            logger.info("Sent task to frontend agent")

            # 发送任务到后端 Agent
            await self.producer.send_and_wait(
                self.topics["backend_requirements"],
                json.dumps({
                    "type": "task",
                    "content": task_description
                }).encode()
            )
            logger.info("Sent task to backend agent")

            # 发送任务到测试 Agent
            await self.producer.send_and_wait(
                self.topics["test_requirements"],
                json.dumps({
                    "type": "task",
                    "content": task_description
                }).encode()
            )
            logger.info("Sent task to test agent")

        except Exception as e:
            logger.error(f"Error sending task: {e}")

    async def cleanup(self):
        """Clean up resources."""
        if self.producer:
            await self.producer.stop()


async def main():
    launcher = TaskLauncher()
    try:
        await launcher.initialize_kafka()

        # 从用户输入获取任务描述
        print("Please enter the task description (press Ctrl+D when done):")
        task_description = ""
        while True:
            try:
                line = input()
                task_description += line + "\n"
            except EOFError:
                break

        if not task_description.strip():
            print("No task description provided. Exiting.")
            return

        # 发送任务
        await launcher.send_task(task_description.strip())
        print("Task has been sent to all agents.")

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await launcher.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
