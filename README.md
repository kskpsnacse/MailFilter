# MailFilter

MailFilter is a Python-based project that sync emails from the email servers and do actions based on custom filters. 
This README provides step-by-step instructions to set up the environment for the project.

## Prerequisites

Ensure you have the following installed on your system:

- `Python 3.12`
- `python3-pip` for managing Python packages
- `git` for cloning the repository

# TL;DR
`
apt-get update && 
DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata &&
apt-get install -y vim curl python3 python3-pip git python3.12-venv &&
cd /home/ubuntu &&
git clone https://github.com/kskpsnacse/MailFilter.git &&
cd MailFilter &&
python3 -m venv ./venv &&
source venv/bin/activate &&
pip install -r requirements.txt &&
mkdir user_creds
`
download `credentials.json` and place it under `user_creds` directory
`mypy main.py && python main.py`

in a new tab, run `python add_user.py` to add user

## Installation

Follow the steps below to set up the project.

### Step 1: Install the Python Virtual Environment Package

For Python 3.12, install the virtual environment package:

`sudo apt-get install -y python3.12-venv`

### Step 2: Clone the Repository

Navigate to your preferred directory (e.g., `/home/ubuntu`) and clone the repository:

`git clone https://github.com/kskpsnacse/MailFilter.git`

### Step 3: Set Up Virtual Environment

Navigate to the project directory and create a virtual environment:

`cd MailFilter && python3 -m venv ./venv`

Activate the virtual environment:

`source venv/bin/activate`

### Step 4: Install Required Python Packages

Once the virtual environment is activated, install the necessary dependencies:

`pip install -r requirements.txt`

### Step 5: Configuring GMail Client

After installing the packages, download the `credentials.json` by following the steps mentioned in the link :
https://developers.google.com/gmail/api/quickstart/python

`mkdir user_creds/`

and copy the downloaded `credentials.json` in to the above created directory `user_creds/`

You are now ready to run the project.

## Running the Project

Then you can start the application with the below command.

`mypy main.py && python main.py`

now you should be able to see some logs in terminal.

## Adding Users to Start Sync

Once, the application is started we should add a user, so that the application can start syncing.

To add a user, we can use the below command

`python add_user.py`

## License

This project is licensed under the Apache License Version 2.0.
