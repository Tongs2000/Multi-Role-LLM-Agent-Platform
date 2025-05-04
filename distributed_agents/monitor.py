import asyncio
import json
import time
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ProjectMonitor:
    def __init__(self):
        self.kafka_bootstrap_servers = "localhost:9092"
        self.consumer = None
        self.producer = None
        self.topics = {
            "user_queries": "user-queries",
            "frontend_requirements": "frontend-requirements",
            "backend_requirements": "backend-requirements",
            "frontend_code": "frontend-code",
            "backend_code": "backend-code",
            "frontend_bugs": "frontend-bugs",
            "backend_bugs": "backend-bugs",
            "test_results": "test-results",
            "project_documentation": "project-documentation",
            "updates": "updates"
        }
        self.agents_status = {
            "planning": False,
            "frontend": False,
            "backend": False,
            "validation": False,
            "integration": False
        }
        self.project_completed = False
        self.completion_steps = {
            "requirements_generated": False,
            "frontend_completed": False,
            "backend_completed": False,
            "validation_completed": False,
            "integration_completed": False
        }
        self.test_queries = []
        self.start_time = None
        self.time_limit = 240  # 4 minutes in seconds
        self.force_completion_notified = False
        self.force_completed = False

    async def initialize_kafka(self):
        """Initialize Kafka consumer and producer."""
        self.consumer = AIOKafkaConsumer(
            *self.topics.values(),  # Listen to all topics
            bootstrap_servers=self.kafka_bootstrap_servers,
            group_id="monitor-group",
            max_poll_interval_ms=300000,
            max_poll_records=10,
            auto_offset_reset='latest'  # Only read the latest messages
        )
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_bootstrap_servers
        )
        await self.consumer.start()
        await self.producer.start()
        self.start_time = time.time()

        # 清空所有 topics
        await self.clear_kafka_topics()

        # Send a test message to create the updates topic
        await self.producer.send_and_wait(
            self.topics["updates"],
            json.dumps({
                "type": "monitor_started",
                "message": "Monitor initialized"
            }).encode()
        )
        logger.info("Monitor initialized and updates topic created")

    async def clear_kafka_topics(self):
        """Clear all Kafka topics."""
        logger.info("Clearing all Kafka topics...")
        try:
            # Get all topics
            topics = [
                # Planning Agent topics
                self.topics["user_queries"],
                self.topics["frontend_requirements"],
                self.topics["backend_requirements"],
                self.topics["project_documentation"],

                # Frontend Agent topics
                self.topics["frontend_code"],
                self.topics["frontend_bugs"],

                # Backend Agent topics
                self.topics["backend_code"],
                self.topics["backend_bugs"],

                # Validation Agent topics
                self.topics["test_results"],

                # Common topics
                self.topics["updates"]
            ]

            # Use Docker commands to delete and recreate each topic
            for topic in topics:
                try:
                    # Delete topic
                    delete_cmd = f"docker exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic {topic}"
                    await asyncio.create_subprocess_shell(
                        delete_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    logger.info(f"Deleted topic: {topic}")

                    # 重新创建 topic
                    create_cmd = f"docker exec kafka kafka-topics --bootstrap-server localhost:9092 --create --topic {topic} --partitions 1 --replication-factor 1"
                    await asyncio.create_subprocess_shell(
                        create_cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    logger.info(f"Recreated topic: {topic}")
                except Exception as e:
                    logger.error(f"Error handling topic {topic}: {e}")

            logger.info("All Kafka topics cleared and recreated successfully")
        except Exception as e:
            logger.error(f"Error clearing Kafka topics: {e}")

    async def check_time_limit(self):
        """Check if time limit has been reached."""
        if time.time() - self.start_time > self.time_limit and not self.force_completion_notified:
            logger.warning("Time limit reached! Forcing completion...")
            await self.notify_force_completion()
            self.force_completion_notified = True
            return True
        return False

    async def notify_force_completion(self):
        """Notify all agents to complete their current tasks and stop."""
        force_completion_message = {
            "type": "force_completion",
            "status": "time_limit_reached",
            "message": "Time limit reached. Please complete current tasks and stop."
        }

        # Notify all relevant topics
        topics = [
            self.topics["user_queries"],
            self.topics["frontend_requirements"],
            self.topics["backend_requirements"],
            self.topics["frontend_code"],
            self.topics["backend_code"],
            self.topics["test_results"],
            self.topics["project_documentation"],
            self.topics["updates"],
            self.topics["frontend_bugs"],
            self.topics["backend_bugs"]
        ]

        for topic in topics:
            await self.producer.send_and_wait(
                topic,
                json.dumps(force_completion_message).encode()
            )
            logger.info(f"Sent force completion notification to {topic}")

    async def monitor_messages(self):
        """Monitor messages from all topics and track project progress."""
        try:
            async for msg in self.consumer:
                try:
                    # Check time limit
                    if await self.check_time_limit():
                        break

                    message = json.loads(msg.value.decode())
                    topic = msg.topic

                    # Track agent activity
                    if topic == self.topics["user_queries"]:
                        self.agents_status["planning"] = True
                        logger.info("Planning agent is active")
                    elif topic == self.topics["frontend_requirements"]:
                        self.agents_status["frontend"] = True
                        logger.info("Frontend agent is active")
                    elif topic == self.topics["backend_requirements"]:
                        self.agents_status["backend"] = True
                        logger.info("Backend agent is active")
                    elif topic == self.topics["test_results"]:
                        self.agents_status["validation"] = True
                        logger.info("Validation agent is active")
                    elif topic == self.topics["updates"]:
                        self.agents_status["integration"] = True
                        logger.info("Integration agent is active")
                    elif topic == self.topics["frontend_bugs"] or topic == self.topics["backend_bugs"]:
                        logger.info("Bug agent is active")

                    # Track project completion steps
                    if topic == self.topics["frontend_code"] and "status" in message and message["status"] == "completed":
                        self.completion_steps["frontend_completed"] = True
                        logger.info("Frontend code completed")
                    elif topic == self.topics["backend_code"] and "status" in message and message["status"] == "completed":
                        self.completion_steps["backend_completed"] = True
                        logger.info("Backend code completed")
                    elif topic == self.topics["test_results"] and "status" in message and message["status"] == "completed":
                        self.completion_steps["validation_completed"] = True
                        logger.info("Validation completed")
                    elif topic == self.topics["project_documentation"] and "status" in message and message["status"] == "completed":
                        self.completion_steps["integration_completed"] = True
                        logger.info("Integration completed")

                    # Handle test queries
                    if topic == self.topics["user_queries"] and "type" in message and message["type"] == "test":
                        self.test_queries.append(message)
                        logger.info(f"Received test query: {message.get('content', '')}")

                    # Print message content for monitoring
                    logger.info(f"Received message on topic {topic}: {message}")

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

                    # Check if all steps are completed
                    if all(self.completion_steps.values()):
                        self.project_completed = True
                        logger.info("Project completed successfully!")
                        await self.notify_completion()
                        break

                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {msg.value}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Error in monitor_messages: {e}")

    async def notify_completion(self):
        """Notify all agents about project completion."""
        completion_message = {
            "type": "completion",
            "status": "completed",
            "message": "Project has been completed successfully"
        }

        # Notify all relevant topics
        topics = [
            self.topics["user_queries"],
            self.topics["frontend_requirements"],
            self.topics["backend_requirements"],
            self.topics["frontend_code"],
            self.topics["backend_code"],
            self.topics["test_results"],
            self.topics["project_documentation"],
            self.topics["updates"],
            self.topics["frontend_bugs"],
            self.topics["backend_bugs"]
        ]

        for topic in topics:
            await self.producer.send_and_wait(
                topic,
                json.dumps(completion_message).encode()
            )
            logger.info(f"Sent completion notification to {topic}")

    async def cleanup(self):
        """Clean up Kafka resources."""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
        logger.info("Project monitor stopped")

    def get_agent_status(self):
        """Get current status of all agents."""
        return {
            "agents": self.agents_status,
            "completion_steps": self.completion_steps,
            "project_completed": self.project_completed,
            "test_queries": self.test_queries,
            "time_remaining": max(0, self.time_limit - (time.time() - self.start_time)) if self.start_time else self.time_limit
        }

    async def handle_user_input(self):
        """Handle user input for requirements."""
        try:
            while True:
                if self.project_completed or self.force_completed:
                    print("\n" + "="*50)
                    print("Project status:")
                    print(f"- Planning phase: {'completed' if self.completion_steps['requirements_generated'] else 'in progress'}")
                    print(f"- Frontend development: {'completed' if self.completion_steps['frontend_completed'] else 'in progress'}")
                    print(f"- Backend development: {'completed' if self.completion_steps['backend_completed'] else 'in progress'}")
                    print(f"- Code validation: {'completed' if self.completion_steps['validation_completed'] else 'in progress'}")
                    print(f"- Integration deployment: {'completed' if self.completion_steps['integration_completed'] else 'in progress'}")
                    print("="*50 + "\n")

                    logger.info("Project completed. Waiting for new input...")
                    self.project_completed = False
                    self.force_completed = False
                    self.completion_steps = {k: False for k in self.completion_steps}
                    # Reset all agents status
                    self.agents_status = {k: False for k in self.agents_status}
                    # Wait for a short time to ensure all agents have processed the completion
                    await asyncio.sleep(2)

                requirement = input("\nPlease enter your requirements (enter 'exit' to quit): ")

                if requirement.lower() == 'exit':
                    break

                # Check if any agent is still active
                if any(self.agents_status.values()):
                    logger.warning("Previous task is still in progress. Please wait...")
                    continue

                # Create message
                message = {
                    "type": "requirement",
                    "content": requirement
                }

                # Send message
                await self.producer.send_and_wait(
                    self.topics["user_queries"],
                    json.dumps(message).encode()
                )
                logger.info("Requirement sent, waiting for task completion...")

        except KeyboardInterrupt:
            logger.warning("Operation interrupted")
        except Exception as e:
            logger.error(f"Error handling user input: {e}")

async def main():
    monitor = ProjectMonitor()
    try:
        await monitor.initialize_kafka()
        logger.info("Project monitor initialized and listening for updates...")

        # Run message processing and user input handling concurrently
        await asyncio.gather(
            monitor.monitor_messages(),
            monitor.handle_user_input()
        )

    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        await monitor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
