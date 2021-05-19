---
title: "MEAN stack vulnerabilities diagnose with Kubernetes monitoring tools"
author:
  - Aakriti Talwar<at4793@nyu.edu>
  - Ramneek Kaur <rk3994@nyu.edu>
---



# Motivation

Using microservice architecture like kubernetes makes it easier and faster to scale applications without impacting the whole system and hence is a widely growing ecosystem. Since microservice architecture has numerous services talking to each other, monitoring applications becomes a challenging task.
 
MEAN stack is a popular javascript based open source full stack framework that includes MongoDB, Express.js, Angular.js and Node.js used  to create dynamic, fast, and secure websites and web applications that scale. This framework is although pretty flexible and powerful comes with its own set of difficulties. Some common problems faced by MEAN stack applications are:
 
* Uncaught exception or error event in JavaScript code
* Unresponsive application, possibly looping or hanging
* Excessive memory usage, which may result in an out-of-memory error
* Heavy weight computation causes poor performance.
 
So in scenarios where these MEAN Stack applications are running on Kubernetes clusters it becomes all the more difficult to diagnose the above mentioned problems. Our goal is to use four different monitoring tools namely, cAdvisor, EFK, Kubernetes dashboard and Grafana to monitor and find out which out of these can provide the most accurate metric for fast diagnosis of the above mentioned issues which would in turn lead to shorter issue resolution time.


#  Approach
# # Tools and Technologies encountered:-
  
* Grafana
Grafana is an open source solution for running data analytics, pulling up metrics that make sense of the massive amount of data & to monitor our apps with the help of variety of customizable dashboards. We created 2 dashboards for our project – one for cluster level metrics and another for application semantics.
 
* Prometheus:
For this project , we used Prometheus as a data store that would provide the metrices to Grafana. We also used Prometheus’s ‘/metrics’ endpoint to expose cadvisor’s metrics. Prometheus itself has alerting and monitoring capabilities but we haven’t explored that for this project.
 
* EFK Stack
A centralised logging solution to help analyze heavy volume of log data produced by the Pods. It consists of 3 parts –
Elasticsearch is a real-time, distributed, and scalable search engine used to index and search through large volumes of log data
Kibana - a powerful data visualization frontend and dashboard for Elasticsearch. 
Fluentd to collect, transform, and ship log data to the Elasticsearch backend
As mentioned we used this to check the logs for different applications in different namespaces to check if we could see desirable log results after inducing mentioned problems with a mean stack cluster

* cAdvisor
cAdvisor (Container Advisor) provides container users an understanding of the resource usage and performance characteristics of their running containers. We configured it as a running daemon that collects, aggregates, processes, and exports information about running containers. We used Prometheus web used UI to access this metrics.
 
* Metrics server
Metrics Server is a cluster add-on that collects resource usage data from each node and provides aggregated metrics . Metrics Server makes resource metrics such as CPU and memory available for users to query.
 
* Kubernetes Dashboard
Kubernetes Dashboard can be used to deploy containerized applications to a Kubernetes cluster, troubleshoot your containerized application, and manage the cluster resources. 
 

# Experiment Results

## Heavy Weight Computation causing poor performance:
When sending very high load on the application the app at times became unresponsive or the map on the application interface failed to load.
For a possible solution we applied horizontal Pod autoscalar, to avoid heavy load on one pod and we were able to solve the performance issue of the MEAN app. Results can be seen in figures below.
![Figure 1: HPA scales up due to high CPU utilization](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/Picture2.png)

![Figure 2: MEAN App running on High Load before crash](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/Screen%20Shot%202021-05-11%20at%2011.10.14%20AM.png)

![ Figure 3: MEAN App running on High Load after crash](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/Screen%20Shot%202021-05-11%20at%2011.09.34%20AM.png)


## Unresponsive application, possible looping or hanging:
We induce an infinite loop in the javascript code of the backend. While infinite loop was evoked, application was stuck and CPU and Memory usage for that pod was continuously increasing. After reaching the resource limit specified for the pod, we saw sharp decline in CPU and memory usage and application worked properly after. Results can be seen in figures below.

![Figure 4:CPU and Memory usage sharp increase](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/WhatsApp%20Image%202021-05-18%20at%2010.11.26%20PM.jpeg)

## Out of memory error:
Pod crashed when memory usage exceeded the resource limit. We were able to diagnose this error from Kubernetes backend and  Kubernetes dashboard as seen in figure below.

![Figure 5:CPU and Kubernetes dashboard showing Error](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/WhatsApp%20Image%202021-05-18%20at%2010.18.57%20PM.jpeg)

![Figure 6:Kubernetes Backend Pod Description catching error ](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/WhatsApp%20Image%202021-05-18%20at%2010.19.05%20PM.jpeg)

## Uncaught exception or error event in Javascript code:
None of the selected tools were able to catch the exception throw by application. In order to catch the exception, explicit modifications need to be done both on application side and EFK configuration side to obtain the logs for the exceptions.

# Conclusions

![alt text](https://github.com/Ramneek99/final-project-report/blob/main/rk3994-at4793/Picture1.png)

# Related Work 

One other option is to use DataDog. Datadog as a single monitoring tool was able to diagnose maximum problems and vulnerabilities with MEAN stack applications, but it was a paid tool so we specifically worked with free open source tools.
Apart from that we were able to find some research on Kubernetes Monitoring tools and non-Kubernetes based  tools that could be used to diagnose some of the issues, but we were not able to find any research done taking both in mind.


# Future Work

Due to time constraints and other problems faced during project development we were not able to work on the last 2 problems mentioned for MEAN Stack that are Query Selector Injection Attacks and Cross Site Scripting Attacks, but we were able to research a bit on that.
1. MongoDB is immune to SQL injection Attacks but prone toQuery Selector Attacks
2. ToolslikeNeoVector(Kubernetes based) and  practices like Dynamic Application Security Testing (DAST)  can help find security vulnerabilities and weaknesses in running applications.
3. Crosssitescriptingattacks can be detected using various vulnerability scanners available in the market , wasn’t able to find any particular Kubernetes based monitoring tool for that.


