![Minecart Rapid Transit Logo](https://www.minecartrapidtransit.net/wp-content/uploads/2015/01/logo-with-title2.png)

# MRT File Server

A simple Flask web application that allows players to upload and download map item .dat files and WorldEdit schematics to a Minecraft server. This application also hosts world download files for players to use in their own offline single-player games.

This application was built for the **[Minecart Rapid Transit (MRT) Minecraft Server](https://www.minecartrapidtransit.net)**.

<div align="center">
  <img src="https://github.com/Frumple/mrt-file-server/blob/master/homepage.png" />
</div>

## Prerequisites

This application uses **[Python 3.8.6](https://www.python.org/downloads/release/python-386/)**. Python 3.9.0 or higher currently does not work due to an unresolved deprecation in the NBT package.

After installing Python, install the required packages by navigating to the application root directory and running **pip** with the provided requirements file:

    pip install -r requirements/development.txt

Then, copy the contents of the **instance_template** directory into a new directory named **instance**:

    cp -R instance_template instance

Finally in **config.py**:
- You must set **`SECRET_KEY`** to a unique and random phrase. For more details on how to generate a good secret key, see **[the "Sessions" section in the Flask quickstart documentation](http://flask.pocoo.org/docs/1.0/quickstart/#sessions)**.
- If you are running your production server with basic authentication enabled, set the basic auth username and password in **`BASIC_AUTH_USERNAME`** and **`BASIC_AUTH_PASSWORD`**. Otherwise, basic authentication can be disabled by setting **`BASIC_AUTH_FORCE`** to `False`.

## Application Mode

The server can be run in three different modes. To change modes, set the environment variable **`MRT_FILE_SERVER_MODE`** to one of the following values:

- **`development`** - Used for Flask development servers. Default if `MRT_FILE_SERVER_MODE` is not set.
- **`test`** - Used when running tests.
- **`production`** - Used for production servers.

In the **instance** directory, there are three subdirectories each corresponding to one of the application modes. For example, if `MRT_FILE_SERVER_MODE` was set to `PRODUCTION`, the application would read and write files from the **instance/production** directory. Each subdirectory has the following contents:

- **config.py** - The main configuration file
- **logs** - Where all log files are written
- **uploads** - Where all schematics are uploaded
- **downloads** - Where all schematics and worlds are downloaded

If you want both of the schematic upload and download directories to point to your WorldEdit schematics directory on your Minecraft server so that schematics are immediately available, you have a couple of options to achieve this:

- Use symbolic links to point both directories to the schematic directory.
- Deploy this application within a Docker container and use Docker volumes to map both directories to the schematic directory.

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

    pytest

## Running the Application

The Flask development server can be run by setting the **`FLASK_APP`** environment variable to **`mrt_file_server`**, and then running the server:

    export FLASK_APP=mrt_file_server
    flask run

For a production server, I recommend running this application using a Docker image, such as tiangolo's **[uwsgi-nginx-flask](https://github.com/tiangolo/uwsgi-nginx-flask-docker)**.