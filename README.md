## Installation

1. Install required libraries:
   ```sh
   pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

2. Set up OAuth Credentials

    i.      Go to the [Google Cloud Console](https://console.cloud.google.com) and create a new project(https://console.cloud.google.com/projectcreate).

    ii.    [Enable](https://console.cloud.google.com/marketplace/product/google/gmail.googleapis.com) the Gmail API.

    iii.    Set up OAuth2.0 credentials and download the credentials.json file - [OAuth Consent](https://console.cloud.google.com/apis/credentials/consent): Scope - `gmail.readonly`; Test users: `Add tester email address`, [Credentials](https://console.cloud.google.com/apis/credentials/oauthclient): Authorized redirect URIs - `https://developers.google.com/oauthplayground`
