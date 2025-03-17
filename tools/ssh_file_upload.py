from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import io
import os
import socket
import traceback
import tempfile

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SshFileUploadTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 提取参数
        host = tool_parameters.get('host')
        port = int(tool_parameters.get('port', 22))
        username = tool_parameters.get('username')
        auth_type = tool_parameters.get('auth_type')
        password = tool_parameters.get('password')
        private_key = tool_parameters.get('private_key')
        passphrase = tool_parameters.get('passphrase')
        remote_path = tool_parameters.get('remote_path')
        files = tool_parameters.get('files', [])
        
        # 验证必要参数
        if not host or not username or not remote_path:
            yield self.create_json_message({
                "success": False,
                "error": "Missing required parameters: host, username, and remote_path are required."
            })
            return
            
        # 验证认证参数
        if auth_type == 'password' and not password:
            yield self.create_json_message({
                "success": False,
                "error": "Password is required for password authentication."
            })
            return
        elif auth_type == 'key' and not private_key:
            yield self.create_json_message({
                "success": False,
                "error": "Private key is required for key authentication."
            })
            return
        
        # 验证文件参数
        if not files or len(files) == 0:
            yield self.create_json_message({
                "success": False,
                "error": "No files provided for upload."
            })
            return
            
        try:
            # 创建SSH客户端
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 根据认证类型连接
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
                if passphrase:
                    pkey = paramiko.RSAKey.from_private_key(key_file, password=passphrase)
                else:
                    pkey = paramiko.RSAKey.from_private_key(key_file)
                
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=pkey,
                    timeout=10
                )
            
            # 创建SFTP客户端
            sftp = client.open_sftp()
            
            # 上传文件
            results = []
            for file in files:
                try:
                    # 获取文件名
                    filename = file.filename
                    
                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_file.write(file.blob)
                        temp_file_path = temp_file.name
                    
                    # 确定远程文件路径
                    remote_file_path = remote_path
                    if remote_path.endswith('/'):
                        remote_file_path = os.path.join(remote_path, filename)
                    
                    # 上传文件
                    sftp.put(temp_file_path, remote_file_path)
                    
                    # 删除临时文件
                    os.unlink(temp_file_path)
                    
                    # 添加结果
                    results.append({
                        "filename": filename,
                        "remote_path": remote_file_path,
                        "size": len(file.blob),
                        "status": "success"
                    })
                    
                except Exception as e:
                    results.append({
                        "filename": filename if 'filename' in locals() else "unknown",
                        "error": str(e),
                        "status": "failed"
                    })
            
            # 关闭连接
            sftp.close()
            client.close()
            
            # 返回结果
            success_count = sum(1 for r in results if r["status"] == "success")
            
            result = {
                "success": success_count > 0,
                "total_files": len(files),
                "successful_uploads": success_count,
                "results": results
            }
            
            yield self.create_json_message(result)
            
            # 创建文本消息
            if success_count == 0:
                yield self.create_text_message("Failed to upload any files.")
            elif success_count == len(files):
                yield self.create_text_message(f"Successfully uploaded all {success_count} files.")
            else:
                yield self.create_text_message(f"Uploaded {success_count} out of {len(files)} files.")
            
        except paramiko.AuthenticationException:
            yield self.create_json_message({
                "success": False,
                "error": "Authentication failed. Please check your credentials."
            })
        except paramiko.SSHException as e:
            yield self.create_json_message({
                "success": False,
                "error": f"SSH error: {str(e)}"
            })
        except socket.error as e:
            yield self.create_json_message({
                "success": False,
                "error": f"Connection error: {str(e)}"
            })
        except Exception as e:
            yield self.create_json_message({
                "success": False,
                "error": f"Error: {str(e)}",
                "traceback": traceback.format_exc()
            }) 