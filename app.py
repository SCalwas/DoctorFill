# DoctorFill
#
# A GitHub App that keeps AWS SDK repos healthy and happy.

########################################
# Imports

import hashlib
import hmac
import json
import logging
import os

from flask import Flask, request, jsonify
import github                     # PyGitHub

########################################
# Global variables

DRFILL_VERSION = 'v0.10'

LOG_LEVEL = logging.DEBUG  # Set to logging.INFO in production version

CREDENTIALS_FILE = 'github_app_credentials'
CREDENTIALS_KEYS = ['ID', 'WEBHOOK_SECRET', 'PRIVATE_KEY_FILE']
credentials = {}

FILE_EXTENSIONS = ['.cpp',
                   '.cs',
                   '.go',
                   '.java',
                   '.js',
                   '.json',
                   '.php',
                   '.py',
                   '.rb',
                   '.ts']

app = Flask(__name__)
gh_integration = None


########################################
def get_installation_access_token(installation_id):
    """Get an installation access token so GitHub client can call GitHub API

    :param installation_id: integer ID of installation
    :return: string access token
    """
    global gh_integration

    return gh_integration.get_access_token(installation_id).token


########################################
@app.route('/', methods=['POST'])
def sdk_docs_github_app():
    """Root URL POST handler

    All GitHub requests/notifications are received through this entry point.
    """

    global credentials, gh_integration

    GITHUB_SIGNATURE_HEADER = 'x-hub-signature'
    GITHUB_EVENT_HEADER = 'x-github-event'

    logging.info('Received POST / request')

    # Verify this request was sent by GitHub
    # Extract GitHub digest from request header
    if GITHUB_SIGNATURE_HEADER not in request.headers:
        logging.critical('Unknown sender')
        return jsonify('Bad Request'), 400
    github_signature_header = request.headers[GITHUB_SIGNATURE_HEADER]  # Alt: request.environ['HTTP_X_HUB_SIGNATURE']
    parsed_signature = github_signature_header.split('=', maxsplit=1)
    algorithm = parsed_signature[0]
    if algorithm not in hashlib.algorithms_available:
        logging.critical('Unknown signature hash algorithm: %s', algorithm)
        return jsonify('Bad Request'), 400
    github_digest = bytes(parsed_signature[1], 'UTF-8')

    # Calculate received digest
    hl = hmac.new(credentials['WEBHOOK_SECRET_BYTES'], request.get_data(), algorithm)
    drfill_digest = bytes(hl.hexdigest(), 'UTF-8')

    logging.debug('GitHub digest: %s', github_digest)
    logging.debug('DrFill digest: %s', drfill_digest)

    # Digests must match
    if not hmac.compare_digest(github_digest, drfill_digest):
        logging.critical('Could not verify request originated from GitHub')
        return jsonify('Bad Request'), 400

    # Extract the GitHub event
    if GITHUB_EVENT_HEADER not in request.headers:
        logging.critical('Missing event type')
        return jsonify('Bad Request'), 400
    event_type = request.headers[GITHUB_EVENT_HEADER]  # Alt: request.environ['HTTP_X_GITHUB_EVENT']
    payload = request.get_json()    # GitHub always sends JSON, otherwise call request.get_data()
    logging.info('GitHub event notification: %s', event_type)
    if event_type != 'push':        # push events don't have an 'action' key
        logging.info('Event action: %s', payload['action'])

    # Is this an event we want to process?
    if event_type == 'push':
        github_client = github.Github(get_installation_access_token(payload['installation']['id']))
        # Note: This GitHub client/access token expires in one hour.

        # Cycle through each commit
        for commit in payload['commits']:
            for filename in commit['added']:
                # Process only source code files
                _, ext = os.path.splitext(filename.lower())
                if ext not in FILE_EXTENSIONS:
                    continue

                logging.info('Processing file: %s', filename)
                # Retrieve file contents
                repo = github_client.get_repo(payload['repository']['full_name'])
                try:
                    response = repo.get_file_contents(filename, ref=payload['ref'])
                except Exception as e:
                    logging.critical('Could not get contents of file %s', payload['ref'])
                    logging.critical(e)
                    continue
                contents = response.decoded_content     # contents are of type bytes

                ### Pass to linter ###
                # updated = add_your_function_here(contents)

                # Append test line
                contents += b'\nDoctor Fill prescribes one tall, cold line of text.\n'
                updated = True

                if updated:
                    # Commit modified file contents
                    try:
                        response_update = repo.update_file(path=response.path,
                                                           message='Doctor Fill updated {}'.format(response.path),
                                                           content=contents,
                                                           sha=response.sha,
                                                           branch=payload['ref'])
                    except Exception as e:
                        logging.critical('Could not commit modified file %s', response.path)
                        logging.critical(e)
                        continue
                    logging.info('Updated %s', response.path)

    # Add a label to a new issue.
    # Can be used to verify the app is installed and working.
    # Disable in production by not subscribing to Issues events.
    elif event_type == 'issues':
        github_client = github.Github(get_installation_access_token(payload['installation']['id']))

        if payload['action'] == 'opened':
            repo = github_client.get_repo(payload['repository']['full_name'])
            issue = repo.get_issue(payload['issue']['number'])
            try:
                issue.add_to_labels('enhancement')
            except Exception as e:
                logging.critical('Could not add "enhancement" label to issue')
                logging.critical(e)
            else:
                logging.info('Added label "enhancement" to issue #%d', payload['issue']['number'])

    return jsonify('OK'), 200


########################################
def load_github_app_credentials():
    """Load the app's GitHub App credentials

    Credentials are stored in the following files:
        -- File referenced by global variable CREDENTIALS_FILE
        -- File referenced by CREDENTIALS_FILE['PRIVATE_KEY_FILE']

    Credentials (except for the file referenced by PRIVATE_KEY_FILE) can alternatively be stored in env variables.

    :return True if credentials are loaded, otherwise False.
    """

    global CREDENTIALS_FILE, CREDENTIALS_KEYS, credentials

    try:
        with open(CREDENTIALS_FILE) as cf:
            credentials = json.load(cf)
    except IOError as e:
        logging.critical(e)
        return False

    # Validate that all credential keys were specified
    for key in CREDENTIALS_KEYS:
        if key not in credentials:
            logging.critical('Missing key in credentials file: %s', key)
            return False

    # Store bytes version of WEBHOOK_SECRETS
    credentials['WEBHOOK_SECRET_BYTES'] = bytes(credentials['WEBHOOK_SECRET'], 'UTF-8')

    # Read private key and add to credentials
    try:
        with open(credentials['PRIVATE_KEY_FILE']) as pkf:
            credentials['PRIVATE_KEY'] = pkf.read()
    except IOError as e:
        logging.critical(e)
        return False
    logging.info('Loaded GitHub credentials')
    return True


########################################
def main():
    """Program entry point
    """

    global LOG_LEVEL, gh_integration

    logging.basicConfig(level=LOG_LEVEL,
                        # filename='drFillLog.txt',
                        format='%(asctime)s: %(levelname)s: %(message)s'
                        )
    logging.info('Doctor Fill %s', DRFILL_VERSION)

    if not load_github_app_credentials():
        exit(-1)

    # Create a GithubIntegration object
    gh_integration = github.GithubIntegration(credentials['ID'], credentials['PRIVATE_KEY'])
    logging.info('Waiting for GitHub notifications...')


########################################
if __name__ == 'app':           # Enables debugging in PyCharm
    main()
elif __name__ == '__main__':    # Enables running from command line
    main()
    app.run(port=3000)
