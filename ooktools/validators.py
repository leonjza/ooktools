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

import json
import wave

import click


def validate_wave(ctx, param, value):
    """
        Validate the wave file by trying to open it
        and checking that its got a single channel.

        :param ctx:<class 'click.core.Context'>
        :param param:<class 'click.core.Option'>
        :param value:str
        :return:<class 'wave.Wave_read'>
    """

    try:
        wave_read = wave.open(value)

        if wave_read.getnchannels() is not 1:
            raise click.BadParameter('Only mono wave files are supported')

        return wave_read

    except wave.Error as e:
        raise click.BadParameter('Not a valid wave file. {}'.format(e.__str__()))


def validate_binary_string(ctx, param, value):
    """
        Ensure that a binary string only has 1's and 0's

        :param ctx:<class 'click.core.Context'>
        :param param:<class 'click.core.Option'>
        :param value:str
        :return:str
    """

    valid_characters = '10'

    # If we string the value of valid characters, are there
    # any other characters left over?
    left_overs = value.strip(valid_characters)

    # Except if there are characters left
    if left_overs:
        raise click.BadParameter('Only the characters "{}" is considered valid bitsring input.'
                                 ' The following were invalid: {}'.format(valid_characters, left_overs))

    return value


def validate_hex_string(ctx, param, value):
    """
        Ensure that a value is valid hex

        :param ctx:<class 'click.core.Context'>
        :param param:<class 'click.core.Option'>
        :param value:str
        :return:str
    """

    try:
        int(value, 16)
    except ValueError:
        raise click.BadParameter('\'{}\' is not a valid hex string.'.format(value))

    return value


def validate_recording_json(ctx, param, value):
    """
        Ensure that a source Json recording file is valid

        :param ctx:
        :param param:
        :param value:
        :return:dict
    """

    # Load the JSON from the source file
    try:
        with open(value) as f:
            data = json.load(f)
    except ValueError:
        raise click.BadParameter('The source file appears to be corrupt. '
                                 'You can try to fix it manually by ensuring that '
                                 'it contains valid JSON formatted data.')

    # Ensure that we got a dict back
    if not isinstance(data, dict):
        raise click.BadParameter('The source file \'{}\' appears to be improperly '
                                 'formatted.'.format(value))

    # Make sure all the keys are present
    required_keys = ['date', 'frequency', 'baud', 'framecount', 'frames']
    if not all(k in data for k in required_keys):
        raise click.BadParameter('The source file \'{}\' is missing values.'.format(value))

    return data


def validate_series(ctx, param, value):
    """
        Ensure that a series input is valid

        :param ctx:
        :param param:
        :param value:
        :return:tuple
    """

    # Dont validate if the default value of None is received
    if not value:
        return None

    seperator = ':'

    if seperator not in value:
        raise click.BadParameter('A series must be seperated by a \'{}\' '
                                 'character.'.format(seperator))

    # Check that a split by seperator only returns 2
    # values in the tuple
    if len(value.split(seperator)) != 2:
        raise click.BadParameter('Only one seperator characters is valid.')

    # Split the values and cast them to integers.
    start, end = value.split(':')
    start = int(start)
    end = int(end)

    # Check that the values 'make sense'
    if end < start:
        raise click.BadParameter('The start value must be less than the end value.')

    if start == end:
        raise click.BadParameter('The start value and the end value most not be the same.')

    return start, end
