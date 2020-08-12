# Copyright 2020 D-Wave Systems Inc.
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

import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import unittest

def run_jn(jn, timeout):
    
    open_jn = open(jn, "r", encoding='utf-8')
    notebook = nbformat.read(open_jn, nbformat.current_nbformat)
    open_jn.close()
        
    preprocessor = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    preprocessor.allow_errors = True    
    preprocessor.preprocess(notebook, {'metadata': {'path': os.path.dirname(jn)}})

    errors = []
    for cell in notebook.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    if output.evalue == 'no embedding found':
                        return notebook, ["Embedding failed"]
                    else:
                        errors.append(output)

    return notebook, errors

def robust_run_jn(jn, timeout, retries):

    run_num = 1
    notebook, errors = run_jn(jn, timeout)

    while errors == ['Embedding failed'] and run_num < retries:
        run_num += 1
        notebook, errors = run_jn(jn, timeout)

    return notebook, errors

jn_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestJupyterNotebook(unittest.TestCase):

    MAX_EMBEDDING_RETRIES = 3    

    def test_jn1(self):
        # Smoketest
        MAX_RUN_TIME = 200

        jn_file = os.path.join(jn_dir, '01-hybrid-computing-getting-started.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Test cell outputs:
        # Section A Sample Problem, create a BQM
        self.assertIn("-1.0", nb["cells"][7]["outputs"][0]["text"])


    def test_jn2(self):
        # Smoketest
        MAX_RUN_TIME = 100

        jn_file = os.path.join(jn_dir, '02-hybrid-computing-workflows.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

    def test_jn3(self):
        # Smoketest
        MAX_RUN_TIME = 100

        jn_file = os.path.join(jn_dir, '03-hybrid-computing-components.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])
 
