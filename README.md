# Vaccine Facility Simulation using SimPy

### **Modules used:** simpy, random, numpy, and matplotlib

### simpy can be installed via pip with: **pip install simpy**

This is a discrete event based simulation of a Vaccine Facility using SimPy. This Vaccine Facility produces COVID and Flu vaccines for a fixed population that can be set by the user. This facility is fixed as well, meaning the number of machines and human resources (workers) are non-adaptive. The Flu vaccine is the sole vaccine in production at the beginning of simulation time. Then, a COVID vaccine begins mass production at the facility due to the demand of needing to vaccinate the population. The demand for the vaccine is 90% of the population as no one has been vaccinated yet (anti-vaxxers are remaining 10%). The COVID vaccines will be rolled out in four phases for health workers, at risk, adults, and finally not at risk. As supply increases, the people that get vaccinated are no longer a part of the demand. As demand decreases, the facility will move to produce both COVID and Flu vaccines. 

Running the ***main.py*** program will run the Vaccine Facility Simulation. Parameters may be changed as indicated in the code to simulate different resource amounts and process times, as well as demand levels. 
- **Lines 20-24:** Change parameters for the work time, this will calculate the total simulation time (SIM_TIME).
- **Lines 28-31:** Change the number of general workers, as well as machines used in the processes and packaging.
- **Lines 36-45:** Change initial amounts, storage capacity and cost for each ingredient.
- **Lines 49-59:** Change store capacities for the vaccine ingredients post proccesses.
- **Lines 63-83:** Change the amount of each ingredient that is used in each of the processes.
- **Lines 86-98:** Change the time (in hours) for each of the processes as well as changing the capacity for dispatch that COVID and Flu share.
- **Lines 101-111:** Change the critical stock for each ingredient, this is the amount used for stock control.
- **Lines 114-119:** Change the order interval, amount and initial order for the COVID and Flu vaccines.
- **Lines 122-129:** Change the population size and distribution (antivaxxers, health workers, at risk, and adults)

Outputs of the code are prints of the ingredient amounts (remaining and processed), the vaccine amounts (processed, packaged, and distributed), stock control for when ingredients are below a certain level, dispatch control to call the distributor, the total cost of producing these vaccines, and finally the average time to produce both the COVID and Flu vaccines. Five plots are also created, these will be listed below.
- Vaccinated and Unvaccinated Population vs Time
- Dispatch Level vs Time (for COVID and Flu)
- Ingredient 1 Level vs Time (COVID Ingredient)
- Ingredient 5 Level vs Time (Flu Ingredient)
- Vaccine Production vs Time (COVID and Flu)
