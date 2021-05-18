---
title: "Project Title"
author:
  - Paddington Bear <bear@paddington.com>
  - John Appleseed <ja@example.com>
---

# Introduction and Related Work
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

# Experiment Results

# Conclusion

# Future Work
> In what follows instructions (including this one) are in blockquotes, while
> text not in blockquotes is a sample. You should of course replace the title
> author metadata that shows up above with appropriate values.
>
> You should start your proposal by stating a problem statement or an overall
> goal  as below.

For our Big Data and Machine Learning final project we plan to develop a
framework for writing distributed quantum computing applications.

# Motivation
> Next you should talk about why, citing sources for your beliefs.

Recently there has been a lot of excitement around quantum computing, and in the
last three years [Google](https://www.nature.com/articles/s41586-019-1666-5),
[Microsoft](https://azure.microsoft.com/en-us/solutions/quantum-computing/) and
others have begun to demonstrate that we are getting close to the point where we
can feasibly build and run programs on quantum computers. A lot of the
excitement around quantum computing stems from its ability to solve some
problems exponentially faster than classical computers. However, all current
quantum computers have limited memory resources, mostly only a few qubits.
Therefore, actual applications are likely to require resources across multiple
quantum computers, but this problem has not been considered thus far.

# Proposed Solution
> Next you should talk about how you plan to address the problem. 
> This should include information about what infrastructure (e.g., CloudLab
> resources) you plan to use, how you plan to make progress, and how you plan to
> evaluate your view.

Since quantum computers are not easily accessible at the moment, we plan to
rely on the [Qx](http://qutech.nl/qx-quantum-computer-simulator/) simulator, and
build on the work done in [ScaffCC](https://github.com/epiqc/ScaffCC). Currently
QX can only simulate O(10) qubits and hence closely matches our assumptions
above. Our plan then proceeds as follows:

* We plan to start by creating large circuits in ScaffCC, building test programs
that cannot be simulated using Qx. 
* Next, we will partition these circuits by hand into portion that can be run on
  individual Qx instances. 
* Next, we will develop a wrapper around Qx so that results from one instance
    can be communicated to another. We will use this wrapper to assemble the
    individual pieces of the circuit into one program and show that we can
    compute the entire program.
* Next, we plan to work on developing techniques to automatically partition code
  circuits rather than hand partitioning them. We will begin by developing
  simple heuristics for this, and extend if time allows.

We plan to run our experiments on multiple CloudLab nodes, each of which
executes one instance of QX.

> You should also talk about how you will evaluate your progress, and what you
> think the ideal end goal would look like.

We will evaluate our project by running a variety of circuits both large and
small. We will use large circuits to demonstrate that our approach makes some
computations feasible, while we will use small circuits (which can be run on
both a single instance and distributed) to measure the performance overhead.

# Timeline
> You should lay out a plan for what you hope to have done by each checkin. Note
> we understand that sometimes unexpected bugs or other problems lead to slip
> ups, but the idea behind the timeline is to provide you with the ability to
> determine where you are in this process. It is important you propose a
> realistic timeline that accounts for classes, interviews and other things
> going on in your life.

* Checkin I (03/30): Have QX and ScaffCC running, have a large circuit that
    cannot be run on one machine, and a manual partitioning where each part can
    be run on a machine.
* Checkin II (04/20): We plan to have an initial implementation where multiple
    Qx instances can communicate with each other. We will have an initial
    measure of performance overheads. We also plan to have decided whether and
    how to optimize our implementation to reduce these overheads.
* Final Handin (05/11): We will have the distributed implementation, and an
    initial system that uses heuristics to partition the circuit.

