# Contributing

In addition to the general guidelines there are specific details for
contributing to terra, these are documented below.

### Contents
* [Pull request checklist](#pull-request-checklist)
* [Test](#test)
* [Style and Lint](#style-and-lint)
* [Development Cycle](#development-cycle)
  * [Branches](#branches)
* [Using dependencies](#using-dependencies)
  * [Adding a requirement](#adding-a-requirement)


### Pull request checklist

When submitting a pull request and you feel it is ready for review,
please ensure that:

1. The code follows the code style of the project and successfully
   passes the tests. For convenience, you can execute `tox` locally,
   which will run these checks and report any issues.

   If your code fails the local style checks (specifically the black
   code formatting check) you can use `tox -eblack` to automatically
   fix update the code formatting.
2. The documentation has been updated accordingly. In particular, if a
   function or class has been modified during the PR, please update the
   *docstring* accordingly.

3. If it makes sense for your change that you have added new tests that
   cover the changes.
4. Ensure that if your change has an end user facing impact (new feature,
   deprecation, removal etc) that you have added a reno release note for that
   change and that the PR is tagged for the changelog.

## Test

Once you've made a code change, it is important to verify that your change
does not break any existing tests and that any new tests that you've added
also run successfully. Before you open a new pull request for your change,
you'll want to run the test suite locally.

The easiest way to run the test suite is to use
[**tox**](https://tox.readthedocs.io/en/latest/#). You can install tox
with pip: `pip install -U tox`. Tox provides several advantages, but the
biggest one is that it builds an isolated virtualenv for running tests. This
means it does not pollute your system python when running. Additionally, the
environment that tox sets up matches the CI environment more closely and it
runs the tests in parallel (resulting in much faster execution). To run tests
on all installed supported python versions and lint/style checks you can simply
run `tox`. Or if you just want to run the tests once run for a specific python
version: `tox -epy310` (or replace py310 with the python version you want to use,
py39 or py311).

If you just want to run a subset of tests you can pass a selection regex to
the test runner. For example, if you want to run all tests that have "dag" in
the test id you can run: `tox -epy310 -- dag`. You can pass arguments directly to
the test runner after the bare `--`. To see all the options on test selection
you can refer to the stestr manual:
https://stestr.readthedocs.io/en/stable/MANUAL.html#test-selection

If you want to run a single test module, test class, or individual test method
you can do this faster with the `-n`/`--no-discover` option. For example:

to run a module:
```
tox -epy310 -- -n test.python.test_examples
```
or to run the same module by path:

```
tox -epy310 -- -n test/python/test_examples.py
```
to run a class:

```
tox -epy310 -- -n test.python.test_examples.TestPythonExamples
```
to run a method:
```
tox -epy310 -- -n test.python.test_examples.TestPythonExamples.test_all_examples
```


## Style and lint

ChatTutor uses two tools for verify code formatting and lint checking. The
first tool is [black](https://github.com/psf/black) which is a code formatting
tool that will automatically update the code formatting to a consistent style.
The second tool is [pylint](https://www.pylint.org/) which is a code linter
which does a deeper analysis of the Python code to find both style issues and
potential bugs and other common issues in Python. Only a very small number
of rules are enabled.

You can check that your local modifications conform to the style rules by
running `tox -elint` which will run `black`, `ruff`, and `pylint` to check the
local code formatting and lint. If black returns a code formatting error you can
run `tox -eblack` to automatically update the code formatting to conform to the
style. However, if `ruff` or `pylint` return any error you will have to fix
these issues by manually updating your code.

Because `pylint` analysis can be slow, there is also a `tox -elint-incr` target,
which runs `black` and `ruff` just as `tox -elint` does, but only applies
`pylint` to files which have changed from the source github. On rare occasions
this will miss some issues that would have been caught by checking the complete
source tree, but makes up for this by being much faster (and those rare
oversights will still be caught by the CI after you open a pull request).

Because they are so fast, it is sometimes convenient to run the tools `black` and `ruff` separately
rather than via `tox`. If you have installed the development packages in your python environment via
`pip install -r requirements-dev.txt`, then `ruff` and `black` will be available and can be run from
the command line. See [`tox.ini`](tox.ini) for how `tox` invokes them.

## Development Cycle

The development cycle for ChatTutor is all handled in the open using
the project boards in Github for project management. We use milestones
in Github to track work for specific releases. The features or other changes
that we want to include in a release will be tagged and discussed in Github.
As we're preparing a new release we'll document what has changed since the
previous version in the release notes.

### Branches

* `main`:

The main branch is used for the current version of ChatTutor.
It will be considered stable. The API
can and will change on main as we introduce and refine new features.

* `beta-main`:
The beta-main branch is used for the development of ChatTutor. It is
updated frequently and should be considered unstable.

* `feat/*` branches:
To add a new feature, create a `feat/*` branch. When your feature
is ready to merge, create a Pull Request to merge your branch into beta-main.

## Using dependencies

A requirement is a package that is absolutely necessary for core functionality in ChatTutor, such as Numpy or Scipy.

### Adding a requirement

Any new requirement must have broad system support; it needs to be supported on all the Python versions and operating systems that ChatTutor supports.
It also cannot impose many version restrictions on other packages.
Users often install ChatTutor into virtual environments with many different packages in, and we need to ensure that neither we, nor any of our requirements, conflict with their other packages.
When adding a new requirement, you must add it to [`requirements.txt`](requirements.txt) with as loose a constraint on the allowed versions as possible.
