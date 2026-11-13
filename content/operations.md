# Operations guide

## Health checks

The status check should complete within the configured timeout and report a non-zero exit code when the service cannot be verified.

## Configuration

Monitoring settings are stored separately from credentials. Secrets are supplied through environment variables and are not committed to Git.
