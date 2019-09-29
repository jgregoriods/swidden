import numpy as np
from random import random, randint, uniform

from household import Household


class Model:
    def __init__(self, height, width, adaptive, init_households, move_rate,
                 harvest_rate, farm_rate, clearing_rate, fertility_loss_rate,
                 restore_rate, fission_energy, swidden_radius, bad_years):
        self.height = height
        self.width = width

        self.adaptive = adaptive

        self.init_households = init_households
        self.init_energy = 100
        self.max_veg = 50
        self.cum_bad_years = 0
        self.divisor = 1

        self.move_rate = move_rate / 100
        self.harvest_rate = harvest_rate / 100
        self.farm_rate = farm_rate / 100
        self.clearing_rate = clearing_rate / 100
        self.fertility_loss_rate = fertility_loss_rate / 100
        self.restore_rate = restore_rate / 100

        self.fission_energy = fission_energy
        self.swidden_radius = swidden_radius

        self.grid = {}
        self.agents = {}
        self.current_id = 0

        self.bad_years = bad_years

        self.setup_patches()
        self.setup_households()
        self.ticks = 0

    def setup_patches(self):
        self.grid['vegetation'] = np.full((self.height, self.width), 50)
        self.grid['color'] = np.full((self.height, self.width), 'green',
                                     dtype='<U10')
        self.grid['field'] = np.full((self.height, self.width), 0)
        self.grid['fertility'] = np.full((self.height, self.width), 1.0)
        self.grid['owner'] = np.full((self.height, self.width), 0)
        self.grid['fallow'] = np.full((self.height, self.width), 0)
        self.grid['state'] = np.full((self.height, self.width), 'unused',
                                     dtype='<U10')
        self.grid['site'] = np.full((self.height, self.width), False)
        self.grid['farmstead'] = np.full((self.height, self.width), 0)
        self.grid['veg_clear_cost'] = np.full((self.height, self.width),
                                              (self.init_energy *
                                               self.clearing_rate))

    def random_coords(self):
        return (randint(0, self.width - 1), randint(0, self.height - 1))

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def setup_households(self):
        if self.adaptive:
            for i in range(self.init_households):
                new_household = Household(model=self,
                                          coords=self.random_coords(),
                                          energy=self.init_energy,
                                          move_threshold=random(),
                                          move_dist=randint(1, 5),
                                          farm_dist=randint(1, 20),
                                          fission_rate=uniform(1, 2),
                                          min_fertility=random())
                new_household.claim_land()
        else:
            for i in range(self.init_households):
                new_household = Household(model=self,
                                          coords=self.random_coords(),
                                          energy=self.init_energy,
                                          move_threshold=(self.init_energy *
                                                          self.move_rate),
                                          move_dist=randint(1, 5),
                                          farm_dist=self.swidden_radius,
                                          fission_rate=self.fission_energy,
                                          min_fertility=0.8)
                new_household.claim_land()

    def regrow_patch(self):
        pass

    def step(self):
        if self.bad_years != 0 and randint(1, 100) <= self.bad_years:
            self.divisor = 2
            self.cum_bad_years += 1
        else:
            self.divisor = 1

        agent_list = list(self.agents.keys())
        for unique_id in agent_list:
            self.agents[unique_id].step()

        self.regrow_patch()

        self.ticks += 1
