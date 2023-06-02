"use strict";

/**
 * Spin up development server.
 */

const childProcess = require("child_process");
const concurrently = require("concurrently");
const crypto = require("crypto");
const path = require("path");

const resetToken = crypto.randomBytes(32).toString("hex");
const smtpPassword = crypto.randomBytes(16).toString("hex");
const smtpUsername = "admin@acronyms.127-0-0-1.nip.io";
const verificationToken = crypto.randomBytes(32).toString("hex");

// Ensure that Javascript assests are available when backend first starts.
childProcess.execSync("npx vite build --mode development", {
  stdio: "inherit",
});

concurrently(
  [
    {
      command: "poetry run acronyms --reload --reload-dir src/acronyms",
      env: {
        ACRONYMS_RESET_TOKEN: resetToken,
        ACRONYMS_SMTP_HOST: "localhost",
        ACRONYMS_SMTP_PASSWORD: smtpPassword,
        ACRONYMS_SMTP_PORT: "1025",
        ACRONYMS_SMTP_TLS: "false",
        ACRONYMS_SMTP_USERNAME: smtpUsername,
        ACRONYMS_VERIFICATION_TOKEN: verificationToken,
      },
      name: "backend",
    },
    {
      command: `maildev --incoming-user ${smtpUsername} --incoming-pass ${smtpPassword}`,
      name: "email",
    },
    { command: "vite build --watch --mode development", name: "frontend" },
  ],
  {
    cwd: path.resolve(__dirname, ".."),
    killOthers: ["failure", "success"],
    restartTries: 3,
  }
);
