![Minecart Rapid Transit Logo](https://github.com/Frumple/mrt-docker-services/assets/68396/32a557d8-f5ad-44ae-9d71-da1ad7d31a55)

# MRT File Server

A Flask web application that allows players to upload/download WorldEdit schematics and NBT map .dat files to a Minecraft server. This application also hosts world download files for players to use in their own offline single-player games.

This application was built and is currently in use for the **[Minecart Rapid Transit (MRT) Minecraft Server](https://www.minecartrapidtransit.net)**.

<div align="center">
  <img src="https://github.com/Frumple/mrt-file-server/blob/master/homepage.png" />
</div>

## Prerequisites

This application uses **[Python 3.10.2](https://www.python.org/downloads/release/python-3102/)**.

After installing Python, install the required packages by navigating to the application root directory and running **pip** with the provided requirements file:

    pip install -r requirements/development.txt

Next, copy the contents of the **instance_template** directory into a new directory named **instance**:

    cp -R instance_template instance

Then in **config.py**:
- You must set **`SECRET_KEY`** to a unique and random phrase. For more details on how to generate a good secret key, see **[the "Sessions" section in the Flask quickstart documentation](https://flask.palletsprojects.com/en/2.2.x/quickstart/#sessions)**.
- If you are running your production server with basic authentication enabled, set the basic auth username and password in **`BASIC_AUTH_USERNAME`** and **`BASIC_AUTH_PASSWORD`**. Otherwise, basic authentication can be disabled by setting **`BASIC_AUTH_FORCE`** to `False`.

## Application Mode

The server can be run in three different modes. To change modes, set the environment variable **`MRT_FILE_SERVER_MODE`** to one of the following values:

- **`development`** - Used for Flask development servers. Default if `MRT_FILE_SERVER_MODE` is not set.
- **`test`** - Used when running tests.
- **`production`** - Used for production servers.

In the **instance** directory, there are three subdirectories each corresponding to one of the application modes. For example, if `MRT_FILE_SERVER_MODE` was set to `PRODUCTION`, the application would read and write files from the **instance/production** directory. Each subdirectory has the following contents:

- **config.py** - The main configuration file
- **logs** - Where all log files are written
- **uploads/schematics** - Where all schematics are uploaded to
- **uploads/maps** - Where all maps are uploaded to
- **downloads/schematics** - Where all schematics are downloaded from
- **downloads/maps** - Where all maps are donwnloaded from
- **downloads/worlds** - Where all worlds are downloaded from

Your upload and download directories should point directly to your WorldEdit /schematics directory and world /data directory (for maps). For this you have a couple options:

- Use symbolic links.
- Deploy this application within a Docker container and use Docker volumes.

**The one exception is that you should NOT point the map upload directory directly to the world /data directory containing all your map .dat files.** Uploading .dat files directly while a Minecraft server running tends to cause the uploaded map file to not persist when the server restarts. You should instead have map files uploaded to the file server's upload directory as normal, and then have a separate script that moves these files to the /data directory when the server is shut down (usually as part of a daily restart script).

## Configuration

`SECRET_KEY` is the only mandatory configuration setting in config.py. You may choose to set other optional settings:

- **`SCHEMATIC_UPLOAD_MAX_NUMBER_OF_FILES`** - Maximum number of schematic files that can be uploaded at one time. (Default: 10)
- **`SCHEMATIC_UPLOAD_MAX_FILE_SIZE`** - Maximum number of bytes that can be uploaded per schematic file. (Default: 100 kilobytes)
- **`MAP_UPLOAD_MAX_NUMBER_OF_FILES`** - Maximum number of map files that can be uploaded at one time. (Default: 10)
- **`MAP_UPLOAD_MAX_FILE_SIZE`** - Maximum number of bytes that can be uploaded per map file. (Default: 100 kilobytes)
- **`MAX_UPLOAD_LAST_ALLOWED_ID_RANGE`** - Number of last map IDs that are allowed to be uploaded. (Default: 1000)
  - Example: If last map ID in `idcounts.dat` is 2500, and `MAX_UPLOAD_LAST_ALLOWED_ID_RANGE` is 1000, then the range of allowed map IDs is 1501 to 2500.

These basic authentication settings are from the **[Flask-BasicAuth](https://github.com/jpvanhal/flask-basicauth)** extension:
- **`BASIC_AUTH_FORCE`** - Set to True to enable basic authentication on the whole application. (Default: False in development and test environments, True in production)
- **`BASIC_AUTH_USERNAME`** - The username needed to access the application if basic authentication is enabled.
- **`BASIC_AUTH_PASSWORD`** - The plaintext password needed to access the application if basic authentication is enabled.

## Running the Tests

Run the tests by navigating to the project root directory and running the following command:

    python -m pytest

## Running the Application

The Flask development server can be run by setting the **`FLASK_APP`** environment variable to **`mrt_file_server`**, and then running the server:

    export FLASK_APP=mrt_file_server
    flask run

For a production server, I recommend running this application using a Docker image, such as tiangolo's **[uwsgi-nginx-flask](https://github.com/tiangolo/uwsgi-nginx-flask-docker)**.
