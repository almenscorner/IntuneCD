![PyPI - License](https://img.shields.io/pypi/l/IntuneCD?style=flat-square)
[![Downloads](https://pepy.tech/badge/intunecd/month)](https://pepy.tech/project/intunecd)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/IntuneCD?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/IntuneCD?style=flat-square)
![Maintenance](https://img.shields.io/maintenance/yes/2021?style=flat-square)

# IntuneCD tool

IntuneCD or, Intune Continuous Delivery as it stands for is a Python package that is used to backup data from Intune and update configurations in Intune. It was created with running it from a pipeline in mind. Using this approach we get complete history of which configurations has been changed and what setting has been changed.

The main function is to back up configurations from Intune to a Git repositry from a DEV environment and if any configurations has changed, push them to PROD Intune environment.

The package can also be run standalone outside of a pipeline, or in one to only backup data. Since 1.0.4, configurations are also created if they cannot be found. This means this tool could be used in a tenant to tenant migration scenario as well.

## Whats new in 1.0.4
- Backup of assignments
- Update of assignments on existing configurations
- Creation of configurations if they cannot be found by the script
- For compliance, all rules are now backed up and can be updated

:eyes: **Note** that since this version includes assignments, additional API permissions are needed. Refer to the required permissions below.

## Install this package
```python
pip install IntuneCD
```

## Update this package
```python
pip install IntuneCD --upgrade
```

## What is backed up?
- Application Configuration Policies
    - Including assignments
- Application Protection Policies
    - Including assignments
- Compliance Policies
    - Including assignments
- Device Configurations
    - Including assignments
    - For custom macOS and iOS configurations, mobileconfigs are backed up
- Enrollment profiles
    - Apple Business Manager
    - Windows Autopilot
        - Including assignments
- Endpoint Security
    - Including assignments
    - Security Baselines
    - Antivirus
    - Disk Encryption
    - Firewall
    - Endpoint Detection and Response
    - Attach Surface Reduction
    - Account Protection
- Filters
- Notification Templates
- Scripts
    - Including assignments
    - Powershell
    - Shell
- Settings Catalog Policies
    - Including assignments

## What can be updated?
Well... all of the above ;)

- Application Configuration Policies
    - Including assignments
- Application Protection Policies
    - Including assignments
- Compliance Policies
    - Including assignments
- Device Configurations
    - Including assignments
    - Including custom macOS/iOS .mobileconfigs and custom Windows profiles
- Enrollment profiles
    - Apple Business Manager
    - Windows Autopilot
        - Including assignments
- Endpoint Security
    - Including assignments
    - Security Baselines
    - Antivirus
    - Disk Encryption
    - Firewall
    - Endpoint Detection and Response
    - Attach Surface Reduction
    - Account Protection
- Filters
- Notification Templates
- Scripts
    - Including assignments
    - Powershell
    - Shell
- Settings Catalog Policies
    - Including assignments

## What can be created?
If the configuration the script is looking for cannot be found, it will create it. Supported configurations for creation are:

- Application Configuration Policies
    - Including assignments
- Application Protection Policies
    - Including assignments
- Compliance Policies
    - Including assignments
- Device Configurations
    - Including assignments
    - Including custom macOS/iOS .mobileconfigs and custom Windows profiles
- Endpoint Security
    - Including assignments
    - Security Baselines
    - Antivirus
    - Disk Encryption
    - Firewall
    - Endpoint Detection and Response
    - Attach Surface Reduction
    - Account Protection
- Filters
- Notification Templates
- Scripts
    - Including assignments
    - Powershell
    - Shell
- Settings Catalog Policies
    - Including assignments

## Required Azure AD application Graph API permissions
- DeviceManagementApps.ReadWrite.All
- DeviceManagementConfiguration.ReadWrite.All
- DeviceManagementServiceConfig.ReadWrite.All
- Group.Read.All

If you just want to backup you can get away with only Read permission!

## How do I use it?
You have two options, using a pipeline or running it locally. Let's have a look at both.

## Parameters
To see which parameters you have to prove just type: IntuneCD-startbackup --help or IntuneCD-startupdate --help

Options:
  * -h, --help  show this help message and exit
  * -o OUTPUT, --output=OUTPUT
    * The format backups will be saved as, valid options are
    json or yaml. Default is json
  * -p PATH, --path=PATH  
    * The path to which the configurations will be saved.
    Default value is $(Build.SourcesDirectory)
  * -m MODE, --mode=MODE  
    * The mode in which the script is run, 0 = devtoprod
    (backup from dev -> update to prod) uses os.environ
    DEV_TENANT_NAME, DEV_CLIENT_ID, DEV_CLIENT_SECRET, 1 =
    standalone (backup from prod) uses os.environ
    TENANT_NAME, CLIENT_ID, CLIENT_SECRET
  * -a LOCALAUTH, --localauth=LOCALAUTH
    * When this paramater is set, provide a path to a local
    json file containing the following keys:
    params:TENANT_NAME, CLIENT_ID, CLIENT_SECRET when run
    in standalone mode and params:DEV_TENANT_NAME,
    DEV_CLIENT_ID, DEV_CLIENT_SECRET when run in devtoprod

For IntuneCD-startupdate 1.0.4 the -u parameter has been added which, if set, updates assignments for existing configurations. Again the groups are matched with displayName, so they must be the same in both tenants.

### Run locally
First install the package using pip, then you must create a json which contains authentication parameters in the following format:
```json
{
    "params":{
        "TENANT_NAME": "",
        "CLIENT_ID": "",
        "CLIENT_SECRET": ""
    }
}
```

When you have created the json, you can now run these commands
```python
IntuneCD-startbackup -m 1 -o yaml -p /path/to/save/in -a /path/to/auth.json/
```

If you run without the -m parameter, make sure you have one auth.json pointing to DEV and another pointing to PROD, example:
```json
{
    "params":{
        "DEV_TENANT_NAME": "",
        "DEV_CLIENT_ID": "",
        "DEV_CLIENT_SECRET": ""
    }
}
```

```json
{
    "params":{
        "PROD_TENANT_NAME": "",
        "PROD_CLIENT_ID": "",
        "PROD_CLIENT_SECRET": ""
    }
}
```

```python
IntuneCD-startbackup -o yaml -p /path/to/save/in -a /path/to/auth_DEV.json/
```

```python
IntuneCD-startupdate -p /path/to/save/in -a /path/to/auth_PROD.json/
```

### Run from a pipeline
I have tested this with Azure DevOps which is what I will give an example to. But it could just as well be run using GitHub Actions.

In the example pipeline below I'm running with the parameters -m 1 (standalone mode) and -o yaml (output configurations in yaml format). If you are running this in DEV -> PROD mode, remove -m and add DEV_ in front of all env: variables except for REPO_DIR. CLIENT_SECRET should be added as a secret variable.

DEV env variables:
```yaml
  env:
    REPO_DIR: $(REPO_DIR)
    DEV_TENANT_NAME: $(TENANT_NAME)
    DEV_CLIENT_ID: $(CLIENT_ID)
    DEV_CLIENT_SECRET: $(CLIENT_SECRET)
```

**Example backup pipeline:**
```yaml
pool:
  vmImage: ubuntu-latest

variables:
  REPO_DIR: $(Build.SourcesDirectory)
  TENANT_NAME: example.onmicrosoft.com
  CLIENT_ID: xxxxxxxx-xxxxx-xxxx-xxxx-xxxxxxxxxxxx

steps:

- checkout: self
  persistCredentials: true

- script: pip3 install IntuneCD
  displayName: Install IntuneCD

- script: |
      git config --global user.name "autopkgpipeline"
      git config --global user.email "autopkgpipeline@azuredevops.local"
  displayName: Configure Git

- script: IntuneCD-startbackup -m 1 -o yaml
  env:
    REPO_DIR: $(REPO_DIR)
    TENANT_NAME: $(TENANT_NAME)
    CLIENT_ID: $(CLIENT_ID)
    CLIENT_SECRET: $(CLIENT_SECRET)
  displayName: Run IntuneCD backup

- script: |
    cd $(REPO_DIR)
    git add --all
    git commit -m "Updated configurations"
    git push origin HEAD:main
  displayName: Commit changes
```
The following shows a pipeline which updates configurations in Intune. Again I'm running with -m 1. If this should update PROD, add PROD_ in front of all env: variables except REPO_DIR. CLIENT_SECRET should be added as a secret variable.

PROD env variables:
```yaml
  env:
    REPO_DIR: $(REPO_DIR)
    PROD_TENANT_NAME: $(TENANT_NAME)
    PROD_CLIENT_ID: $(CLIENT_ID)
    PROD_CLIENT_SECRET: $(CLIENT_SECRET)
```

**Example update pipeline:**
```yaml
pool:
  vmImage: ubuntu-latest

variables:
  REPO_DIR: $(Build.SourcesDirectory)
  TENANT_NAME: example.onmicrosoft.com
  CLIENT_ID: xxxxxxxx-xxxxx-xxxx-xxxx-xxxxxxxxxxxx

steps:

- checkout: self
  persistCredentials: true

- script: pip3 install IntuneCD
  displayName: Install IntuneCD

- script: IntuneCD-startupdate -m 1
  env:
    REPO_DIR: $(REPO_DIR)
    TENANT_NAME: $(TENANT_NAME)
    CLIENT_ID: $(CLIENT_ID)
    CLIENT_SECRET: $(CLIENT_SECRET)
  displayName: Run update
```

## Good to know
When this tool tries to update configurations, it filters or searches for the displayname. Therefore the displayname from DEV must match in PROD.

## Current known limitations
Updating Windows Update Rings configurations is currently not supported, the tool can however create update rings if they don't exist.