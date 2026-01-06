from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import io
import socket
import traceback

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SshTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        host = tool_parameters.get('host')
        port = int(tool_parameters.get('port', 22))
        username = tool_parameters.get('username')
        auth_type = tool_parameters.get('auth_type')
        password = tool_parameters.get('password')
        private_key = tool_parameters.get('private_key')
        passphrase = tool_parameters.get('passphrase')
        command = tool_parameters.get('command')
        
        if not host or not username or not command:
            yield self.create_json_message({
                "error": "Missing required parameters: host, username, and command are required."
            })
            return
            
        if auth_type == 'password' and not password:
            yield self.create_json_message({
                "error": "Password is required for password authentication."
            })
            return
        elif auth_type == 'key' and not private_key:
            yield self.create_json_message({
                "error": "Private key is required for key authentication."
            })
            return
            
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if auth_type == 'password':
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            else:  # key authentication
                key_file = io.StringIO(private_key)
                password_arg = passphrase if passphrase else None
                pkey = None
                last_key_error: Exception | None = None

                key_classes: list[type] = []
                for key_cls_name in ("Ed25519Key", "ECDSAKey", "RSAKey", "DSSKey", "DSAKey"):
                    key_cls = getattr(paramiko, key_cls_name, None)
                    if key_cls is not None and key_cls not in key_classes:
                        key_classes.append(key_cls)

                for key_cls in key_classes:
                    key_file.seek(0)
                    try:
                        pkey = key_cls.from_private_key(key_file, password=password_arg)
                        break
                    except paramiko.PasswordRequiredException as e:
                        last_key_error = e
                        raise paramiko.SSHException("Passphrase is required for encrypted private key") from e
                    except Exception as e:
                        last_key_error = e
                        continue

                if pkey is None:
                    if last_key_error is not None:
                        raise paramiko.SSHException(f"Unsupported or invalid private key: {str(last_key_error)}") from last_key_error
                    raise paramiko.SSHException("Unsupported or invalid private key type")
                
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=pkey,
                    timeout=10
                )
                
            env_cmd = (
                'if [ -n "$ZSH_VERSION" ] && [ -f "$HOME/.zshrc" ]; then . "$HOME/.zshrc"; '
                'elif [ -n "$BASH_VERSION" ] && [ -f "$HOME/.bashrc" ]; then . "$HOME/.bashrc"; '
                'elif [ -f "$HOME/.profile" ]; then . "$HOME/.profile"; '
                'fi; '
                'export PATH="$PATH:/usr/local/bin"; '
                f'{command}'
            )

            stdin, stdout, stderr = client.exec_command(env_cmd)
            
            stdout_bytes = stdout.read()
            stderr_bytes = stderr.read()
            exit_status = stdout.channel.recv_exit_status()

            stdout_str = stdout_bytes.decode('utf-8', errors='replace')
            stderr_str = stderr_bytes.decode('utf-8', errors='replace')
            
            client.close()
            
            result = {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "exit_status": exit_status,
                "success": exit_status == 0
            }
            
            yield self.create_json_message(result)
            
        except paramiko.AuthenticationException as e:
            yield self.create_json_message({
                "error": "Authentication failed. Please check your credentials.",
                "detail": str(e),
                "exception_type": e.__class__.__name__,
                "success": False
            })
        except paramiko.SSHException as e:
            yield self.create_json_message({
                "error": f"SSH error: {str(e)}",
                "detail": str(e),
                "exception_type": e.__class__.__name__,
                "success": False
            })
        except socket.error as e:
            yield self.create_json_message({
                "error": f"Connection error: {str(e)}",
                "detail": str(e),
                "exception_type": e.__class__.__name__,
                "success": False
            })
        except Exception as e:
            yield self.create_json_message({
                "error": f"Error: {str(e)}",
                "detail": str(e),
                "exception_type": e.__class__.__name__,
                "traceback": traceback.format_exc(),
                "success": False
            })
