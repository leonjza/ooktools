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

from __future__ import absolute_import

import click

from .commands import converstions
from .commands import graphing
from .commands import grc
from .commands import information
from .commands import signalling
from .validators import validate_binary_string
from .validators import validate_hex_string
from .validators import validate_recording_json
from .validators import validate_series
from .validators import validate_wave


# Start the Click command group
@click.group()
def cli():
    pass


@cli.group()
def wave():
    """
        Wave File Commands.
    """

    pass


@cli.group()
def gnuradio():
    """
        GNU Radio Commands.
    """

    pass


@cli.group()
def signal():
    """
        Signal Commands.
    """

    pass


@signal.group()
def send():
    """
        Send signals using a RFCat dongle.
    """

    pass


@wave.command()
@click.option('--source', '-S', required=True, help='Wave file to use as input.',
              type=click.Path(exists=True), callback=validate_wave)
def info(source):
    """
        Print information about a wave file.
    """

    information.get_wave_info(source)
    return


@wave.command()
@click.option('--source', '-S', required=True, help='Wave file to use as input.',
              type=click.Path(exists=True), callback=validate_wave)
@click.option('--destination', '-D', required=True, help='Destination, cleaned up wave file.',
              type=click.Path(writable=True, resolve_path=True))
def clean(source, destination):
    """
        Cleanup a PWM source Wave file.
    """

    converstions.clean_pwm_wave(**locals())
    return


@wave.command()
@click.option('--source', '-S', required=True, help='Wave file to use as input.',
              type=click.Path(exists=True), callback=validate_wave)
@click.option('--peaks', '-p', is_flag=True, default=False, help='Include peaks in graph.')
def graph(source, peaks):
    """
        Plot wave file values.
    """

    graphing.generate_wave_graph(**locals())
    return


@wave.command()
@click.option('--source', '-S', required=True, help='Wave file to use as input.',
              type=click.Path(exists=True), callback=validate_wave)
def binary(source):
    """
        Search for a binary sequence.
    """

    information.get_wave_binary(**locals())
    return


@signal.command()
@click.option('--start-frequency', '-S', default=430000000, show_default=True,
              help='Start listening for packets on a specific frequency.')
@click.option('--end-frequency', '-E', default=440000000, show_default=True,
              help='Start listening for packets on a specific frequency.')
@click.option('--baud', '-b', default=38400, show_default=True,
              help='Baud rate to receive at.')
@click.option('--increment', '-i', default=50000, show_default=True,
              help='Increment when searching frequencies.')
@click.option('--framecount', '-f', default=5, show_default=True,
              help='Number of frames to receive per frequency.')
def search(start_frequency, end_frequency, baud, increment, framecount):
    """
        Search for signals.
    """

    signalling.search(**locals())
    return


@signal.command()
@click.option('--frequency', '-F', default=433920000, show_default=True,
              help='Frequency to record.')
@click.option('--baud', '-b', default=38400, show_default=True,
              help='Baud rate to receive at.')
@click.option('--framecount', '-f', default=120, show_default=True,
              help='Number of frames to record.')
@click.option('--destination', '-D', required=True, help='Destination filename for the recording.',
              type=click.Path(writable=True, resolve_path=True))
def record(frequency, baud, framecount, destination):
    """
        Record frames to a file.
    """

    signalling.record(**locals())
    return


@signal.command()
@click.option('--source', '-S', required=True, help='Source recording file as input.',
              type=click.Path(exists=True), callback=validate_recording_json)
@click.option('--repeat', '-r', default=10, show_default=True,
              help='Number of times to repeat a frame.')
def play(source, repeat):
    """
        Play frames from a source file.
    """

    signalling.play(**locals())
    return


@signal.command()
@click.option('--source', '-S', required=True, help='Source recording file as input.',
              type=click.Path(exists=True), callback=validate_recording_json)
@click.option('--count', '-c', default=5, show_default=True,
              help='Number of frames to plot. Starts at the first frame.')
@click.option('--series', '-s', default=None, metavar='start:end',
              help='Graph a specific series of fields from a recorded file.',
              callback=validate_series)
def plot(source, count, series):
    """
        Plot frames from a recorded signal.
    """

    graphing.generage_saved_recording_graphs(**locals())
    return


@signal.command()
@click.option('--frequency', '-F', default=433920000, show_default=True,
              help='Frequency to use.')
@click.option('--data', '-D', default='ffffffff', metavar='HEXSTRING',
              help='Data to use in the jam.', callback=validate_hex_string)
@click.option('--baud', '-b', default=4800, show_default=True,
              help='Baud rate to use.')
@click.option('--maxpower', '-m', is_flag=True, default=False,
              help='Set the radio to max output power.')
def jam(frequency, data, baud, maxpower):
    """
        Jam a frequency by just sending noise.
    """

    signalling.jam(**locals())
    return


@signal.command()
@click.option('--frequency', '-F', default=433920000, show_default=True,
              help='Frequency to use.')
@click.option('--baud', '-b', default=4800, show_default=True,
              help='Baud rate to use.')
@click.option('--maxpower', '-m', is_flag=True, default=False,
              help='Set the radio to max output power.')
@click.option('--start', '-S', default='000000000000', help='Start sequence.',
              callback=validate_binary_string, show_default=True)
@click.option('--end', '-E', default='111111111111', help='End sequence.',
              callback=validate_binary_string, show_default=True)
@click.option('--repeat', '-r', default=5, show_default=True,
              help='Number of times to repeat a frame.')
@click.option('--prefix', '-p', default='', help='Signal prefix.',
              callback=validate_binary_string)
@click.option('--suffix', '-s', default='', help='Signal suffix.',
              callback=validate_binary_string)
def brute(frequency, baud, maxpower, start, end, repeat, prefix, suffix):
    """
        Bruteforce a binary range.
    """

    signalling.bruteforce(**locals())
    return


@send.command()
@click.option('--data', '-D', required=True, help='Source bitstring.',
              callback=validate_binary_string)
@click.option('--prefix', '-p', default='', help='Signal prefix.',
              callback=validate_binary_string)
@click.option('--suffix', '-s', default='', help='Signal suffix.',
              callback=validate_binary_string)
@click.option('--frequency', '-F', default=433920000, show_default=True,
              help='Frequency to use.')
@click.option('--baud', '-b', default=4800, show_default=True,
              help='Baud rate to use.')
@click.option('--full', '-f', is_flag=True, default=False, show_default=True,
              help='Is data a full bitstring.')
@click.option('--repeat', '-r', default=25, show_default=True,
              help='# of times to repeat transmission.')
def binary(frequency, prefix, suffix, baud, repeat, data, full):
    """
        Send binary string.
    """

    signalling.send_binary(**locals())
    return


@send.command()
@click.option('--data', '-D', required=True, help='Source bitstring.',
              callback=validate_hex_string)
@click.option('--frequency', '-F', default=433920000, show_default=True,
              help='Frequency to use.')
@click.option('--baud', '-b', default=4800, show_default=True,
              help='Baud rate to use.')
@click.option('--repeat', '-r', default=25, show_default=True,
              help='# of times to repeat transmission.')
def hexstring(frequency, baud, repeat, data):
    """
        Send hex string.
    """

    signalling.send_hex(**locals())
    return


@gnuradio.command()
@click.option('--destination', '-D', default='remote.grc',
              help='Destination filename for the recording.', show_default=True,
              type=click.Path(writable=True, resolve_path=True))
def template(destination):
    """
        Generate a GNU Radio Tempalte file
    """

    grc.generate_template(**locals())
    return


if __name__ == '__main__':
    cli()
