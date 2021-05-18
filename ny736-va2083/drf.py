import collections
import os
import sys
import ntpath
from collections import deque

class Task:
    def __init__(self, user_id, task_id, arrival_time, burst_time, task_resources):

        self.resources = task_resources
        self.user_id = user_id
        self.task_id = task_id
        self.arrival_time = arrival_time
        self.burst_time= burst_time

        self.runtime = 0
        self.waiting_time = 0

    @property
    def remaining_time(self):
        return self.burst_time - self.runtime

    def wait(self, time):
        self.waiting_time += time

    def residual_time(self, time):
        if self.remaining_time > time:
            self.runtime += time
            return 0
        else:
            res_time = time-self.remaining_time
            self.runtime = self.burst_time
            return res_time

    @property
    def is_completed(self):
        return self.burst_time <= self.runtime

    @property
    def turnaround_time(self):
        return self.runtime + self.waiting_time

    @property
    def completion_time(self):
        return self.arrival_time + self.turnaround_time

class DRF:

    def __init__(self, num_resources, total_capacity):
        self.time_elapsed = 0
        self.waiting_queue = []
        self.running_queue = []

        self.num_resources = num_resources
        self.total_capacities = total_capacity
        self.consumed_resources = [0]*num_resources

        self.users_to_share = collections.defaultdict(int)
        self.users_to_resources = collections.defaultdict(lambda: [0] * num_resources)

    def enqueue_task(self, task):
        self.waiting_queue.append(task)

    def is_resources_available(self):
        for i in range(self.num_resources):
            if self.consumed_resources[i] >= self.total_capacities[i]:
                return False
        return True

    def find_minimum_share_task(self):
        if len(self.waiting_queue)==0:
            return None

        min_task_idx = 0
        m = float('inf')
        for i,task in enumerate(self.waiting_queue):
            if self.users_to_share[task.user_id] < m:
                m = self.users_to_share[task.user_id]
                min_task_idx = i
        return min_task_idx

    def is_allocate_task(self, task):
        for i in range(len(task.resources)):
            if task.resources[i] + self.consumed_resources[i] > self.total_capacities[i]:
                return False
        return True

    def update_consumption(self, task):
        for i in range(len(task.resources)):
            self.consumed_resources[i] += task.resources[i]

    def update_users_resources(self, task):
        for i in range(len(task.resources)):
            #print(i, task.resources, task.user_id,self.users_to_resources[task.user_id])
            self.users_to_resources[task.user_id][i] += task.resources[i]

    def update_user_dom_share(self, user_id):
        user_alloc_resources = self.users_to_resources[user_id]
        dom_share = 0
        for i in range(len(user_alloc_resources)):
            share = user_alloc_resources[i]/self.total_capacities[i]
            dom_share = max(dom_share, share)
        self.users_to_share[user_id] = dom_share

    def decrease_consumed_resources(self, task):
        for i in range(len(task.resources)):
            self.consumed_resources[i] -= task.resources[i]

    def decrease_users_resources(self, task):
        for i in range(len(task.resources)):
            self.users_to_resources[task.user_id][i] -= task.resources[i]

    def advance_tasks(self, time):
        self.time_elapsed += time

        while time > 0:

            if len(self.running_queue)==0 and len(self.waiting_queue) == 0:
                break

            while self.is_resources_available():
                min_task_idx = self.find_minimum_share_task()
                if min_task_idx is None:
                    break
                task = self.waiting_queue[min_task_idx]

                if self.is_allocate_task(task):
                    self.update_consumption(task)
                    self.update_users_resources(task)
                    self.update_user_dom_share(task.user_id)
                    self.waiting_queue.pop(min_task_idx)
                    self.running_queue.append(task)
                else:
                    break
            max_runtime = 0
            for i,task in enumerate(self.running_queue):
                res_time = task.residual_time(time)
                if task.is_completed:
                    self.running_queue.pop(i)
                    self.decrease_consumed_resources(task)
                    self.decrease_users_resources(task)
                    self.update_user_dom_share(task.user_id)

                max_runtime = max(max_runtime, time - res_time)

            for task in self.waiting_queue:
                task.wait(max_runtime)

            time -= max_runtime

    def scheduler_policy_name(self):
        return self.__class__.__name__

class Simulator:
    def simulate(self, tasks_list, sched_policy):
        for task in tasks_list:
            time = max(0, task.arrival_time-sched_policy.time_elapsed)
            sched_policy.advance_tasks(time)
            sched_policy.enqueue_task(task)

        time = 0
        for task in sched_policy.waiting_queue:
            time += task.remaining_time
        for task in sched_policy.running_queue:
            time += task.remaining_time
        sched_policy.advance_tasks(time)
        self.write_output(tasks_list, sched_policy)

    def write_output(self, tasks_list, sched_policy):
        output_list = sorted(tasks_list, key=lambda tasks : tasks.user_id)
        file = open("tasks_stat_"+ filename + "_"+sched_policy.scheduler_policy_name(), 'w')
        for task in output_list:
            file.write(str(task.user_id)+ " " + str(task.completion_time) + " " +str(task.waiting_time) + " " +str(task.turnaround_time))
            file.write('\n')
        file.close()

        users_to_waiting_time = collections.defaultdict(int)
        for task in tasks_list:
            users_to_waiting_time[task.user_id] += task.waiting_time
        file = open("users_stat_"+ filename + "_"+sched_policy.scheduler_policy_name(), 'w')
        for user, wait_time in users_to_waiting_time.items():
            file.write(str(user) + " " + str(wait_time))
            file.write('\n')
        file.close()

def extract_filename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

if __name__ == '__main__':
    file = sys.argv[1]
    filename = extract_filename(file).split('.')[0]
    scheduler_algo_to_run = 'DRF'
    if len(sys.argv) > 2:
        scheduler_algo_to_run = sys.argv[2]
    total_capacity = []
    number_of_resources = 0
    with open(file) as f:
        process_entries = f.readlines()
        tasks_list = []
        for i,line in enumerate(process_entries):
            if i==0:
                resource_arr = line.split()
                total_capacity = [float(x) for x in resource_arr]
                number_of_resources = len(total_capacity)
            else:
                line_arr = line.split()
                user_id = int(line_arr[0])
                task_id = int(line_arr[1])
                arrival_time = float(line_arr[2])
                burst_time = float(line_arr[3])
                resources_required = [float(x) for x in line_arr[4:]]
                tasks_list.append(Task(user_id, task_id, arrival_time, burst_time, resources_required))
                #print('a', type(arrival_time))
                # print('id', user_id)
                # print('b',burst_time)
    if scheduler_algo_to_run == 'DRF':
        sched_policy = DRF(number_of_resources, total_capacity)
    else:
        raise ValueError("Valid algorithm : DRF")
    sim = Simulator()
    sim.simulate(tasks_list, sched_policy)













