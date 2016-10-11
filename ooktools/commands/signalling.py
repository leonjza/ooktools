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
from __future__ import print_function

import json
import time
from datetime import datetime

import bitstring
import click
import numpy
import rflib
from rflib.chipcon_usb import keystop

from ..utilities import configure_dongle
from ..utilities import oneline_print
from ..utilities import valid_packet


def search(start_frequency, end_frequency, baud, increment, framecount):
    """
        Search for a signal

        :param start_frequency:
        :param end_frequency:
        :param baud:
        :param increment:
        :param framecount:
        :return:
    """

    click.secho('Starting on frequency: {}'.format(start_frequency), fg='green')
    click.secho('Ending on frequency:   {}'.format(end_frequency), fg='red')

    # Setup RFCat
    click.secho('Configuring Radio', fg='yellow')
    d = rflib.RfCat()
    configure_dongle(d, frequency=start_frequency, pktflen=0, baud=baud, lowball=True)

    # The frequency variable is used to track the current
    # frequency that we are scanning.
    frequency = start_frequency

    # The signals variable will hold all of the frequencies
    # and the valid data packets found for that frequency.
    signals = dict()

    click.secho('\nScanning frequency range. Press [ENTER] to stop.',
                fg='green', bold=True)

    # Lables for the values that will update during scanning
    click.secho('Frequency | Framecount | Found', dim=True)

    # While ENTER has not yet been pressed, iterate over
    # the frequencies as calculated for x abount of frame counts.
    # Each time valid data is detected, the data frame is added
    # to a dictionary using the frequency it was detected on as
    # the key.
    while not keystop():

        # Read packets 'framecount' amount of times
        for framecounter in xrange(0, framecount):

            # Status Update. Spacing is to match up with the previously
            # echoed 'lables'.
            oneline_print('{} | {}/{}        | {}'.format(frequency,
                                                          framecounter,
                                                          framecount,
                                                          len(signals)))

            # This try/except is just to catch the UsbTimeout
            # that gets thrown if data has not been received in
            # the time specified in RFrecv.
            try:

                # Get a packet from the RFcat radio
                pkt, _ = d.RFrecv(timeout=1000)
                packet = pkt.encode('hex')

                # If we have a 'valid' packet, append it as a frame
                # to the frequency. A valid packet is defined as one
                # that has 38 0's in its hex representation.
                if valid_packet(packet=packet, constraint='0' * 38):

                    # If this is the first time we are seeing valid
                    # data on this frequency, prepare a data dict
                    # with the first packet added.
                    if frequency not in signals:
                        signals[frequency] = {'data': [(pkt, packet)]}

                    # Otherwise, just append the packet we just got
                    # to the existing dict for this frequency
                    else:
                        signals[frequency]['data'].append((pkt, packet))

            # A timeout in RFrecv will raise an exception.
            except rflib.ChipconUsbTimeoutException:
                pass

        # Set the new frequency incremented by the
        # increment count. If we have passed the end
        # frequency, reset back to the start.
        if frequency > end_frequency:
            frequency = start_frequency
        else:
            frequency += increment

        # Update the radio to the new frequency
        d.setFreq(freq=frequency)

    # Try and be nice to the radio by setting it to Idle.
    click.secho('\nIdling Radio\n', fg='yellow')
    d.setModeIDLE()

    # If we found nothing, just end.
    if not signals:
        click.secho('No signals were found.', fg='red')
        return

    # Sort the output signals.
    # signals.items() translates into a list of tuples with
    # t[0] being the frequency and t[1] the data:
    #   eg:
    #       [(433800000, {'data': ['x', 'x', 'x']})]
    f = sorted(signals.items(), key=lambda t: (len(t[1]['data']), t[0]), reverse=True)

    # Iterate the sorted list, printing how many data packets
    # were found on what frequency.
    click.secho('# of valid packets per frequency', fg='green')
    click.secho('Frequency  |   # packets', bold=True)
    for frequency, data in f:
        click.secho('{}  |   {}'.format(frequency, len(data['data'])))

    return


def record(frequency, baud, framecount, destination):
    """
        Record symbols from an RFCat dongle to a file.

        :param frequency:
        :param baud:
        :param framecount:
        :param destination:
        :return:
    """

    click.secho('Recording on frequency: {} to {}'.format(frequency, destination), fg='green')

    # Setup RFCat
    click.secho('Configuring Radio', fg='yellow')
    d = rflib.RfCat()
    configure_dongle(d, frequency=frequency, pktflen=0, baud=baud, lowball=True)

    # The final payload that will be written
    payload = {
        'date': time.mktime(datetime.now().timetuple()),
        'frequency': frequency,
        'baud': baud,
        'framecount': 0,
        'frames': []
    }

    # A help message to get maximum # of frames written to file.
    click.secho('For maximum frames, press and release the remote multiple times.', fg='green')

    # Capture frames!
    for c in xrange(0, framecount):
        oneline_print('Progress [{}/{}] Frames: {}'.format(c, framecount, len(payload['frames'])))

        # This try/except is just to catch the UsbTimeout
        # that gets thrown if data has not been received in
        # the time specified in RFrecv.
        try:

            # Get a packet from the RFcat radio
            pkt, _ = d.RFrecv(timeout=1000)
            packet = pkt.encode('hex')

            # If we have a 'valid' packet, append it as a frame
            # to the frequency. A valid packet is defined as one
            # that has 38 0's in its hex representation.
            if valid_packet(packet=packet, constraint='0' * 38):
                payload['framecount'] += 1
                payload['frames'].append(packet)

        # A timeout in RFrecv will raise an exception.
        except rflib.ChipconUsbTimeoutException:
            pass

    # Try and be nice to the radio by setting it to Idle.
    click.secho('\nIdling Radio\n', fg='yellow')
    d.setModeIDLE()

    click.secho('Writing saved payload to: {}'.format(destination), bold=True)
    with open(destination, 'wb') as f:
        f.write(json.dumps(payload))

    return


def play(source, repeat):
    """
        Replay frames from a previous recording

        :param source:
        :param repeat:
        :return:
    """

    click.secho('Source Information:')
    click.secho('Recording Date:        {}'.format(datetime.fromtimestamp(source['date'])), bold=True, fg='green')
    click.secho('Recording Frequency:   {}'.format(source['frequency']), bold=True, fg='green')
    click.secho('Recording Baud:        {}'.format(source['baud']), bold=True, fg='green')
    click.secho('Recording Framecount:  {}'.format(source['framecount']), bold=True, fg='green')

    # Setup RFCat
    click.secho('Configuring Radio', fg='yellow')
    d = rflib.RfCat()
    configure_dongle(d, frequency=source['frequency'], pktflen=0, baud=source['baud'])

    # Transmit the frames from the recordin
    click.secho('Processing {} frames from the source file'.format(source['framecount']), bold=True)
    for (index,), frame in numpy.ndenumerate(source['frames']):
        oneline_print('Progress [{}/{}]'.format(index + 1, source['framecount']))

        # Transmit the frame!
        d.RFxmit(data=frame.decode('hex'), repeat=repeat)

    # Try and be nice to the radio by setting it to Idle.
    click.secho('\nIdling Radio\n', fg='yellow')
    d.setModeIDLE()

    return


def send_binary(frequency, prefix, suffix, baud, repeat, data, full):
    """
        Send a binary string as hex over an RFcat radio

        :param frequency:
        :param prefix:
        :param suffix:
        :param baud:
        :param repeat:
        :param data:
        :param full:
        :return:
    """

    click.secho('Building RF Data from binary string: {}'.format(data), bold=True)

    if full:
        # Warn that the data length is a little short for a 'full' key
        if len(data) <= 12:
            click.secho('WARNING: Data specified as full binary '
                        'but its only {} long'.format(len(data)), fg='yellow')

        # Convert the data to bytes for the radio to send
        rf_data = bitstring.BitArray(bin=data).tobytes()

    else:
        # Calculate the PWM version of the binary we got.

        # First, we instantiate the final data string with
        # the prefix value
        rf_data_string = prefix

        # Next, flip the 1's and 0's to their PWM versions
        for bit in data:

            # rf_data_string += '100' if bit == '1' else '110'
            x = None

            if bit == '1':
                x = '100'

            if bit == '0':
                x = '110'

            rf_data_string += x

        # Finally, add the suffix
        rf_data_string += suffix
        click.secho('Full PWM key:          {}'.format(rf_data_string), fg='green')

        # Convert the data to bytes for the radio to send
        rf_data = bitstring.BitArray(bin=rf_data_string).tobytes()

    # Print some information about what we have so far
    click.secho('RF data packet length: {}'.format(len(rf_data)), fg='green')
    click.secho('Packet as hex:         {}'.format(rf_data.encode('hex')), fg='green')
    click.secho('Preparing radio', fg='yellow')

    # Setup the Radio
    click.secho('Configuring Radio', fg='yellow')
    d = rflib.RfCat()
    configure_dongle(d, frequency=frequency, pktflen=len(rf_data), baud=baud)

    # Transmit the data
    click.secho('Sending transmission \'{}\' time(s)...'.format(repeat), fg='red', bold=True)
    d.RFxmit(data=rf_data, repeat=repeat)

    # Idle the radio
    click.secho('Idling radio', fg='yellow')
    d.setModeIDLE()

    return


def send_hex(frequency, baud, repeat, data):
    """
        Send a hex string as hex over an RFcat radio

        :param frequency:
        :param baud:
        :param repeat:
        :param data:
        :return:
    """

    click.secho('Building RF Data from hex string: {}'.format(data), bold=True)
    rf_data = bitstring.BitArray(hex=data)

    # Print some information about what we have so far
    click.secho('Full PWM key:          {}'.format(rf_data.bin), fg='green')
    click.secho('RF data packet length: {}'.format(len(rf_data)), fg='green')
    click.secho('Packet as hex:         {}'.format(rf_data), fg='green')
    click.secho('Preparing radio', fg='yellow')

    # Setup the Radio
    click.secho('Configuring Radio', fg='yellow')
    d = rflib.RfCat()
    configure_dongle(d, frequency=frequency, pktflen=len(rf_data), baud=baud)

    # Transmit the data
    click.secho('Sending transmission \'{}\' time(s)...'.format(repeat), fg='red', bold=True)
    d.RFxmit(data=rf_data.tobytes(), repeat=repeat)

    # Idle the radio
    click.secho('Idling radio', fg='yellow')
    d.setModeIDLE()

    return


def jam(frequency, data, baud, maxpower):
    """
        Jam a frequency by continuously sending crap.

        :param frequency:
        :param data:
        :param baud:
        :param maxpower:
        :return:
    """

    click.secho('Configuring Radio', fg='yellow')
    d = rflib.RfCat()
    configure_dongle(d, frequency=frequency, pktflen=len(data), baud=baud,
                     maxpower=maxpower)

    click.secho('Starting jam on frequency: {}. Press [ENTER] to stop.'.format(frequency), fg='green')

    # Fire Ze Lazers!
    while not keystop():
        d.RFxmit(data=data)

    # Idle the radio
    click.secho('Idling radio', fg='yellow')
    d.setModeIDLE()
