# Copyright 2020 DeepMind Technologies Limited. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests & test utils for serialization.py."""

import threading

from absl.testing import absltest
from launchpad import program as lp_program
from launchpad.launch import serialization
from launchpad.nodes.python import node as python


class NotSeriazableNode(python.PyNode):

  def __init__(self):
    self._event = threading.Event()  # Not serializable

  def __call__(self):
    return


@absltest.skip('base class')
class ErrorOnSerializationMixin(absltest.TestCase):
  """A mixin class to be used in tests for launch code using `serialization`."""

  @property
  def _launch(self):
    raise NotImplementedError('Any child class should override _get_launch.')

  def _get_program(self):
    program = lp_program.Program('quick_stop')
    program.add_node(python.PyNode(NotSeriazableNode()), label='my_node')
    return program

  def test_raises_error_on_serialize_py_nodes(self):
    program = self._get_program()
    with self.assertRaisesRegex(  
        RuntimeError,
        "The nodes associated to the label 'my_node' were not serializable "
    ):
      self._launch(program, test_case=self, serialize_py_nodes=True).wait()

  def test_serialize_py_nodes_is_false(self):
    program = self._get_program()
    self._launch(program, test_case=self, serialize_py_nodes=False).wait()


class SerializationTest(absltest.TestCase):

  def test_quick_stop(self):
    nodes = [python.PyNode(NotSeriazableNode())]

    with self.assertRaisesRegex(
        RuntimeError,
        "The nodes associated to the label 'my_node' were not serializable "
        'using cloudpickle. Make them pickable, or `serialize_py_nodes=False` '
        'to `lp.launch` if you want to disable this check.'):
      serialization.check_nodes_are_serializable('my_node', nodes)


if __name__ == '__main__':
  absltest.main()
