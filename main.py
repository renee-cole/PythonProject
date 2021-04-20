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
NUM_MACHINES1 = 100
NUM_MACHINES2 = 50

NUM_PACKAGING = 10
packagetime = 5
DISPATCH_CAPACITY_C = 500 #these should change based on supply demand
DISPATCH_CAPACITY_F = 500


F_ORDER_INTER = 3
F_INIT_NUM_ORDER = 10
C_ORDER_INTER = 3
C_INIT_NUM_ORDER = 10

work_days = 7
work_hours = 8
SIM_TIME = work_days*work_hours*1000 # 1 work week
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

C1_process1 = 50
C2_process2 = 40
C3_process3 = 30
F1_process1 = 50
F2_process2 = 40
F3_process3 = 30

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
CF1time = 20
CF2time = 30

INITF1 = 1000
INITF2 = 500
INITF3 = 500
INITF4 = 500

CF1_process = 50
CF2_process = 40

C1_critical_stock = 3*(C1_process1)*C1TIME/work_hours
C2_critical_stock = 3*(C2_process2)*C2TIME/work_hours
C3_critical_stock = 3*(C3_process3)*C3TIME/work_hours
F1_critical_stock = 3*(F1_process1)*F1time/work_hours
F2_critical_stock = 3*(F2_process2)*F2time/work_hours
F3_critical_stock = 3*(F3_process3)*F3time/work_hours
CF1_critical_stock = 3*(CF1_process)*CF1time/work_hours
CF2_critical_stock = 3*(CF2_process)*CF2time/work_hours

F1_CAPACITY = 1000
F2_CAPACITY = 1000
F3_CAPACITY = 1000
F4_CAPACITY = 1000
POST_F1_CAPACITY = 500
POST_F2_CAPACITY = 500
POST_F3_CAPACITY = 500
FLU_VACCINE_CAPACITY = 1000

CF1_CAPACITY = 60000
CF2_CAPACITY = 60000
INITCF1 = 50000
INITCF2 = 50000

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
        self.C1_control = env.process(self.C1_stock_control(env))
        self.C2_control = env.process(self.C2_stock_control(env))
        self.C3_control = env.process(self.C3_stock_control(env))
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
        self.F1_control = env.process(self.F1_stock_control(env))
        self.F2_control = env.process(self.F2_stock_control(env))
        self.F3_control = env.process(self.F3_stock_control(env))
        self.postF1 = simpy.Container(env, capacity = POST_F1_CAPACITY, init = 0)
        self.postF2 = simpy.Container(env, capacity = POST_F2_CAPACITY, init = 0)
        self.postF3 = simpy.Container(env, capacity = POST_F3_CAPACITY, init = 0)
        self.postF = simpy.Container(env, capacity = FLU_VACCINE_CAPACITY, init = 0)
        
        self.CF1 = simpy.Container(env, capacity = CF1_CAPACITY, init = INITCF1)
        self.CF2 = simpy.Container(env, capacity = CF2_CAPACITY, init = INITCF2)
        self.CF1_control = env.process(self.CF1_stock_control(env))
        self.CF2_control = env.process(self.CF2_stock_control(env))
        
        self.package_time = packagetime
        self.dispatchC = simpy.Container(env, capacity = DISPATCH_CAPACITY_C, init = 0)
        self.dispatchF = simpy.Container(env, capacity = DISPATCH_CAPACITY_F, init = 0)

    def C_process1(self):
        yield self.C1.get(C1_process1)
        yield self.postC1.put(50)
        yield self.env.timeout(random.randint(self.processC1_time - 1, self.processC1_time + 1))

    def C_process2(self):
        yield self.C2.get(C2_process2)
        yield self.postC2.put(1)
        yield self.env.timeout(random.randint(self.processC2_time - 1, self.processC2_time + 1 ))

    def C_process3(self):
        yield self.C3.get(C3_process3)
        yield self.CF1.get(CF1_process)
        yield self.postC3.put(20)
        yield self.env.timeout(random.randint(self.processC3_time - 1, self.processC3_time + 1))
        
    def C_process_final(self):
        yield self.postC1.get(5)
        yield self.postC2.get(5)
        yield self.postC3.get(5)
        yield self.postC.put(10)
        yield self.env.timeout(random.randint(self.processC_time - 1, self.processC_time + 1))
        
    def F_process1(self):
        yield self.F1.get(F1_process1)
        yield self.postF1.put(50)
        yield self.env.timeout(random.randint(self.processF1_time - 1, self.processF1_time + 1))

    def F_process2(self):
        yield self.F2.get(F2_process2)
        yield self.postF2.put(1)
        yield self.env.timeout(random.randint(self.processF2_time - 1, self.processF2_time + 1 ))

    def F_process3(self):
        yield self.F3.get(F3_process3)
        yield self.CF1.get(CF1_process)
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

    def C1_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.C1.level <= C1_critical_stock:
                print('Ingredient C1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.C1.level, int(env.now/8), env.now % 8))
                print('calling C1 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('C1 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.C1.put(300)
                print('new ingredient stock is {0}'.format(
                    self.C1.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def C2_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.C2.level <= C2_critical_stock:
                print('Ingredient C2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.C2.level, int(env.now/8), env.now % 8))
                print('calling C2 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('C2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.C2.put(300)
                print('new ingredient stock is {0}'.format(
                    self.C2.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def C3_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.C3.level <= C3_critical_stock:
                print('Ingredient C3 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.C3.level, int(env.now/8), env.now % 8))
                print('calling C3 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('C3 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.C3.put(300)
                print('new ingredient stock is {0}'.format(
                    self.C3.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
    
    def F1_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.F1.level <= F1_critical_stock:
                print('Ingredient F1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.F1.level, int(env.now/8), env.now % 8))
                print('calling F1 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('F1 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.F1.put(300)
                print('new ingredient stock is {0}'.format(
                    self.F1.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def F2_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.F2.level <= F2_critical_stock:
                print('Ingredient F2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.F2.level, int(env.now/8), env.now % 8))
                print('calling F2 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('F2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.F2.put(300)
                print('new ingredient stock is {0}'.format(
                    self.F2.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def F3_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.F3.level <= F3_critical_stock:
                print('Ingredient F3 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.F3.level, int(env.now/8), env.now % 8))
                print('calling F3 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('F3 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.F3.put(300)
                print('new ingredient stock is {0}'.format(
                    self.F3.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)


    def CF1_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.CF1.level <= CF1_critical_stock:
                print('Ingredient CF1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.CF1.level, int(env.now/8), env.now % 8))
                print('calling CF1 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('CF1 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.CF1.put(300)
                print('new ingredient stock is {0}'.format(
                    self.CF1.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def CF2_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.CF2.level <= CF2_critical_stock:
                print('Ingredient CF2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.CF2.level, int(env.now/8), env.now % 8))
                print('calling CF2 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('CF2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.CF2.put(300)
                print('new ingredient stock is {0}'.format(
                    self.CF2.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
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
            print('COVID vaccines processed: ', vf.postC.level)
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
            print('Flu vaccines processed: ', vf.postF.level)
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

    # # Create initial demand
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
# print(F_TIME_LIST)