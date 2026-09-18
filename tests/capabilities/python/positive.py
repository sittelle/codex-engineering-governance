"""One deliberate trigger per capability rule in semgrep/capabilities/python.yml.
Used by scripts/test-registration-conformance.py to confirm each rule still
fires (recall). Not runnable application code.
"""
import boto3
import bcrypt
import smtplib
import subprocess
import sqlite3
import requests


def network_connections_example():
    requests.get("https://example.invalid/api")


def persistence_example():
    conn = sqlite3.connect("app.db")
    return conn


def authentication_example(password: bytes):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def elevated_access_example():
    subprocess.run(["echo", "hello"])


def write_or_delete_actions_example(path):
    import shutil
    shutil.rmtree(path)


def cloud_example():
    return boto3.client("s3")


def external_recipients_example():
    server = smtplib.SMTP("smtp.example.invalid")
    return server
