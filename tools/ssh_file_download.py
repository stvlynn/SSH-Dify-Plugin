from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import io
import os
import socket
import traceback
import tempfile
import mimetypes

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SshFileDownloadTool(Tool):
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
            
            try:
                # 获取文件名
                filename = os.path.basename(remote_path)
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file_path = temp_file.name
                
                # 下载文件
                sftp.get(remote_path, temp_file_path)
                
                # 读取文件内容
                with open(temp_file_path, 'rb') as f:
                    file_content = f.read()
                
                # 获取文件大小
                file_size = len(file_content)
                
                # 获取文件MIME类型
                mime_type, _ = mimetypes.guess_type(filename)
                if not mime_type:
                    mime_type = 'application/octet-stream'
                
                # 创建blob消息
                yield self.create_blob_message(
                    file_content,
                    meta={
                        "mime_type": mime_type,
                        "filename": filename
                    }
                )
                
                # 删除临时文件
                os.unlink(temp_file_path)
                
                # 返回结果
                result = {
                    "success": True,
                    "filename": filename,
                    "remote_path": remote_path,
                    "size": file_size,
                    "mime_type": mime_type
                }
                
                yield self.create_json_message(result)
                yield self.create_text_message(f"Successfully downloaded file: {filename} ({file_size} bytes)")
                
            except Exception as e:
                yield self.create_json_message({
                    "success": False,
                    "error": f"Failed to download file: {str(e)}",
                    "remote_path": remote_path
                })
                yield self.create_text_message(f"Failed to download file: {str(e)}")
            
            # 关闭连接
            sftp.close()
            client.close()
            
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