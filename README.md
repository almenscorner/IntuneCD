# IntuneCD tool

IntuneCD or, Intune Continuous Delivery as it stands for is a Python package that is used to backup data from Intune and update configurations in Intune. It was created with running it from a pipeline in mind. Using this approach we get complete history of which configurations has been changed and what setting has been changed.

The main function is to back up configurations from Intune to a Git repositry from a DEV environment and if any configurations has changed, push them to PROD Intune environment.

The package can also be run standalone outside of a pipeline, or in one to only backup data.

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
- Application Protection Policies
- Compliance Policies
- Device Configurations
    - For custom macOS and iOS configurations, mobileconfigs are backed up
- Endpoint Security
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
    - Powershell
    - Shell
- Settings Catalog Policies

## What can be updated?
Well... all of the above ;)

- Application Configuration Policies
- Application Protection Policies
- Compliance Policies
- Device Configurations
    - Including custom macOS/iOS .mobileconfigs and custom Windows profiles
- Endpoint Security
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
    - Powershell
    - Shell
- Settings Catalog Policies

## Required Azure AD application Graph API permissions
- DeviceManagementApps.ReadWrite.All
- DeviceManagementConfiguration.ReadWrite.All
- DeviceManagementServiceConfig.ReadWrite.All

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

### Run from a pipeline
I have tested this with Azure DevOps which is what I will give an example to. But it could just as well be run using GitHub Actions.

In the example pipeline below I'm running with the parameters -m 1 (standalone mode) and -o yaml (output configurations in yaml format). If you are running this in DEV -> PROD mode, remove -m and add DEV_ in front of all env: variables except for REPO_DIR. CLIENT_SECRET or DEV_CLIENT_SECRET should be added as a secret variable.

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
The following shows a pipeline which updates configurations in Intune. Again I'm running with -m 1. If this should update PROD, add PROD_ in front of all env: variables except REPO_DIR. CLIENT_SECRET or PROD_CLIENT_SECRET should be added as a secret variable.

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
