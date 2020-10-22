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
                    errors.append(output)

    return errors

def embedding_fail(error_list):
    return error_list and error_list[0].evalue == 'no embedding found'

def robust_run_jn(jn, timeout, retries):

    run_num = 1
    notebook = run_jn(jn, timeout)
    errors = collect_jn_errors(notebook)

    while embedding_fail(errors) and run_num < retries:
        run_num += 1
        notebook = run_jn(jn, timeout)
        errors = collect_jn_errors(notebook)

    return notebook, errors

def cell_text(nb, cell):
    return nb["cells"][cell]["outputs"][0]["text"]

jn_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestJupyterNotebook(unittest.TestCase):

    MAX_EMBEDDING_RETRIES = 3    

    def test_jn1(self):
        # Smoketest
        MAX_RUN_TIME = 800

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
        self.assertIn("-1.0", cell_text(nb, 7))

        # Section Using Leap's Hybrid Solvers, run default, print set size & energy 
        _check_set_energy(nb["cells"][10])

        # Section Sampler: Kerberos, run default, print set size & energy
        _check_set_energy(nb["cells"][15]) 
 
        # Section Sampler: Kerberos, max_iter=10, print set size & energy 
        _check_set_energy(nb["cells"][17])

        # Section Configuring the Sampler, exercise, return more sample sets 
        cell_output_str = cell_text(nb, 20)
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
        self.assertIn("FixedTemperatureSampler", cell_text(nb, 33))

        # Section Operational Utilities, print_counters()  
        self.assertIn("FixedTemperatureSampler", cell_text(nb, 35))

        # Section Operational Utilities, print_counters()  
        self.assertIn("INFO", cell_text(nb, 37))

    def test_jn2(self):
        # Smoketest
        MAX_RUN_TIME = 800

        def _check_energy(cell):
            """Check energy<0."""
            energy_str = re.findall(r'-\d+\.?\d+', cell["outputs"][0]["text"])
            self.assertLess(float(energy_str[0]), 0)

        jn_file = os.path.join(jn_dir, '02-hybrid-computing-workflows.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Test cell outputs:

        # Section Basic Workflows, subsection States, create initial state  
        self.assertIn("problem", cell_text(nb, 6))

        # Section Basic Workflows, subsection Runnables, run Identity
        self.assertIn("True", cell_text(nb, 9))

        # Section Basic Workflows, subsection Runnables, run Duplicate
        self.assertIn("2", cell_text(nb, 11))

        # Section Basic Workflows, subsection Runnables, Const for samples=None
        self.assertIn("True", cell_text(nb, 14))

        # Section Basic Workflows, subsection Runnables, default tabu
        _check_energy(nb["cells"][16])

        # Section Basic Workflows, subsection Runnables, tabu with long timeout
        _check_energy(nb["cells"][19])

        # Section Basic Workflows, subsection Runnables
        self.assertIn("info", cell_text(nb, 22))

        # Section Basic Workflows, subsection Branch, print_counters()
        self.assertIn("Branch", cell_text(nb, 24))

        # Section Basic Workflows, subsection Branch, tabu generates initial samples
        _check_energy(nb["cells"][26])

        # Section Basic Workflows, subsection Branch, tabu all-1s initial samples
        _check_energy(nb["cells"][29])

        # Section A Practical Example, initial energy
        _check_energy(nb["cells"][31])
 
        # Section Parallel Branches: Blocking, SIMO
        self.assertIn("2", cell_text(nb, 33))

        # Section Parallel Branches: Blocking, MIMO, problem versus subproblem
        cell_output = re.findall(r'\d+', cell_text(nb, 35))
        self.assertGreater(int(cell_output[0]), int(cell_output[1]))

        # Section Parallel Branches: Blocking, MIMO, exercise with two-branch energies
        cell_output_str = cell_text(nb, 38)
        energies_str = re.findall(r'\[(.*?)\]', cell_output_str)[0].split(',')
        self.assertLess(float(energies_str[0]), 0)
        self.assertLess(float(energies_str[1]), 0)

        # Section Parallel Branches Non-Blocking, sample sets in two states 
        cell_output_str = cell_text(nb, 40)
        energies_str = re.findall(r'\d+', cell_output_str)
        self.assertGreater(int(energies_str[0]), 0)
        self.assertGreater(int(energies_str[1]), 0)

        # Section Selecting Samples, lowest energy
        _check_energy(nb["cells"][42])

        # Section Customizing Sample Selection, default tabu search, lowest energy
        _check_energy(nb["cells"][44])

        # Section Customizing Sample Selection, lowest energy weighted by runtime
        cell_output_str = cell_text(nb, 47)
        energies_str = re.findall(r'-\d+', cell_output_str) 
        self.assertEqual(len(energies_str), 7)

        # Section Customizing Sample Selection, bonus exercise, lowest energy
        _check_energy(nb["cells"][50])

        # Section Customizing Sample Selection, bonus exercise, test cell
        cell_output_str = cell_text(nb, 51)
        energies_str = re.findall(r'-\d+.\d+', cell_output_str) 
        self.assertGreater(len(energies_str), 0)

        # Section Iterating, print_counters()
        self.assertIn("Loop", cell_text(nb, 53))

        # Section Sample Workflows, Decomposition, Unwind with rolling_history 
        cell_output_str = cell_text(nb, 70)
        variables_str = re.findall(r'\d+', cell_output_str) 
        self.assertGreater(len(variables_str), 20)

        # Section Sample Workflows, Postprocessing, num_reads=10, before pp  
        _check_energy(nb["cells"][73])

        # Section Sample Workflows, Postprocessing, num_reads=10, with pp  
        _check_energy(nb["cells"][75])

        # Section Experimenting with Auto-Embedding Vs Pre-Embedding, print_structure()
        self.assertIn("SplatComposer", cell_text(nb, 80))

        # Section Experimenting with Auto-Embedding Vs Pre-Embedding, print_counters()
        self.assertIn("QPUSubproblemAutoEmbeddingSampler", cell_text(nb, 82))


    def test_jn3(self):
        # Smoketest
        MAX_RUN_TIME = 800

        jn_file = os.path.join(jn_dir, '03-hybrid-computing-components.ipynb')
        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, self.MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Test cell outputs:

        # Section Creating States, create a state from the example problem
        self.assertIn("hybrid.core.SampleSet", cell_text(nb, 7))

        # Section Creating States, max_sample used, read energy 
        energy_str = re.findall(r'\d+.\d+', cell_text(nb, 9)) 
        self.assertGreater(len(energy_str), 0)

        # Section Updating States, updated() method
        self.assertIn("Some information", cell_text(nb, 11))

        # Section Updating States, updated() method plus dup()
        self.assertIn("Some more information", cell_text(nb, 13))

        # Section Resolving States
        self.assertIn("state=", cell_text(nb, 15))

        # Section Resolving States, using result()
        self.assertIn("Future", cell_text(nb, 17))

        # Section Resolving States, Run Identity in a loop  
        energy_str = re.findall(r'\d+.\d+', cell_text(nb, 19)) 
        self.assertGreater(len(energy_str), 0)

        # Section Executing Runnables, using error()
        self.assertIn("int", cell_text(nb, 22))

        # Section Executing Runnables, using next()  
        energy_str = re.findall(r'\d+.\d+', cell_text(nb, 24)) 
        self.assertGreater(len(energy_str), 0)

        # Section Terminating Runnables, using stop()
        self.assertIn("state=", cell_text(nb, 27))

        # Section Terminating Runnables, using stop()
        self.assertIn("state=finished", cell_text(nb, 29))

        # Section A Simple Runnable, counter after one execution
        self.assertIn("1", cell_text(nb, 34))

        # Section A Simple Runnable, Exercise, counter after one execution
        self.assertIn("1", cell_text(nb, 38))

        # Section Customizing Termination, run less than 10 sec 
        counter_str = re.findall(r'\d+', cell_text(nb, 42))
        self.assertGreater(int(counter_str[0]), 0)

        # Section Customizing Termination, Loop implements @stoppable 
        counter_str = re.findall(r'\d+', cell_text(nb, 44))
        self.assertGreater(int(counter_str[0]), 0)

        # Section Section Customizing Termination, halt() method
        self.assertIn("Terminated", cell_text(nb, 47))

        # Section Customizing Termination, exercise, halt() method 
        counter_str = re.findall(r'\d+', cell_text(nb, 51))
        self.assertGreater(int(counter_str[0]), 0)

        # Section Example Trait: SISO, IncrementCount on a States-class object
        self.assertIn("object has no attribute", cell_text(nb, 55))

        # Section Example Trait: SISO, IncrementCount with the SISO trait
        self.assertIn("single state required", cell_text(nb, 59))

        # Section Example Trait: MIMO, exercise
        #self.assertIn("state sequence required", cell_text(nb, 65))

        # Section Example: Existing Trait SamplesProcessor
        #self.assertIn("input state is missing", nb["cells"][70]["outputs"][1]["text"])

        # Section Example: New Trait TraitCounterIntaking
        self.assertIn("input state is missing", cell_text(nb, 73))

        # Section A Custom Sampler, exercise output
        filtered_nodes = re.findall(r'\[(.*?)\]', cell_text(nb, 78))[0].split()
        self.assertGreater(len(filtered_nodes), 0)

        # Section Dimod Conversion 
        energy_str = re.findall(r'-\d+.\d+', cell_text(nb, 82)) 
        self.assertLess(float(energy_str[0]), 0)

        # Section Dimod Conversion, run the converted workflow 
        energy_str = re.findall(r'-\d+.\d+', cell_text(nb, 86)) 
        self.assertLess(float(energy_str[0]), 0)

        # Section Dimod Conversion, specifying selected nodes in filter_nodes
        filtered_nodes = re.findall(r'\[(.*?)\]', cell_text(nb, 90))[0].split()
        self.assertGreater(len(filtered_nodes), 0)


        # Section Dimod Conversion, converted TabuProblemSamplerFilteredNodes
        filtered_nodes = re.findall(r'\[(.*?)\]', cell_text(nb, 94))[0].split()
        self.assertGreater(len(filtered_nodes), 0)

