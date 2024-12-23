MSI DDSS - Python
=====

Developed by Simão Sousa, 2020226115, simaosousa@student.dei.uc.pt


Requirements
---
- To execute this project it is required to have installed:
    * Docker

Development
---
The folder [`app`](app) is mapped into the container. 
You can modify the contents and the server will update the sources without requiring to rebuild or restart the container.


Setup and Run
---

To build the docker image you should run:


```sh
sh build.sh
```

To run the container:


```sh
sh run.sh
```

* *note: modifying the `run.sh` script to include -dit will make the container work in background. But dont forget to use `stop.sh` to stop/remove it later.*


To stop the container:

```sh
sh stop.sh
