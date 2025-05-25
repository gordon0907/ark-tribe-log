# ark-tribe-log

A Flask HTTP server for displaying your ARK: Survival Evolved tribe log. Designed specifically for deployment on
Synology DSM using the "Containerized Script Language Website" feature with alias-based web portals.

## Preparation

Update the `TRIBE_FILE_PATH` in `server.py` to match the Tribe ID of the tribe you want to host.

## Installation

This guide demonstrates how to host the website using DSM's "Containerized Script Language Website" feature.  
Reference: [Synology Help - Web Service](https://kb.synology.com/en-us/DSM/help/WebStation/application_webserv_webservice?version=7)

> Note: Some terminology may differ from the official English-language DSM, as this guide is based on a translated
> (non-English native) DSM interface.

### 1. Download and Place Files

Download this repository and extract it. Copy `server.py` to a suitable DSM directory. Optionally, you can also copy
`icon.png` to the same directory to enable the page favicon.  
Example path:  
`/volume1/web_packages/docker/ark-tribe-log`

> It's recommended to use directories under `web` or `web_packages`, as they are granted read access by default to the
`http` user group.

### 2. Create a Python Web Service

- Open **Web Station** and go to the **Web Service** tab.
- Click **Add** → **Containerized Script Language Website**.
- Choose **Python**, version **3.13** (or the latest available).

### 3. Configure Web Service Settings

Fill in the fields as follows:

- **Name**: `ark-tribe-log`
- **Description**: `/volume1/web_packages/docker/ark-tribe-log`  
  _(Optional, just for personal reference)_
- **Main Directory**: `web_packages/docker/ark-tribe-log`
- **HTTP Backend Server**: `Nginx`
- **WSGI File**: `server.py`
- **Callable**: `app`

Other settings can remain as default.

### 4. uWSGI Settings

Leave all settings at their default values.

### 5. Install Python Modules

- Click **Browse** under the Python environment configuration.
- Upload `requirements.txt` from this repository to install required modules.

### 6. Database Settings

Skip this section; no database configuration is needed.

### 7. Finalize Container Setup

- Once the project is created (named `ark-tribe-log` as configured), open **Container Manager**.
- In the **Project** tab, select `ark-tribe-log` and click **Clear**.

### 8. Mount ARK Save Directory

- Go to the detailed configuration of the project.
- In the YAML editor, add the following under the `volumes:` section to mount your ARK save directory:

  ```yaml
  - "/volume1/docker/SteamCMD/steamapps/common/ARK Survival Evolved Dedicated Server/ShooterGame/Saved/SavedArks:/SavedArks:ro"
  ```

- Save and choose **Create and Restart Project (Rebuild Image)**.

### 9. Set Up Web Portal

- Back in **Web Station**, go to the **Web Portal** tab.
- Click **Add Customized Portal**.
- Configure with the following:
    - **Service**: `ark-tribe-log`
    - **Protocol Type**: `Alias-based`
    - **Alias**: _(choose a custom path)_

Other settings can remain as default.

## Debug

For local testing or debugging via Docker:

```bash
docker build --tag ark-tribe-log:latest .
```

```bash
docker run -it --rm \
  --publish 80:80/tcp \
  --mount "type=bind,source=<host-side path to the ARK server's SavedArks directory>,target=/SavedArks,readonly" \
  ark-tribe-log:latest
```
