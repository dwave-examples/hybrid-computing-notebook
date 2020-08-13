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
import re

def run_jn(jn, timeout):
    
    open_jn = open(jn, "r", encoding='utf-8')
    notebook = nbformat.read(open_jn, nbformat.current_nbformat)
    open_jn.close()
        
    preprocessor = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    preprocessor.allow_errors = True    
    preprocessor.preprocess(notebook, {'metadata': {'path': os.path.dirname(jn)}})

    return notebook

def collect_jn_errors(nb):

    errors = []
    for cell in nb.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    if output.evalue == 'no embedding found':
                        return ["Embedding failed"]
                    else:
                        errors.append(output)

    return errors

def robust_run_jn(jn, timeout, retries):

    run_num = 1
    notebook = run_jn(jn, timeout)
    errors = collect_jn_errors(notebook)

    while errors == ['Embedding failed'] and run_num < retries:
        run_num += 1
        notebook = run_jn(jn, timeout)
        errors = collect_jn_errors(notebook)

    return notebook, errors

jn_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestJupyterNotebook(unittest.TestCase):

    MAX_EMBEDDING_RETRIES = 3    

    def test_jn1(self):
        # Smoketest
        MAX_RUN_TIME = 200

        def _check_set_energy(cell):
            """Check set>0 and energy<0."""
            cell_output = re.findall(r'[-+]?\d+\.?\d+', cell["outputs"][0]["text"])
            self.assertGreater(float(cell_output[0]), 0)
            self.assertLess(float(cell_output[1]), 0)

        jn_file = os.path.join(jn_dir, '01-hybrid-computing-getting-started.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Test cell outputs:
        # Section A Sample Problem, create a BQM
        self.assertIn("-1.0", nb["cells"][7]["outputs"][0]["text"])

        # Section Using Leap's Hybrid Solvers, run default, print set size & energy 
        _check_set_energy(nb["cells"][10])

        # Section Sampler: Kerberos, run default, print set size & energy
        _check_set_energy(nb["cells"][15]) 
 
        # Section Sampler: Kerberos, max_iter=10, print set size & energy 
        _check_set_energy(nb["cells"][17])

        # Section Configuring the Sampler, exercise, return more sample sets 
        cell_output_str = nb["cells"][20]["outputs"][0]["text"]
        cell_output = list(map(float, re.findall(r'\[(.*?)\]', cell_output_str)[0].split()))
        for energy in cell_output:
            self.assertLess(energy, 0)

        # Section Configuring the Sampler, advanced exercise, feature-based selection  
        _check_set_energy(nb["cells"][23])

        # Section Workflow: Parallel Tempering, default run, print set size & energy  
        _check_set_energy(nb["cells"][26])

        # Section Workflow: Parallel Tempering, configured parameters, print set size & energy  
        _check_set_energy(nb["cells"][30])

        # Section Operational Utilities, print_structure()  
        self.assertIn("FixedTemperatureSampler", nb["cells"][33]["outputs"][0]["text"])

        # Section Operational Utilities, print_counters()  
        self.assertIn("FixedTemperatureSampler", nb["cells"][35]["outputs"][0]["text"])

        # Section Operational Utilities, print_counters()  
        self.assertIn("INFO", nb["cells"][37]["outputs"][0]["text"])

    def test_jn2(self):
        # Smoketest
        MAX_RUN_TIME = 100

        def _check_energy(cell):
            """Check energy<0."""
            energy_str = re.findall(r'-\d+\.?\d+', cell["outputs"][0]["text"])
            self.assertLess(float(energy_str[0]), 0)

        jn_file = os.path.join(jn_dir, '02-hybrid-computing-workflows.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Section Basic Workflows, subsection States, create initial state  
        self.assertIn("problem", nb["cells"][6]["outputs"][0]["text"])

        # Section Basic Workflows, subsection Runnables, run Identity
        self.assertIn("True", nb["cells"][9]["outputs"][0]["text"])

        # Section Basic Workflows, subsection Runnables, run Duplicate
        self.assertIn("2", nb["cells"][11]["outputs"][0]["text"])

        # Section Basic Workflows, subsection Runnables, Const for samples=None
        self.assertIn("True", nb["cells"][14]["outputs"][0]["text"])

        # Section Basic Workflows, subsection Runnables, default tabu
        _check_energy(nb["cells"][16])

        # Section Basic Workflows, subsection Runnables, tabu with long timeout
        _check_energy(nb["cells"][19])

        # Section Basic Workflows, subsection Runnables
        self.assertIn("info", nb["cells"][22]["outputs"][0]["text"])

        # Section Basic Workflows, subsection Branch, print_counters()
        self.assertIn("TabuProblemSampler", nb["cells"][24]["outputs"][0]["text"])

        # Section Basic Workflows, subsection Branch, tabu generates initial samples
        _check_energy(nb["cells"][26])

        # Section Basic Workflows, subsection Branch, tabu all-1s initial samples
        _check_energy(nb["cells"][29])

        # Section A Practical Example, initial energy
        _check_energy(nb["cells"][31])
 
        # Section Parallel Branches: Blocking, SIMO
        self.assertIn("2", nb["cells"][33]["outputs"][0]["text"])

        # Section Parallel Branches: Blocking, MIMO, problem versus subproblem
        cell_output = re.findall(r'\d+', nb["cells"][35]["outputs"][0]["text"])
        self.assertGreater(int(cell_output[0]), int(cell_output[1]))

        # Section Parallel Branches: Blocking, MIMO, exercise with two-branch energies
        cell_output_str = nb["cells"][38]["outputs"][0]["text"]
        energies_str = re.findall(r'\[(.*?)\]', cell_output_str)[0].split(',')
        self.assertLess(float(energies_str[0]), 0)
        self.assertLess(float(energies_str[1]), 0)

        # Section Parallel Branches Non-Blocking, sample sets in two states 
        cell_output_str = nb["cells"][40]["outputs"][0]["text"]
        energies_str = re.findall(r'\d+', cell_output_str)
        self.assertGreater(int(energies_str[0]), 0)
        self.assertGreater(int(energies_str[1]), 0)

        # Section Selecting Samples, lowest energy
        _check_energy(nb["cells"][42])

        # Section Customizing Sample Selection, default tabu search, lowest energy
        _check_energy(nb["cells"][44])

        # Section Customizing Sample Selection, lowest energy weighted by runtime
        cell_output_str = nb["cells"][47]["outputs"][0]["text"]
        energies_str = re.findall(r'-\d+', cell_output_str) 
        self.assertEqual(len(energies_str), 7)

        # Section Customizing Sample Selection, bonus exercise, lowest energy
        _check_energy(nb["cells"][50])

        # Section Customizing Sample Selection, bonus exercise, test cell
        cell_output_str = nb["cells"][51]["outputs"][0]["text"]
        energies_str = re.findall(r'-\d+.\d+', cell_output_str) 
        self.assertEqual(len(energies_str), 9)

        # Section Iterating, print_counters()
        self.assertIn("TabuProblemSampler", nb["cells"][53]["outputs"][0]["text"])

        # Section Sample Workflows, Decomposition, Unwind with rolling_history 
        cell_output_str = nb["cells"][70]["outputs"][0]["text"]
        variables_str = re.findall(r'\d+', cell_output_str) 
        self.assertGreater(len(variables_str), 20)

        # Section Sample Workflows, Postprocessing, num_reads=10, before pp  
        _check_energy(nb["cells"][73])

        # Section Sample Workflows, Postprocessing, num_reads=10, with pp  
        _check_energy(nb["cells"][75])

        # Section Experimenting with Auto-Embedding Vs Pre-Embedding, print_structure()
        self.assertIn("SplatComposer", nb["cells"][80]["outputs"][0]["text"])

        # Section Experimenting with Auto-Embedding Vs Pre-Embedding, print_counters()
        self.assertIn("QPUSubproblemAutoEmbeddingSampler", nb["cells"][82]["outputs"][0]["text"])


    def test_jn3(self):
        # Smoketest
        MAX_RUN_TIME = 100

        jn_file = os.path.join(jn_dir, '03-hybrid-computing-components.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])
 
