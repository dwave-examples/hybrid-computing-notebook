# Hybrid Computing Jupyter Notebooks

These notebooks demonstrate how you can apply hybrid solvers to your problem, 
create hybrid workflows, and develop custom hybrid components. 

Notebook 01 will 
start you off with Leap's cloud-based hybrid solvers and out-of-the-box 
dwave-hybrid samplers and workflows, and requires only familiarity with the binary 
quadratic model (BQM) approach to formulating problems for solution on quantum 
computers. 

Notebook 02 shows how you create your own workflows using existing dwave-hybrid 
components. 

Notebook 03 is aimed at developers interested in developing their own hybrid components 
for optimal performance.

## Usage

To enable notebook extensions:

```bash
jupyter contrib nbextension install --sys-prefix
jupyter nbextension enable toc2/main
jupyter nbextension enable exercise/main
jupyter nbextension enable exercise2/main
jupyter nbextension enable python-markdown/main
```

To run the notebook:

```bash
jupyter notebook
```

## License

Released under the Apache License 2.0. See LICENSE file.
