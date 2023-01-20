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

The package can also be run standalone outside a pipeline, or in one to only backup data. Since 1.0.4, configurations are also created if they cannot be found. This means this tool could be used in a tenant to tenant migration scenario as well.

# Exciting news 📣
The front end for IntuneCD has now been released. Check it out [here](https://github.com/almenscorner/intunecd-monitor)


## What's new in 1.3.2
The authentication module has been updated to MSAL, which replaces the deprecated ADAL library. This update brings additional authentication options, including Client Credentials and Certificate-based authentication.

- **Client Credentials:** This method utilizes the `CLIENT_ID` and `CLIENT_SECRET` to authenticate.

- **Certificate-based Authentication:** You can use a certificate uploaded to your Azure AD App Registration by adding the `-c` parameter. Additionally, you must set the environment variables `KEY_FILE` and `THUMBPRINT` to specify the path to the private key of the certificate and the thumbprint of the certificate, respectively. When using this option, **do not** specify the `-m` parameter.

- **Interactive Authentication:** If you are running the tool interactively and wish to authenticate with your own account, add the `-i` parameter. This will open a browser window prompting you to authenticate. When using this option, **do not** specify the `-m` parameter.

## What's new in 1.3.1
- Bug fix for Filters not being able to created if they do not exist
- Bug fix for Conditional Access policies not being able to be created if `authenticationStrength` is configured
- Added Graph throttling handling to `makeapirequestPost` to handle creation of large amounts of CA policies

## What's new in 1.3.0
- New summary of changes, instead of just a count, a summary of the changes with old and new values are sent to the front end
- Report mode, if you want to send a summary of changes to the front end without actually updating the configuration in Intune, you can activate report mode when running the update using `-r` -> `IntuneCD-startupdate -r`

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

### Authentication
There are three options to choose from when running the tool to authenticate to Microsoft Graph.

- Client Credentials
  - This is using the client ID and client secret to authenticate
- Certificate
  - You can choose to authenticate with a certificate uploaded to your Azure AD App Registration by adding the `-c` parameter. In addition you must set ENV variables for `KEY_FILE` and specify the path to the private key of the certificate, and, `THUMBPRINT` and specify the thumbprint of the certificate added to the app registration. If using this option, **do not** specify the `-m` parameter.
- Interactive
  - If you are running the tool interactivly and want to authenticate with your own account, add the `-i` parameter. When the tool is run a browser window will open asking you to authenticate. If using this option, **do not** specify the `-m` parameter.

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
