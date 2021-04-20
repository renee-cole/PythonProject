# the goal is to determine the average wait time for people getting their COVID-19 Vaccines at UT Austin

# Things to be done...
# - Add supply-demand curve for orders
# - Add ordering process
# - Add financial elements

import simpy
import random
import numpy as np

# WORK DAY INFORMATION--------------------------------------------------------------------------------------------------
work_days = 7
work_hours = 8
SIM_TIME = work_days*work_hours*52 # year

# RESOURCES-------------------------------------------------------------------------------------------------------------
# Resources: resources: three different machines and generic technicians------------------------------------------------
num_workers = 25
num_machines1 = 100
num_machines2 = 50
num_packaging_machines = 10

# Resources: containers-------------------------------------------------------------------------------------------------
# Ingredient and their inital amounts and their raw store capacities----------------------------------------------------
initial_ingredient1 = 500
initial_ingredient2 = 500
initial_ingredient3 = 400
initial_ingredient4 = 400
initial_ingredient5 = 1000
initial_ingredient6 = 500
initial_ingredient7 = 500
initial_ingredient8 = 500
initial_ingredient9 = 50000
initial_ingredient10 = 50000

ingredient1_capacity = 1000
ingredient2_capacity = 1000
ingredient3_capacity = 1000
ingredient4_capacity = 1000
ingredient5_capacity = 1000
ingredient6_capacity = 1000
ingredient7_capacity = 1000
ingredient8_capacity = 1000
ingredient9_capacity = 60000
ingredient10_capacity = 60000

# INGREDIENTS & STORES--------------------------------------------------------------------------------------------------
# Ingredients post-processing (pocesses 1-3) store capacities-----------------------------------------------------------
COVID_postProcess1_capacity = 500
COVID_postProcess2_capacity = 500
COVID_postProcess3_capacity = 500
COVID_postAssembly_capacity = 1000
COVID_dispatch_capacity = 500

FLU_postProcess1_capacity = 500
FLU_postProcess2_capacity = 500
FLU_postProcess3_capacity = 500
FLU_postAssembly_capacity = 1000
FLU_dispatch_capacity = 500

# Ingredients used in each initial process raw ingredients (these are used to determine reordering of stock)------------
# COVID process 1 uses ingredient 1
ingredient1_in_COVIDprocess1 = 50
# COVID process 2 uses ingredient 2
ingredient2_in_COVIDprocess2 = 40
# COVID process 3 uses ingredient 3 & ingredient 9
ingredient3_in_COVIDprocess3 = 30
ingredient9_in_COVIDprocess3 = 50

# FLU process 1 uses ingredient 4
ingredient4_in_FLUprocess1 = 50
# FLU process 2 uses ingredient 5
ingredient5_in_FLUprocess2 = 40
# FLU process 3 uses ingredient 6 & ingredient 9
ingredient5_in_FLUprocess3 = 30
ingredient9_in_FLUprocess3 = 40

# Packaging is the same for COVID and FLU
ingredient10_in_packaging = 40

# PROCESSES-------------------------------------------------------------------------------------------------------------
COVID_process1_time = 5
COVID_process2_time = 5
COVID_process3_time = 5
COVID_assembly_time = 10
COVID_dispatch_capacity = 500 #these should change based on supply demand curves
FLU_process1_time = 5
FLU_process2_time = 5
FLU_process3_time = 5
FLU_assembly_time = 15
Package_time = 5
FLU_dispatch_capacity = 500

# STOCK ORDERING--------------------------------------------------------------------------------------------------------
C1_critical_stock = 3 * (ingredient1_in_COVIDprocess1) * COVID_process1_time / work_hours
C2_critical_stock = 3 * (ingredient2_in_COVIDprocess2) * COVID_process2_time / work_hours
C3_critical_stock = 3 * (ingredient3_in_COVIDprocess3) * COVID_process3_time / work_hours
F1_critical_stock = 3 * (ingredient4_in_FLUprocess1) * FLU_process1_time / work_hours
F2_critical_stock = 3 * (ingredient5_in_FLUprocess2) * FLU_process2_time / work_hours
F3_critical_stock = 3 * (ingredient5_in_FLUprocess3) * FLU_process3_time / work_hours
CF1_critical_stock = 3 * (ingredient9_in_COVIDprocess3) * (COVID_process3_time + FLU_process3_time) / work_hours
CF2_critical_stock = 3 * (ingredient10_in_packaging) * Package_time / work_hours

# DEMAND----------------------------------------------------------------------------------------------------------------
COVID_order_interval = 3
COVID_initial_order_numbers = 10
FLU_order_interval = 3
FLU_initial_order_numbers = 10

# START SIMULATION------------------------------------------------------------------------------------------------------
COVID_time_list = []
FLU_time_list = []

class vaccineFacility(object):
    def __init__(self, env):
        # Initialize everything lol
        self.worker = simpy.Resource(env, num_workers)
        self.machine1 = simpy.Resource(env, num_machines1)
        self.machine2 = simpy.Resource(env, num_machines2)
        self.packaging_machine = simpy.Resource(env, num_packaging_machines)
        self.env = env

        self.Ingredient1 = simpy.Container(env, capacity = ingredient1_capacity, init = initial_ingredient1)
        self.Ingredient2 = simpy.Container(env, capacity = ingredient2_capacity, init = initial_ingredient2)
        self.Ingredient3 = simpy.Container(env, capacity = ingredient3_capacity, init = initial_ingredient3)
        self.Ingredient4 = simpy.Container(env, capacity = ingredient4_capacity, init = initial_ingredient4)
        self.Ingredient5 = simpy.Container(env, capacity = ingredient5_capacity, init = initial_ingredient5)
        self.Ingredient6 = simpy.Container(env, capacity = ingredient6_capacity, init = initial_ingredient6)
        self.Ingredient7 = simpy.Container(env, capacity = ingredient7_capacity, init = initial_ingredient7)
        self.Ingredient8 = simpy.Container(env, capacity = ingredient8_capacity, init = initial_ingredient8)
        self.Ingredient9 = simpy.Container(env, capacity = ingredient9_capacity, init = initial_ingredient9)
        self.Ingredient10 = simpy.Container(env, capacity = ingredient10_capacity, init = initial_ingredient10)

        self.ingredient1_stock_control = env.process(self.I1_stock_control(env))
        self.ingredient2_stock_control = env.process(self.I2_stock_control(env))
        self.ingredient3_stock_control = env.process(self.I3_stock_control(env))
        self.ingredient5_stock_control = env.process(self.I5_stock_control(env))
        self.ingredient6_stock_control = env.process(self.I6_stock_control(env))
        self.ingredient7_stock_control = env.process(self.I7_stock_control(env))
        self.ingredient9_stock_control = env.process(self.I9_stock_control(env))
        self.ingredient10_stock_control = env.process(self.I10_stock_control(env))

        self.COVID_postProcess1_capacity = simpy.Container(env, capacity = COVID_postProcess1_capacity, init = 0)
        self.COVID_postProcess2_capacity = simpy.Container(env, capacity = COVID_postProcess2_capacity, init = 0)
        self.COVID_postProcess3_capacity = simpy.Container(env, capacity = COVID_postProcess3_capacity, init = 0)
        self.COVID_postAssembly_capacity = simpy.Container(env, capacity = COVID_postAssembly_capacity, init = 0)

        self.FLU_postProcess1_capacity = simpy.Container(env, capacity=FLU_postProcess1_capacity, init=0)
        self.FLU_postProcess2_capacity = simpy.Container(env, capacity=FLU_postProcess2_capacity, init=0)
        self.FLU_postProcess3_capacity = simpy.Container(env, capacity=FLU_postProcess3_capacity, init=0)
        self.FLU_postAssembly_capacity = simpy.Container(env, capacity=FLU_postAssembly_capacity, init=0)
        self.COVID_dispatch = simpy.Container(env, capacity = COVID_dispatch_capacity, init = 0)
        self.FLU_dispatch = simpy.Container(env, capacity = FLU_dispatch_capacity, init = 0)

        self.COVID_process1_time = COVID_process1_time
        self.COVID_process2_time = COVID_process2_time
        self.COVID_process3_time = COVID_process3_time
        self.COVID_assembly_time = COVID_assembly_time
        self.FLU_process1_time = FLU_process1_time
        self.FLU_process2_time = FLU_process2_time
        self.FLU_process3_time = FLU_process3_time
        self.FLU_assembly_time = FLU_assembly_time
        self.package_time = Package_time

    # Define each process-----------------------------------------------------------------------------------------------
    def COVID_process1(self):
        yield self.Ingredient1.get(ingredient1_in_COVIDprocess1)
        yield self.COVID_postProcess1_capacity.put(50)
        yield self.env.timeout(random.randint(self.COVID_process1_time - 1, self.COVID_process1_time + 1))

    def COVID_process2(self):
        yield self.Ingredient2.get(ingredient2_in_COVIDprocess2)
        yield self.COVID_postProcess2_capacity.put(1)
        yield self.env.timeout(random.randint(self.COVID_process2_time - 1, self.COVID_process2_time + 1))

    def COVID_process3(self):
        yield self.Ingredient3.get(ingredient3_in_COVIDprocess3)
        yield self.Ingredient9.get(ingredient9_in_COVIDprocess3)
        yield self.COVID_postProcess3_capacity.put(20)
        yield self.env.timeout(random.randint(self.COVID_process3_time - 1, self.COVID_process3_time + 1))
        
    def COVID_process_assembly(self):
        yield self.COVID_postProcess1_capacity.get(5)
        yield self.COVID_postProcess2_capacity.get(5)
        yield self.COVID_postProcess3_capacity.get(5)
        yield self.COVID_postAssembly_capacity.put(10)
        yield self.env.timeout(random.randint(self.COVID_assembly_time - 1, self.COVID_assembly_time + 1))
        
    def FLU_process1(self):
        yield self.Ingredient5.get(ingredient4_in_FLUprocess1)
        yield self.FLU_postProcess1_capacity.put(50)
        yield self.env.timeout(random.randint(self.FLU_process1_time - 1, self.FLU_process1_time + 1))

    def FLU_process2(self):
        yield self.Ingredient6.get(ingredient5_in_FLUprocess2)
        yield self.FLU_postProcess2_capacity.put(1)
        yield self.env.timeout(random.randint(self.FLU_process2_time - 1, self.FLU_process2_time + 1))

    def FLU_process3(self):
        yield self.Ingredient7.get(ingredient5_in_FLUprocess3)
        yield self.Ingredient9.get(ingredient9_in_FLUprocess3)
        yield self.FLU_postProcess3_capacity.put(20)
        yield self.env.timeout(random.randint(self.FLU_process3_time - 1, self.FLU_process3_time + 1))
        
    def FLU_process_assembly(self):
        yield self.FLU_postProcess1_capacity.get(5)
        yield self.FLU_postProcess2_capacity.get(5)
        yield self.FLU_postProcess3_capacity.get(5)
        yield self.FLU_postAssembly_capacity.put(10)
        yield self.env.timeout(random.randint(self.FLU_assembly_time - 1, self.FLU_assembly_time + 1))
        
    def packaging(self, C = True):
        if C is True:
            yield self.COVID_postAssembly_capacity.get(1)
            yield self.COVID_dispatch.put(1)
        else:
            yield self.FLU_postAssembly_capacity.get(1)
            yield self.FLU_dispatch.put(1)
        yield self.Ingredient10.get(1)
        yield self.env.timeout(random.randint(self.package_time - 1, self.package_time + 1))

    # Define stock control----------------------------------------------------------------------------------------------
    def I1_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient1.level <= C1_critical_stock:
                print('Ingredient C1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient1.level, int(env.now / 8), env.now % 8))
                print('calling C1 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('C1 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient1.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient1.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def I2_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient2.level <= C2_critical_stock:
                print('Ingredient C2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient2.level, int(env.now / 8), env.now % 8))
                print('calling C2 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('C2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient2.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient2.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def I3_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient3.level <= C3_critical_stock:
                print('Ingredient C3 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient3.level, int(env.now / 8), env.now % 8))
                print('calling C3 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('C3 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient3.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient3.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
    
    def I5_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient5.level <= F1_critical_stock:
                print('Ingredient F1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient5.level, int(env.now / 8), env.now % 8))
                print('calling F1 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('F1 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient5.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient5.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def I6_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient6.level <= F2_critical_stock:
                print('Ingredient F2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient6.level, int(env.now / 8), env.now % 8))
                print('calling F2 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('F2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient6.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient6.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def I7_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient7.level <= F3_critical_stock:
                print('Ingredient F3 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient7.level, int(env.now / 8), env.now % 8))
                print('calling F3 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('F3 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient7.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient7.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)


    def I9_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient9.level <= CF1_critical_stock:
                print('Ingredient CF1 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient9.level, int(env.now / 8), env.now % 8))
                print('calling CF1 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('CF1 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient9.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient9.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
                
    def I10_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.Ingredient10.level <= CF2_critical_stock:
                print('Ingredient CF2 stock bellow critical level ({0}) at day {1}, hour {2}'.format(
                    self.Ingredient10.level, int(env.now / 8), env.now % 8))
                print('calling CF2 supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('CF2 supplier arrives at day {0}, hour {1}'.format(
                    int(env.now/8), env.now % 8))
                yield self.Ingredient10.put(300)
                print('new ingredient stock is {0}'.format(
                    self.Ingredient10.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)

# COVID vaccine recipe--------------------------------------------------------------------------------------------------
def C_vaccine(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.COVID_process1())
            print('C1 remaing: ', vf.Ingredient1.level)
            print('C1 processed: ', vf.COVID_postProcess1_capacity.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.COVID_process2())
            print('C2 remaing: ', vf.Ingredient2.level)
            print('C2 processed: ', vf.COVID_postProcess2_capacity.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.COVID_process3())
            print('C3 remaing: ', vf.Ingredient3.level)
            print('C3 processed: ', vf.COVID_postProcess3_capacity.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.COVID_process_assembly())
            print('COVID vaccines processed: ', vf.COVID_postAssembly_capacity.level)
    with vf.packaging_machine.request() as request:
        yield request
        yield env.process(vf.packaging())

    fin_time = env.now
    print('%s spent %.2f to be manufactured.' % (name, fin_time-init_time))
    COVID_time_list.append(fin_time - init_time)

# FLU vaccine recipe----------------------------------------------------------------------------------------------------
def F_vaccine(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.FLU_process1())
            print('F1 remaing: ', vf.Ingredient5.level)
            print('F1 processed: ', vf.FLU_postProcess1_capacity.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.FLU_process2())
            print('F2 remaing: ', vf.Ingredient6.level)
            print('F2 processed: ', vf.FLU_postProcess2_capacity.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.FLU_process3())
            print('F3 remaing: ', vf.Ingredient7.level)
            print('F3 processed: ', vf.FLU_postProcess3_capacity.level)
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.FLU_process_assembly())
            print('Flu vaccines processed: ', vf.FLU_postAssembly_capacity.level)
    with vf.packaging_machine.request() as request:
        yield request
        yield env.process(vf.packaging(C = False))

    fin_time = env.now
    print('%s spent %.2f to be manufactured.' % (name, fin_time-init_time))
    FLU_time_list.append(fin_time - init_time)

def setup(env):
    """Create a vaccine facility, a number of initial orders and keep creating orders
    approx. every ``order_inter`` minutes."""
    # Create the vaccine center
    vf = vaccineFacility(env)

    # # Create initial demand
    for i in range(COVID_initial_order_numbers):
        env.process(C_vaccine(env, 'Covid #%d' % i, vf))

    # Create initial demand
    for i in range(FLU_initial_order_numbers):
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
env.process(setup(env))
env.run(until=SIM_TIME)

print('It took an average of %.2f for each COVID vaccine to be produced.' % np.mean(COVID_time_list))
print('It took an average of %.2f for each FLU vaccine to be produced.' % np.mean(FLU_time_list))