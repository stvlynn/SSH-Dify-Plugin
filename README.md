# SSH Command Execution Plugin

**Author:** [Steven Lynn](https://github.com/stvlynn)
**Version:** 0.0.1
**Type:** tool

## Description

The SSH Command Execution Plugin allows users to execute commands on remote servers via SSH protocol and transfer files to/from remote servers. It supports both password and private key authentication methods.
![](./_assets/image.png)

> Don't know where to start? Try this [DSL Template](https://raw.githubusercontent.com/stvlynn/SSH-Dify-Plugin/refs/heads/main/example.yml) !

## Features

- Supports password and private key authentication
- Executes remote commands and returns standard output and standard error
- Uploads files to remote servers
- Downloads files from remote servers
- Securely handles connection and authentication errors

## Tools

### 1. SSH Command Execution

Execute commands on remote servers via SSH.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| host | string | Yes | Hostname or IP address of the remote server |
| port | number | Yes | SSH port, default is 22 |
| username | string | Yes | Username for authentication |
| auth_type | select | Yes | Authentication type: password or key |
| password | string | Conditional | Password for password authentication (required if auth_type is password) |
| private_key | string | Conditional | Private key content for key authentication (required if auth_type is key) |
| passphrase | string | No | Passphrase for the private key (if the key is encrypted) |
| command | string | Yes | Command to execute on the remote server |

#### Return Values

When the plugin executes successfully, it returns data in the following JSON format:

```json
{
  "stdout": "Command standard output",
  "stderr": "Command standard error",
  "success": true
}
```

When execution fails, it returns an error message:

```json
{
  "error": "Error description",
  "success": false
}
```

### 2. SSH File Upload

Upload files to remote servers via SSH.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| host | string | Yes | Hostname or IP address of the remote server |
| port | number | Yes | SSH port, default is 22 |
| username | string | Yes | Username for authentication |
| auth_type | select | Yes | Authentication type: password or key |
| password | string | Conditional | Password for password authentication (required if auth_type is password) |
| private_key | string | Conditional | Private key content for key authentication (required if auth_type is key) |
| passphrase | string | No | Passphrase for the private key (if the key is encrypted) |
| remote_path | string | Yes | Path on the remote server where the file will be uploaded |
| files | files | Yes | Files to upload to the remote server |

#### Return Values

When the plugin executes successfully, it returns data in the following JSON format:

```json
{
  "success": true,
  "total_files": 2,
  "successful_uploads": 2,
  "results": [
    {
      "filename": "example1.txt",
      "remote_path": "/path/to/example1.txt",
      "size": 1024,
      "status": "success"
    },
    {
      "filename": "example2.txt",
      "remote_path": "/path/to/example2.txt",
      "size": 2048,
      "status": "success"
    }
  ]
}
```

### 3. SSH File Download

Download files from remote servers via SSH.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| host | string | Yes | Hostname or IP address of the remote server |
| port | number | Yes | SSH port, default is 22 |
| username | string | Yes | Username for authentication |
| auth_type | select | Yes | Authentication type: password or key |
| password | string | Conditional | Password for password authentication (required if auth_type is password) |
| private_key | string | Conditional | Private key content for key authentication (required if auth_type is key) |
| passphrase | string | No | Passphrase for the private key (if the key is encrypted) |
| remote_path | string | Yes | Path on the remote server of the file to download |

#### Return Values

When the plugin executes successfully, it returns the file as a blob and data in the following JSON format:

```json
{
  "success": true,
  "filename": "example.txt",
  "remote_path": "/path/to/example.txt",
  "size": 1024,
  "mime_type": "text/plain"
}
```

## Usage Examples

### Using Password Authentication

```json
{
  "host": "example.com",
  "port": 22,
  "username": "user",
  "auth_type": "password",
  "password": "your_password",
  "command": "ls -la"
}
```

### Using Private Key Authentication

```json
{
  "host": "example.com",
  "port": 22,
  "username": "user",
  "auth_type": "key",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----",
  "command": "ls -la"
}
```

### Real Example (Sanitized)

#### Input:
```json
{
  "private_key": "",
  "passphrase": "",
  "host": "156.22************52",
  "port": "22",
  "username": "root",
  "auth_type": "password",
  "password": "TUIFfl************87",
  "command": "neofetch"
}
```

#### Output:
```json
{
  "text": "",
  "files": [],
  "json": [
    {
      "stderr": "",
      "stdout": "\u001b[?25l\u001b[?7l\u001b[37m\u001b[0m\u001b[1m       _,met$$$$$gg.\n    ,g$$$$$$$$$$$$$$$P.\n  ,g$$P\"     \"\"\"Y$$.\".\n ,$$P'              `$$$.\n',$$P       ,ggs.     `$$b:\n`d$$'     ,$P\"'   \u001b[0m\u001b[31m\u001b[1m.\u001b[37m\u001b[0m\u001b[1m    $$$\n $$P      d$'     \u001b[0m\u001b[31m\u001b[1m,\u001b[37m\u001b[0m\u001b[1m    $$P\n $$:      $$.   \u001b[0m\u001b[31m\u001b[1m-\u001b[37m\u001b[0m\u001b[1m    ,d$$'\n $$;      Y$b._   _,d$P'\n Y$$.    \u001b[0m\u001b[31m\u001b[1m`.\u001b[37m\u001b[0m\u001b[1m`\"Y$$$$P\"'\n\u001b[37m\u001b[0m\u001b[1m `$$b      \u001b[0m\u001b[31m\u001b[1m\"-.__\n\u001b[37m\u001b[0m\u001b[1m  `Y$$\n   `Y$$.\n     `$$b.\n       `Y$$b.\n          `\"Y$b._\n              `\"\"\"\u001b[0m\n\u001b[17A\u001b[9999999D\u001b[30C\u001b[0m\u001b[1m\u001b[31m\u001b[1mroot\u001b[0m@\u001b[31m\u001b[1mde1-20250312144616b256f2\u001b[0m \n\u001b[30C\u001b[0m-----------------------------\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mOS\u001b[0m\u001b[0m:\u001b[0m Debian GNU/Linux 11 (bullseye) x86_64\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mHost\u001b[0m\u001b[0m:\u001b[0m KVM/QEMU (Standard PC (i440FX + PIIX, 1996) pc-i440fx-9.0)\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mKernel\u001b[0m\u001b[0m:\u001b[0m 5.10.0-26-cloud-amd64\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mUptime\u001b[0m\u001b[0m:\u001b[0m 33 mins\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mPackages\u001b[0m\u001b[0m:\u001b[0m 366 (dpkg)\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mShell\u001b[0m\u001b[0m:\u001b[0m bash 5.1.4\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mCPU\u001b[0m\u001b[0m:\u001b[0m Intel Xeon E5-2698 v4 (1) @ 2.197GHz\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mGPU\u001b[0m\u001b[0m:\u001b[0m 00:02.0 Vendor 1234 Device 1111\u001b[0m \n\u001b[30C\u001b[0m\u001b[31m\u001b[1mMemory\u001b[0m\u001b[0m:\u001b[0m 47MiB / 979MiB\u001b[0m \n\n\u001b[30C\u001b[30m\u001b[40m   \u001b[31m\u001b[41m   \u001b[32m\u001b[42m   \u001b[33m\u001b[43m   \u001b[34m\u001b[44m   \u001b[35m\u001b[45m   \u001b[36m\u001b[46m   \u001b[37m\u001b[47m   \u001b[m\n\u001b[30C\u001b[38;5;8m\u001b[48;5;8m   \u001b[38;5;9m\u001b[48;5;9m   \u001b[38;5;10m\u001b[48;5;10m   \u001b[38;5;11m\u001b[48;5;11m   \u001b[38;5;12m\u001b[48;5;12m   \u001b[38;5;13m\u001b[48;5;13m   \u001b[38;5;14m\u001b[48;5;14m   \u001b[38;5;15m\u001b[48;5;15m   \u001b[m\n\n\n\n\n\u001b[?25h\u001b[?7h",
      "success": true
    }
  ]
}
```

## Safety Tip

Keep your instance IP and password safe in **Environment Varriable -> secret**!

![](./_assets/environment.png)

## Input and Output Example

### Input:
```json
{
  "private_key": "",
  "passphrase": "",
  "host": "192.************1",
  "port": "22",
  "username": "root",
  "auth_type": "password",
  "password": "T************87",
  "command": "neofetch"
}
```

### Output:
```json
{
  "text": "",
  "files": [],
  "json": [
    {
      "stderr": "",
      "stdout": "***some output***",
      "success": true
    }
  ]
}
```

## Security Considerations

- Ensure you have permission to access the target server
- Sensitive information such as private keys and passwords should be kept secure
- Follow the principle of least privilege, granting only necessary execution permissions

## License

[MIT](./LICENSE)



