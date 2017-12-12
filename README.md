![Minecart Rapid Transit Logo](https://www.minecartrapidtransit.net/wp-content/uploads/2015/01/logo-with-title2.png)

# MRT File Server

A simple Flask web application that allows players to upload and download WorldEdit schematics to a Minecraft server. This application also hosts world download files for players to use in their own offline single-player games.

This application was built for the **[Minecart Rapid Transit (MRT) Minecraft Server](https://www.minecartrapidtransit.net)**.

## Prerequisites

This application was built using **Python 3.6.2**. Install it from **[https://www.python.org](https://www.python.org/)**.

After installing Python, install the required packages by navigating to the application root directory and running **pip** with the provided requirements file:

    pip install -r requirements.txt

Finally, copy the contents of the **instance_template** directory into a new directory named **instance**:

    cp -R instance_template instance

## Application Mode

The server can be run in three different modes. To change modes, set the environment variable **`MRT_FILE_SERVER_MODE`** to one of the following values:

- **`DEVELOPMENT`** - Used for Flask development servers. Default if `MRT_FILE_SERVER_MODE` is not set.
- **`TEST`** - Used when running tests.
- **`PRODUCTION`** - Used for production servers.

In the **instance** directory, there are three subdirectories each corresponding to one of the application modes. For example, if `MRT_FILE_SERVER_MODE` was set to `PRODUCTION`, the application would read and write files from the **instance/production** directory. Each subdirectory has the following contents:

- **config.py** - The main configuration file
- **logs** - Where all log files are written
- **uploads** - Where all schematics are uploaded
- **downloads** - Where all schematics and worlds are downloaded

If you want the schematic upload and download directories to point to your WorldEdit schematics directory on your Minecraft server so that schematics are immediately available, you have a couple of options to achieve this:

- Use symbolic links to point both directories to the schematic directory.
- Deploy this application within a Docker container and use Docker volumes to map your directories to the schematic directory.

## Configuration

In **config.py**, you must set **`SECRET_KEY`** to a unique and random phrase. For more details on how to generate a good secret key, see **[the "Sessions" section in the Flask documentation](http://flask.pocoo.org/docs/0.12/quickstart/#sessions)**.

`SECRET_KEY` is the only mandatory configuration setting. You may choose to set other optional settings:

- **`MAX_NUMBER_OF_UPLOAD_FILES`** - Maximum number of files that can be uploaded at one time. (Default: 10)
- **`MAX_UPLOAD_FILE_SIZE`** - Maximum number of bytes that can be uploaded per file. (Default: 100 kilobytes)

## Running the Tests

Run the tests by navigating to the project root directory and running the following command:

    python -m unittest discover tests

## Running the Application

The Flask development server can be run by setting the **`FLASK_APP`** environment variable to **`mrt_file_server`**, and then running the server:

    export FLASK_APP=mrt_file_server
    flask run

For a production server, I recommend running this application using a Docker image, such as **[uwsgi-nginx-flask](https://github.com/tiangolo/uwsgi-nginx-flask-docker)**.