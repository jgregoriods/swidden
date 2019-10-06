from math import hypot
from random import random, randint, choice


class Household:
    def __init__(self, model, coords, energy, move_threshold, move_dist,
                 farm_dist, fission_rate, min_fertility):
        self.model = model
        self.coords = coords
        self.unique_id = self.model.next_id()
        self.energy = energy
        self.move_threshold = move_threshold
        self.move_dist = move_dist
        self.farm_dist = farm_dist
        self.fission_rate = fission_rate
        self.min_fertility = min_fertility

        self.model.agents[self.unique_id] = self

        x, y = self.coords
        self.model.grid['agents'][y, x].append(self.unique_id)

        self.owned_land = []

    def move_to(self, new_coords):
        xi, yi = self.coords
        xj, yj = new_coords
        self.model.grid['agents'][yi, xi].remove(self.unique_id)

        self.coords = (xj, yj)
        self.model.grid['agents'][yj, xj].append(self.unique_id)

    def claim_land(self):
        x, y = self.coords

        # Establish new farmstead
        self.model.grid['color'][y, x] = 2
        self.model.grid['state'][y, x] = 'active'
        self.model.grid['fertility'][y, x] = 0
        self.model.grid['owner'][y, x] = self.unique_id
        self.owned_land.append((x, y))

        # Claim ownership of unowned land around farmstead
        for (x, y) in self.get_neighborhood(self.farm_dist):
            if self.model.grid['owner'][y, x] == -1:
                self.model.grid['color'][y, x] = 3
                self.model.grid['owner'][y, x] = self.unique_id
                self.model.grid['state'][y, x] = 'active'
                self.model.grid['fallow'][y, x] = 0
                self.owned_land.append((x, y))

    def get_neighborhood(self, radius):
        neighborhood = []
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                x = self.coords[0] + dx
                y = self.coords[1] + dy
                if (0 <= x < self.model.width and
                    0 <= y < self.model.height and
                        self.get_distance((x, y)) <= radius):
                    neighborhood.append((x, y))
        return neighborhood

    def get_distance(self, next_coords):
        xi, yi = self.coords
        xj, yj = next_coords
        return hypot((xj - xi), (yj - yi))

    def check_move(self):
        if self.energy < self.move_threshold:
            self.move()
        elif (self.move_threshold < (self.model.init_energy *
                                     self.model.move_rate) and
                self.energy > self.move_threshold):
            self.move_threshold += 1

    def agents_here(self):
        x, y = self.coords
        return len(self.model.grid['agents'][y, x])

    def move(self):
        if not self.model.adaptive:
            self.move_dist = randint(1, 5)
        neighborhood = self.get_neighborhood((self.farm_dist *
                                              self.move_dist) + 1)
        potential_farms = [(x, y) for (x, y) in neighborhood
                           if (self.model.grid['fertility'][y, x] >
                               self.min_fertility and
                               not self.model.grid['agents'][y, x] and
                               self.model.grid['owner'][y, x] == -1)]

        if potential_farms:
            old_farm = self.coords
            new_farm = choice(potential_farms)

            x, y = self.coords

            if len(self.model.grid['agents'][y, x]) == 1:
                self.model.grid['state'][y, x] = 'abandoned'
                self.model.grid['color'][y, x] = 4
                self.model.grid['site'][y, x] = True

            self.relinquish_land()
            self.move_to(new_farm)
            self.claim_land()

            self.energy -= ((self.model.init_energy *
                             self.model.move_cost_rate) -
                            (self.get_distance(old_farm) / 5))
            if self.energy <= self.move_threshold:
                self.move_threshold -= ((self.model.init_energy *
                                         self.model.move_cost_rate) + 1)

    def relinquish_land(self):
        for (x, y) in self.owned_land:
            self.model.grid['owner'][y, x] = -1
            self.model.grid['fallow'][y, x] = 0
            self.model.grid['color'][y, x] = 1
            self.model.grid['state'][y, x] = 'unused'

        self.owned_land = []

    def choose_land(self):
        potential_farms = {}
        for (x, y) in self.get_neighborhood(self.farm_dist):
            if (self.model.grid['fertility'][y, x] > 0 and
                    (self.model.grid['owner'][y, x] == -1 or
                     self.model.grid['owner'][y, x] == self.unique_id)):
                attractiveness = ((self.model.grid['fertility'][y, x] *
                                   self.model.harvest_rate *
                                   self.model.init_energy) -
                                  (self.model.farm_rate *
                                   self.model.init_energy) -
                                  self.model.grid['veg_clear_cost'][y, x] -
                                  (self.get_distance((x, y)) / 5))
                potential_farms[(x, y)] = attractiveness

        if potential_farms:
            # new_farm = max(potential_farms, key=potential_farms.get)
            new_farm = choice(list(potential_farms))
            x, y = new_farm
            self.model.grid['owner'][y, x] = self.unique_id
            self.farm(new_farm)
        else:
            self.energy -= (0.1 * self.model.init_energy)

    def farm(self, land):
        x, y = land
        if self.model.grid['vegetation'][y, x] > 0:
            self.model.grid['vegetation'][y, x] = 0
        self.model.grid['fallow'][y, x] = 0
        self.model.grid['field'][y, x] = 1
        self.model.grid['color'][y, x] = 5

        fval = self.model.grid['fertility'][y, x]

        if self.model.grid['fertility'][y, x] > 0:
            self.model.grid['fertility'][y, x] -= (
                self.model.fertility_loss_rate
            )
        elif self.model.grid['fertility'][y, x] < 0:
            self.model.grid['fertility'][y, x] = 0
        net_return = (((self.model.harvest_rate * self.model.init_energy) *
                       fval / self.model.divisor) -
                      (self.model.farm_rate * self.model.init_energy) -
                      self.model.grid['veg_clear_cost'][y, x] -
                      (self.get_distance(land) / 5))
        self.energy += net_return

    def reproduce(self):
        if (self.energy > (self.model.init_energy *
                           self.fission_rate) and
                self.energy / 2 > self.move_threshold):
            self.energy /= 2

            if self.energy <= self.move_threshold:
                self.move_threshold = (self.energy - (0.1 * self.energy))

            new_household = Household(model=self.model,
                                      coords=self.coords,
                                      energy=self.energy,
                                      move_threshold=self.move_threshold,
                                      move_dist=self.move_dist,
                                      farm_dist=self.farm_dist,
                                      fission_rate=self.fission_rate,
                                      min_fertility=self.min_fertility)

            if (self.model.adaptive and
                    randint(1, 1000) <= self.model.innovation_rate):
                new_household.innovate()

            new_household.move()

    def innovate(self):
        innovation = randint(1, 5)
        if innovation == 1:
            self.move_dist = randint(0, 4)
        elif innovation == 2:
            self.move_rate = random()
        elif innovation == 3:
            self.fission_rate = random()
        elif innovation == 4:
            self.farm_dist = randint(1, 20)
        elif innovation == 5:
            self.min_fertility = random()

    def check_death(self):
        if self.energy <= 0:
            x, y = self.coords
            self.model.grid['agents'][y, x].remove(self.unique_id)
            if not self.model.grid['agents'][y, x]:
                self.model.grid['color'][y, x] = 6
                self.model.grid['site'][y, x] = True
                self.model.grid['state'][y, x] = 'died'
            self.relinquish_land()
            self.die()

    def die(self):
        del self.model.agents[self.unique_id]
        del self

    def step(self):
        self.check_move()
        self.choose_land()
        self.reproduce()
        self.check_death()
