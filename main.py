# The goal of the simulation is to simulate production of the COVID and Flu vaccines in a vaccine facility using the 
# pandemic model of supply and demand to queue production

# Imports and fuctions/classes needed to define simulation paramenters--------------------------------------------------
import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

class ingredient:
    def __init__(self, initialAmount, capacity, cost):
        self.initial = initialAmount
        self.amount = capacity
        self.capacity = capacity
        self.cost = cost #per unit
        
# CHANGE INFORMATION BELOW TO CUSTOMIZE SIMULATION----------------------------------------------------------------------

# WORK DAY INFORMATION--------------------------------------------------------------------------------------------------
years = 10
work_days = 7
work_hours = 8
work_weeks = 52*years
SIM_TIME = work_days * work_hours * work_weeks   # Total Work Time

# RESOURCES------------------------------------------------------------------------------------------------------------
# Resources: resources: three different machines and generic technicians------------------------------------------------
num_workers = 7000
num_machines1 = 20000
num_machines2 = 30000
num_packaging_machines = 5000

# Resources: containers-------------------------------------------------------------------------------------------------
# Ingredient and their inital amounts and their raw store capacities and their costs------------------------------------
# Assume these goods are inealsitc and govenment is regulating prices to those below------------------------------------
ingredient1 = ingredient(0, 1000, .05)
ingredient2 = ingredient(0, 1000, 1.00)
ingredient3 = ingredient(0, 1000, 1.05)
ingredient4 = ingredient(0, 1000, 0.25)
ingredient5 = ingredient(500, 1000, 0.35)
ingredient6 = ingredient(500, 1000, 0.70)
ingredient7 = ingredient(500, 10000, 1.00)
ingredient8 = ingredient(500, 1000, 3.00)
ingredient9 = ingredient(1000, 60000, .25)
ingredient10 = ingredient(1000, 60000, 0.01)

# INGREDIENTS & STORES--------------------------------------------------------------------------------------------------
# Ingredients post-processing (pocesses 1-3) store capacities-----------------------------------------------------------
COVID_postProcess1_capacity = 10000
COVID_postProcess2_capacity = 10000
COVID_postProcess3_capacity = 10000
COVID_postAssembly_capacity = 10000
COVID_dispatch_capacity = 10000

FLU_postProcess1_capacity = 10000
FLU_postProcess2_capacity = 10000
FLU_postProcess3_capacity = 10000
FLU_postAssembly_capacity = 10000
FLU_dispatch_capacity = 10000

# Ingredients used in each initial process raw ingredients (these are used to determine reordering of stock)------------
# COVID process 1 uses ingredient 1
ingredient1_in_COVIDprocess1 = 50
# COVID process 2 uses ingredient 2
ingredient2_in_COVIDprocess2 = 50
# COVID process 3 uses ingredient 3 & ingredient 9
ingredient3_in_COVIDprocess3 = 40
ingredient4_in_COVIDprocess3 = 60
# COVID assembly uses post processed 1, 2, 3, & ingredient 4
ingredient9_in_COVIDassembly = 60

# FLU process 1 uses ingredient 4
ingredient5_in_FLUprocess1 = 60
# FLU process 2 uses ingredient 5
ingredient6_in_FLUprocess2 = 50
# FLU process 3 uses ingredient 6 & ingredient 9
ingredient7_in_FLUprocess3 = 40
ingredient8_in_FLUprocess3 = 50
# FLU assembly uses post processed 1, 2, 3, $ ingredient 8
ingredient9_in_FLUassembly = 60

# Packaging is the same for COVID and FLU
ingredient10_in_packaging = 40

# PROCESSES-------------------------------------------------------------------------------------------------------------
COVID_process1_time = 20
COVID_process2_time = 20
COVID_process3_time = 20
COVID_assembly_time = 20
FLU_process1_time = 40
FLU_process2_time = 40
FLU_process3_time = 40
FLU_assembly_time = 40
Package_time = 20
total_dispatch_capacity = 1000
# TODO: These change with demand
COVID_dispatch_capacity = total_dispatch_capacity / 2
FLU_dispatch_capacity = total_dispatch_capacity / 2

# STOCK ORDERING--------------------------------------------------------------------------------------------------------
C1_critical_stock = 5 * ingredient1_in_COVIDprocess1 * work_hours / COVID_process1_time
C2_critical_stock = 5 * ingredient2_in_COVIDprocess2 * work_hours / COVID_process2_time
C3_critical_stock = 5 * ingredient3_in_COVIDprocess3 * work_hours / COVID_process3_time
C4_critical_stock = 5 * ingredient4_in_COVIDprocess3 * work_hours / COVID_assembly_time
F1_critical_stock = 5 * ingredient5_in_FLUprocess1 * work_hours / FLU_process1_time
F2_critical_stock = 5 * ingredient6_in_FLUprocess2 * work_hours / FLU_process2_time
F3_critical_stock = 5 * ingredient7_in_FLUprocess3 *  work_hours / FLU_process3_time
F4_critical_stock = 5 * ingredient8_in_FLUprocess3 * work_hours / FLU_assembly_time
CF1_critical_stock = 5 * (ingredient9_in_COVIDassembly
                          + ingredient9_in_FLUassembly) * work_hours/ (COVID_process3_time + FLU_process3_time) 
CF2_critical_stock = 5 * ingredient10_in_packaging * work_hours / Package_time

# DEMAND----------------------------------------------------------------------------------------------------------------
COVID_order_interval = 3
COVID_order_amount = 1
COVID_initial_order_numbers = 0
FLU_order_interval = 3
FLU_order_amount = 1
FLU_initial_order_numbers = 10

# POPULATION------------------------------------------------------------------------------------------------------------
total_population = 50000
prop_antivaxxers = 0.1
vaccinated_pop = 0
unvaccinated_pop = total_population * (1 - prop_antivaxxers)
percent_health_workers = 0.12
percent_at_risk = .15
percent_adults = .50
percent_everyone = 1 - percent_adults - percent_at_risk - percent_health_workers

# START SIMULATION------------------------------------------------------------------------------------------------------
COVID_prep_time_list = []
COVID_assembly_time_list = []
COVID_package_time_list = []
FLU_prep_time_list = []
FLU_assembly_time_list = []
FLU_package_time_list = []

class vaccineFacility(object):
    def __init__(self, env):
        # Initialize everything lol
        self.worker = simpy.Resource(env, num_workers)
        self.machine1 = simpy.Resource(env, num_machines1)
        self.machine2 = simpy.Resource(env, num_machines2)
        self.packaging_machine = simpy.Resource(env, num_packaging_machines)
        self.env = env

        self.Ingredient1 = simpy.Container(env, capacity=ingredient1.capacity, init=ingredient1.initial)
        self.Ingredient2 = simpy.Container(env, capacity=ingredient2.capacity, init=ingredient2.initial)
        self.Ingredient3 = simpy.Container(env, capacity=ingredient3.capacity, init=ingredient3.initial)
        self.Ingredient4 = simpy.Container(env, capacity=ingredient4.capacity, init=ingredient4.initial)
        self.Ingredient5 = simpy.Container(env, capacity=ingredient5.capacity, init=ingredient5.initial)
        self.Ingredient6 = simpy.Container(env, capacity=ingredient6.capacity, init=ingredient6.initial)
        self.Ingredient7 = simpy.Container(env, capacity=ingredient7.capacity, init=ingredient7.initial)
        self.Ingredient8 = simpy.Container(env, capacity=ingredient8.capacity, init=ingredient8.initial)
        self.Ingredient9 = simpy.Container(env, capacity=ingredient9.capacity, init=ingredient9.initial)
        self.Ingredient10 = simpy.Container(env, capacity=ingredient10.capacity, init=ingredient10.initial)

        self.ingredient1_stock_control = env.process(self.stock_control(env, self.Ingredient1, 'Ingredient 1', ingredient1.cost))
        self.ingredient2_stock_control = env.process(self.stock_control(env, self.Ingredient2, 'Ingredient 2', ingredient2.cost))
        self.ingredient3_stock_control = env.process(self.stock_control(env, self.Ingredient3, 'Ingredient 3', ingredient3.cost))
        self.ingredient4_stock_control = env.process(self.stock_control(env, self.Ingredient4, 'Ingredient 4', ingredient4.cost))
        self.ingredient5_stock_control = env.process(self.stock_control(env, self.Ingredient5, 'Ingredient 5', ingredient5.cost))
        self.ingredient6_stock_control = env.process(self.stock_control(env, self.Ingredient6, 'Ingredient 6', ingredient6.cost))
        self.ingredient7_stock_control = env.process(self.stock_control(env, self.Ingredient7, 'Ingredient 7', ingredient7.cost))
        self.ingredient8_stock_control = env.process(self.stock_control(env, self.Ingredient8, 'Ingredient 8', ingredient8.cost))
        self.ingredient9_stock_control = env.process(self.stock_control(env, self.Ingredient9, 'Ingredient 9', ingredient9.cost))
        self.ingredient10_stock_control = env.process(self.stock_control(env, self.Ingredient10, 'Ingredient 10', ingredient10.cost))
        self.cost = ingredient1.initial*ingredient1.cost + ingredient2.initial*ingredient2.cost +ingredient3.initial*ingredient3.cost 
        + ingredient4.initial*ingredient4.cost + ingredient5.initial*ingredient5.cost + ingredient6.initial*ingredient6.cost 
        + ingredient7.initial*ingredient7.cost +ingredient8.initial*ingredient8.cost +ingredient9.initial*ingredient9.cost 
        + ingredient10.initial*ingredient10.cost

        self.COVID_postProcess1_capacity = simpy.Container(env, capacity=COVID_postProcess1_capacity, init=0)
        self.COVID_postProcess2_capacity = simpy.Container(env, capacity=COVID_postProcess2_capacity, init=0)
        self.COVID_postProcess3_capacity = simpy.Container(env, capacity=COVID_postProcess3_capacity, init=0)
        self.COVID_postAssembly_capacity = simpy.Container(env, capacity=COVID_postAssembly_capacity, init=0)
        self.COVID_dispatch = simpy.Container(env, capacity=COVID_dispatch_capacity, init=0)

        self.FLU_postProcess1_capacity = simpy.Container(env, capacity=FLU_postProcess1_capacity, init=0)
        self.FLU_postProcess2_capacity = simpy.Container(env, capacity=FLU_postProcess2_capacity, init=0)
        self.FLU_postProcess3_capacity = simpy.Container(env, capacity=FLU_postProcess3_capacity, init=0)
        self.FLU_postAssembly_capacity = simpy.Container(env, capacity=FLU_postAssembly_capacity, init=0)
        self.FLU_dispatch = simpy.Container(env, capacity=FLU_dispatch_capacity, init=0)

        self.FLU_distribution = env.process(self.dispatch_control(env, self.FLU_dispatch, False))
        self.COVID_distribution = env.process(self.dispatch_control(env, self.COVID_dispatch, True))

        self.COVID_process1_time = COVID_process1_time
        self.COVID_process2_time = COVID_process2_time
        self.COVID_process3_time = COVID_process3_time
        self.COVID_assembly_time = COVID_assembly_time
        self.FLU_process1_time = FLU_process1_time
        self.FLU_process2_time = FLU_process2_time
        self.FLU_process3_time = FLU_process3_time
        self.FLU_assembly_time = FLU_assembly_time
        self.package_time = Package_time
        
        self.total_population = total_population
        self.prop_antivaxxers = prop_antivaxxers
        self.vaccinated_pop = 0
        self.percent_health_workers = percent_health_workers
        self.percent_at_risk = percent_at_risk
        self.percent_adults = percent_adults
        self.percent_everyone = 1 - self.percent_adults - self.percent_at_risk - self.percent_health_workers
        self.unvaccinated_pop = self.total_population * (1 - self.prop_antivaxxers)
        
        self.demand_control = env.process(self.demand_control(env))
        self.COVID_order_amount = COVID_order_amount
        
    # Define each process-----------------------------------------------------------------------------------------------
    def COVID_process1(self):
        yield self.Ingredient1.get(ingredient1_in_COVIDprocess1)
        yield self.env.timeout(random.randint(self.COVID_process1_time - 1, self.COVID_process1_time + 1))
        yield self.COVID_postProcess1_capacity.put(50)

    def COVID_process2(self):
        yield self.Ingredient2.get(ingredient2_in_COVIDprocess2)
        yield self.env.timeout(random.randint(self.COVID_process2_time - 1, self.COVID_process2_time + 1))
        yield self.COVID_postProcess2_capacity.put(50)
        
    def COVID_process3(self):
        yield self.Ingredient3.get(ingredient3_in_COVIDprocess3)
        yield self.Ingredient4.get(ingredient4_in_COVIDprocess3)
        yield self.env.timeout(random.randint(self.COVID_process3_time - 1, self.COVID_process3_time + 1))
        yield self.COVID_postProcess3_capacity.put(20)

    def COVID_process_assembly(self):
        yield self.COVID_postProcess1_capacity.get(5)
        yield self.COVID_postProcess2_capacity.get(5)
        yield self.COVID_postProcess3_capacity.get(5)
        yield self.Ingredient9.get(ingredient9_in_COVIDassembly)
        yield self.env.timeout(random.randint(self.COVID_assembly_time - 1, self.COVID_assembly_time + 1))
        yield self.COVID_postAssembly_capacity.put(8)

    def FLU_process1(self):
        yield self.Ingredient5.get(ingredient5_in_FLUprocess1)
        yield self.env.timeout(random.randint(self.FLU_process1_time - 1, self.FLU_process1_time + 1))
        yield self.FLU_postProcess1_capacity.put(50)

    def FLU_process2(self):
        yield self.Ingredient6.get(ingredient6_in_FLUprocess2)
        yield self.env.timeout(random.randint(self.FLU_process2_time - 1, self.FLU_process2_time + 1))
        yield self.FLU_postProcess2_capacity.put(50)

    def FLU_process3(self):
        yield self.Ingredient7.get(ingredient7_in_FLUprocess3)
        yield self.Ingredient8.get(ingredient8_in_FLUprocess3)
        yield self.env.timeout(random.randint(self.FLU_process3_time - 1, self.FLU_process3_time + 1))
        yield self.FLU_postProcess3_capacity.put(50)

    def FLU_process_assembly(self):
        yield self.FLU_postProcess1_capacity.get(5)
        yield self.FLU_postProcess2_capacity.get(5)
        yield self.FLU_postProcess3_capacity.get(5)
        yield self.Ingredient9.get(ingredient9_in_FLUassembly)
        yield self.env.timeout(random.randint(self.FLU_assembly_time - 1, self.FLU_assembly_time + 1))
        yield self.FLU_postAssembly_capacity.put(10)

    def packaging(self, C=True):
        if C is True:
            yield self.COVID_postAssembly_capacity.get(10)
        else:
            yield self.FLU_postAssembly_capacity.get(10)
        yield self.Ingredient10.get(1)
        yield self.env.timeout(random.randint(self.package_time - 1, self.package_time + 1))
        if C is True:
            yield self.COVID_dispatch.put(10)
        else:
            yield self.FLU_dispatch.put(10)

    # Define stock control----------------------------------------------------------------------------------------------
    def stock_control(self, env, ingred, name, cost):
        yield env.timeout(0)
        while True:
            if ingred.level <= C1_critical_stock:
                print('{0} stock below critical level ({1}) at day {2}, hour {3}'.format(name, ingred.level,
                                                                                          int(env.now / 8),
                                                                                          env.now % 8))
                print('calling', name, 'supplier')
                print('----------------------------------')
                yield env.timeout(16)
                print('{0} supplier arrives at day {1}, hour {2}'.format(name, int(env.now / 8), env.now % 8))
                yield ingred.put(ingred.capacity/2)
                self.cost += cost*ingred.capacity/2
                print('New {0} stock is {1}'.format(name, ingred.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)
    
    # Define dispatch control-------------------------------------------------------------------------------------------
    def dispatch_control(self, env, vaccine, C):
        yield env.timeout(0)
        while True:
            # print('Vaccine Level', vaccine.level)
            if C:
                name='COVID'
            else:
                name='FLU'
            if vaccine.level >= 50:
                print(
                    'dispatch stock is {0}, calling distributor to pick up {1} vaccines at day {2}, hour {3}'.format(
                        vaccine.level, name, int(env.now / 8), env.now % 8))
                print('----------------------------------')
                yield env.timeout(4)
                print('Distributed {0} vaccines at day {1}, hour {2}'.format(vaccine.level, int(env.now / 8),
                                                                             env.now % 8))
                if C:
                    self.vaccinated_pop += vaccine.level
                    self.unvaccinated_pop -= vaccine.level
                yield vaccine.get(vaccine.level)
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)

    # Define population demand------------------------------------------------------------------------------------------
    def demand_control(self,env):
        yield env.timeout(0)
        while True:
             if self.unvaccinated_pop > 0:

                    unvaccinated_percent = self.unvaccinated_pop / self.total_population * (1 - self.prop_antivaxxers)
                    COVID_dispatch_capacity = total_dispatch_capacity * unvaccinated_percent
                    FLU_dispatch_capacity = total_dispatch_capacity - COVID_dispatch_capacity
                    # stage 1: only vaccinate health workers in 1 month
                    if (self.vaccinated_pop / self.total_population) <= self.percent_health_workers:
                        self.COVID_order_amount = 3 * self.percent_health_workers * self.total_population / (8 * 7 * 4)
                        yield env.timeout(1)
                    # stage 2: vaccinate at risk in 2 months
                    elif (self.vaccinated_pop / self.total_population) <= (self.percent_health_workers + self.percent_at_risk):
                        self.COVID_order_amount = 3 * self.percent_at_risk * self.total_population / (8 * 7 * 6)
                        yield env.timeout(1)
                    # stage 3: vaccinate adults in 3 months
                    elif (self.vaccinated_pop / self.total_population) <= (self.percent_health_workers + self.percent_at_risk + self.percent_adults):
                        self.COVID_order_amount = 3 * self.percent_adults * self.unvaccinated_pop / (8 * 7 * 30)
                        yield env.timeout(1)
                    # stage 4: vaccinate everyone whenever
                    else:
                        self.COVID_order_amount = 5
                        yield env.timeout(1)
             else:
                yield env.timeout(1)

# COVID vaccine recipe--------------------------------------------------------------------------------------------------
def COVID_ingredients(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.COVID_process1()) & env.process(vf.COVID_process2()) & env.process(vf.COVID_process3()) 
            print('I1 remaining:', vf.Ingredient1.level)
            print('I1 processed:', vf.COVID_postProcess1_capacity.level)
            print('I2 remaining:', vf.Ingredient2.level)
            print('I2 processed:', vf.COVID_postProcess2_capacity.level)
            print('I3 remaining:', vf.Ingredient3.level)
            print('I3 processed:', vf.COVID_postProcess3_capacity.level)
            print('I4 remaining:', vf.Ingredient4.level)
            print('I4 processed:', vf.COVID_postProcess3_capacity.level)
            fin_time = env.now
            COVID_prep_time_list.append(fin_time - init_time)

def COVID_assembler(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.COVID_process_assembly())
            print('COVID vaccines processed:', vf.COVID_postAssembly_capacity.level) 
            fin_time = env.now
            COVID_assembly_time_list.append(fin_time - init_time)

def COVID_packager(env, name, vf):
    init_time = env.now
    with vf.packaging_machine.request() as request:
        yield request
        yield env.process(vf.packaging())
        print('COVID vaccines packaged:', vf.COVID_dispatch.level)
        fin_time = env.now
        COVID_package_time_list.append(fin_time - init_time)

# FLU vaccine recipe----------------------------------------------------------------------------------------------------
def FLU_ingredients(env, name, vf):
    init_time = env.now

    with vf.worker.request() as request:
        yield request
        with vf.machine1.request() as request:
            yield request
            yield env.process(vf.FLU_process1()) & env.process(vf.FLU_process2()) & env.process(vf.FLU_process3()) 
            print('I5 remaining:', vf.Ingredient5.level)
            print('I5 processed:', vf.FLU_postProcess1_capacity.level)
            print('I6 remaining:', vf.Ingredient6.level)
            print('I6 processed:', vf.FLU_postProcess2_capacity.level)
            print('I7 remaining:', vf.Ingredient7.level)
            print('I7 processed:', vf.FLU_postProcess3_capacity.level)
            print('I8 remaining:', vf.Ingredient8.level)
            print('I8 processed:', vf.FLU_postProcess3_capacity.level)
            fin_time = env.now
            FLU_prep_time_list.append(fin_time - init_time)

def FLU_assembler(env, name, vf):
    init_time = env.now
    with vf.worker.request() as request:
        yield request
        with vf.machine2.request() as request:
            yield request
            yield env.process(vf.FLU_process_assembly())
            print('FLU vaccines processed:', vf.FLU_postAssembly_capacity.level)
            fin_time = env.now
            FLU_assembly_time_list.append(fin_time - init_time)

def FLU_packager(env, name, vf):
    init_time = env.now
    with vf.packaging_machine.request() as request:
        yield request
        yield env.process(vf.packaging(C=False))
        print('FLU vaccines packaged:', vf.FLU_dispatch.level)
        fin_time = env.now
        FLU_package_time_list.append(fin_time - init_time)

time=[]
populations=[]
ingredients1=[]
ingredients5=[]
dispatchs=[]

# Simulation Setup------------------------------------------------------------------------------------------------------
def setup(env):
    """Create a vaccine facility, a number of initial orders and keep creating orders
    approx. every ``order_inter`` minutes."""
    # Create the vaccine center
    vf = vaccineFacility(env)
    # # Create initial demand
    for i in range(COVID_initial_order_numbers):
        env.process(COVID_ingredients(env, 'Covid #%d' % i, vf))
        env.process(COVID_assembler(env, 'Covid #%d' % i, vf))
        env.process(COVID_packager(env, 'Covid #%d' % i, vf))
        
    # Create initial demand
    for i in range(FLU_initial_order_numbers):
        env.process(FLU_ingredients(env, 'Flu #%d' % i, vf))
        env.process(FLU_assembler(env, 'Flu #%d' % i, vf))
        env.process(FLU_packager(env, 'Flu #%d' % i, vf))
    
    # Create more orders while the simulation is running
    while vf.unvaccinated_pop > 0:
        print('Vaccinated Pop:', vf.vaccinated_pop)
        yield env.timeout(random.randint(COVID_order_interval - 2, COVID_order_interval + 2))
        i = vf.COVID_order_amount
        print('COVID demand', vf.COVID_order_amount)
        env.process(COVID_ingredients(env, 'Covid #%d' % i, vf))
        env.process(COVID_assembler(env, 'Covid #%d' % i, vf))
        env.process(COVID_packager(env, 'Covid #%d' % i, vf))

        yield env.timeout(random.randint(FLU_order_interval - 2, FLU_order_interval + 2))
        i += FLU_order_amount
        env.process(FLU_ingredients(env, 'Flu #%d' % i, vf))
        env.process(FLU_assembler(env, 'Flu #%d' % i, vf))
        env.process(FLU_packager(env, 'Flu #%d' % i, vf))
        
        print('Total cost: ${0}'.format(vf.cost))
        
        """Change vf.Ingredient# to change what is plotted"""
        time.append(env.now/(work_days*work_hours))
        ingredients1.append([vf.Ingredient1.level])
        ingredients5.append([vf.Ingredient5.level])
        populations.append([vf.vaccinated_pop,vf.unvaccinated_pop])
        dispatchs.append([vf.COVID_dispatch.level,vf.FLU_dispatch.level])
        
    print(env.now)
    
# Run Simulation--------------------------------------------------------------------------------------------------------
env = simpy.Environment()
env.process(setup(env))
env.run(until=SIM_TIME)

# Printing relevant information-----------------------------------------------------------------------------------------
print('It took an average of %.2f for each COVID vaccine batch to be produced.' % (np.mean(COVID_prep_time_list)
      +  np.mean(COVID_assembly_time_list) + np.mean(COVID_package_time_list)))
print('It took an average of %.2f for each FLU vaccine batch to be produced.' % (np.mean(FLU_prep_time_list)
      +  np.mean(FLU_assembly_time_list) + np.mean(FLU_package_time_list)))

if SIM_TIME>12*work_days*work_hours:
    shortplot=12
else:
    shortplot=time[-1]
    
fig1=plt.figure(1)
plt.plot(time,populations)
plt.xlabel('Time (Weeks)')
plt.gca().legend(['Vaccinated','Unvaccinated'])
plt.title('Vaccinated and Unvaccinated Population vs Time')

fig2=plt.figure(2)
plt.plot(time,dispatchs)
plt.xlabel('Time (Weeks)')
plt.ylabel('Dispatch Facility Level')
plt.title('Dispatch Level vs Time')
plt.gca().legend(['COVID','FLU'])
plt.xlim([0,shortplot])

fig3=plt.figure(3)
plt.plot(time,ingredients1)
plt.xlabel('Time (Weeks)')
plt.ylabel('Ingredient 1 Level')
plt.title('Ingredient 1 Level vs Time')
plt.xlim([0,shortplot])

fig4=plt.figure(4)
plt.plot(time,ingredients5)
plt.xlabel('Time (Weeks)')
plt.ylabel('Ingredient 5 Level')
plt.title('Ingredient 5 Level vs Time')
plt.xlim([0,shortplot])

CProd=[]
temp=0
count=0
for i in dispatchs:
    CProd.append(i[0]+temp)
    temp=CProd[count]
    count+=1
    
FProd=[]
temp=0
count=0
for i in dispatchs:
    FProd.append(i[1]+temp)
    temp=FProd[count]
    count+=1
    
fig5=plt.figure(5)
plt.plot(time,CProd,time,FProd)
plt.xlabel('Time (Weeks)')
plt.ylabel('Vaccines Produced')
plt.title('Vaccine Production vs Time')
plt.gca().legend(['COVID','FLU'])
# plt.xlim([0,12])


plt.show()