# Make sure to configure your AWS credentials and Azure authentication properly before running this script.
# This script transfers secrets from Azure Key Vault to AWS SSM Parameter Store.
# This script takes the following parameters:
# - az_key_vault_name: The name of the Azure Key Vault.
# - aws_ssm_param_prefix: The name of the AWS SSM parameter prefix for the secrets.
# - aws_profile_name: The AWS profile name to use for authentication.
# - dry_run: If set, the script will not perform any actual migration but will output the secrets that would be migrated.


import argparse
import boto3 as boto3
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from botocore.exceptions import ClientError

def get_azure_secrets(azure_vault_url):
    """
    Retrieve secrets from Azure Key Vault.
    
    :param azure_vault_url: URL of the Azure Key Vault
    :return: Dictionary of secret names and their values
    """
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=azure_vault_url, credential=credential, verify_challenge_resource=False)
    
    secrets = {}
    for secret in client.list_properties_of_secrets():
        secret_name = secret.name
        secret_value = client.get_secret(secret_name).value
        secrets[secret_name] = secret_value
    
    print(f"Retrieved {len(secrets)} secrets from Azure Key Vault")
    return secrets


def put_ssm_parameter(secret_name, value, aws_ssm_param_prefix=None, aws_profile_name=None):
    """
    Store a secret in AWS SSM Parameter Store.
    
    :param ssm_client: Boto3 SSM client
    :param secret_name: Name of the secret
    :param value: Value of the SSM parameter
    """
    session = boto3.session.Session(aws_profile=aws_profile_name)
    ssm_client = session.client('ssm')
    ssm_param_name = f"{aws_ssm_param_prefix}/{secret_name}"

    # Ensure parameter name starts with '/' for fully qualified name
    if aws_ssm_param_prefix:
        ssm_param_name = f"{aws_ssm_param_prefix}/{secret_name}"
    else:
        ssm_param_name = f"/{secret_name}"

    # Remove double slashes if they exist
    ssm_param_name = ssm_param_name.replace('//', '/')

    try:
        ssm_client.put_parameter(
            Name=ssm_param_name,
            Value=value,
            Type='SecureString',
            Overwrite=True
        )
        print(f"Stored {secret_name} in AWS SSM Parameter Store")
    except ClientError as e:
        print(f"Failed to store {secret_name} in AWS SSM Parameter Store: {e}")


def main(az_key_vault_name = None, aws_ssm_param_prefix=None, aws_profile_name=None, dry_run=False):
    """
    Main function to transfer secrets from Azure Key Vault to AWS SSM Parameter Store.
    """
    if not az_key_vault_name:
        print("Azure Key Vault name is required.")
        return

    key_vault_url = f"https://{az_key_vault_name}.vault.azure.net/"
        
    secrets = get_azure_secrets(key_vault_url)

    if dry_run:
        print(f"DRY RUN MODE: No actual migration will occur.")
        print(f"\nFound {len(secrets)} secrets to migrate from Azure Key Vault:")
        print("-" * 80)
        print("Creating CSV output for dry run:")
        with open('migration_output.csv', 'w') as f:
            f.write("Secret Name,SSM Param name,Value\n")
            for secret_name, value in secrets.items():
                f.write(f"{secret_name},{aws_ssm_param_prefix}/{secret_name},{value}\n")
    else:
        print(f"\nFound {len(secrets)} secrets to migrate from Azure Key Vault:")
        print("-" * 80)
        print("Migrating secrets to AWS SSM Parameter Store:")
        for secret_name, value in secrets.items():
            put_ssm_parameter(secret_name, value, aws_ssm_param_prefix, aws_profile_name)
    print("Migration completed.")


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='Migrate secrets from Azure Key Vault to AWS SSM Parameter Store.'
                    epilog="""
Examples:
  python az_secrets_to_ssm_param.py my-vault
  python az_secrets_to_ssm_param.py my-vault --prefix /myapp/secrets
  python az_secrets_to_ssm_param.py my-vault --prefix /myapp/secrets --aws-profile production
  python az_secrets_to_ssm_param.py my-vault --prefix /myapp/secrets --dry-run
        """)
    

    parser.add_argument('az_key_vault_name', type=str, help='Name of the Azure Key Vault (without .vault.azure.net suffix)')
    parser.add_argument('--aws_ssm_param_prefix', type=str, default=None, help='Prefix for AWS SSM parameters (optional) (e.g., /myapp/secrets)')
    parser.add_argument('--aws_profile_name', type=str, default=None, help='AWS profile name for authentication')
    parser.add_argument('--dry-run', action='store_true', help='If set, will not perform actual migration but output the secrets that would be migrated to CSV')

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    main(az_key_vault_name=args.az_key_vault_name, aws_ssm_param_prefix=args.aws_ssm_param_prefix, aws_profile_name=args.aws_profile_name, dry_run=args.dry_run)
    print("Script executed successfully.")