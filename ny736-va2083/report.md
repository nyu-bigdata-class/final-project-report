---
title: "Project Title"
author:
  - Paddington Bear <bear@paddington.com>
  - John Appleseed <ja@example.com>
---

# Motivation
Resource allocation is very crucial in a cluster where many users compete with each other 
over multiple resources. [Dominant Resource Fairness](http://web.eecs.umich.edu/~mosharaf/Readings/DRF.pdf) computes the share of each resource
allocated to a user. It defines dominant resource of a user as the resource with maximum share among all the resources allocated to the user.
DRF seeks to maximize the minimum dominant share across all users.For example, if dominant resource of user X is CPU and dominant resource of user Y is  memory, DRF attempts to equalize user X’s share of CPUs with user Y’s share of memory. DRF is essentially max-min fairness if we restrict the number of resources to one.
DRF is sharing incentive in case of homogeneous jobs. But if jobs have varied runtimes then DRF fails the sharing incentive criteria. Consider a case, when a resource hog job arrives first and then resource mice arrives. In this scenario, the later arriving resource mice would have large waiting times. This is because DRF doesn't preempt the jobs. It allocates the resources, by computing the dominant share of all the available jobs at a particular point of time. Once a job gets the resource, there is no notion of preemption. 

[Themis](https://cs.nyu.edu/~apanda/classes/sp21/papers/themis.pdf) overcomes the sharing incentive problem of DRF. It uses a preemptive approach and seeks to achieve a finish time fairness. We take inspiration from Themis and DRF. We devise a new fairness metric. Our algorithm is preemptive and is sharing incentive in a more general setting i.e. jobs can be resource hogs or mice.  

# Approach

* Similar to DRF, we compute the share of each resource allocated to a user. We take the maximum of all the shares i.e. dominant share. The resource correspondint to the maximum share is called as dominant share.
* The above mentioned dominant share and dominant resource are as per the DRF. We define a new metric Sharing Incentive Dominant Share (SIDS) for each user. SIDS is defined as the linear combination of the user's dominant share as per the DRF algorithm and the time for which the user had the resources.  
```
Sharing Incentive Dominant Share (SIDS) = p * (DRF's Dominant Share) + (1-p) * (t)
where p ∈ (0, 1) and t is the time for which user had the resources
```
* We seek to maximize the minimum Sharing Incentive Dominant Share (SIDS) across all users. We allocate resources to a user with least SIDS. 

* In our algorithm, 'p' acts like a weighing factor between user's dominant share and time for which the user had the resources. If a user is having the resources for long time then it would increase his SIDS and hence his priority would be decreased. This solves the problem when a User X has million of resource mice tasks, while another user Y has a resource hog. Clearly user Y has a high DRF's dominant share compared to user X. Hence user X's mice tasks would be allocated first in case of DRF. It might be possible that the mice tasks of user X occupy huge chunk of the cluster's resources and they have a very long running time. Since DRF doesn't preempt, the tasks of user Y would have to wait. While in case of our algorithm, the SIDS value of user X would increase with time and after a certain point of time, SIDS of X would become larger than the SIDS of user Y. Hence user Y wouldn't have to wait for a long time.  

* We maintain running queue and waiting queue. Running queue contains the jobs which are having the resources while the waiting queue contain the jobs
which aren't having the resources. Our preemption strategy is based on the load factor. We compute the load factor by summing the waiting times of all the jobs in 
the waiting queue and divide it by the summation of the running time of all the jobs in the running queue.
```
Let there are m jobs in waiting queue with waiting time as t_1, t_2, ...,t_m
Let there are n jobs in running queue with running time as t_1, t_2,...., t_n 
t_wait = t_1 + t_2 + ... + t_m
t_run = t_1 + t_2 + ... + t_n
Load Factor = t_wait/ t_run 
```
* If the load factor is greater than the threshold alpha, then we say that it's the time to start preemption. Also, note that how frequently we check the load factor depends on the simulator frequency "Gamma". As the load factor crosses threshold, we kicks on preemption strategy. We go over all the running jobs and if the runtime of the user to which that job belongs is greater than the minimum of average finish time of job divided by waiting queue length and a constant beta then the job is preempted.
```
\\Preemption strategy
if Load Factor > alpha
  if user's run time of job > min (average finish time of jobs/waiting queue length, beta)
      preempt the job
  else
      don't preempt
```
* We use preemption mechanism to avoid the cases like, a resource hog job arrives first and DRF allocates resource to the hog. After sometime, a resource mice arrives, since DRF doesn't preempt the resource mice would have to wait till the hog finishes. However, if we have a preemption mechanism then we can preempt the 
hog, thus reducing waiting time for mice.

# Experiment Results

## Experiment 1
* We have two users X and Y.
* We assume that tasks are independent
* We sample 300 tasks for each user demanding two resources <CPU, Memory>
* Both User X and User Y have same arrival rate

![xa](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/xa.png) ![ya](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/ya.png)
* Runtime is sampled using exponential distribution with mean runtime of user X < mean runtime of user Y
![xr](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/xr.png) ![yr](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/yr.png)

* Resources CPU is sampled using binomial distribution with mean cpu usage of user X < mean cpu usage of user Y

![xc](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/xc.png) ![yc](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/yc.png)

* Resources Memory is sampled using binomial distribution with mean memory usage of user X < mean memory usage of user Y

![xm](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/xm.png) ![ym](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/ym.png)
* Clearly user X is resource mice and user Y is resource hog
* Total resources available <1000, 10000>. We set p = 0.5, alpha = 2, beta = 50 and gamma = 50.

![ux](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/ux.png)  ![uy](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/uy.png)

## Experiment 2
* We have two users X and Y.
* We assume that tasks are independent
* We sample 1000 tasks for each user X and 500 tasksfor user Y demanding two resources <CPU, Memory>
* Both User X and User Y have same arrival rate

![xa](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/x2a.png) ![ya](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/y2a.png)
* Runtime is sampled using exponential distribution with mean runtime of user X > mean runtime of user Y
![xr](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/x2r.png) ![yr](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/y2r.png)

* Resources CPU is sampled using binomial distribution with mean cpu usage of user X < mean cpu usage of user Y

![xc](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/x2c.png) ![yc](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/y2c.png)

* Resources Memory is sampled using binomial distribution with mean memory usage of user X < mean memory usage of user Y

![xm](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/x2m.png) ![ym](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/y2m.png)
* In this setup, user X demands lot of time consuming mice tasks i.e. 1000 tasks demanding less cpu and memory resources but for a large amount of time while user Y has fewer resource hog tasks i.e. demanding more of cpu and memeory but having a smaller runtime
* Total resources available <1000, 10000>. We set p = 0.5, alpha = 2, beta = 50 and gamma = 50.

![ux](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/u2x.png)  ![uy](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/u2y.png)

## Effect of Hyperparameter

![ux](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/p.png)


![ux](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/a.png)


![ux](https://github.com/neeraj71/final-project-report/blob/main/ny736-va2083/images/b.png)


# Conclusion

# Future Work

