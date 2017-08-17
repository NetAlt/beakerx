# Copyright 2017 TWO SIGMA OPEN SOURCE, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''Installs BeakerX into a Jupyter and Python environment.'''

import argparse
import os
import pkg_resources
import shutil
import subprocess
import sys
import tempfile


def _all_kernels():
    kernels = pkg_resources.resource_listdir(
        'beakerx', os.path.join('static', 'kernel'))
    return [kernel for kernel in kernels if kernel != 'base']


def _classpath_for(kernel):
    return pkg_resources.resource_filename(
        'beakerx', os.path.join('static', 'kernel', kernel, 'lib', '*'))


def _install_nbextension():
    subprocess.check_call(["jupyter", "nbextension", "install", "beakerx", "--py", "--sys-prefix"])
    subprocess.check_call(["jupyter", "nbextension", "enable", "beakerx", "--py", "--sys-prefix"])


def _copy_tree(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _install_css(prefix):
    src_base = pkg_resources.resource_filename('beakerx', os.path.join('static', 'custom'))
    dest_base = os.path.join(prefix, 'lib', 'python3.5', 'site-packages', 'notebook', 'static', 'custom')
    _copy_tree(os.path.join(src_base, 'fonts'), os.path.join(dest_base, 'fonts'))
    shutil.copyfile(os.path.join(src_base, 'custom.css'), os.path.join(dest_base, 'custom.css'))


def _install_kernels():
    base_classpath = _classpath_for('base')

    for kernel in _all_kernels():
        kernel_classpath = _classpath_for(kernel)
        classpath = os.pathsep.join([base_classpath, kernel_classpath])
        # TODO: replace with string.Template, though this requires the
        # developer install to change too, so not doing right now.
        template = pkg_resources.resource_string(
            'beakerx', os.path.join('static', 'kernel', kernel, 'kernel.json'))
        contents = template.decode().replace('__PATH__', classpath)
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, 'kernel.json'), 'w') as f:
                f.write(contents)
            install_cmd = [
                'jupyter', 'kernelspec', 'install',
                '--sys-prefix', '--replace',
                '--name', kernel, tmpdir
            ]
            subprocess.check_call(install_cmd)


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix",
                        help="location of the environment to install into",
                        default=sys.prefix)
    return parser


def install():
    try:
        parser = make_parser()
        args = parser.parse_args()
        _install_nbextension()
        _install_kernels()
        _install_css(args.prefix)
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    install()