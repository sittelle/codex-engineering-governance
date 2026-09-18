// One deliberate trigger per capability rule in semgrep/capabilities/typescript.yml.
// Used by scripts/test-registration-conformance.py to confirm each rule still
// fires (recall). Not runnable application code.

import axios from "axios";
import * as child_process from "child_process";
import * as fs from "fs";
import jwt from "jsonwebtoken";
import nodemailer from "nodemailer";
import { S3Client } from "@aws-sdk/client-s3";
import { PrismaClient } from "@prisma/client";

function networkConnectionsExample() {
  return axios.get("https://example.invalid/api");
}

function persistenceExample() {
  return new PrismaClient();
}

function authenticationExample(payload: object) {
  return jwt.sign(payload, "secret");
}

function elevatedAccessExample() {
  return child_process.exec("echo hello");
}

function writeOrDeleteActionsExample(path: string) {
  fs.rmSync(path, { recursive: true, force: true });
}

function cloudExample() {
  return new S3Client({});
}

function externalRecipientsExample() {
  return nodemailer.createTransport({ host: "smtp.example.invalid" });
}
