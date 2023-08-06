#!/usr/bin/python3
import os
import time
import sys
import os.path
import re
import logging 
import traceback
import docker
import uuid
import socket
from logging import Formatter
from flask import Flask, request, Response, redirect, render_template, abort, make_response, send_from_directory
from jinja2.exceptions import TemplateSyntaxError, UndefinedError
from urllib.parse import urlparse

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', int(port))) == 0

# Get environment variables.
env_containername = os.getenv('CONTAINER_NAME', "CargoDeck")
# Below ensured by startup.sh
env_version = os.getenv("CARGODECK_VERSION", "Unknown")
# Below are ensured by Loader.py
env_instance = int(os.getenv("CARGODECK_INSTANCE", 1))          
env_port = os.getenv("PORT", 80)
env_match = os.getenv("MATCH", env_containername)

# Initialize Flask with template folder path set to that of the location of the python file
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(current_dir, 'templates'))
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure log format
env_loglevel = os.environ.get("LOGLEVEL", "INFO")                # Env Args, defaults to INFO.
gunicorn_logger = logging.getLogger('gunicorn.error')
gunicorn_logger.setLevel(logging.WARNING)  # Set log level for Gunicorn
gunicorn_logger.handlers = [logging.StreamHandler()]  # Output logs to stdout
gunicorn_logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s +0000] [%(process)d] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
LOGLEVELS = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
app.logger.setLevel(LOGLEVELS.get(env_loglevel, logging.INFO))  # Set log level for Flask app's logs
app.logger.handlers = gunicorn_logger.handlers  # Use Gunicorn's log handlers
app.logger.propagate = False  # Prevent duplicated logs

app.logger.info(f"----> CargoDeck instance '{env_instance} [{os.getpid()}]', running as '{env_containername}', on port '{env_port}', matching '{env_match}'")


def is_numeric_and_greater_than(s, value):
    try:
        val = int(s)      # Try to convert the string to an int, catch error.
        return val > value
    except ValueError:
        return False

        
last_update = None
labels_cache = {}
siteinfo_cache = {}
def update_labels():
    global last_update, labels_cache, siteinfo_cache
    
    if last_update is None or (time.time() - last_update) > 15: # Seconds between label cache updates.
        app.logger.debug(f"{last_update} -> Rescan Docker labels")
        client = docker.from_env()
        labels = {}
        siteinfo = {}
        siteinfo["version"] = env_version
        
        for container in sorted(client.containers.list(), key=lambda c: c.name): # Alpha sort.
            container_labels = container.labels

            for label, value in container_labels.items():
                if not label.startswith(env_match+'.'):
                    continue
                parts = label.split('.')

                app.logger.debug(f"Label found: {label}, parts: {parts}")

                # First, parse the labels key.
                # Ignoring the instance match, each label entry must be parset to these 
                #    three setments: section_name, container_name and detail
                partsCount = len(parts)
                if partsCount == 2:     # instance-match.detail=value                             0, 1
                    section_name = 'index'  #default name for un-sectioned entries.
                    container_name = container.name
                    detail = parts[1]
                elif partsCount == 3:   # instance-match.directoryName.detail                     0, 1, 2
                    section_name = parts[1]
                    container_name = container.name
                    detail = parts[2]
                elif partsCount == 4:   # instance-match.directoryName.containerName.detail       0, 1, 2, 3
                    section_name = parts[1]
                    container_name = parts[2]
                    detail = parts[3]
                else:
                    app.logger.warning(f"Malformed label with {len(parts)} parts: {label}")
                    continue

                # Keys are always matched in lower-cases.
                detail = detail.lower()

                # Second, set the labels value part as needed
                if detail in ('site_name',                  'site_icon',
                              'display_right',              'site_image',
                              'site_footer_text',           'site_default_card_icon',
                              'site_missing_card_text',     'site_missing_card_icon',  
                              'site_wrong_section_text',    'site_wrong_section_icon', 
                              'site_expected_section_text', 'site_expected_section_icon', 
                              'site_auto_refresh',          'template_debug'
                              ):
                        
                    if detail == 'site_auto_refresh':
                        # Default to 30 if not numeris or less than 30
                        if not is_numeric_and_greater_than(value,30):
                            value = 30
                        
                    if detail not in siteinfo:
                        siteinfo[detail] = value
                    app.logger.debug(f"   siteinfo[{detail}] = {value}\n")
                    continue

                # Ensure Section exist.
                if section_name not in labels:
                    labels[section_name] = {}
                    
                # Extract Section details.
                if detail in ('section_name',       'section_expected_body',    'section_direct_link',
                              'section_header',     'section_header_icon',      'section_header_body', 
                              'section_footer',     'section_footer_icon',      'section_footer_body' 
                              ):
                    # section info.
                    if detail not in labels[section_name]:
                        labels[section_name][detail] = ""
                    if detail in ('section_expected_body',  'section_header_body',  'section_footer_body' 
                    ):
                        labels[section_name][detail] += value
                    else:
                        labels[section_name][detail] = value
                    app.logger.debug(f"   labels[{section_name}][{detail}] = {value}\n")
                    continue
                    
                # Extract entries info.
                elif detail in ('card_name',    'card_unique_id',   'card_note', 
                                'card_url',     'card_icon',        'card_image', 
                                'card_expected_name'):

                    if detail == 'card_expected_name':
                        # The expectation should create the card, it expects.
                        container_name = value
                                
                    if 'entries' not in labels[section_name]:
                        labels[section_name]['entries'] = {}
                    if container_name not in labels[section_name]['entries']:
                        labels[section_name]['entries'][container_name] = {}
                        labels[section_name]['entries'][container_name]['card_unique_id'] = str(uuid.uuid4())
                    labels[section_name]['entries'][container_name][detail] = value
                    app.logger.debug(f"   labels[{section_name}][{container_name}][entries][{detail}] = {value}\n")
                    continue
                else:
                    app.logger.warning(f"Unknown label detail '{detail}' in {label}")
                    continue
        # Save values to cache.
        last_update = time.time()
        labels_cache = labels
        siteinfo_cache = siteinfo
        
    return siteinfo_cache, labels_cache

@app.after_request
def log_request_response(response):
    response_status = response.status_code

    if response.status_code >= 400:
        app.logger.warning('Response: %s   Request: %s %s', response.status_code, request.method, request.url)
    else:
        app.logger.info('Response: %s   Request: %s %s', response.status_code, request.method, request.url)

    return response


@app.route('/<name>', methods=['GET'])
def get_labels(name):
    siteinfo, labels = update_labels();
    
    sanitized_name = re.sub(r'[^a-zA-Z0-9_]', '', name)  # Only allows letters, numbers and underscores

    # If no section is requested it remaps to index or the first section available.
    if sanitized_name == "":
        if "index" in labels:
            current_name = "index"
        else:
            current_name = next(iter(labels), "404")
            if current_name == "404":
                app.logger.error(f"No sections exist. Defaulting to Error")
                current_name = "Error"
    else:
        current_name = sanitized_name
        
    if current_name not in labels:
        app.logger.error(f"Section named '/{current_name}' does not exist.")
        #abort(404)
        
    # Check if template file exists and render the output.
    template_path = os.path.join(app.template_folder, 'CargoDeck.html')
    if not os.path.isfile(template_path):
        app.logger.error(f"Template file not found at {template_path}")
        abort(410)
    try:
        return render_template('CargoDeck.html', siteinfo=siteinfo, labels=labels, current_name=current_name)
    except (TemplateSyntaxError, UndefinedError) as e:
        app.logger.error("Template related error:")
        for line in traceback.format_exc().splitlines():
            if '%' in line or line.startswith('jinja2'):
                app.logger.error(line.strip())
        abort(404)
    except Exception as e:
        # For other exceptions, fall back to the default 404 error template
        app.logger.error(e)
        abort(404)

@app.route('/', methods=['GET'])
def index_html():
    return get_labels('')

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = env_port)
