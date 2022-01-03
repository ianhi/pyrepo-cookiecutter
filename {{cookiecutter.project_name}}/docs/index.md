
# {{ cookiecutter.project_name }}'s Documentation

{{ cookiecutter.project_short_description }}


## Basic Usage

```python
# a basic usage example can go here
print(1+1)
```

## Install
```bash
pip install {{ cookiecutter.project_name }}
```



```{toctree}
:maxdepth: 2

API <api/{{ cookiecutter.project_slug }}>
contributing
```

```{toctree}
:caption: Examples
:maxdepth: 1

examples/basic-example.ipynb
```
