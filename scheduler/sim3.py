#!/usr/bin/env python2.4

from sim  import *
from sim1 import *
from sim2 import *
import sys




class EasyBackfillScheduler(Scheduler):
    
    def __init__(self, total_nodes = 100):
        self.cpu_snapshot = CpuSnapshot(total_nodes)
        self.waiting_list_of_unscheduled_jobs = []

        
    def handleArrivalOfJobEvent(self, just_arrived_job, time):
        """ Here we first add the new job to the waiting list. We then try to schedule
        the jobs in the waiting list, returning a collection of new termination events """
        self.waiting_list_of_unscheduled_jobs.append(just_arrived_job)
        return self._schedule_jobs(time)  
    

    def handleTerminationOfJobEvent(self, job, time):
        """ Here we first delete the tail of the just terminated job (in case it's
        done before user estimation time). We then try to schedule the jobs in the waiting list,
        returning a collection of new termination events """
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return self._schedule_jobs(time)
    
    
    def _schedule_jobs(self, current_time):
        newEvents = Events()
        
        if len(self.waiting_list_of_unscheduled_jobs) == 0:
            return newEvents # waiting list is empty
        self._schedule_the_head_of_the_waiting_list(current_time, newEvents)
        self._backfill_the_tail_of_the_waiting_list(current_time, newEvents)
        return newEvents


    

    def _schedule_the_head_of_the_waiting_list(self, time, newEvents):
        while len(self.waiting_list_of_unscheduled_jobs) > 0: 
            first_job = self.waiting_list_of_unscheduled_jobs[0]
            start_time_of_first_job = self.cpu_snapshot.jobEarliestAssignment(first_job, time)
            if start_time_of_first_job == time:
                self.waiting_list_of_unscheduled_jobs.remove(first_job)
                self.cpu_snapshot.assignJob(first_job, time)
                termination_time = time + first_job.actual_duration
                newEvents.add_job_termination_event(termination_time, first_job) 
            else:
                break

    def _backfill_the_tail_of_the_waiting_list(self, time, newEvents):
        if len(self.waiting_list_of_unscheduled_jobs) > 1:
            first_job = self.waiting_list_of_unscheduled_jobs[0]
            for next_job in self.waiting_list_of_unscheduled_jobs[1:] : 
                if self.canBeBackfilled(first_job, next_job, time):
                    self.waiting_list_of_unscheduled_jobs.remove(next_job)
                    time = self.cpu_snapshot.jobEarliestAssignment(next_job, time)
                    self.cpu_snapshot.assignJob(next_job, time)
                    termination_time = time + next_job.actual_duration
                    newEvents.add_job_termination_event(termination_time, next_job)                    
 
    

    def canBeBackfilled(self, first_job, second_job, time):
        print "... Let's check if the job can be backfilled"
        
        start_time_of_second_job = self.cpu_snapshot.jobEarliestAssignment(second_job, time)
        print "start time of the 2nd job: ", start_time_of_second_job, second_job.id

        if start_time_of_second_job > time:
            return False
    
        shadow_time = self.cpu_snapshot.jobEarliestAssignment(first_job, time)
        print "shadow time, the reserved start time of the first job: ", shadow_time, first_job.id
        
        # TODO: shouldn't this method not change the state?
        self.cpu_snapshot.assignJob(second_job, time)
        start_time_of_1st_if_2nd_job_assigned = self.cpu_snapshot.jobEarliestAssignment(first_job, time)
        print "start time of the 1st job after assigning the 2nd: ",  start_time_of_1st_if_2nd_job_assigned
        
        self.cpu_snapshot.delJobFromCpuSlices(second_job)
       
        if start_time_of_1st_if_2nd_job_assigned > shadow_time:
            print "reserved_start_time_of_first_job", shadow_time
            print "strat_time_of_1st_if_2nd_job_assigned", start_time_of_1st_if_2nd_job_assigned
            return False 
                #this means that assigning the second job at current time postphones the
                #first job in the waiting list, and so the second job cannot be back filled 
        else:
            return True 
      

    def handleEndOfSimulationEvent(self, current_time):
         if current_time == sys.maxint:
            # otherewise, it might be the case that the simulation stoped
            # before some jobs were scheduled properly 
            self.cpu_snapshot.CpuSlicesTestFeasibility()





# a first toy version for the maui -- essentillay the diffrence between this simplified version of maui and easy
# backfilling is that the maui has more degree of freedom: maui may consider the jobs
# not necessarily by order of arrival, as opposed to the easy backfill.    

class MauiScheduler(EasyBackfillScheduler):
    def __init__(self, total_nodes = 100):
        self.cpu_snapshot = CpuSnapshot(total_nodes)
        self.waiting_list_of_unscheduled_jobs = []
        self.maui_global_stamp = 0
    
    def handleArrivalOfJobEvent(self, just_arrived_job, time):
        """ Here we first add the new job to the waiting list. We then try to schedule
        the jobs in the waiting list, returning a collection of new termination events """
        just_arrived_job.maui_stamp = self.maui_global_stamp
        self.maui_global_stamp += 1
        self.waiting_list_of_unscheduled_jobs.append(just_arrived_job)
        return self._schedule_jobs(time)  
        
        
    def _schedule_jobs(self, current_time):
        newEvents = Events()
                             
        if len(self.waiting_list_of_unscheduled_jobs) == 0:
            return newEvents # waiting list is empty        
        
        # schedule the "head" of the waiting list:
        # first reorder the list by the respective order
        # and then call the regular easy backfill's method for scheduling the head  
        self.waiting_list_of_unscheduled_jobs.sort(self.waiting_list_compare)
        self._schedule_the_head_of_the_waiting_list(current_time, newEvents)
        # schedule the "tail": here we override/load the regular method for tail scheduling  
        self._backfill_the_tail_of_the_waiting_list(current_time, newEvents)
        return newEvents

    
    def _backfill_the_tail_of_the_waiting_list(self, time, newEvents):
        # this method is based on the analogue method of EasyBackfill.
        # however it has some modifications, see the lines that are marked with # + 
        if len(self.waiting_list_of_unscheduled_jobs) > 1:
            first_job = self.waiting_list_of_unscheduled_jobs.pop(0) # + 
            print "While trying to backfill ...."
            print "first job is:", first_job
            print ">>>> waiting list by waiting list priority:"
            self.print_waiting_list()
            self.waiting_list_of_unscheduled_jobs.sort(self.backfilling_compare) # + 
            print ">>>> waiting list by backfilling priority:"
            self.print_waiting_list()
            for next_job in self.waiting_list_of_unscheduled_jobs:
                if self.canBeBackfilled(first_job, next_job, time):
                    self.waiting_list_of_unscheduled_jobs.remove(next_job)
                    self.increament_bypass_counters_while_backfilling(first_job, next_job) # +  
                    time = self.cpu_snapshot.jobEarliestAssignment(next_job, time)
                    self.cpu_snapshot.assignJob(next_job, time)
                    termination_time = time + next_job.actual_duration
                    newEvents.add_job_termination_event(termination_time, next_job)
            self.waiting_list_of_unscheduled_jobs.append(first_job) # + 
        return newEvents

    def increament_bypass_counters_while_backfilling(self, first_job, backfilled_job):
        if first_job.maui_stamp < backfilled_job.maui_stamp: # and first_job has entered to the waiting list before next_job   
            first_job.maui_bypass_counter += 1
        for job in self.waiting_list_of_unscheduled_jobs:
            if job.maui_stamp < backfilled_job.maui_stamp: # and first_job has entered to the waiting list before next_job   
                job.maui_bypass_counter += 1
            


    def waiting_list_compare(self, job_a, job_b):
        weight_a = 1 * job_a.admin_QoS + 0 * job_a.user_QoS + 0.0001 * job_a.maui_bypass_counter + 0.1 * job_a.nodes  
        weight_b = 1 * job_b.admin_QoS + 0 * job_b.user_QoS + 0.0001 * job_b.maui_bypass_counter + 0.1 * job_a.nodes
         
        if weight_a > weight_b:
            return -1
        elif weight_a == weight_b:
            return  0
        else:
            return  1
        

    def backfilling_compare(self, job_a, job_b):
        weight_a = 0 * job_a.admin_QoS + 1 * job_a.user_QoS + 0.0001 * job_a.maui_bypass_counter + 0.1 * job_a.nodes 
        weight_b = 0 * job_b.admin_QoS + 1 * job_b.user_QoS + 0.0001 * job_a.maui_bypass_counter + 0.1 * job_b.nodes

        if weight_a > weight_b:
            return -1
        elif weight_a == weight_b:
            return  0
        else:
            return  1
        
    
    def print_waiting_list(self):
        for job in self.waiting_list_of_unscheduled_jobs:
            print job, "bypassed:", job.maui_bypass_counter
        print
        



