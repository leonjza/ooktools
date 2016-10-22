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

import sys

import click
import numpy
import rflib


def valid_packet(packet, constraint):
    """
        Check if a hex encoded packet received from
        rflib.Rfcat.RFrecv has the constraint value in it.

        Idea From:
            https://github.com/mossmann/stealthlock/blob/master/sl.py#L17

        :param packet:
        :param constraint:
        :return:
    """

    if constraint not in packet:
        return False

    return True


def oneline_print(string):
    """
        Print a string with a carriage return

        :param string:
        :return:
    """

    sys.stdout.write('{}\r'.format(string))
    sys.stdout.flush()


def chunks(data, l):
    """
        Yield l-sized chunks from data.

        :param data:
        :param l:
        :return:
    """

    for i in range(0, len(data), l):
        yield data[i:i + l]


def pwm_encode(data, prefix=None, suffix=None):
    """
        Encode a binary string with PWM:
            https://en.wikipedia.org/wiki/Pulse-width_modulation

        :param data:
        :param prefix:
        :param suffix:
        :return:str
    """

    # For performance reasons (https://www.python.org/doc/essays/list2str/),
    # lets append the bits to a list and join them later.

    # Start the bits array by adding the prefix if its defined
    pwm_bits = [prefix] if prefix is not None else []

    # Next, flip the 1's and 0's to their PWM versions
    for bit in data:
        pwm_bits.append('100' if bit == '1' else '110')

    # Finally, add the suffix if its defined
    if suffix is not None:
        pwm_bits.append(suffix)

    # Return a string from the list of bits
    return ''.join(pwm_bits)


def cleanup_wave_data(data):
    """

        :param data:
        :return:
    """

    # Determine the min, max and average values.
    minval, maxval, valcount = numpy.amin(data), numpy.amax(data), len(data)
    meanval = numpy.mean([minval, maxval])
    click.secho('Total Samples: {}, Min: {}, Max: {}, Mean: {}'.format(
        valcount, minval, maxval, meanval), fg='green')

    # Give some information about what is going to happen now.
    click.secho('Cleaning up {} data points...'.format(valcount), dim=True)

    # Some constant values that will determine hard values
    # for legit data
    sample_border = 40000  # Calculate averages every x samples
    significant_max = minval + 3000  # Must have at least one data point with more than this
    clean_data = []

    # Ensure the source data is OK to work with by checking that we have
    # data points with at least a certain max and not less than a certain min
    if maxval < significant_max:
        click.secho('Data source has values that are not more than {}. These '
                    'values may skew average calculations. Please try and re-record '
                    'your data source.'.format(significant_max), fg='red')
        return clean_data

    for samples in chunks(data, sample_border):

        # Determine new min, max and means for this sample range
        sample_minval, sample_maxval = numpy.amin(samples), numpy.amax(samples)
        sample_mean = numpy.mean([sample_minval, sample_maxval])

        # Debug
        # print(sample_minval, sample_maxval, sample_mean)

        # Ensure we have data in this sample range that is workable
        if significant_max > sample_maxval:
            # click.secho('Dont have data in minimum range.', fg='yellow')
            continue

        for value in samples:

            # print (value, sample_mean)
            if (value > 500) and (value > sample_mean):
                clean_data.append(1)
                continue

            clean_data.append(0)
            # Apply the clean_values function to the sample range
            # average_func = numpy.vectorize(clean_values)
            # clean_data.append(average_func(samples, numpy.mean([sample_minval, sample_maxval])))

    # return list(itertools.chain(*clean_data))
    return clean_data


def configure_dongle(d, frequency, pktflen, baud, modulation=rflib.MOD_ASK_OOK,
                     syncmode=0, lowball=False, maxpower=False):
    """
        Configure an instance of rflib.RFCat

        :param d:
        :param frequency:
        :param pktflen:
        :param baud:
        :param modulation:
        :param syncmode:
        :param lowball:
        :param maxpower:
        :return:
    """

    # Set the radio frequency
    if frequency is not None:
        d.setFreq(frequency)
        click.secho('[radio] Frequency:     {}'.format(frequency), dim=True)

    # Set the rest of the values
    d.setMdmModulation(modulation)
    d.makePktFLEN(pktflen)
    d.setMdmDRate(baud)
    d.setMdmSyncMode(syncmode)  # Disable preamble

    click.secho('[radio] MdmModulation: {}'.format(modulation), dim=True)
    click.secho('[radio] PktFLEN:       {}'.format(pktflen), dim=True)
    click.secho('[radio] MdmDRate:      {}'.format(baud), dim=True)
    click.secho('[radio] MdmSyncMode:   {}'.format(syncmode), dim=True)

    # set the radio to lowest filtering mode
    if lowball:
        d.lowball()
        click.secho('[radio] Lowball:       {}'.format(lowball), dim=True, bold=True)

    # set the radio to its loudest
    if maxpower:
        d.setMaxPower()
        click.secho('[radio] MaxPower:      {}'.format(maxpower), dim=True, bold=True)

    return
