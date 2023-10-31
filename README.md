[![Open in GitHub Codespaces](
  https://img.shields.io/badge/Open%20in%20GitHub%20Codespaces-333?logo=github)](
  https://codespaces.new/dwave-examples/hybrid-computing-notebook?quickstart=1)
[![Linux/Mac/Windows build status](
  https://circleci.com/gh/dwave-examples/hybrid-computing-notebook.svg?style=shield)](
  https://circleci.com/gh/dwave-examples/hybrid-computing-notebook)

# Hybrid Computing

These notebooks demonstrate how you can apply hybrid solvers to your problem,
create hybrid workflows, and develop custom hybrid components.

* **Notebook 01** will start you off with Leap's cloud-based hybrid solvers and
  out-of-the-box dwave-hybrid samplers and workflows, and requires only familiarity
  with the
  [binary quadratic model](https://docs.ocean.dwavesys.com/en/stable/concepts/bqm.html)
  (BQM) approach to formulating problems for solution on quantum computers.
* **Notebook 02** shows how you create your own workflows using existing dwave-hybrid
  components.
* **Notebook 03** is aimed at developers interested in developing their own hybrid
  components for optimal performance.

## A Few Words on Hybrid Computing

Quantum-classical hybrid is the use of both classical and quantum resources to
solve problems, exploiting the complementary strengths that each provides. As
quantum processors grow in size, offloading hard optimization problems to quantum
computers promises performance benefits similar to CPUs' outsourcing of
compute-intensive graphics-display processing to GPUs.

This [Medium Article](https://medium.com/d-wave/three-truths-and-the-advent-of-hybrid-quantum-computing-1941ba46ff8c)
provides an overview of, and motivation for, hybrid computing.

D-Wave's [Leap quantum cloud service](https://cloud.dwavesys.com/leap) provides
cloud-based hybrid solvers you can submit arbitrary quadratic models to. These
solvers, which implement state-of-the-art classical algorithms together with
intelligent allocation of the quantum processing unit (QPU) to parts of the
problem where it benefits most, are designed to accommodate even very large
problems. Leap's solvers can relieve you of the burden of any current and future
development and optimization of hybrid algorithms that best solve your problem.

[*dwave-hybrid*](https://docs.ocean.dwavesys.com/en/stable/docs_hybrid/sdk_index.html)
provides you with a Python framework for building a variety of flexible hybrid
workflows. These use quantum and classical resources together to find good
solutions to your problem. For example, a hybrid workflow might use classical
resources to find a problem’s hard core and send that to the QPU, or break a large
problem into smaller pieces that can be solved on a QPU and then recombined.

The *dwave-hybrid* framework enables rapid development of experimental prototypes,
which provide insight into expected performance of the productized versions. It
provides reference samplers and workflows you can quickly plug into your
application code. You can easily experiment with customizing workflows that best
solve your problem. You can also develop your own hybrid components to optimize
performance.

![hybrid workflow](images/kerberos.png)

## Installation

You can run this example without installation in cloud-based IDEs that support 
the [Development Containers specification](https://containers.dev/supporting)
(aka "devcontainers").

For development environments that do not support ``devcontainers``, install 
requirements:

    pip install -r requirements.txt

If you are cloning the repo to your local system, working in a 
[virtual environment](https://docs.python.org/3/library/venv.html) is 
recommended.

## Usage

Your development environment should be configured to 
[access Leap’s Solvers](https://docs.ocean.dwavesys.com/en/stable/overview/sapi.html).
You can see information about supported IDEs and authorizing access to your 
Leap account [here](https://docs.dwavesys.com/docs/latest/doc_leap_dev_env.html).  

The notebooks can be opened by clicking on the ``.ipynb`` files
(e.g., ``01-hybrid-computing-getting-started.ipynb``) in VS Code-based IDEs. 

To run a locally installed notebook:

```bash
jupyter notebook
```

## License

Released under the Apache License 2.0. See LICENSE file.
