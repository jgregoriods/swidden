import matplotlib.pyplot as plt
import matplotlib.figure as mplfig
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.colors import from_levels_and_colors
import tkinter as tk

from model import Model


class App:
    def __init__(self, master):
        self.master = master
        master.title('Swidden Farming')

        # Model visualization
        self.figure = mplfig.Figure(figsize=(6, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = tkagg.FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().grid(row=1, column=3, columnspan=6,
                                         rowspan=12)

        self.cmap, self.norm = from_levels_and_colors([1, 2, 3, 4, 5, 6, 7, 8, 9],
                                                      ['forestgreen',
                                                       'crimson',
                                                       'mediumseagreen',
                                                       'tab:pink',
                                                       'tab:brown',
                                                       'mediumpurple',
                                                       'palegreen',
                                                       'white'])

        # Controls
        self.setup_button = tk.Button(master, text='Setup',
                                      command=self.setup_model)
        self.setup_button.grid(row=1, column=1)

        self.run_button = tk.Button(master, text='Run',
                                    command=self.run_model)
        self.run_button.grid(row=1, column=2)

        self.pause_button = tk.Button(master, text='Pause',
                                      command=self.pause_model)
        self.pause_button.grid(row=1, column=3)

        self.step_button = tk.Button(master, text='Step',
                                     command=self.step_model)
        self.step_button.grid(row=1, column=4)

        # Parameters
        self.init_households_slider = tk.Scale(master, from_=1, to=50,
                                               orient=tk.HORIZONTAL,
                                               label='Initial households')
        self.init_households_slider.grid(row=2, column=1)

        self.fission_energy_slider = tk.Scale(master, from_=100, to=200,
                                              orient=tk.HORIZONTAL,
                                              label='Fission energy')
        self.fission_energy_slider.set(150)
        self.fission_energy_slider.grid(row=3, column=1)

        self.swidden_radius_slider = tk.Scale(master, from_=1, to=20,
                                              orient=tk.HORIZONTAL,
                                              label='Swidden radius')
        self.swidden_radius_slider.set(12)
        self.swidden_radius_slider.grid(row=4, column=1)

        self.harvest_rate_slider = tk.Scale(master, from_=1, to=100,
                                            orient=tk.HORIZONTAL,
                                            label='Harvest rate')
        self.harvest_rate_slider.set(12)
        self.harvest_rate_slider.grid(row=5, column=1)

        self.farm_rate_slider = tk.Scale(master, from_=1, to=100,
                                         orient=tk.HORIZONTAL,
                                         label='Farm cost')
        self.farm_rate_slider.set(3)
        self.farm_rate_slider.grid(row=6, column=1)

        self.clearing_rate_slider = tk.Scale(master, from_=1, to=100,
                                             orient=tk.HORIZONTAL,
                                             label='Clearing cost')
        self.clearing_rate_slider.set(3)
        self.clearing_rate_slider.grid(row=7, column=1)

        self.max_fallow_slider = tk.Scale(master, from_=1, to=40,
                                          orient=tk.HORIZONTAL,
                                          label='Max fallow')
        self.max_fallow_slider.set(20)
        self.max_fallow_slider.grid(row=8, column=1)

        self.move_rate_slider = tk.Scale(master, from_=1, to=100,
                                         orient=tk.HORIZONTAL,
                                         label='Move threshhold')
        self.move_rate_slider.set(50)
        self.move_rate_slider.grid(row=2, column=2)

        self.move_cost_rate_slider = tk.Scale(master, from_=1, to=100,
                                              orient=tk.HORIZONTAL,
                                              label='Move cost')
        self.move_cost_rate_slider.set(2)
        self.move_cost_rate_slider.grid(row=3, column=2)

        self.fert_loss_slider = tk.Scale(master, from_=1, to=100,
                                         orient=tk.HORIZONTAL,
                                         label='Fertility loss')
        self.fert_loss_slider.set(20)
        self.fert_loss_slider.grid(row=4, column=2)

        self.restore_rate_slider = tk.Scale(master, from_=1, to=100,
                                            orient=tk.HORIZONTAL,
                                            label='Restore rate')
        self.restore_rate_slider.set(2)
        self.restore_rate_slider.grid(row=5, column=2)

        self.bad_years_slider = tk.Scale(master, from_=1, to=100,
                                         orient=tk.HORIZONTAL,
                                         label='Bad years')
        self.bad_years_slider.set(20)
        self.bad_years_slider.grid(row=6, column=2)

        self.innovation_rate_slider = tk.Scale(master, from_=0, to=500,
                                               orient=tk.HORIZONTAL,
                                               label='Innovation rate')
        self.innovation_rate_slider.set(500)
        self.innovation_rate_slider.grid(row=7, column=2)

        self.adaptive = tk.BooleanVar()
        self.adaptive_check = tk.Checkbutton(master, text='Adaptive',
                                             variable=self.adaptive)
        self.adaptive_check.grid(row=8, column=2)

        self.transfer = tk.BooleanVar()
        self.transfer_check = tk.Checkbutton(master, text='Transfer ownership',
                                             variable=self.transfer)
        self.transfer_check.grid(row=9, column=2)

        self.running = False

    def setup_model(self):
        self.model = Model(height=100, width=100,
                           adaptive=self.adaptive.get(),
                           init_households=self.init_households_slider.get(),
                           fission_energy=self.fission_energy_slider.get(),
                           swidden_radius=self.swidden_radius_slider.get(),
                           harvest_rate=self.harvest_rate_slider.get(),
                           farm_rate=self.farm_rate_slider.get(),
                           clearing_rate=self.clearing_rate_slider.get(),
                           move_rate=self.move_rate_slider.get(),
                           move_cost_rate=self.move_cost_rate_slider.get(),
                           fertility_loss_rate=self.fert_loss_slider.get(),
                           restore_rate=self.restore_rate_slider.get() / 100,
                           bad_years=self.bad_years_slider.get(),
                           innovation_rate=self.innovation_rate_slider.get(),
                           transfer_ownership=self.transfer.get(),
                           max_fallow=self.max_fallow_slider.get())
        self.plot_model()
        self.running = True

    def run_model(self):
        if self.running:
            self.model.step()
            self.plot_model()
            self.master.after(1, self.run_model)

    def pause_model(self):
        if self.running:
            self.running = False

    def step_model(self):
        self.model.step()
        self.plot_model()

    def plot_model(self):
        self.ax.cla()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.imshow(self.model.grid['color'], cmap=self.cmap,
                       norm=self.norm)
        pts = [self.model.agents[unique_id].coords for
               unique_id in self.model.agents]
        sizes = [self.model.agents[unique_id].agents_here()**2 * 20 for
                 unique_id in self.model.agents]
        self.ax.scatter(*zip(*pts), s=sizes, marker="p", color="black")
        self.canvas.draw()


root = tk.Tk()
app = App(root)
root.mainloop()
