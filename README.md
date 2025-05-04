# A Collaborative Multi-Role LLM Agent Platform

A Collaborative Multi-Role LLM Agent Platform is an advanced multi-agent system built on top of [OpenManus](https://github.com/OpenManus/OpenManus) tools, designed for intelligent code analysis and development assistance. The system orchestrates multiple specialized LLM agents working in concert to analyze, understand, and improve code through natural language interactions.

## 🌟 Key Features

- **Multi-Role LLM Architecture**: Coordinated system of specialized language model agents including:
  - Planning Agent: Task decomposition and strategy development
  - Frontend Agent: UI/UX implementation and frontend development
  - Backend Agent: Server-side logic and API development
  - Integration Agent: System integration and communication handling
  - Validation Agent: Code quality assurance and testing
  - Retrieval Agent: Code analysis and context gathering
  - Monitor: System orchestration and agent communication management

- **Message-Driven Architecture**: Kafka-based communication system enabling:
  - Asynchronous agent communication
  - Reliable message delivery
  - Scalable message processing
  - Real-time event streaming

- **Intelligent Code Analysis**: Advanced code understanding and improvement suggestions powered by OpenManus tools
- **Natural Language Processing**: Human-like interaction for code review and development
- **Distributed Processing**: Efficient task distribution across specialized agents

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- OpenManus tools and dependencies
- Apache Kafka 3.0+ (included in Docker setup)

### Installation

#### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/Tongs2000/multi-role-llm-platform.git
   cd multi-role-llm-platform
   ```

2. Start Kafka and other services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Verify Kafka is running:
   ```bash
   docker-compose logs kafka
   ```

#### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Tongs2000/multi-role-llm-platform.git
   cd multi-role-llm-platform
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the project:
   ```bash
   pip install -e .
   ```

4. Install and configure Kafka locally:
   - Download [Apache Kafka](https://kafka.apache.org/downloads)
   - Start Zookeeper:
     ```bash
     bin/zookeeper-server-start.sh config/zookeeper.properties
     ```
   - Start Kafka server:
     ```bash
     bin/kafka-server-start.sh config/server.properties
     ```

## 🔧 Usage

### Basic Usage

1. Ensure Kafka is running:
   ```bash
   # Check Kafka status in Docker
   docker-compose ps
   
   # Or check local Kafka process
   ps aux | grep kafka
   ```

2. Start the monitor:
   ```bash
   python -m distributed_agents.monitor
   ```

3. Start the agents:
   ```bash
   # Start in separate terminals or use screen/tmux
   python -m distributed_agents.planning_agent
   python -m distributed_agents.frontend_agent
   python -m distributed_agents.backend_agent
   python -m distributed_agents.integration_agent
   python -m distributed_agents.validation_agent
   python -m distributed_agents.retrieval_agent
   ```

### Example Use Cases

- Code Review Analysis
- Development Task Planning
- Frontend/Backend Implementation
- System Integration Testing
- Code Validation and Quality Assurance
- Code Improvement Suggestions

## 📁 Project Structure

```
multi-role-llm-platform/
├── app/                  # Web application
├── config/              # Configuration files
├── distributed_agents/  # Core agent implementation
│   ├── planning/       # Planning agent
│   ├── frontend/       # Frontend agent
│   ├── backend/        # Backend agent
│   ├── integration/    # Integration agent
│   ├── validation/     # Validation agent
│   └── retrieval/      # Retrieval agent
├── doc/                # Documents
├── test/               # Test suite
├── workspace/          # Workspace directory
├── docker-compose.yml  # Docker orchestration config
├── Dockerfile          # Docker build file
├── requirements.txt    # Project dependencies
└── setup.py           # Project installation config
```

## 🛠️ Configuration

System configuration files are located in the `config/` directory, including:
- Agent configurations
- System parameters
- Environment variables
- OpenManus tool settings
- Kafka topics and consumer groups
- Message schemas and protocols

### Kafka Configuration

Key Kafka topics used by the system:
- `task-planning`: Task decomposition and planning messages
- `frontend-tasks`: Frontend development tasks
- `backend-tasks`: Backend development tasks
- `integration-tasks`: System integration tasks
- `validation-tasks`: Code validation and testing tasks
- `agent-communication`: Inter-agent communication
- `system-monitoring`: System health and metrics

## 🧪 Performance Evaluation

We conducted extensive performance testing comparing three platforms:
1. Single-agent OpenManus (baseline)
2. Our Multi-Role LLM Agent Platform
3. Cursor Agent

### Test Framework

```
test/
├── test_cases.txt         # Test case definitions
├── test_output/          # Platform outputs
│   ├── workspace_N-1/    # OpenManus results
│   ├── workspace_N-2/    # Our platform results
│   └── workspace_N-3/    # Cursor Agent results
└── test_result/
    ├── test_result_N.txt # Detailed scoring (max 50)
    └── result.xlsx       # Performance summary
```

### Evaluation Metrics

Each test case is evaluated using Claude 3.5 Sonnet as the scoring engine (max 50 points) based on:
- Code correctness and functionality
- Solution completeness
- Implementation efficiency
- Documentation quality
- Best practices adherence

### Performance Analysis

The `test_result/result.xlsx` contains comprehensive metrics including:
- **Execution Time**: Task completion duration for each platform
- **Output Size**: Generated code/content volume
- **Output Quality**: Claude 3.5 Sonnet score (max 50)
- **Average Performance**: Mean values across all test cases

### Test Results

Detailed evaluation results are stored in:
- `test_output/workspace_N-1/`: Single-agent OpenManus outputs
- `test_output/workspace_N-2/`: Our platform outputs
- `test_output/workspace_N-3/`: Cursor Agent outputs
- `test_result/test_result_N.txt`: Detailed scoring and analysis
- `test_result/result.xlsx`: Comparative performance summary

## 📚 Documentation

Detailed project documentation is available in the `doc/` directory:

- [Final Project Report](doc/Final%20Project%20Report.pdf): Comprehensive project details, architecture, implementation, and results
- [Final Project Progress Report](doc/Final%20Project%20Progress%20Report.pdf): Development progress and milestone achievements
- [Revised Final Project Proposal](doc/Revised%20Final%20Project%20Proposal.pdf): Updated project scope and objectives
- [Final Project Proposal](doc/Final%20Project%20Proposal.pdf): Initial project planning and goals
- [Final Project Demo](doc/Final%20Project%20Demo.pptx): Comprehensive presentation of the project features and results

These documents provide in-depth information about:
- System Architecture and Design
- Implementation Details
- Performance Analysis
- Future Development Plans

## 🎥 Demo & Presentation

- [Project Demo Video](https://youtu.be/5L1l9QTQMNM): Watch our system in action with detailed explanations

The demo materials showcase:
- System Architecture Overview
- Agent Interaction Flow
- Live Feature Demonstrations
- Performance Comparison Results
- Real-world Use Cases

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


