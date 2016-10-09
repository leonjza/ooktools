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

import struct
import wave

import click
import numpy

from ..utilities import cleanup_wave_data


def clean_pwm_wave(source, destination):
    """
        Clean up a source wave file with PWM encoded data.

        The basic idea here is to read the source data and calculate
        the average height of the samples. Using this height, we iterate
        over all of the samples and replace the actual value with
        a 1 or a 0.

        Finally, in order to improve the graphing ability, we amplify
        the 1's value by 10000 and write the results out to
        a new wave file with the same attributes as the source.

        :param destination:
        :param source:
        :return:
    """

    # Read the frames into a numpy array
    signal = numpy.fromstring(source.readframes(-1), dtype=numpy.int16)
    signal = cleanup_wave_data(signal)

    # Prepare the output wave file. We will use exactly
    # the same parameters as the source
    output_wave = wave.open(destination, 'w')
    output_wave.setparams(source.getparams())

    click.secho('Normalizing values..')

    frames = []

    for _, value in numpy.ndenumerate(signal):

        # If the value is one, amplify it so that it is
        # *obviously* not 0. This makes graphing easier too.
        if value == 1:
            value *= 10000

        frames.append(struct.pack('h', value))

    click.secho('Writing output to file: {}'.format(destination))
    output_wave.writeframes(''.join(frames))

    return
