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

from os import path

import click


def generate_template(destination):
    """
        Write a copy of the GNU Radio template to
        a new file.

        :param destination:
        :return:
    """

    template_store = '/../share'
    template_file = '/template.grc'

    # Resolve the path to the source template
    source_template = path.realpath(
        path.abspath(path.dirname(__file__) + template_store)) + template_file

    click.secho('Writing a GNU Radio template XML to: {}'.format(destination), fg='green')

    # Open the template
    with open(source_template, 'r') as s:

        # And write it to the new destination.
        with open(destination, 'w') as d:

            # Line by line.
            for line in s.readlines():
                d.write(line)

    click.secho('Done.')
