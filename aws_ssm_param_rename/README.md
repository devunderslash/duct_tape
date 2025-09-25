# AWS SSM Parameter Mass Rename Script

A Python script for bulk renaming AWS Systems Manager (SSM) Parameter Store parameters with pattern-based transformations.

## Features

- **Pattern-based renaming**: Transform parameter names using find/replace patterns
- **Dry-run mode**: Preview changes and generate CSV reports before executing
- **Safe operation**: Built-in confirmation prompts and error handling  
- **Flexible options**: Choose to overwrite existing parameters and delete old ones
- **Comprehensive logging**: Detailed operation tracking and error reporting

## Prerequisites

- Python 3.6+
- AWS CLI configured with appropriate profiles
- Required permissions for SSM Parameter Store operations:
  - `ssm:GetParameter`
  - `ssm:GetParameters`
  - `ssm:GetParametersByPath`
  - `ssm:PutParameter`
  - `ssm:DeleteParameter` (if using `--delete-old`)

## Installation

No additional packages required beyond AWS SDK:

```bash
pip install boto3
```

## Usage

### Basic Syntax

```bash
python ssm_param_mass_rename.py --profile <AWS_PROFILE> --region <AWS_REGION> --old-pattern <OLD_PATTERN> --new-pattern <NEW_PATTERN> [OPTIONS]
```

### Required Arguments

- `--profile`: AWS CLI profile name
- `--region`: AWS region (e.g., us-east-1)
- `--old-pattern`: Pattern to find in parameter names
- `--new-pattern`: Replacement pattern

### Optional Arguments

- `--path-prefix`: Path prefix to search (defaults to old-pattern)
- `--dry-run`: Preview changes without making them
- `--csv-file`: CSV filename for dry-run report (default: parameter_rename_report.csv)
- `--delete-old`: Delete old parameters after creating new ones
- `--overwrite`: Overwrite existing parameters with same names
- `--confirm`: Skip confirmation prompts

## Examples

### 1. Dry Run (Recommended First Step)

Preview parameter transformations without making changes:

```bash
python ssm_param_mass_rename.py \
  --profile production \
  --region us-east-1 \
  --old-pattern "regular/crm" \
  --new-pattern "regular-crm" \
  --dry-run
```

This generates a CSV report showing all proposed changes.

### 2. Basic Rename Operation

Rename parameters from `regular/crm/*` to `regular-crm/*`:

```bash
python ssm_param_mass_rename.py \
  --profile production \
  --region us-east-1 \
  --old-pattern "regular/crm" \
  --new-pattern "regular-crm"
```

### 3. Rename with Old Parameter Cleanup

Create new parameters and delete old ones:

```bash
python ssm_param_mass_rename.py \
  --profile production \
  --region us-east-1 \
  --old-pattern "regular/crm" \
  --new-pattern "regular-crm" \
  --delete-old
```

### 4. Automated Operation (No Prompts)

Skip all confirmation prompts:

```bash
python ssm_param_mass_rename.py \
  --profile production \
  --region us-east-1 \
  --old-pattern "regular/crm" \
  --new-pattern "regular-crm" \
  --delete-old \
  --confirm
```

### 5. Custom Search Path

Search in a specific path different from the old pattern:

```bash
python ssm_param_mass_rename.py \
  --profile production \
  --region us-east-1 \
  --old-pattern "crm" \
  --new-pattern "customer-management" \
  --path-prefix "/application/regular"
```

## How It Works

1. **Parameter Discovery**: Searches SSM Parameter Store using the specified path prefix
2. **Name Transformation**: Applies pattern replacement to each parameter name
3. **Validation**: Checks for conflicts and validates transformations
4. **Parameter Creation**: Creates new parameters with transformed names
5. **Optional Cleanup**: Deletes old parameters if requested

## Safety Features

- **Dry-run mode**: Always test your pattern first
- **Confirmation prompts**: Manual approval before destructive operations
- **Error handling**: Graceful failure handling with detailed logging
- **Value preservation**: Maintains parameter values, types, and descriptions
- **Conflict detection**: Warns about existing parameters that would be overwritten

## Output Files

### CSV Report (Dry-run)
Contains columns:
- **Old Name**: Original parameter name
- **New Name**: Transformed parameter name  
- **Type**: Parameter type (String, StringList, SecureString)
- **Value Preview**: First 50 characters of parameter value

## Common Use Cases

1. **Namespace Migration**: Moving parameters from one namespace to another
2. **Naming Convention Updates**: Changing delimiter styles (/ to -, etc.)
3. **Application Refactoring**: Renaming parameters after code changes
4. **Environment Consolidation**: Restructuring parameter hierarchies

## Troubleshooting

### Permission Errors
Ensure your AWS profile has the necessary SSM permissions listed in Prerequisites.

### No Parameters Found
- Verify the path prefix exists and contains parameters
- Check that parameters are in the specified AWS region
- Ensure the AWS profile can access the parameters

### Pattern Not Matching
- Use `--dry-run` to verify pattern matching
- Check that the old pattern exists in parameter names
- Remember patterns are case-sensitive

### Parameter Already Exists
- Use `--overwrite` to replace existing parameters
- Or modify your pattern to avoid conflicts

## Best Practices

1. **Always dry-run first**: Use `--dry-run` to preview changes
2. **Test with small batches**: Start with a limited scope
3. **Backup critical parameters**: Consider manual backups before bulk operations
4. **Use descriptive patterns**: Make transformations clear and predictable
5. **Monitor logs**: Check output for any errors or warnings