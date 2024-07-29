# ML System Design

## Overview
This repository demonstrates the deployment of a Machine Learning pipeline. It includes various scripts and configuration files necessary for setting up and running the pipeline in a test environment.

## Repository Structure
- `genesis_arena/` - Contains baseline configurations and scripts.
- `.gitignore` - Lists files and directories to be ignored by Git.
- `Dockerfile` - Defines the Docker container setup.
- `env_sample.txt` - Sample environment variables file.
- `requirements.txt` - Python dependencies list.
- `update_baseline.sh` - Script to update the baseline configurations.

## Getting Started

### Prerequisites
- Docker
- Python 3.8+
- Git

### Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/3yungar/ml_system_design.git
    cd ml_system_design
    ```
2. Set up the environment variables:
    ```bash
    cp env_sample.txt .env
    ```
3. Build the Docker container:
    ```bash
    docker build -t ml_system_design .
    ```

### Running the Pipeline
To execute the ML pipeline, use the following command:
```bash
docker run --env-file .env ml_system_design
```

## Contributing
1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch`.
3. Commit your changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-branch`.
5. Open a pull request.

## License
This project is licensed under the MIT License.

---

For more details, visit the [repository](https://github.com/3yungar/ml_system_design).
