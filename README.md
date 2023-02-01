![PyPI - License](https://img.shields.io/pypi/l/IntuneCD?style=flat-square)
[![Downloads](https://pepy.tech/badge/intunecd/month)](https://pepy.tech/project/intunecd)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/IntuneCD?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/IntuneCD?style=flat-square)
![Maintenance](https://img.shields.io/maintenance/yes/2023?style=flat-square)
![Unit tests](https://github.com/almenscorner/IntuneCD/actions/workflows/unit-test.yml/badge.svg)
![Publish](https://github.com/almenscorner/IntuneCD/actions/workflows/pypi-publish.yml/badge.svg)
[![codecov](https://codecov.io/gh/almenscorner/IntuneCD/branch/main/graph/badge.svg?token=SNTOJ0N5MU)](https://codecov.io/gh/almenscorner/IntuneCD)

<p align="center">
  <img src="https://user-images.githubusercontent.com/78877636/204297420-4b5373a8-4864-4710-a4a5-802ea4ec08d5.png#gh-dark-mode-only" width="500" height="300">
</p>
<p align="center">
  <img src="https://user-images.githubusercontent.com/78877636/204501041-a7cc2321-8991-4abb-a622-97f72f19051f.png#gh-light-mode-only" width="500" height="300">
</p>

IntuneCD or, Intune Continuous Delivery as it stands for is a Python package that is used to back up and update configurations in Intune. It was created with running it from a pipeline in mind. Using this approach we get complete history of which configurations have been changed and what setting has been changed.

The main function is to back up configurations from Intune to a Git repository from a DEV environment and if any configurations has changed, push them to PROD Intune environment.

The package can also be run standalone outside a pipeline, or in one to only backup data.

# Exciting news 📣
The front end for IntuneCD has now been released. Check it out [here](https://github.com/almenscorner/intunecd-monitor)

***

### Getting started

For help getting started, check out [Getting started](https://github.com/almenscorner/IntuneCD/wiki/Getting-started).

Have a look at the [Wiki](https://github.com/almenscorner/IntuneCD/wiki) to find documentation on how to use and configure the tool.

For release notes, have a look [here](https://github.com/almenscorner/IntuneCD/releases).


### Get help

There are a number of ways you can get help,
- Open an [issue](https://github.com/almenscorner/IntuneCD/issues) on this GitHub repo
- Start a [discussion](https://github.com/almenscorner/IntuneCD/discussions) on this GitHub repo
- Ask a question on [Discord](https://discord.gg/msems)
- Ask a question on [Slack](https://join.slack.com/t/intunecd/shared_invite/zt-1nf255xvo-POv60XoewYfY65TH9~tV_g)
- Check the [FAQ](https://github.com/almenscorner/IntuneCD/wiki/FAQ)
