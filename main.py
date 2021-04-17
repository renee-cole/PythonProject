# the goal is to determine the average wait time for people getting their COVID-19 Vaccines at UT Austin

import simpy
import random
import numpy as np

NUM_NURSES = 25
VACCINE_TIME = 5
PAPER_TIME = 15
CHECK_TIME = 10
WAIT_TIME = 15
APPT_INTER = 5
INIT_NUM_PEOPLE = 25
SIM_TIME = 1000
TIME_LIST = []

class vaccineCenter(object):
    def __init__(self, env, num_nurses, vaccine_time, paper_time, check_time, wait_time):
        self.nurse = simpy.Resource(env, num_nurses)
        self.env = env
        self.vaccination_time = vaccine_time
        self.paperwork_time = paper_time
        self.reaction_check_time = check_time
        self.waiting_time = wait_time

    def wait_in_line(self):
        yield self.env.timeout(random.randint(self.waiting_time-2, self.waiting_time+3))

    def fill_paperwork(self):
        yield self.env.timeout(random.randint(self.paperwork_time - 2, self.paperwork_time + 3))

    def get_vaccinated(self):
        yield self.env.timeout(random.randint(self.vaccination_time - 2, self.paperwork_time + 3))

    def wait_for_reaction(self):
        yield self.env.timeout(random.randint(self.reaction_check_time - 2, self.reaction_check_time + 3))


def person(env, name, vc):
    # print('%s arrives at the vaccine center at %.2f.' % (name, env.now))
    init_time = env.now
    with vc.nurse.request() as request:
        yield request
        # print('%s enters the vaccine center at %.2f.' % (name, env.now))
        yield env.process(vc.wait_in_line())
        yield env.process(vc.fill_paperwork())
        yield env.process(vc.get_vaccinated())
        yield env.process(vc.wait_for_reaction())

        # print('%s leaves the vaccine center at %.2f.' % (name, env.now))
        fin_time = env.now
    print('%s spent %.2f to get their shot.' % (name, fin_time-init_time))
    TIME_LIST.append(fin_time-init_time)


def setup(env, num_nurses, vaccine_time, paper_time, check_time, wait_time, appointment_inter):
    """Create a vaccine center, a number of initial people and keep creating people
    approx. every ``appointment_inter`` minutes."""
    # Create the vaccine center
    center = vaccineCenter(env, num_nurses, vaccine_time, paper_time, check_time, wait_time)

    # Create initial patients
    for i in range(INIT_NUM_PEOPLE):
        env.process(person(env, 'Person %d' % i, center))

    # Create more patients while the simulation is running
    while True:
        yield env.timeout(random.randint(appointment_inter - 2, appointment_inter + 2))
        i += 1
        env.process(person(env, 'Person %d' % i, center))


env = simpy.Environment()
env.process(setup(env, NUM_NURSES, VACCINE_TIME, PAPER_TIME, CHECK_TIME, WAIT_TIME, APPT_INTER))

env.run(until=SIM_TIME)
print('It took an average of %.2f for each person to get their shot.' % np.mean(TIME_LIST))
