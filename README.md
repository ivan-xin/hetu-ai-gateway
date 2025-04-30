### Hetu AI Gateway
This README provides an overview of the Hetu AI Gateway project structure and its components.

### Project Overview

Hetu AI Gateway appears to be an API gateway for AI services, providing a unified interface for various AI model interactions. The project is structured with the following main components:


#### Core Components

- API Layer: Handles HTTP requests and responses
- Model Management: Manages different AI models and their configurations
- Authentication & Authorization: Handles user authentication and access control
- Logging & Monitoring: Tracks system performance and user interactions
- Configuration Management: Manages system settings and environment variables
  
#### Key Features
- Support for multiple AI models and providers
- API rate limiting and quota management
- Request routing and load balancing
- Authentication and authorization
- Logging and monitoring
- Configuration management

#### Installation

```
pip install -r requirements.txt
```

### Usage
To start the Hetu AI Gateway service:
```
python -m hetu_ai_gw.main
```

#### Configuration
Configuration can be done through environment variables or configuration files. See the configuration directory for more details.

#### API Documentation
The API documentation is available at the /docs endpoint when the service is running.

#### Development
For development, set up a virtual environment:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

