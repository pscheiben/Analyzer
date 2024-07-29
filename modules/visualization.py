import matplotlib.pyplot as plt

def plot_histogram(hist):
    fig, ax = plt.subplots()
    hist.plot(ax=ax)
    return fig

def plot_fft(freq, fft_values):
    fig, ax = plt.subplots()
    ax.plot(freq, np.abs(fft_values))
    return fig

def plot_power_spectrum(freq, power_spectrum):
    fig, ax = plt.subplots()
    ax.plot(freq, power_spectrum)
    return fig

def plot_psd(freq, psd):
    fig, ax = plt.subplots()
    ax.plot(freq, psd)
    return fig
