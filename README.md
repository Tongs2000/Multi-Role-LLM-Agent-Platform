# Multi-Role-LLM-Agent-Platform

Multi-Role-LLM-Agent-Platform is a multi-role LLM agent collaboration platform based on [OpenManus](https://github.com/OpenManus/OpenManus). The platform enables distributed collaboration between multiple agents through Kafka, supporting frontend, backend, and test agents working together.

## Project Background

This project is a modification of OpenManus with the following major improvements:

1. **Distributed Architecture**: Using Kafka as a message broker to enable asynchronous communication between multiple agents
2. **Multi-Role Collaboration**:
   - Frontend Agent: Responsible for generating frontend code
   - Backend Agent: Responsible for generating backend code
   - Test Agent: Responsible for running tests and reporting issues
3. **Task-Driven Development**: Defining development requirements through task description files, with agents collaborating to complete tasks
4. **Real-time Feedback Mechanism**: Agents can exchange information in real-time and fix issues promptly

## System Architecture

```
+----------------+     +----------------+     +----------------+
|  Frontend      |     |  Backend       |     |  Test         |
|    Agent       |     |    Agent       |     |    Agent      |
+----------------+     +----------------+     +----------------+
        |                     |                     |
        v                     v                     v
+--------------------------------------------------+
|                    Kafka Message Queue            |
+--------------------------------------------------+
        ^                     ^                     ^
        |                     |                     |
+----------------+     +----------------+     +----------------+
|  Task          |     |  Code          |     |  Test         |
|  Description   |     |  Generator     |     |  Reports      |
+----------------+     +----------------+     +----------------+
```

## Quick Start

### Requirements

- Python 3.8+
- Docker & Docker Compose
- Kafka (provided via Docker Compose)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/your-username/Multi-Role-LLM-Agent-Platform.git
cd Multi-Role-LLM-Agent-Platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Kafka services:
```bash
docker-compose up -d
```

4. Configure LLM API:
Edit the `config.json` file to configure your LLM API keys.

### Running Examples

1. Start the Frontend Agent:
```bash
python distributed_agents/frontend/frontend_agent.py
```

2. Start the Backend Agent:
```bash
python distributed_agents/backend/backend_agent.py
```

3. Start the Test Agent:
```bash
python distributed_agents/test/test_agent.py
```

4. Launch a Task:
```bash
python distributed_agents/task_launcher.py
```

## Project Structure

```
Multi-Role-LLM-Agent-Platform/
├── distributed_agents/          # Distributed agent code
│   ├── frontend/               # Frontend agent
│   ├── backend/                # Backend agent
│   ├── test/                   # Test agent
│   └── shared/                 # Shared resources
├── docker-compose.yml          # Docker configuration
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Key Features

- **Distributed Collaboration**: Multiple agents communicate asynchronously through Kafka
- **Task-Driven**: Development requirements are defined through JSON task description files
- **Real-time Feedback**: Agents can exchange information and status updates in real-time
- **Automated Testing**: Integrated test agent for running tests and reporting issues
- **Extensibility**: Support for adding new agent roles and functionalities

## Contributing

We welcome issues and pull requests to help improve the project.

## License

This project is based on OpenManus and follows the same open-source license.

## Acknowledgments

Thanks to the [OpenManus](https://github.com/OpenManus/OpenManus) project for providing an excellent foundation.
