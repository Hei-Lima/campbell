<h1 align="center">Campbell</h1>

<p align="center">
  <img src="app/static/media/logobranco.svg" alt="Logo" width="200">
</p>

<h3 align="center">
Quickly generate cloud-like VMs for Proxmox with the use of templates.
</h3>

<p align="center">
  <a href="https://github.com/Hei-Lima/campbell/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Hei-Lima/campbell" alt="License">
  </a>
</p>

(Currently in development) In the future, the application will be containerized with Docker, featuring stronger authentication and enhanced security measures. The software comes with no guarantee.

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)

## Description

Campbell is a tool designed to streamline the process of generating virtual machines (VMs) for Proxmox. It provides a user-friendly interface and a set of utilities to quickly create, manage, and configure VMs, making it easier for administrators and developers to work with Proxmox environments. 

## Features

- **Quick VM Creation**: Easily create VMs with predefined configurations.
- **User-Friendly Interface**: Simple and intuitive UI for managing VMs.
- **Configuration Management**: Manage VM configurations with ease.
- **Integration with Proxmox**: Seamless integration with Proxmox VE.

## Installation

To install Campbell, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/Hei-Lima/campbell.git
    cd campbell
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Run Campbell:
    ```sh
    python3 run.py
    ```
Then, open your browser and navigate to http://127.0.0.1:5000 to access the Campbell interface.

## Contributing
We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (git checkout -b feature/your-feature).
3. Make your changes and commit them (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature/your-feature).
5. Open a pull request.

## License
This project is licensed under the Apache 2 License. See the LICENSE file for details.

