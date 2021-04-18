# the goal is to determine the average wait time for people getting their COVID-19 Vaccines at UT Austin

# Things to be done...
# RENEE
# - Clean up function variables

# - Add supply-demand curve for orders
# - Add ordering process
# - Add financial elements

import simpy
import random
import numpy as np

NUM_WORKERS = 25
NUM_MACHINES1 = 10
NUM_MACHINES2 = 5

NUM_PACKAGING = 10
packagetime = 5
DISPATCH_CAPACITY_C = 500 #these should change based on supply demand
DISPATCH_CAPACITY_F = 200


F_ORDER_INTER = 1000
F_INIT_NUM_ORDER = 5
C_ORDER_INTER = 1000
C_INIT_NUM_ORDER = 5

SIM_TIME = 7*8 # 1 work week
C_TIME_LIST = []
F_TIME_LIST = []

C1TIME = 5
C2TIME = 5
C3TIME = 5
Ctime = 10

INITC1 = 500
INITC2 = 500
INITC3 = 400
INITC4 = 400

C1_CAPACITY = 1000
C2_CAPACITY = 1000
C3_CAPACITY = 1000
C4_CAPACITY = 1000
POST_C1_CAPACITY = 500
POST_C2_CAPACITY = 500
POST_C3_CAPACITY = 500
COVID_VACCINE_CAPACITY = 1000

F1time = 5
F2time = 5
F3time = 5
Ftime = 15

INITF1 = 500
INITF2 = 500
INITF3 = 400
INITF4 = 400

F1_CAPACITY = 1000
F2_CAPACITY = 1000
F3_CAPACITY = 1000
F4_CAPACITY = 1000
POST_F1_CAPACITY = 500
POST_F2_CAPACITY = 500
POST_F3_CAPACITY = 500
FLU_VACCINE_CAPACITY = 1000

CF1_CAPACITY = 6000
CF2_CAPACITY = 6000
INITCF1 = 5000
INITCF2 = 5000

class vaccineFacility(object):
    def __init__(self, env, num_workers, num_machines1, num_machines2, C1time, C2time, C3time):
        self.worker = simpy.Resource(env, num_workers)
        self.machine1 = simpy.Resource(env, num_machines1)
        self.machine2 = simpy.Resource(env, num_machines2)
        self.packaging_machine = simpy.Resource(env, NUM_PACKAGING)
        self.env = env
        
        self.processC1_time = C1time
        self.processC2_time = C2time
        self.processC3_time = C3time
        self.processC_time = Ctime
        self.C1 = simpy.Container(env, capacity = C1_CAPACITY, init = INITC1)
        self.C2 = simpy.Container(env, capacity = C2_CAPACITY, init = INITC2)
        self.C3 = simpy.Container(env, capacity = C3_CAPACITY, init = INITC3)
        self.C4 = simpy.Container(env, capacity = C4_CAPACITY, init = INITC4)
        self.postC1 = simpy.Container(env, capacity = POST_C1_CAPACITY, init = 0)
        self.postC2 = simpy.Container(env, capacity = POST_C2_CAPACITY, init = 0)
        self.postC3 = simpy.Container(env, capacity = POST_C3_CAPACITY, init = 0)
        self.postC = simpy.Container(env, capacity = COVID_VACCINE_CAPACITY, init = 0)
        
        self.processF1_time = F1time
        self.processF2_time = F2time
        self.processF3_time = F3time
        self.processF_time = Ftime
        self.F1 = simpy.Container(env, capacity = F1_CAPACITY, init = INITF1)
        self.F2 = simpy.Container(env, capacity = F2_CAPACITY, init = INITF2)
        self.F3 = simpy.Container(env, capacity = F3_CAPACITY, init = INITF3)
        self.F4 = simpy.Container(env, capacity = F4_CAPACITY, init = INITF4)
        self.postF1 = simpy.Container(env, capacity = POST_F1_CAPACITY, init = 0)
        self.postF2 = simpy.Container(env, capacity = POST_F2_CAPACITY, init = 0)
        self.postF3 = simpy.Container(env, capacity = POST_F3_CAPACITY, init = 0)
        self.postF = simpy.Container(env, capacity = FLU_VACCINE_CAPACITY, init = 0)
        
        self.CF1 = simpy.Container(env, capacity = CF1_CAPACITY, init = INITCF1)
        self.CF2 = simpy.Container(env, capacity = CF2_CAPACITY, init = INITCF2)
        
        self.package_time = packagetime
        self.dispatchC = simpy.Container(env, capacity = DISPATCH_CAPACITY_C, init = 0)
        self.dispatchF = simpy.Container(env, capacity = DISPATCH_CAPACITY_F, init = 0)

    def C_process1(self):
        yield self.C1.get(50)
        yield self.postC1.put(50)
        yield self.env.timeout(random.randint(self.processC1_time - 1, self.processC1_time + 1))

    def C_process2(self):
        yield self.C2.get(3)
        yield self.postC2.put(1)
        yield self.env.timeout(random.randint(self.processC2_time - 1, self.processC2_time + 1 ))

    def C_process3(self):
        yield self.C3.get(5)
        yield self.CF1.get(5)
        yield self.postC3.put(20)
        yield self.env.timeout(random.randint(self.processC3_time - 1, self.processC3_time + 1))
        
    def C_process_final(self):
        yield self.postC1.get(5)
        yield self.postC2.get(5)
        yield self.postC3.get(5)
        yield self.postC.put(10)
        yield self.env.timeout(random.randint(self.processC_time - 1, self.processC_time + 1))
        
    def F_process1(self):
        yield self.F1.get(50)
        yield self.postF1.put(50)
        yield self.env.timeout(random.randint(self.processF1_time - 1, self.processF1_time + 1))

    def F_process2(self):
        yield self.F2.get(3)
        yield self.postF2.put(1)
        yield self.env.timeout(random.randint(self.processF2_time - 1, self.processF2_time + 1 ))

    def F_process3(self):
        yield self.F3.get(5)
        yield self.CF1.get(5)
        yield self.postF3.put(20)
        yield self.env.timeout(random.randint(self.processF3_time - 1, self.processF3_time + 1))
        
    def F_process_final(self):
        yield self.postF1.get(5)
        yield self.postF2.get(5)
        yield self.postF3.get(5)
        yield self.postF.put(10)
        yield self.env.timeout(random.randint(self.processF_time - 1, self.processF_time + 1))
        
    def packaging(self, C = True):
        if C is True:
            yield self.postC.get(1)
            yield self.dispatchC.put(1)
        else:
            yield self.postF.get(1)
            yield self.dispatchF.put(1)
        yield self.CF2.get(1)
        yield self.env.timeout(random.randint(self.package_time - 1, self.package_time + 1))

def C_vaccine(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.C_process1())
            print('C1 remaing: ', vf.C1.level)
            print('C1 processed: ', vf.postC1.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.C_process2())
            print('C2 remaing: ', vf.C2.level)
            print('C2 processed: ', vf.postC2.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.C_process3())
            print('C3 remaing: ', vf.C3.level)
            print('C3 processed: ', vf.postC3.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.C_process_final())
            print('Vaccines processed: ', vf.postC.level)
    with vf.packaging_machine.request() as request:
        yield request
        yield env.process(vf.packaging())

    fin_time = env.now
    print('%s spent %.2f to be manufactured.' % (name, fin_time-init_time))
    C_TIME_LIST.append(fin_time-init_time)
    
def F_vaccine(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.F_process1())
            print('F1 remaing: ', vf.F1.level)
            print('F1 processed: ', vf.postF1.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.F_process2())
            print('F2 remaing: ', vf.F2.level)
            print('F2 processed: ', vf.postF2.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.F_process3())
            print('F3 remaing: ', vf.F3.level)
            print('F3 processed: ', vf.postF3.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.F_process_final())
            print('Vaccines processed: ', vf.postF.level)
    with vf.packaging_machine.request() as request:
        yield request
        yield env.process(vf.packaging(C = False))

    fin_time = env.now
    print('%s spent %.2f to be manufactured.' % (name, fin_time-init_time))
    F_TIME_LIST.append(fin_time-init_time)

def setup(env, num_workers, num_machine1, num_machine2, C1time, C2time, C3time, C_order_inter, F_order_inter):
    """Create a vaccine center, a number of initial people and keep creating people
    approx. every ``appointment_inter`` minutes."""
    # Create the vaccine center
    vf = vaccineFacility(env, num_workers, num_machine1, num_machine2, C1time, C2time, C3time)

    # Create initial demand
    for i in range(C_INIT_NUM_ORDER):
        env.process(C_vaccine(env, 'Covid #%d' % i, vf))

    # Create initial demand
    for i in range(F_INIT_NUM_ORDER):
        env.process(F_vaccine(env, 'Flu #%d' % i, vf))

    # Create more orders while the simulation is running
    while True:
        yield env.timeout(random.randint(C_order_inter - 2, C_order_inter + 2))
        i += 1
        env.process(C_vaccine(env, 'Covid #%d' % i, vf))
        
        yield env.timeout(random.randint(F_order_inter - 2, F_order_inter + 2))
        i += 1
        env.process(F_vaccine(env, 'Flu #%d' % i, vf))

env = simpy.Environment()
env.process(setup(env, NUM_WORKERS, NUM_MACHINES1, NUM_MACHINES2, C1TIME, C2TIME, C3TIME, C_ORDER_INTER, F_ORDER_INTER))
env.run(until=SIM_TIME)

print('It took an average of %.2f for each COVID vaccine to be produced.' % np.mean(C_TIME_LIST))
print('It took an average of %.2f for each FLU vaccine to be produced.' % np.mean(F_TIME_LIST))
