import numpy as np
from random import random, randint, uniform

from household import Household


class Model:
    def __init__(self, height, width, adaptive, init_households, move_rate,
                 harvest_rate, farm_rate, clearing_rate, move_cost_rate,
                 fertility_loss_rate, restore_rate, fission_energy,
                 swidden_radius, bad_years, innovation_rate, max_fallow,
                 transfer_ownership):
        self.height = height
        self.width = width

        self.adaptive = adaptive
        self.transfer_ownership = transfer_ownership

        self.init_households = init_households
        self.init_energy = 100
        self.max_veg = 50
        self.cum_bad_years = 0
        self.divisor = 1

        self.move_rate = move_rate / 100
        self.harvest_rate = harvest_rate / 100
        self.farm_rate = farm_rate / 100
        self.clearing_rate = clearing_rate / 100
        self.move_cost_rate = move_cost_rate / 100
        self.fertility_loss_rate = fertility_loss_rate / 100
        self.restore_rate = restore_rate / 100

        self.fission_energy = fission_energy / 100
        self.swidden_radius = swidden_radius

        self.grid = {}
        self.agents = {}
        self.current_id = 0

        self.bad_years = bad_years
        self.innovation_rate = innovation_rate
        self.max_fallow = max_fallow

        self.setup_patches()
        self.setup_households()
        self.ticks = 0

    def setup_patches(self):
        self.grid['vegetation'] = np.full((self.height, self.width), 50)
        self.grid['color'] = np.full((self.height, self.width), 1)
        self.grid['field'] = np.full((self.height, self.width), 0)
        self.grid['fertility'] = np.full((self.height, self.width), 1.0)
        self.grid['owner'] = np.full((self.height, self.width), -1)
        self.grid['fallow'] = np.full((self.height, self.width), 0)
        self.grid['state'] = np.full((self.height, self.width), 'unused',
                                     dtype='<U10')
        self.grid['site'] = np.full((self.height, self.width), False)
        self.grid['veg_clear_cost'] = np.full((self.height, self.width),
                                              (self.init_energy *
                                               self.clearing_rate))
        self.grid['agents'] = np.empty((self.height, self.width),
                                       dtype=np.object)
        filler = np.frompyfunc(lambda x: list(), 1, 1)
        filler(self.grid['agents'], self.grid['agents'])

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
        for y in range(self.height):
            for x in range(self.width):

                if self.grid['fertility'][y, x] < 1:
                    self.grid['fertility'][y, x] += self.restore_rate
                else:
                    self.grid['fertility'][y, x] = 1

                if (not self.grid['agents'][y, x] and
                    not self.grid['field'][y, x] and
                    not self.grid['site'][y, x] and
                        self.grid['vegetation'][y, x] < 50):
                    self.grid['vegetation'][y, x] += 1
                    if self.grid['vegetation'][y, x] < 50:
                        self.grid['color'][y, x] = 7
                    else:
                        self.grid['color'][y, x] = 1

                if (self.grid['owner'][y, x] != -1 and
                        not self.grid['field'][y, x]):
                    self.grid['fallow'][y, x] += 1

                self.grid['field'][y, x] = 0

                if (self.transfer_ownership and
                    self.grid['fallow'][y, x] > self.max_fallow and
                    not self.grid['agents'][y, x] and
                        not self.grid['site'][y, x]):
                    self.grid['owner'][y, x] = -1

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
