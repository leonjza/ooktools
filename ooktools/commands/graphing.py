# The MIT License (MIT)
#
# Copyright (c) 2016 Leon Jacobs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime

import click
import numpy
import peakutils

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    plotting = True

except RuntimeError:
    plotting = False


def _can_plot():
    if not plotting:
        click.secho('Plotting library was not sucesfully imported.\n'
                    'Ensure your python installation can run `import '
                    'matplotlib.pyplot` without errors.', fg='red')

        return False

    return True


def generate_wave_graph(source, peaks):
    """
        Generate a plot from a wave file source.
        Optionally, include peak calculations.

        Source:
            https://github.com/MonsieurV/py-findpeaks/blob/master/tests/vector.py

        :param source:
        :param peaks:
        :return:
    """

    if not _can_plot():
        return

    click.secho('Reading {} frames from source.'.format(source.getnframes()), fg='green')
    click.secho('Preparing plot.', fg='green', dim=True)

    # Read the source data
    signal = source.readframes(-1)
    signal = numpy.fromstring(signal, dtype=numpy.int16)

    _, ax = plt.subplots(1, 1, figsize=(8, 4))
    ax.plot(signal, 'b', lw=1)

    # If we have to include peak information, calculate that
    if peaks:
        click.secho('Calculating peak information too.', dim=True)
        indexes = peakutils.indexes(signal, thres=0.02 / max(signal), min_dist=100)

        if indexes.size:
            label = 'peak'
            label = label + 's' if indexes.size > 1 else label
            ax.plot(indexes, signal[indexes], '+', mfc=None, mec='r', mew=2, ms=8,
                    label='%d %s' % (indexes.size, label))
            ax.legend(loc='best', framealpha=.5, numpoints=1)

    # Continue graphing the source information
    ax.set_xlim(-.02 * signal.size, signal.size * 1.02 - 1)
    ymin, ymax = signal[numpy.isfinite(signal)].min(), signal[numpy.isfinite(signal)].max()
    yrange = ymax - ymin if ymax > ymin else 1
    ax.set_ylim(ymin - 0.1 * yrange, ymax + 0.1 * yrange)
    ax.set_xlabel('Frame #', fontsize=14)
    ax.set_ylabel('Amplitude', fontsize=14)

    # Finally, generate the graph
    plt.show()

    return


def generage_saved_recording_graphs(source, count, series):
    """
        Plot frames from a recording

        :param source:
        :param count:
        :param series:
        :return:
    """

    if not _can_plot():
        return

    click.secho('Source Information:')
    click.secho('Recording Date:        {}'.format(datetime.fromtimestamp(source['date'])), bold=True, fg='green')
    click.secho('Recording Frequency:   {}'.format(source['frequency']), bold=True, fg='green')
    click.secho('Recording Baud:        {}'.format(source['baud']), bold=True, fg='green')
    click.secho('Recording Framecount:  {}'.format(source['framecount']), bold=True, fg='green')

    # If we dont have a series to plot, plot the number of frames
    # from the start to count
    if not series:
        data = source['frames'][:count]
        click.secho('Preparing Graph for {} plots...'.format(count))
    else:
        start, end = series
        data = source['frames'][start:end]
        click.secho('Preparing Graph for {} plots from {} to {}...'.format(len(data), start, end))

    # Place holder to check if we have set the first plot yet
    fp = False

    # Start the plot.
    fig = plt.figure(1)
    fig.canvas.set_window_title('Frame Data Comparisons')

    # Loop over the frames, plotting them
    for (index,), frame in numpy.ndenumerate(data):

        # If it is not the first plot, set it keep note of the
        # axo variable. This is the original plot.
        if not fp:

            axo = plt.subplot(len(data), 1, index + 1)
            axo.grid(True)
            axo.set_xlabel('Symbols')
            axo.set_ylabel('Aplitude')
            axo.xaxis.set_label_position('top')

            # Flip the first plot variable as this is done
            fp = True

        # If we have plotted before, set the new subplot and share
        # the X & Y axis with axo
        else:
            ax = plt.subplot(len(data), 1, index + 1, sharex=axo, sharey=axo)
            ax.grid(True)

        # Plot the data
        plt.plot(numpy.frombuffer(buffer=str(frame), dtype=numpy.int16))

    # Show the plot!
    click.secho('Launching the graphs!')
    plt.show()
