![PyPI - License](https://img.shields.io/pypi/l/IntuneCD?style=flat-square)
[![Downloads](https://pepy.tech/badge/intunecd/month)](https://pepy.tech/project/intunecd)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/IntuneCD?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/IntuneCD?style=flat-square)
![Maintenance](https://img.shields.io/maintenance/yes/2022?style=flat-square)
![Unit tests](https://github.com/almenscorner/IntuneCD/actions/workflows/unit-test.yml/badge.svg)
![Publish](https://github.com/almenscorner/IntuneCD/actions/workflows/pypi-publish.yml/badge.svg)
[![codecov](https://codecov.io/gh/almenscorner/IntuneCD/branch/main/graph/badge.svg?token=SNTOJ0N5MU)](https://codecov.io/gh/almenscorner/IntuneCD)

![icdlogo](https://user-images.githubusercontent.com/78877636/192514344-ab4e3fd5-8d6a-40d6-a56c-814c0149373f.png)

# IntuneCD tool

IntuneCD or, Intune Continuous Delivery as it stands for is a Python package that is used to back up and update configurations in Intune. It was created with running it from a pipeline in mind. Using this approach we get complete history of which configurations have been changed and what setting has been changed.

The main function is to back up configurations from Intune to a Git repository from a DEV environment and if any configurations has changed, push them to PROD Intune environment.

The package can also be run standalone outside a pipeline, or in one to only backup data. Since 1.0.4, configurations are also created if they cannot be found. This means this tool could be used in a tenant to tenant migration scenario as well.

# Exciting news 📣
The front end for IntuneCD has now been released. Check it out [here](https://github.com/almenscorner/intunecd-monitor)

## What's new in 1.2.2
- Updated the Graph request module to handle `429` responses (throttling). If the response code is `429` the module will re-try the request after the amount of seconds specified in the `Retry-After` section in the response. If `429` is hit again, it will re-try until it succeeds. Example output,
  ```
  Hit Graph throttling, trying again after 10 seconds
  Backing up Conditional Access policy: 19
  Hit Graph throttling, trying again after 1 seconds
  ```

## What's new in 1.2.1
- Bug fix for back up of Conditional Access throwing `AttributeError: 'NoneType' object has no attribute 'pop'` when no `grantControls` were configured.

## What's new in 1.2.0
- Improvements to documentation
  - If a setting within a table cell has multiple entries, they are now separated by a new line instead of just a comma
  - Setting name is now separated, for example, `dataRoamingBlocked` will be `Data Roaming Blocked`
- Conditional access :tada:
  - Conditional access is now backed up, this means you will **have to add additional permissions to the Azure AD App Registration**. More information can be found under [Required Azure AD application Graph API permissions](#required-azure-ad-application-graph-api-permissions).
  - If you do not wish to back up/update Conditional access, make sure you add it to exclusions
    - `IntuneCD-startbackup -e ConditionalAccess`
    - `IntuneCD-startupdate -e ConditionalAccess`
  - Assignments are currently not updated, changes to settings on policies are detected however and updated

## What's new in 1.1.4
- Bugfix where filters was not able to be updated with new values
- Bugfix where notification templates was not able to be updated with new values
- Update to how management intents are compared for diffs. Before there was a small chance it compared the wrong definitionId

## I use Powershell, Do I need to learn Python?
No.

Just install Python and IntuneCD, that's it!

## Install this package
```python
pip install IntuneCD
```

## Update this package
```python
pip install IntuneCD --upgrade
```

## What is backed up, updated, created and documented?
| Payload                             |   Back up   | Update | Document |   Create    | Notes                                                                                                                                                     |
|-------------------------------------|:-----------:|:------:|:--------:|:-----------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Apple Push Notification             |   :tada:    |        |  :tada:  |             |                                                                                                                                                           |
| Apple Volume Purchase Program tokens |   :tada:    |        |  :tada:  |             |                                                                                                                                                           |
| Application Configuration Policies  |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Application Protection Policies     |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           | 
| Applications                        |   :tada:    |        |  :tada:  |             |                                                                                                                                                           |
| Compliance Policies                 |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Conditional Access                  |   :tada:    | :tada: |  :tada:  |   :tada:    | Assignments are not updated currently                                                                                                                     |
| Device Configurations               |   :tada:    | :tada: |  :tada:  |   :tada:    | For custom macOS and iOS configurations,</br>mobileconfigs are backed up                                                                                  |
| Group Policy Configurations         |   :tada:    |        |  :tada:  |             |                                                                                                                                                           |
| Enrollment profiles                 | :tada: [^1] | :tada: |  :tada:  | :tada: [^2] |                                                                                                                                                           |
| Enrollment Status Page              |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Endpoint Security                   |   :tada:    | :tada: |  :tada:  |   :tada:    | Security Baselines</br>Antivirus</br>Disk Encryption</br>Firewall</br>Endpoint Detection and Response</br>Attack Surface Reduction</br>Account Protection |
| Filters                             |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Managed Google Play                 |   :tada:    |        |  :tada:  |             |                                                                                                                                                           |
| Notification Templates              |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Proactive Remediation               |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Partner Connections                 |   :tada:    |        |  :tada:  |             | Compliance</br>Management</br>Remote Assistance                                                                                                           |
| Shell Scripts                       |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Powershell Scripts                  |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |
| Settings Catalog Policies           |   :tada:    | :tada: |  :tada:  |   :tada:    |                                                                                                                                                           |

[^1]: Only Apple Business Manager and Windows Autopilot profiles are backed up.
[^2]: Only Windows Autopilot profiles are created.

## Required Azure AD application Graph API permissions
- DeviceManagementApps.ReadWrite.All
- DeviceManagementConfiguration.ReadWrite.All
- DeviceManagementServiceConfig.ReadWrite.All
- Group.Read.All
- Policy.Read.All
- Policy.ReadWrite.ConditionalAccess

If you just want to back up you can get away with only Read permission (except for DeviceManagementConfiguration)!

## How do I use it?
You have two options, using a pipeline or running it locally. Let's have a look at both.

## Parameters
To see which parameters you have to provide just type: IntuneCD-startbackup --help, IntuneCD-startupdate --help or IntuneCD-startdocumentation --help

Example options:
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
      git config --global user.name "devopspipeline"
      git config --global user.email "devopspipeline@azuredevops.local"
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

## Run documentation locally
To create a Markdown document from the backup files, run this command
```python
IntuneCD-startdocumentation -p /path/to/backup/directory -o /path/to/create/markdown.md -t nameoftenant -i 'This is a demo introduction'
```

## Run documentation in a pipeline
This step should be added to the backup pipeline to make sure the markdown document is updated when configurations changes. By default it writes to the README.md file in the repo, you can change this with the -o option

```yaml
- script: IntuneCD-startdocumentation -t $(TENANT_NAME) -i 'This is a demo introduction'
  env:
    REPO_DIR: $(REPO_DIR)
  displayName: Run IntuneCD documentation
```

## Good to know
When this tool tries to update configurations, it matches the display name. Therefore, the display name from DEV must match in PROD.

## Current known limitations
Updating Windows Update Rings configurations is currently not supported, the tool can however create update rings if they don't exist.
