#!/usr/bin/env python3
"""
AWS SSM Parameter Store Mass Rename Script

This script allows you to:
1. Find all SSM parameters matching a pattern
2. Transform parameter names (e.g., supex/crm/* -> supex-crm/*)
3. Create new parameters with the same values
4. Optionally delete old parameters
5. Support dry-run mode with CSV output
"""

import boto3
import argparse
import sys
import csv
from botocore.exceptions import ClientError
import logging
from typing import List, Dict, Tuple


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ssm_client(profile: str, region: str) -> boto3.client:
    """Create and return an SSM client with the specified profile and region."""
    try:
        session = boto3.Session(profile_name=profile)
        return session.client('ssm', region_name=region)
    except Exception as e:
        logger.error(f"Error creating SSM client: {e}")
        sys.exit(1)


def get_parameters_by_path(ssm_client, path_prefix: str) -> List[Dict]:
    """Get all parameters that start with the given path prefix."""
    parameters = []
    paginator = ssm_client.get_paginator('get_parameters_by_path')
    
    try:
        for page in paginator.paginate(
            Path=path_prefix,
            Recursive=True,
            WithDecryption=True
        ):
            parameters.extend(page['Parameters'])
    except ClientError as e:
        logger.error(f"Error retrieving parameters: {e}")
        sys.exit(1)
    
    return parameters


def transform_parameter_name(old_name: str, old_pattern: str, new_pattern: str) -> str:
    """Transform parameter name based on pattern replacement."""
    # Replace the old pattern with the new pattern
    if old_pattern in old_name:
        return old_name.replace(old_pattern, new_pattern)
    else:
        logger.warning(f"Pattern '{old_pattern}' not found in '{old_name}'")
        return old_name


def get_parameter_details(ssm_client, param_name: str) -> Dict:
    """Get detailed information about a specific parameter."""
    try:
        response = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
        return response['Parameter']
    except ClientError as e:
        logger.error(f"Error retrieving parameter {param_name}: {e}")
        return None


def create_parameter(ssm_client, param_name: str, param_value: str, param_type: str, description: str = None, overwrite: bool = False) -> bool:
    """Create a new parameter in SSM Parameter Store."""
    try:
        params = {
            'Name': param_name,
            'Value': param_value,
            'Type': param_type,
            'Overwrite': overwrite
        }
        
        if description:
            params['Description'] = description
            
        ssm_client.put_parameter(**params)
        logger.info(f"Created parameter: {param_name}")
        return True
    except ClientError as e:
        logger.error(f"Error creating parameter {param_name}: {e}")
        return False


def delete_parameter(ssm_client, param_name: str) -> bool:
    """Delete a parameter from SSM Parameter Store."""
    try:
        ssm_client.delete_parameter(Name=param_name)
        logger.info(f"Deleted parameter: {param_name}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting parameter {param_name}: {e}")
        return False


def write_csv_report(filename: str, parameter_mappings: List[Tuple[str, str, str, str]]):
    """Write parameter mappings to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Old Name', 'New Name', 'Type', 'Value Preview'])
            
            for old_name, new_name, param_type, value_preview in parameter_mappings:
                # Truncate value for preview (first 50 chars)
                preview = value_preview[:50] + "..." if len(value_preview) > 50 else value_preview
                writer.writerow([old_name, new_name, param_type, preview])
        
        logger.info(f"CSV report written to: {filename}")
    except Exception as e:
        logger.error(f"Error writing CSV file: {e}")


def main():
    parser = argparse.ArgumentParser(description="Mass rename SSM Parameters with pattern replacement.")
    parser.add_argument('--profile', required=True, help='AWS CLI profile name')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--old-pattern', required=True, help='Old pattern to replace (e.g., "supex/crm")')
    parser.add_argument('--new-pattern', required=True, help='New pattern to use (e.g., "supex-crm")')
    parser.add_argument('--path-prefix', help='Path prefix to search for parameters (defaults to old-pattern)')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run and generate CSV report')
    parser.add_argument('--csv-file', default='parameter_rename_report.csv', help='CSV file name for dry run report')
    parser.add_argument('--delete-old', action='store_true', help='Delete old parameters after creating new ones')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing parameters')
    parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Use old-pattern as path-prefix if not specified
    path_prefix = args.path_prefix if args.path_prefix else args.old_pattern
    
    # Ensure path starts with /
    if not path_prefix.startswith('/'):
        path_prefix = '/' + path_prefix
    
    logger.info(f"Searching for parameters with prefix: {path_prefix}")
    logger.info(f"Pattern transformation: '{args.old_pattern}' -> '{args.new_pattern}'")
    
    # Create SSM client
    ssm_client = get_ssm_client(args.profile, args.region)
    
    # Get all parameters matching the path prefix
    parameters = get_parameters_by_path(ssm_client, path_prefix)
    
    if not parameters:
        logger.info("No parameters found matching the specified path prefix.")
        return
    
    logger.info(f"Found {len(parameters)} parameters to process")
    
    # Process parameters and create mappings
    parameter_mappings = []
    
    for param in parameters:
        old_name = param['Name']
        new_name = transform_parameter_name(old_name, args.old_pattern, args.new_pattern)
        
        # Skip if transformation didn't change the name
        if old_name == new_name:
            logger.warning(f"Skipping {old_name} - no transformation applied")
            continue
            
        parameter_mappings.append((
            old_name,
            new_name,
            param['Type'],
            param['Value']
        ))
    
    if not parameter_mappings:
        logger.info("No parameters would be transformed with the given pattern.")
        return
    
    # Dry run mode
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        write_csv_report(args.csv_file, parameter_mappings)
        
        print("\nParameter Transformation Preview:")
        print("-" * 80)
        for old_name, new_name, param_type, _ in parameter_mappings:
            print(f"{old_name} -> {new_name} ({param_type})")
        
        logger.info(f"Dry run complete. Report saved to {args.csv_file}")
        return
    
    # Confirmation prompt
    if not args.confirm:
        print(f"\nAbout to process {len(parameter_mappings)} parameters:")
        for old_name, new_name, param_type, _ in parameter_mappings[:5]:  # Show first 5
            print(f"  {old_name} -> {new_name} ({param_type})")
        
        if len(parameter_mappings) > 5:
            print(f"  ... and {len(parameter_mappings) - 5} more")
        
        if args.delete_old:
            print("\nWARNING: Old parameters will be DELETED after new ones are created!")
        
        response = input("\nProceed? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            logger.info("Operation cancelled by user")
            return
    
    # Create new parameters
    success_count = 0
    created_parameters = []
    
    for old_name, new_name, param_type, param_value in parameter_mappings:
        # Get full parameter details for description, etc.
        param_details = get_parameter_details(ssm_client, old_name)
        if not param_details:
            continue
            
        description = param_details.get('Description', '')
        
        if create_parameter(ssm_client, new_name, param_value, param_type, description, args.overwrite):
            success_count += 1
            created_parameters.append((old_name, new_name))
    
    logger.info(f"Successfully created {success_count}/{len(parameter_mappings)} new parameters")
    
    # Delete old parameters if requested
    if args.delete_old and created_parameters:
        if not args.confirm:
            response = input(f"\nDelete {len(created_parameters)} old parameters? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                logger.info("Deletion cancelled by user")
                return
        
        deleted_count = 0
        for old_name, new_name in created_parameters:
            if delete_parameter(ssm_client, old_name):
                deleted_count += 1
        
        logger.info(f"Successfully deleted {deleted_count}/{len(created_parameters)} old parameters")
    
    logger.info("Operation completed successfully")


if __name__ == "__main__":
    main()