# Home Controller App
Web application developed ad hoc to automate and control different aspects of my house. It is designed to be installed on a Raspberry Pi or any other device with GPIO pins that are able to run Python.

## App Features
This app is under continuous development, so more features will be added in the future. By now, the app provides the following features:
- Watering controller: This feature allows you to automate de process of water the garden. It is composed of the following objects:
    - Circuits (x12): Physical water valves connected to water pipelines to water different areas of the garden. The activation of the circuits is designed to be used along with a demultiplexer, so only 4 pins are needed for the 12 available circuits.
    - Programs (x3): A sequence of consecutive opening and closing of circuits during a programable time. Each program can be programed to be executed automatically at any time and day of the week.
- House water intake controller: This feature allows you to know to control the main valve water of the house and know the current water consumption as well as historic water consumption.
- Web GUI (Spanish): It is exposed on port `5000` and shows all the features and system information.

## Installation
### Install Docker on Debian based distribution
To install Docker, follow the instructions of the official page:

https://docs.docker.com/engine/install/debian/

Also docker compose component is needed. Once Docker is installed, follow the instructions of the official page to install the component:

https://docs.docker.com/compose/install/linux/

### Deploy App
To deploy the docker container, just execute the following command:
```
docker-compose -f docker-compose.pro.yml up --build
```
Once the docker container is deployed, the app will be accesible on port `5000`.
