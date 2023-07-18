/**
 * Spin up development server.
 */

import childProcess from "child_process";
import concurrently from "concurrently";
import getPort from "get-port";
import crypto from "crypto";
import path from "path";
import { fileURLToPath } from "url";

const resetToken = crypto.randomBytes(32).toString("hex");
const smtpPassword = crypto.randomBytes(16).toString("hex");
const smtpUsername = "admin@acronyms.com";
const verificationToken = crypto.randomBytes(32).toString("hex");

// Ensure that Javascript assests are available when backend first starts.
childProcess.execSync("npx vite build --mode development", {
  stdio: "inherit",
});

const smtpPort = await getPort();
const smtpWebPort = await getPort();

concurrently(
  [
    {
      command: "poetry run acronyms --reload --reload-dir src/acronyms",
      env: {
        ACRONYMS_RESET_TOKEN: resetToken,
        ACRONYMS_SMTP_ENABLED: "true",
        ACRONYMS_SMTP_HOST: "localhost",
        ACRONYMS_SMTP_PASSWORD: smtpPassword,
        ACRONYMS_SMTP_PORT: String(smtpPort),
        ACRONYMS_SMTP_TLS: "false",
        ACRONYMS_SMTP_USERNAME: smtpUsername,
        ACRONYMS_VERIFICATION_TOKEN: verificationToken,
      },
      name: "backend",
    },
    {
      command: `maildev --incoming-user ${smtpUsername} --incoming-pass ${smtpPassword} --smtp ${smtpPort} --web ${smtpWebPort}`,
      name: "email",
    },
    { command: "vite build --watch --mode development", name: "frontend" },
  ],
  {
    cwd: path.resolve(fileURLToPath(import.meta.url), "../.."),
    killOthers: ["failure", "success"],
    restartTries: 3,
  }
);
