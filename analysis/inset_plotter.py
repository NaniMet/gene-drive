import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def plot(df):

    not_data_cols = ['time', 'Run_Number', 'expt_name']
    data_cols = [x for x in df.columns.values if x not in not_data_cols]

    fig = plt.figure()
    for c, channel in enumerate(data_cols):
        ax = fig.add_subplot(2,3,c+1)
        sdf = df.groupby(['expt_name', 'time'])[channel].aggregate(np.mean).reset_index()
        for (expt, edf) in sdf.groupby('expt_name') :
            ax.plot(edf['time'], edf[channel], label=expt)

        ax.set_title(channel)
    ax.legend() # Jaline's version
    # plt.legend(bbox_to_anchor=(0,1.02,1,1.02)) #Jon's version
    ### plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1)) #Caitlin's version
    plt.show()

def load_data(sweep_name):

    datafiles = [x for x in os.listdir(sweep_name) if 'alldata' not in x]
    alldata = pd.concat([pd.read_csv(os.path.join(sweep_name, fname)) for fname in datafiles])
    return alldata

if __name__ == '__main__':

    sweep_name = 'Plot'
    df = load_data(sweep_name)
    plot(df)