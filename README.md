# Fast-IoT (fastiot)

FastIoT is a framework for rapid development of IIoT-Systems using Python as main programming language.
It helps to set up a micro-service architecture and create services. The development has been started as basis for 
various research projects at Fraunhofer IVV, Dresden, Germany.  

To get started quickly it is equipped with a powerful command line interface (CLI): `fiot`.
This helps setting up a new project, create new services and run tests. 
It also supports creating cross-architecture Docker-containers and deployment configurations with docker-compose files
and Ansible playbooks to bring the software to the systems they belong. Run `fiot --help` for a full list of features.

As for now the overall framework has only been used and tested on Linux systems.

A full documentation is available at http://docs.dev.ivv-dd.fhg.de/fastiot/_latest/

If you use this framework in your scientific projects please cite: 
> Konstantin Merker, Tilman Klaeger, Lukas Oehm. „A Holistic Approach for Rapid Development of IIoT Systems“, 2022. https://doi.org/10.48550/arXiv.2201.13243.


## Requirements

These are the requirements you need to setup:

* Python 3.8 or newer and the possibility to create virtual environments.

If you want to build services or do integration tests with databases or other services you also need to have a working
docker setup:
* Docker
* docker-compose

If you want to use Ansible for deploying your services you also need to Ansible installed.


## Getting started

It is always recommended to use a separate virtual environment for each project, so let’s create one: `python3 -m venv venv` and use it: `source venv/bin/activate`

Afterwards you can install FastIoT: `python3 -m pip install https+git://github.com/FraunhoferIVV/fastiot.git`

To setup a new project with the name `my_first_project` you can now run: `fiot create new-project my_first_project`

Within this repository you can find some sample services to use as template.
Or you can simply ask the CLI to create a new services: `fiot create new-service my_first_service`.
You should now find a service stub in your project to be extended with your application logic.

You can now also create deployment configurations (e.g. a `docker-compose.yaml`) using `fiot config` and build 
containers for your project using `fiot build`.

For a more comprehensive list of features, a guide to the project structure please refer to the complete documentation.

To run services localy, in your IDE or within a container you may also refer to the complete documentation.

## Developing FastIoT

Simply check out this project and install the dependencies listed in `requirements.txt`. 