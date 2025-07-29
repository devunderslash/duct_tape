# Azure Key Vault to AWS SSM Parameter Store Migration Script

This script migrates secrets from Azure Key Vault to AWS SSM Parameter Store.

## Prerequisites

- Python 3.x
- Azure SDK for Python
- Boto3

## Prep Work

Before using this script, ensure you have the necessary permissions and configurations set up for Azure Key Vault and AWS SSM Parameter Store. This includes:
- Azure Key Vault access permissions
- AWS IAM permissions for SSM Parameter Store

Run the following to login to Azure then follow the terminal instructions:
```bash
az login --use-device-code
```

Test connection to Azure Key Vault:
```bash
az keyvault secret list --vault-name <vault-name>
```

The AWS connection assumes that you have your AWS credentials file set up wirth various account profiles. You can set up your AWS credentials by running:
```bash
aws configure --profile <aws-profile>
```

Test connection to AWS SSM Parameter Store:
```bash
aws ssm get-parameter --name <parameter-name> --profile <aws-profile>
```

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

## Usage (Python)

1. Setup a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ``` 
3. Run the script:
    ```bash
    python az_secrets_to_ssm_param.py <az_key_vault_name> [options]
    ```
4. Deactivate the virtual environment when done:
    ```bash
    deactivate
    ```

### Options

- `--aws_ssm_param_prefix`: Prefix for AWS SSM parameters (optional) (e.g., myapp/secrets)
- `--aws_profile_name`: AWS profile name for authentication
- `--dry-run`: If set, will not perform actual migration but output the secrets that would be migrated to CSV

## Example

```bash
python az_secrets_to_ssm_param.py my-vault --aws_ssm_param_prefix myapp/secrets --aws_profile_name production --dry-run
```

## Output
The script will output the secrets that would be migrated to a CSV file named `az_secrets_to_ssm_param_migration.csv` in the current directory. If the `--dry-run` option is not set, it will also migrate the secrets to AWS SSM Parameter Store.

