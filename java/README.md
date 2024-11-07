MSI DDSS - Java 
=====

This code is to be used in the scope of the *DDSS* course.

**Important:** these sources are merely suggestions of implementations. 
You should modify everything you deem as necessary and be responsible for all the content that is delivered.

## Information

The resources available here use [Spark Java](http://sparkjava.com/), which is *"A micro framework for creating web applications in Java 8 with minimal effort"*.
It is very easy to build a simple web application, and automate its deployment either with `maven` or `Docker`. The two options are available, as described in [Contents](#Contents).

You are free to use other solutions as long as you provide the mechanisms to automated them.
E.g. it is very easy to provide a WebApp using embedded tomcat with maven, or you can also go with docker and include in the image a web/app server.

## Contents

* [maven automated deployment](ddss-mvn) - Requires `maven` and `java`. This is the best option, easy and fast to deploy the application. 
* [Docker automated deployment](.) - Only requires `Docker`. Use this option if you really do not want to install maven, because it is a slower solution. It uses maven inside the container, so you do not need to install maven.

## Requirements

- To execute this project it is required to have installed:
    * Docker
    * Docker compose