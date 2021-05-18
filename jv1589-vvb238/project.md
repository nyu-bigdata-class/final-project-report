---
title: "Load Shedding Mechanism in a Chaotic Multi-Service Distributed System"
author:
  - Jairam Venkitachalam <jv1589@nyu.edu>
  - Vidit Bhargava <vvb238@nyu.edu>
---

# Motivation

Chaos Engineering is a discipline that helps developers build resilient applications. Weaknesses in the system are identified by randomly selecting a subset of services and making them unavailable. This exposes a variety of issues such as improper fallbacks when a downstream service is out, retry storms caused by unspecified timeouts, outages, and cascading failures when dependencies are handled incorrectly.

As Chaos is introduced in a system, even normal activity can overload the functioning servers causing them to spend increasing amounts of their time context switching and becoming too slow to be useful. This is because, under such unexpected circumstances, thread contention, context switching, garbage collection, and I/O contention become more pronounced. All these factors pile on to degrade the throughput of the entire system causing client requests to timeout and fail. 

One way to avoid overload is by utilizing task queues but they come with their complexity and overheads. Another way is to use auto-scaling but it takes time for new pods to come up which can hamper user experience in the meantime. Thus, we need to put measures in place to ensure a smooth transition. 

One of the major ways to handle stress is load shedding, which involves shedding excess load to maintain predictable and consistent performance. However, simply rejecting requests once the servers are overloaded can hinder the end-user experience.

  
# Goal
To build and explore load-shedding strategies which ensure a smooth end-user experience. In other words, all the requests which are in the critical path of a user should be served with minimum latency even when the system is under heavy load. 
The load shedding service should be independent and easy to install with minimal changes to the server and client. Since all requests pass through the load shedder service, the service should have minimal overhead.

# Methodology:

### Assumptions 
1. Different users and requests in this system can be segregated into distinct categories with varying priority levels. Each client knows this information.
2. We have non-byzantine clients:
  a. If the response to a request comes with an HTTP status code 429, they retry only after the calculated backoff time has expired.
  b. Clients do not lie about the request/user priority levels.
  c. These clients do not cause a Denial of Service on the system.
3. All requests can be routed to the load-shedding service. The load shedding service can communicate with existing pods to get their usage metrics.


## System Design
![](https://i.imgur.com/3Ts2nGA.png)


### Sample Services
We built three different services, using Flask, which encompass the majority of workloads in a traditional micro-service system. Each of the services has two different functions to introduce a variety of loads:
1. **CPU Intensive Service** – 
    a. _Generating the hash of a file_ - This function repeatedly takes a 10MB audio file, reads it in 1024 byte chunks, each time updating the SHA512 hash function.
    b. _Repeated multiplication of a big integer_ - This function calculates the square of a large number, and increases the value of the number by one on each iteration.
2. **Memory Intensive Service** –
    a. _Random Nested Dictionary construction_ - This function takes the number of distinct keys as a parameter and generates a randomized key: value pairs and stores it in an in-memory dictionary.
    b. _Sending a call to the I/O service_ - This function repeatedly sends a request to the I/O intensive service to perform a bulk write operation in the DB. It was built to measure how the load-shedding policy translates to inter-service communication.
3. **I/O Intensive Service** – This service was connected to a MongoDB database which has a single collection with over half a million entries.
    a. _Bulk Read_ -  This function takes a parameter that signifies how many items to read from a DB, it then issues a bulk read command for those many items with the ids being randomly selected. This is done to avoid MongoDB's internal cache.
    b. _Bulk Write_ - This function creates a specified number of sample objects, issues a bulk write command, and once that is completed, it issues another bulk delete command.

In addition to these functions, each service has a HealthCheck API to ensure its availability, a Metrics API for gathering the pod’s current CPU and Memory usage, and a Ping API which is called at service start-up to inform the Load Shedder of the pod's IP. 
These services were deployed to GCP using Kubernetes. Each microservice is placed in a separate namespace with a replica count of 3. 

### Load Shedder

The load-shedder service is added to each namespace and is responsible for load-shedding if other pods in the namespace are being over-utilized. To track all the pods in a given namespace, we have an API that is called after the load shedder service starts. This API uses the Kubernetes Python Library to fetch all the pods in its namespace and filters out the IPs of the ones we need to track. If a new pod comes up, it calls an API in the load-shedder to informs its IP address.

The load-shedder periodically queries the services running on the stored IPs using the Metrics API mentioned earlier. The information fetched is kept in a fixed size LRU cache; the average of which (moving average) is used to determine if the pods are under load. All the IP and metrics data is stored in a centralized Redis cache shared by all Load Shedders to ensure availability even if the Load Shedder service dies.

Each time a request comes in, it goes to the load shedder which fetches metrics information from the Redis cache. It was essential for the load-shedder to be lightweight so we maintain a local copy and invalidate it when values in Redis are updated. If the moving average of either the CPU utilization or Memory Utilization is above a certain threshold, we return a response with a status code 429 and an appropriate backoff factor.

The backoff factor is decided based on a combination of three factors: The priority of the user sending the request (paid or free), whether the request is in the critical path (low, mid, high), and the amount of load the service is in; higher the load, higher the backoff factor. For example, at 65% average CPU utilization, a critical path request from a paid user will still be served, however, a non-critical path request would return with a backoff factor of 2. In the same situation, a non-critical path request from a free user would see a backoff factor of 4.

### Monitoring
We setup a monitoring stack on the Kubernetes cluster using Prometheus, and deployed the kube-prometheus-operator helm charts for this purpose. A key component that we include for this integration is the Prometheus exporter plugin within each Flask service. This exporter plugin exposes endpoint "/metrics" which can be queried by a Prometheus daemon to obtain metrics.

We setup appropriate serviceMonitors for all the services following which we begin visualizing the resource consumption on Grafana. The Prometheus deployment was setup in a separate namespace - monitoring and we moved forward with no Role based access control.

### Chaos
We use ChaosKube for the purpose of instilling chaos into the system. Our chaoskube pod was configured to filter out and kill only the CPU-Service, Memory-Service and DB-Service pods, and this activity was performed every 10 minutes.

Killing the pods especially when the system is under heavy load results in more aggressive backoff mechanisms and we measure our results when the system is under chaos.


### Well-Behaved Client
To simulate well-behaved clients, we built a multi-threaded load testing tool that randomly generates requests for the Sample Services listed above. It randomly picks and assigns a user-type (paid or free) and a request-type (low, mid, high) to each generated request.

If a HTTP 429 response is sent by the server, the thread utilizes the backoff factor to calculate sleep times. We tested four strategies to derive the sleep time. These were:

1. $sleep = (backoffFactor)*2^{retryCount – 1}$
2. $sleep = min(threshold, (backoffFactor)*2^{retryCount – 1})$
3. $sleep = random(0, (backoffFactor)*2^{retryCount – 1})$
4. $temp = min(threshold, (backoffFactor)*2^{retryCount – 1})$
$sleep = temp / ( 2 + random(0, temp) )$

Within each of these strategies, we added jitter to all variables to avoid retry storms. The tool records the overall latency time to serve each request as well as the number of retries. 
The load was decided by progressively increasing the number of concurrent requests till a significant portion of requests started giving errors. 


# Related Work
Our work has been inspired by two blogs.
Firstly, Netflix’s post on how they handle Load Shedding while also considering user experience. We utilize their idea of differentiating requests based on how much it affects UX but extended it to fit two distinct customer types, namely, prioritizing paid customers over unpaid ones. Additionally, instead of just using latency to throttle requests, we utilize a combination of latency, CPU, and Memory usage. We believe the multi-tiered approach allows us to preemptively avoid lofty latencies for high-priority requests.
Secondly, Amazon’s post which details how to use Exponential Backoff and Jitter to spread out retries from the client-side. In this project, the server sends the Backoff Factor with HTTP 429 Response depending upon the load on the system.

# Experiments and Analysis:

Our testbench consisted of a multithreaded client sending HTTP requests, while we monitor the CPU and the memory performances along with the overall latency.

We measured the overall latency against all the 4 backoff strategies and the following were the results we observed:

**CPU-Service**:
![cpu-service](https://i.imgur.com/uZAaq3s.png)
**Memory-Service**:
![memory-service](https://i.imgur.com/ibVHvNE.png)
**DB-Service**:
![db-service](https://i.imgur.com/WfSl89R.png)


We observed that the strategy #4, i.e exponential backoff with randomized jitter performed the best across all scenarios, and offered consistent results with low latencies. 
However, we also noticed inconsistent results within the DB Service. We notice a few cases of users with highest priorities experiencing considerable backoff. We reason this to be caused by us not factoring in the latency of the request when calculating backoffs. We assume CPU and Memory consumption to be the only markers detailing when a process is under extreme loads and fail to factor in the time taken by the microservice to cater to current requests. Since we are dealing with a dynamic system with various factors affecting the behavior of services, individual request latency is also an important factor when calculating backoffs.

We continued experimenting and observed the impact of the different strategies on the CPU and Memory consumption of the microservices. 

**Memory Consumption of Memory-Service**:
![MEM-memory-service](https://i.imgur.com/q1SQEOc.png)

**CPU Consumption of CPU-Service**:
![CPU-cpu-service](https://i.imgur.com/kuNBXwX.png)


As we notice, the resource consumption of all services increases as the number of requests increases.
We observe a sharp decline in CPU consumption of the services and attribute this decline to the rapid backing-off of the requests by the request-forwarder. After the backoff time expires, the requests are sent again by the client and this is where they are gradually served.

We do not see a drop in the memory consumption and this is just because of the fact that the Kubernetes Daemon has not started Garbage collecting and reclaiming memory. We have set memory bounds of 100Mb per pod and reclamation begins once we reach that particular threshold.


We believe the backoff strategy 4 is the most optimal among the four different options that we considered. 
Backoff strategy #1 led to unbounded sleep times as the backoffs increased exponentially with an increasing number of retries. Strategy #2 on the other hand capped backoffs at a threshold that led to similar come-alive times for many requests. We moved forward with adding jitter to the backoff which gave the optimal results and finally experimented here with a randomized backoff value and an exponentially increasing value capped at a threshold, with the best results being obtained with strategy #4.

# Conclusion:

Testing under chaos is an effective indicator of the scalability and availability of a solution. We compared the 4 backoff mechanisms with varying loads and priority combinations and found the fourth strategy to be the most optimal in terms of desired average latencies and server load.
We also found that it is crucial to design the backoff factor and thresholds well to ensure high utilization of resources and not have slumps.

# Future Work
To decide whether to load shed, we are monitoring only the CPU and Memory utilization for each service. This needs to be extended to Request Latency as I/O intensive operations don't use much of either.
We are currently assigning different backoff factors based on the priority of the requests and the server load thresholds. These need to be manually tuned as shown in Results but we believe they can be dynamically set depending on the current server load and autoscaling capabilities.
We also want to expand our scope of chaos into other parameters such as network delays and node availability.


# Resources

https://dl.acm.org/doi/10.1145/3267809.3267823

https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/

https://netflixtechblog.com/keeping-netflix-reliable-using-prioritized-load-shedding-6cc827b02f94


