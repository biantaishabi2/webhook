# Tower API 使用指南

本文档基于项目中的Tower API测试代码，提供了主要Tower API端点的使用方法和示例。

## 目录

- [认证](#认证)
  - [获取访问令牌](#获取访问令牌)
- [任务操作](#任务操作)
  - [获取任务详情](#获取任务详情)
  - [更新任务描述](#更新任务描述)
  - [指派任务](#指派任务)
  - [完成任务](#完成任务)
  - [重新打开任务](#重新打开任务)
- [评论操作](#评论操作)
  - [获取任务评论](#获取任务评论)
  - [创建任务评论](#创建任务评论)
- [注意事项](#注意事项)

## 认证

### 获取访问令牌
**端点**: `https://tower.im/oauth/token`  
**方法**: POST  
**请求头**: 
- `Content-Type: application/x-www-form-urlencoded`

**请求参数**:
- `client_id`: 应用客户端ID
- `client_secret`: 应用客户端密钥
- `grant_type`: 授权类型，可为`password`或`authorization_code`
- `username`: (当grant_type为password时) Tower用户名
- `password`: (当grant_type为password时) Tower密码

**示例请求**:
```bash
curl -X POST https://tower.im/oauth/token \
  -d "client_id=$TOWER_CLIENT_ID" \
  -d "client_secret=$TOWER_CLIENT_SECRET" \
  -d "grant_type=password" \
  -d "username=您的Tower用户名" \
  -d "password=您的Tower密码"
```

**示例响应**:
```json
{
  "access_token": "a1b2c3d4e5...",
  "token_type": "bearer",
  "expires_in": 7200,
  "refresh_token": "f6g7h8i9j0..."
}
```

**使用脚本获取**:
```bash
# 使用客户端凭据方式
python scripts/get_tower_token.py client

# 使用密码授权方式
python scripts/get_tower_token.py password <username> <password>
```

## 任务操作

### 获取任务详情
**端点**: `https://tower.im/api/v1/todos/{todo_guid}`  
**方法**: GET  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Content-Type: application/json`

**示例请求**:
```python
response = requests.get(
    f"https://tower.im/api/v1/todos/{todo_guid}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
)
```

**示例响应**:
```json
{
  "data": {
    "id": "todo_guid",
    "type": "todos",
    "attributes": {
      "content": "任务标题",
      "desc": "任务描述",
      "is_completed": false,
      "created_at": "2023-01-01T12:00:00Z",
      "due_at": null
    },
    "relationships": {
      "assignee": {
        "data": {
          "id": "member_guid",
          "type": "members"
        }
      }
    }
  },
  "included": [
    {
      "id": "member_guid",
      "type": "members",
      "attributes": {
        "nickname": "用户名"
      }
    }
  ]
}
```

### 更新任务描述
**端点**: `https://tower.im/api/v1/todos/{todo_guid}`  
**方法**: PATCH  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Content-Type: application/vnd.api+json`
- `Accept: application/vnd.api+json`

**请求体** (JSON:API格式):
```json
{
  "data": {
    "type": "todos",
    "id": "todo_guid",
    "attributes": {
      "desc": "<p>新的HTML格式描述</p>"
    }
  }
}
```

**示例请求**:
```python
response = requests.patch(
    f"https://tower.im/api/v1/todos/{todo_guid}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    },
    json={
        "data": {
            "type": "todos",
            "id": todo_guid,
            "attributes": {
                "desc": new_desc
            }
        }
    }
)
```

**简化方法** (非JSON:API格式):
```python
response = requests.put(
    f"https://tower.im/api/v1/todos/{todo_guid}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    },
    json={
        "desc": new_desc
    }
)
```

### 指派任务
**端点**: `https://tower.im/api/v1/todos/{todo_guid}/assignment`  
**方法**: PATCH  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Content-Type: application/json`
- `Accept: application/vnd.api+json`

**请求体**:
```json
{
  "todos_assignment": {
    "assignee_id": "member_guid"
  }
}
```

**示例请求**:
```python
response = requests.patch(
    f"https://tower.im/api/v1/todos/{todo_guid}/assignment",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.api+json"
    },
    json={
        "todos_assignment": {
            "assignee_id": member_guid
        }
    }
)
```

**备选方法** (JSON:API格式):
```python
response = requests.patch(
    f"https://tower.im/api/v1/todos/{todo_guid}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    },
    json={
        "data": {
            "type": "todos",
            "id": todo_guid,
            "relationships": {
                "assignee": {
                    "data": {
                        "id": member_guid,
                        "type": "members"
                    }
                }
            }
        }
    }
)
```

### 完成任务
**端点**: `https://tower.im/api/v1/todos/{todo_guid}/completion`  
**方法**: POST  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Accept: application/vnd.api+json`

**示例请求**:
```python
response = requests.post(
    f"https://tower.im/api/v1/todos/{todo_guid}/completion",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    }
)
```

**备选方法** (JSON:API格式):
```python
response = requests.patch(
    f"https://tower.im/api/v1/todos/{todo_guid}",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    },
    json={
        "data": {
            "type": "todos",
            "id": todo_guid,
            "attributes": {
                "is_completed": true
            }
        }
    }
)
```

### 重新打开任务
**端点**: `https://tower.im/api/v1/todos/{todo_guid}/reopen`  
**方法**: POST  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Accept: application/vnd.api+json`

**示例请求**:
```python
response = requests.post(
    f"https://tower.im/api/v1/todos/{todo_guid}/reopen",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    }
)
```

**备选方法** (删除完成标记):
```python
response = requests.delete(
    f"https://tower.im/api/v1/todos/{todo_guid}/completion",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    }
)
```

## 评论操作

### 获取任务评论
**端点**: `https://tower.im/api/v1/todos/{todo_guid}/comments`  
**方法**: GET  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Content-Type: application/json`

**示例请求**:
```python
response = requests.get(
    f"https://tower.im/api/v1/todos/{todo_guid}/comments",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
)
```

**示例响应**:
```json
{
  "data": [
    {
      "id": "comment_guid",
      "type": "comments",
      "attributes": {
        "content": "<p>评论内容</p>",
        "created_at": "2023-01-01T12:30:00Z"
      },
      "relationships": {
        "member": {
          "data": {
            "id": "member_guid",
            "type": "members"
          }
        }
      }
    }
  ],
  "included": [
    {
      "id": "member_guid",
      "type": "members",
      "attributes": {
        "nickname": "用户名"
      }
    }
  ]
}
```

### 创建任务评论
**端点**: `https://tower.im/api/v1/todos/{todo_guid}/comments`  
**方法**: POST  
**请求头**:
- `Authorization: Bearer {access_token}`
- `Content-Type: application/json`
- `Accept: application/vnd.api+json`

**请求体** (简单格式):
```json
{
  "content": "<p>评论内容</p>"
}
```

**示例请求**:
```python
response = requests.post(
    f"https://tower.im/api/v1/todos/{todo_guid}/comments",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.api+json"
    },
    json={
        "content": comment_content
    }
)
```

**备选方法** (JSON:API格式):
```python
response = requests.post(
    f"https://tower.im/api/v1/todos/{todo_guid}/comments",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json"
    },
    json={
        "data": {
            "type": "comments",
            "attributes": {
                "content": comment_content
            }
        }
    }
)
```

## 注意事项

1. **认证与授权**:
   - 所有API调用需要有效的访问令牌，令牌有效期默认为2小时(7200秒)
   - 令牌失效后需要重新获取或使用刷新令牌

2. **API格式**:
   - Tower API支持两种格式：
     - 标准的JSON格式 (`Content-Type: application/json`)
     - JSON:API格式 (`Content-Type: application/vnd.api+json`)
   - 某些操作在一种格式失败时可尝试另一种格式

3. **内容格式**:
   - 对任务的描述和评论内容支持HTML格式
   - HTML格式的内容应使用`<p>`等标签结构化

4. **资源标识符**:
   - 任务的GUID和成员的GUID是操作Tower资源的唯一标识符
   - 这些GUID在URL和请求体中必须匹配

5. **响应解析**:
   - 对于GET操作，响应中通常包含任务及相关实体的完整数据
   - 包含嵌套的relationships和included部分，需要正确解析

6. **错误处理**:
   - 401错误通常表示令牌过期或无效
   - 400错误可能表示请求格式错误或缺少必要参数
   - 404错误表示资源不存在

7. **项目工具类**:
   - 项目提供了`tower_api.py`工具类，封装了常见操作的API调用
   - 建议在新代码中复用这些工具类，避免重复代码