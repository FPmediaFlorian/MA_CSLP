# Enhancing Cybersecurity Awareness in Children through Serious Games and Gamification

## Description:
This master's thesis project explores the synergistic potential of Serious Games, Digital Wellness, and Gamification in the realm of education, with a particular emphasis on boosting cybersecurity awareness among children. Through an extensive literature review, this research underscores the effectiveness of gamification as a dynamic learning tool, the importance of fostering digital wellness from a young age, and the role of gamification in keeping students engaged.

The core of this project is the development of a prototype platform designed to educate children about cybersecurity principles. This platform serves not only as a knowledge repository but also as a tool to instill habits that promote digital well-being. The project extends beyond theoretical research, incorporating practical testing and evaluation of existing gamification apporaches and Serious Games. This approach enriches the empirical foundation of the prototype, ensuring its effectiveness and relevance.

Aiming to contribute to a digitally literate and responsible younger generation, this project represents a significant step towards melding educational content with digital best practices. It adopts a multi-dimensional approach, combining pedagogical strategies with interactive technologies to nurture a secure and conscientious digital society, one child at a time​​.

## Deployment

In this section of the master's thesis, the focus is on the critical
phase of transitioning the cybersecurity learning platform from
development to either a testing or live environment. Successful
deployment hinges on the fulfillment of specific prerequisites and the
utilization of Docker containerization to guarantee a seamless and
consistent transition. This portion aims to clarify the prerequisites
for deployment, underscore the essential function of Docker in this
operation, and offer a detailed, step-by-step guide for platform
deployment.

### Prerequisites

In order to deploy and also use the protoype some prerequsites have to
be matched.

-   Docker installed: Docker is essential for containerization, ensuring
    consistent and efficient deployment.

-   Docker compose installed: Docker compose is used to build and
    compose the application's container.

-   Browser installed: A modern web browser is required to access and
    monitor the platform's user interface.

-   *Recommended* Git installed: While Git is not mandatory to start the
    application, it is highly advisable to use it to pull the project
    and also control several changes that might be made to the source
    code.

### Dockerization

Using Docker for projects offers numerous advantages. It provides
isolation and consistency, ensuring the application behaves consistently
across different environments. Docker's portability simplifies
deployment and scaling, and it aids in managing dependencies. Docker
containers are resource-efficient and scalable, making them ideal for
handling variable workloads. Versioning and rollbacks are easy,
enhancing stability. For the cybersecurity learning platform, Docker
ensures security, consistency, and ease of management throughout
development, testing, and deployment phases.

The Docker container comprises two distinct images. Firstly, the backend
(API) relies on a Python image, where all necessary packages are
installed through a \"requirements.txt\" file. This ensures the correct
setup of Python libraries and dependencies.

The second image is responsible for hosting the frontend (UI) and is
based on a Node.js image. This component handles the user interface and
user interaction.

### How to deploy - Step by Step

1.  **Meet Prerequisites**: To be able to tryout the prototype you need
    to meet the prerequisites.

2.  **Pull the project**: Pull the project from Github\
    Terminal: `pull https://github.com/maproject`

3.  **Navigate to project folder**:\
    Terminal: `cd ma_cs_project`

4.  ***Optional* change frontend port**: If you encounter any problems
    regarding the fronend not starting because of port colision, you can
    just change the port in `docker_compose.yml` line 22. Initial port
    is 8080.

5.  **add entry to hosts file** Find your hosts file according to you
    operating system (Table [7.1](#tab:hosts_path){reference-type="ref"
    reference="tab:hosts_path"}).

    ::: {#tab:hosts_path}
      OS        Version                                               Path
      --------- ----------------------------------------------------- --------------------------------------------
      Windows   NT, 2000, XP, 2003, Vista, 2008, 7, 2012, 8, 10, 11   C:\\Windows\\System32\\drivers\\etc\\hosts
      macOS     Mac OS X 10.2 and newer                               /private/etc/hosts
      Linux                                                           /etc/hosts

      : Hosts file path
    :::

    Add these hosts:\
    `127.0.0.1 cslearning`\
    `127.0.0.1 cslearning.local`

6.  **docker build** in the root folder of the project open a teminal
    and submit `docker-compose build`

7.  **docker compose** in the same folder after a successfull build
    submit `docker-compose up -d`

8.  ***Optional* Initialize backend with dummydata**: Navigate to
    <http://cslearning:5050/cleaninstall>. This will create the
    dummydata. You can also use this link to delete all changes in the
    Database and recreate the dummy data. You already got 3 courses
    built up. Feel free to create new ones of customize the existing.

    -   Teacher:\
        username: teacher2\
        password: J9o\$&7qVKk

    -   Teacher:\
        username: teacher3\
        password: GJC4Zwmu2#

    -   Student:\
        username: student2\
        password: ELMjQ\$0Lk2

    -   Student:\
        username: student3\
        password: 8b&tS!T38C

9.  **Navigate to Frontend** either by using this link:
    <http://cslearning:8080/> or a customized one for your port.
