# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 22:44:54 2021

@author: renee
"""
  
import simpy
import random

COVID_made = 0

print(f'STARTING SIMULATION')
print(f'----------------------------------')

#-------------------------------------------------
# Buisness hours
hours = 8

# Business days
days = 23

# Total working time (hours)
total_time = hours * days

# Containers
# COVID ingredients
C1_capacity = 500
initial_C1 = 200

C2_capacity = 100
initial_C2 = 60

C1_pre_assemble_capacity = 60
C2_pre_assemble_capacity = 60
COVID_post_assemble_capacity = 120

    
# dispatch
dispatch_capacity = 500

# employees per activity
# C1
num_C1 = 2
mean_C1 = 1
std_C1 = 0.1

# C2
num_C2 = 1
mean_C2 = 1
std_C2 = 0.2

# Assembling
num_assem = 2
mean_assem = 1
std_assem = 0.2


# critical levels
# critical stock should be 1 business day greater than supplier take to come
C1_critical_stock = (((8/mean_C1) * num_C1) * 3) #2 days to deliver + 1 marging
C2_critical_stock = (((8/mean_C2) * num_C2) * 3) #2 days to deliver + 1 marging
assem_critical_stock = (8/mean_assem) * num_assem * 2 #1 day to deliver + 1 marging


#-------------------------------------------------

class Vaccine_Facility:
    def __init__(self, env):
        self.C1 = simpy.Container(env, capacity = C1_capacity, init = initial_C1)
        self.C2 = simpy.Container(env, capacity = C2_capacity, init = initial_C2)
        self.C1_control = env.process(self.C1_stock_control(env))
        self.C2_control = env.process(self.C2_stock_control(env))
        self.C1_pre_assemble = simpy.Container(env, capacity = C1_pre_assemble_capacity, init = 0)
        self.C2_pre_assemble = simpy.Container(env, capacity = C2_pre_assemble_capacity, init = 0)
        self.COVID_post_assemble = simpy.Container(env, capacity = COVID_post_assemble_capacity, init = 0)
        self.dispatch = simpy.Container(env ,capacity = dispatch_capacity, init = 0)
        self.dispatch_control = env.process(self.dispatch_COVID_control(env))

        
    def C1_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.C1.level <= C1_critical_stock:
                print('COVID ingredient C1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
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
                print('COVID ingredient C2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.C2.level, int(env.now/8), env.now % 8))
                print('calling C2 supplier')
                print('----------------------------------')
                yield env.timeout(9)
                print('C2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.C2.put(30)
                print('new C2 stock is {0}'.format(
                    self.C2.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def dispatch_COVID_control(self, env):
        global COVID_made
        yield env.timeout(0)
        while True:
            if self.dispatch.level >= 50:
                print('dispach stock is {0}, calling distributer to pick up COVID vaccines at day {1}, hour {2}'.format(
                    self.dispatch.level, int(env.now/8), env.now % 8))
                print('----------------------------------')
                yield env.timeout(4)
                print('ditributed {0} vaccines at day {1}, hour {2}'.format(
                    self.dispatch.level, int(env.now/8), env.now % 8))
                COVID_made += self.dispatch.level
                yield self.dispatch.get(self.dispatch.level)
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
            
        
        
def C1_process(env, vaccine_facility):
    while True:
        yield vaccine_facility.C1.get(1)
        processC1_time = random.gauss(mean_C1, std_C1)
        yield env.timeout(processC1_time)
        yield vaccine_facility.C2_pre_assemble.put(1)

def C2_process(env, vaccine_facility):
    while True:
        yield vaccine_facility.C2.get(1)
        processC2_time = random.gauss(mean_C2, std_C2)
        yield env.timeout(processC2_time)
        yield vaccine_facility.C1_pre_assemble.put(1)

def COVID_assembler(env, vaccine_facility):
    while True:
        yield vaccine_facility.C1_pre_assemble.get(1)
        yield vaccine_facility.C2_pre_assemble.get(1)
        assembling_time = max(random.gauss(mean_assem, std_assem), 1)
        yield env.timeout(assembling_time)
        yield vaccine_facility.dispatch.put(1)
        
#Generators
        
def C1_maker_gen(env, vaccine_facility):
    for i in range(num_C1):
        env.process(C1_process(env, vaccine_facility))
        yield env.timeout(0)

def C2_maker_gen(env, vaccine_facility):
    for i in range(num_C2):
        env.process(C2_process(env, vaccine_facility))
        yield env.timeout(0)

def assembler_maker_gen(env, vaccine_facility):
    for i in range(num_assem):
        env.process(COVID_assembler(env, vaccine_facility))
        yield env.timeout(0)


#-------------------------------------------------
        

env = simpy.Environment()
vaccine_facility = Vaccine_Facility(env)

C1_gen = env.process(C1_maker_gen(env, vaccine_facility))
C2_gen = env.process(C2_maker_gen(env, vaccine_facility))
assembler_gen = env.process(assembler_maker_gen(env,vaccine_facility))
env.run(until = total_time)


print('Pre assembly has {0} C1 and {1} C2 processed'.format(
    vaccine_facility.C1_pre_assemble.level, vaccine_facility.C2_pre_assemble.level))
print(f'Dispatch has %d COVID vaccines ready to go!' % vaccine_facility.dispatch.level)
print(f'----------------------------------')
print('total vaccines made: {0}'.format(COVID_made + vaccine_facility.dispatch.level))
print(f'----------------------------------')
print(f'SIMULATION COMPLETED')