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

"""A utility to serialize nodes and raise an error if they are not serializable.


For the launch configurations that use this feature, one can test them using:

```
from launchpad.launch import serialization_test

class SerializationTest(serialization_test.ErrorOnSerializationMixin):

  @property
  def _launch(self):
    return launch.launch
```
"""

from absl import flags
import cloudpickle
from launchpad import flags as lp_flags  

FLAGS = flags.FLAGS


def check_nodes_are_serializable(label, nodes):
  """Raises an exception if some `PyNode` objects are not serializable."""
  # We don't check explicitly for the `PyNode` type to prevent a circular
  # dependency.
  for node in nodes:
    if not hasattr(node, 'function'):
      raise NotImplementedError(
          'Only PyNodes are currently supported in this launch type.')

  functions = [node.function for node in nodes]
  try:
    cloudpickle.dumps(functions)
  except Exception as e:
    raise RuntimeError(
        f"The nodes associated to the label '{label}' were not serializable "
        "using cloudpickle. Make them pickable, or `serialize_py_nodes=False` "
        "to `lp.launch` if you want to disable this check, for example when you"
        " want to use FLAGS, mocks, threading.Event etc in your test."
    ) from e


def serialize_nodes(data_file_path: str, label: str, nodes):
  """Serializes into a file at path `data_file_path` nodes functions.

  Args:
    data_file_path: The path of the (local) file to write to.
    label: The name of the worker group. This is propagated to enrich the error
      message.
    nodes: The list of PyNodes.
  """
  for node in nodes:
    if not hasattr(node, 'function'):
      raise NotImplementedError(
          'Only PyNodes are currently supported in this launch type.')

  functions = [node.function for node in nodes]
  with open(data_file_path, 'wb') as f:
    try:
      cloudpickle.dump(functions, f)
    except Exception as e:
      raise RuntimeError(
          f"The nodes associated to the label '{label}' were not serializable "
          "using cloudpickle. Make them pickable, or use a launch type which "
          "does not need serialization. "
      ) from e
