from math import hypot


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

    def move_to(self, coords):
        self.coords = coords

    def claim_land(self):
        x, y = self.coords

        self.model.grid['color'][y, x] = 'red'
        self.model.grid['farmstead'][y, x] += 1
        self.model.grid['state'][y, x] = 'active'
        self.model.grid['fertility'][y, x] = 0

        for (x, y) in self.get_neighborhood(self.farm_dist):
            if self.model.grid['owner'][y, x] == 0:
                self.model.grid['owner'][y, x] = self.unique_id
                self.model.grid['state'][y, x] = 'active'
                self.model.grid['fallow'][y, x] = 0

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
        return round(hypot((xj - xi), (yj - yi)))

    def check_move(self):
        pass

    def choose_land(self):
        pass

    def reproduce(self):
        pass

    def check_death(self):
        pass

    def step(self):
        self.check_move()
        self.choose_land()
        self.reproduce()
        self.check_death()
