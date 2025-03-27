Tower API Docs
入门
文档说明
欢迎使用 Tower API。

本文档部署在 GitHub Page 上，对于文中出现的错误我们非常欢迎您进行反馈，您可以创建 issue 或 pull request 进行更正。

快速起步
- 创建 Tower API
1. 进入你的 Tower 团队，点击左上方团队名称。
2. 选择应用中心，可以看到 Tower API。
3. 选择创建新应用。
4. 输入名称和回调地址，Scopes 可以留空。
5. 创建成功后，可以看到多出来的应用 ID和私钥，他们就是后面提到的 client_id 和 client_sercet。
回调地址测试时可以使用 urn:ietf:wg:oauth:2.0:oob，开发者应该设置自己的回调地址，例如 https://www.example.com/oauth2/callback，稍后可以看到回调地址的具体作用。

- 尝试第一次授权
推荐使用 Postman 进行尝试

1. 自动授权
准备工作：
- 需要将 https://www.getpostman.com/oauth2/callback 添加到创建应用时候的回调地址中。

开始配置：


在填写完 Client ID 和 Client Secret 及其他相关信息后，点击 Request Token 按照提示流程，就可以完成整个授权流程。
- 发送第一个请求
通过前面的步骤拿到了 Access Token



开发
OAuth 认证
Tower API 使用 OAuth2.0 进行认证，Access Token 是全局唯一接口调用凭据，开发者调用各接口时都需使用 Access Token，请妥善保存。Access Token 的有效期目前为 2 个小时，需定时刷新，重复获取将导致上次获取的 Access Token 失效。

您在获取后，将 Access Token 添加到 API 的 Headers 中，从而确保能够获得正确的数据。

更多关于 OAuth2.0 的信息可以在这里查看和了解。

获取 Access Token
1、浏览器访问 Tower 授权地址
 https://tower.im/oauth/authorize?client_id={client_id}&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code
注意，在这里没有替换 redirect_uri，开发者在使用中一定要记得替换。

2、授权完成后，会调用回调地址，此时需要截取浏览器中的重定向，获取回调携带的授权码。
例如你的回调地址是https://www.example.com/oauth2/callback，在授权成功后会调用https://www.example.com/oauth2/callback?code=authorizationcode

3、拿到授权码后，获取 Token
 POST https://tower.im/oauth/token

参数
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述client_idstring应用 IDclient_secretstring私钥codestring客户端传来的 Authorization Codegrant_typestring此处填写为 authorization_coderedirect_uristring一定要和之前填写的回调地址相同

Status: 200 OK

{
    "access_token": "d4e949df783404f22e882430158f3b0440b608709d833f9b981e9a96b850f05c",
    "token_type": "bearer",
    "expires_in": 7199,
    "refresh_token": "c426d5ab6a211310df088c77b36b38592f6752d5238f291b79174d93f7dc2ed5",
    "created_at": 1523420694,
    "email": "tower@tower.im"
}

- 两步认证
如果授权账户开启了两步认证的话，在获取 Token 的时候，会自动给用户发送验证码，并同时返回：
Status: 200 OK

{
    "error": "otp_required",
    "error_description": "",
}

error = otp_required 就代表是需要两步认证，此时附带上验证码，再次发起获取 Token 请求即可。

POST https://tower.im/oauth/token
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述client_idstring应用 IDclient_secretstring私钥codestring客户端传来的 Authorization Codecaptchastring两步认证的验证码grant_typestring此处填写为 authorization_coderedirect_uristring一定要和之前填写的回调地址相同

刷新 Access Token
每一个 Token 默认在 2 小时后到期，此时需要用户进行刷新，同时您也需要注意 API 返回的 expires_in 数据，确保代码对过期时间改变后能够自动做出应对。

POST https://tower.im/oauth/token

Headers
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述Authorizationstring此处应该填写为 Bearer + access token，例如：Bearer d4e949df783404f22e882430158f3b0440b608709d833f9b981e9a96b850f05c

参数
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述client_idstring应用 IDclient_secretstring私钥grant_typestring此处填写为 refresh_tokenredirect_uristring一定要和之前填写的回调地址相同refresh_tokenstringrefresh_token 的值
Status: 200 OK

{
    "access_token": "d4e949df783404f22e882430158f3b0440b608709d833f9b981e9a96b850f05c",
    "token_type": "bearer",
    "expires_in": 7199,
    "refresh_token": "c426d5ab6a211310df088c77b36b38592f6752d5238f291b79174d93f7dc2ed5",
    "created_at": 1523420694,
    "email": "tower@tower.im"
}

BaseUrl
Tower API 的网址为:
https://tower.im/api/v1

JSON API
Tower API 使用的是 JSON-API，它是一种使用 JSON 构建 API 的规范，可以在不影响可读性、灵活性或可发现性的情况下最大限度地减少请求数量以及客户端和服务器之间传输的数据量。

相关文档参阅：Latest Specification (v1.0)

Java：
- Moshi-jsonapi

iOS:
- Japx

API 示例
获取当前用户在团队中的信息
GET https://tower.im/api/v1/teams/{team_id}/member

Headers
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述Authorizationstring此处应该填写为Bearer access_token

安全性推荐
部署用于 OAuth Token 的服务器（推荐）。
服务器不是必须的，但我们极力推荐开发者将私钥部署在服务器上，避免客户端代码中携带私钥而造成安全隐患。

流程




API
用户
获取当前账号信息
GET /user

Status: 200 OK

{
    "data": {
        "id": "fc6527027d1c4d4c935e618",
        "type": "users",
        "attributes": {
            "nickname": "nickname",
            "email": "email",
            "gavatar": "https://avatar.tower.im/658e00779",
            "created_at": "2014-05-15T10:43:26.000+08:00",
            "updated_at": "2018-04-16T15:55:31.000+08:00"
        }
    },
    "jsonapi": {
        "version": "1.0"
    }
}

团队
获取加入的团队列表
GET https://tower.im/api/v1/teams

Status: 200 OK

{
    "data": [
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7",
            "type": "teams",
            "attributes": {
                "name": "team 1",
                "created_at": "2014-05-15T10:32:12.000+08:00",
                "updated_at": "2018-02-10T05:44:59.000+08:00"
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7",
            "type": "teams",
            "attributes": {
                "name": "team 2",
                "created_at": "2017-07-12T10:47:29.000+08:00",
                "updated_at": "2018-04-16T10:16:34.000+08:00"
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7",
            "type": "teams",
            "attributes": {
                "name": "team 3",
                "created_at": "2017-11-30T11:51:34.000+08:00",
                "updated_at": "2018-01-23T12:24:34.000+08:00"
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}


创建团队
POST https://tower.im/api/v1/teams

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "1f9118b07cf1485ba4b97a4cbc5",
        "type": "teams",
        "attributes": {
            "name": "Tower Team",
            "created_at": "2018-04-16T16:35:29.000+08:00",
            "updated_at": "2018-04-16T16:35:29.000+08:00"
        }
    },
    "jsonapi": {
        "version": "1.0"
    }
}


更改团队名称
PATCH https://tower.im/api/v1/teams/{id}

参数
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述{ team: { name: 'Tower Team 2' } }jsonteam name
Status: 200 OK

{
    "data": {
        "id": "1f9118b07cf1485ba4b97a4cbc50bba8",
        "type": "teams",
        "attributes": {
            "name": "Tower Team 2",
            "created_at": "2018-04-16T16:35:29.000+08:00",
            "updated_at": "2018-04-16T16:36:56.000+08:00"
        }
    },
    "jsonapi": {
        "version": "1.0"
    }
}


通知
获取通知列表
GET https://tower.im/api/v1/teams/{team_id}/notifications

参数
<!--br {mso-data-placement:same-cell;}--> td {white-space:nowrap;border:0.5pt solid #dee0e3;font-size:10pt;font-style:normal;font-weight:normal;vertical-align:middle;word-break:normal;word-wrap:normal;}名称类型描述{ page: { number: 1, size: 25 } }URLEncodingpage 从 1 开始计数
Status: 200 OK

{
  "data": [
    {
      "id": "d08045c534335893b63860c8ee63d802",
      "type": "notifications",
      "attributes": {
        "notifyable_type": "Message",
        "read": false,
        "target_guid": "135857b4f34e1bf76418be27b45411a3",
        "created_at": "2019-07-25T08:59:24.000Z",
        "extra_info": {
        }
      },
      "relationships": {
        "progress": {
          "data": {
            "id": "287",
            "type": "progresses"
          }
        }
      }
    }
  ],
  "included": [
    {
      "id": "287",
      "type": "progresses",
      "attributes": {
        "nickname": "毕必隆",
        "avatar": "https://avatar.tower.im/default_avatars/path.jpg",
        "subject_str": "M 0725 165924.390",
        "action_str": "创建了讨论",
        "content_str": "时高时低杀鸡取卵勃然大怒谈虎色变, 人声鼎沸秋月似钩优柔寡断生离死别行云流水, 惊慌失措天昏地暗人山人海千姿百态鱼目混珠毫无希望泪如雨下, 两全其美人声鼎沸万古长青管中窥豹胆小如鼠一毛不拔千变万化徐徐。",
        "progress_ty": "message_add"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  },
  "links": {
    "self": "http://test.host/api/v1/teams/52e91b1c84e56abcc899eef044f32f52/notifications?page%5Bnumber%5D=1&page%5Bsize%5D=25",
    "first": "http://test.host/api/v1/teams/52e91b1c84e56abcc899eef044f32f52/notifications?page%5Bnumber%5D=1&page%5Bsize%5D=25",
    "prev": null,
    "next": null,
    "last": "http://test.host/api/v1/teams/52e91b1c84e56abcc899eef044f32f52/notifications?page%5Bnumber%5D=1&page%5Bsize%5D=25"
  }
}


动态
获取动态列表
GET https://tower.im/api/v1/teams/{team_id}/events

参数
Unable to copy while content loads
Status: 200 OK

{
  "data": [
    {
      "id": "24",
      "type": "events",
      "attributes": {
        "ancestor_type": "Project",
        "ancestor_name": "Proj 0725 170506.175",
        "created_at": "2019-07-25T09:05:07.000Z",
        "action": "创建了回复",
        "title": "M 0725 170506.408"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "5206fad7bbce4c23a8e0984ba5875f0b",
            "type": "members"
          }
        }
      }
    },
    {
      "id": "23",
      "type": "events",
      "attributes": {
        "ancestor_type": "Project",
        "ancestor_name": "Proj 0725 170506.175",
        "created_at": "2019-07-25T09:05:06.000Z",
        "action": "创建了讨论",
        "title": "M 0725 170506.408"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "5206fad7bbce4c23a8e0984ba5875f0b",
            "type": "members"
          }
        }
      }
    }
  ],
  "included": [
    {
      "id": "5206fad7bbce4c23a8e0984ba5875f0b",
      "type": "members",
      "attributes": {
        "nickname": "银群惟",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/waves.jpg",
        "role": "owner"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}


上传附件
获取客户端直传签名
Tower 使用阿里云 OSS 文件存储，支持客户端 javascript 直传，文件上传前需通过本 API 接口获取对应的签名和上传地址等。
阿里云 OSS 上传相关介绍

POST https://tower.im/api/v1/teams/{team_id}/direct_uploads

参数
Unable to copy while content loads
Status: 200 OK

{
  "guid": "d326b6e2c7a22d472dab783894fe0024",
  "directUpload": {
    "OSSAccessKeyId": "your_aliyun_key",
    "policy": "eyJleHBpcmF0aW9uIjoiMjAxOS0wNy0yNVQxMjoyMDowMS4wMDBaIiwiY29uZGl0aW9ucyI6W3siYnVja2V0IjoidG93ZXIyIn0sWyJlcSIsIiRrZXkiLCI2NDEvZDMyNmI2ZTJjN2EyMmQ0NzJkYWI3ODM4OTRmZTAwMjQiXV19",
    "Signature": "5r9OKoFQrkZKrAGFd7e9IMoP8N8=",
    "url": "https://alioss.tower.im/",
    "callback": "eyJjYWxsYmFja1VybCI6Imh0dHBzOi8vdG93ZXIuaW0vb3NzL2F0dGFjaG1lbnRzL2NhbGxiYWNrLmpzb24iLCJjYWxsYmFja0hvc3QiOiJ0b3dlci5pbSIsImNhbGxiYWNrQm9keSI6ImtleT0ke29iamVjdH1cdTAwMjZzaXplPSR7c2l6ZX1cdTAwMjZtaW1lVHlwZT0ke21pbWVUeXBlfVx1MDAyNmhlaWdodD0ke2ltYWdlSW5mby5oZWlnaHR9XHUwMDI2d2lkdGg9JHtpbWFnZUluZm8ud2lkdGh9XHUwMDI2ZmlsZW5hbWU9dGVzdC5wbmdcdTAwMjZhdHRmaWxlX2d1aWQ9ZDMyNmI2ZTJjN2EyMmQ0NzJkYWI3ODM4OTRmZTAwMjQiLCJjYWxsYmFja0JvZHlUeXBlIjoiYXBwbGljYXRpb24veC13d3ctZm9ybS11cmxlbmNvZGVkIn0=",
    "key": "641/d326b6e2c7a22d472dab783894fe0024"
  }
}

成员
获取团队全部成员
GET https://tower.im/api/v1/teams/{team_id}/members

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": [
        {
            "id": "c979895c5a754c35b3e98f1c7268724c",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/658e007790c24bcb9745172",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:35:29.000+08:00",
                "updated_at": "2018-04-16T16:36:50.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "1f9118b07cf1485ba4b97a4cbc50",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        }
    ],
    "included": [
        {
            "id": "1f9118b07cf1485ba4b97a4cbc50b",
            "type": "teams",
            "attributes": {
                "name": "Tower Team",
                "created_at": "2018-04-16T16:35:29.000+08:00",
                "updated_at": "2018-04-16T16:36:56.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    },
    "links": {
        "self": "https://tower.im/api/v1/teams/:id/members?page%5Bnumber%5D=1&page%5Bsize%5D=200",
        "first": "https://tower.im/api/v1/teams/:id/members?page%5Bnumber%5D=1&page%5Bsize%5D=200",
        "prev": null,
        "next": null,
        "last": "https://tower.im/api/v1/teams/:id/members?page%5Bnumber%5D=1&page%5Bsize%5D=200"
    }
}

获取当前账户在团队中的信息
GET https://tower.im/api/v1/teams/{team_id}/member

Status: 200 OK

{
    "data": {
        "id": "c979895c5a754c35b3e98f1c72",
        "type": "members",
        "attributes": {
            "nickname": "nickname",
            "is_active": true,
            "gavatar": "https://avatar.tower.im/658e007790c24bcb9745172",
            "role": "owner",
            "comment": null,
            "phone": null,
            "created_at": "2018-04-16T16:35:29.000+08:00",
            "updated_at": "2018-04-16T16:36:50.000+08:00"
        },
        "relationships": {
            "team": {
                "data": {
                    "id": "1f9118b07cf1485ba4b97a4c",
                    "type": "teams"
                }
            },
            "groups": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "1f9118b07cf1485ba4b97a4cb",
            "type": "teams",
            "attributes": {
                "name": "Tower Team",
                "created_at": "2018-04-16T16:35:29.000+08:00",
                "updated_at": "2018-04-16T16:36:56.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

获取成员信息
GET https://tower.im/api/v1/members/{member_id}

Status: 200 OK

获取指派给成员未完成任务
GET /members/{member_id}/assigned_uncompleted_todos
box 为分类属性，不要使用到期日作为分类。 0代表新任务，1代表今天，2代表接下来，3代表以后
Status: 200 OK

获取指派给成员已完成任务
GET https://tower.im/api/v1/members/{member_id}/assigned_completed_todos

参数
Unable to copy while content loads
Status: 200 OK

获取成员创建的未完成任务
GET https://tower.im/api/v1/members/{member_id}/created_uncompleted_todos

Status: 200 OK

获取成员创建的已完成任务
GET https://tower.im/api/v1/members/{member_id}/created_completed_todos

参数
Unable to copy while content loads
Status: 200 OK


项目
获取团队中所有项目
GET https://tower.im/api/v1/teams/{team_id}/projects

Status: 200 OK

{
    "data": [
        {
            "id": "974de405781644e09e187109bb0386de",
            "type": "projects",
            "attributes": {
                "name": "熟悉 Tower",
                "desc": "工欲善其事，必先利其器。",
                "is_pinned": false,
                "is_archived": false
            },
            "relationships": {
                "project_groups": {
                    "data": []
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}


创建项目
POST https://tower.im/api/v1/teams/{team_id}/projects

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "fa9413082dc0456ab98576d2e882",
        "type": "projects",
        "attributes": {
            "name": "Project",
            "desc": "Project Desc",
            "is_archived": false,
            "created_at": "2018-04-16T16:49:27.000+08:00",
            "updated_at": "2018-04-16T16:49:27.000+08:00"
        },
        "relationships": {
            "team": {
                "data": {
                    "id": "1f9118b07cf1485ba4b97a4cbc5",
                    "type": "teams"
                }
            },
            "creator": {
                "data": {
                    "id": "c979895c5a754c35b3e98f1c726",
                    "type": "members"
                }
            },
            "todolists": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "1f9118b07cf1485ba4b97a4cbc50",
            "type": "teams",
            "attributes": {
                "name": "Tower Team123",
                "created_at": "2018-04-16T16:35:29.000+08:00",
                "updated_at": "2018-04-16T16:36:56.000+08:00"
            }
        },
        {
            "id": "c979895c5a754c35b3e98f1c7268",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:35:29.000+08:00",
                "updated_at": "2018-04-16T16:36:50.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "1f9118b07cf1485ba4b97a4cbc50bba8",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}



获取项目信息
GET https://tower.im/api/v1/projects/{project_id}

Status: 200 OK

{
    "data": {
        "id": "5448bef3f013403db51b82d5ba3c473e",
        "type": "projects",
        "attributes": {
            "name": "Project Name",
            "desc": "Project desc",
            "is_archived": false,
            "created_at": "2018-04-16T16:07:48.000+08:00",
            "updated_at": "2018-04-16T16:26:12.000+08:00"
        },
        "relationships": {
            "team": {
                "data": {
                    "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                    "type": "teams"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "todolists": {
                "data": [
                    {
                        "id": "462c6ca5442c4d6394b8bed46480e195",
                        "type": "todolists"
                    },
                    {
                        "id": "382dbd2306194d9380e3f96221b26720",
                        "type": "todolists"
                    }
                ]
            }
        }
    },
    "included": [
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:09:27.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "desc": "",
                "is_active": true,
                "is_archived": false,
                "is_default": false,
                "position": 1
            },
            "relationships": {
                "todos": {
                    "data": [
                        {
                            "id": "2388246f04414e1aa286cd1cdb60a5b3",
                            "type": "todos"
                        }
                    ]
                }
            }
        },
        {
            "id": "2388246f04414e1aa286cd1cdb60a5b3",
            "type": "todos",
            "attributes": {
                "content": "任务名称",
                "desc": "<p>任务描述</p>",
                "is_active": true,
                "is_completed": false,
                "due_at": null,
                "closed_at": "2018-04-16T16:17:50.000+08:00"
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        },
        {
            "id": "382dbd2306194d9380e3f96221b26720",
            "type": "todolists",
            "attributes": {
                "name": "清单外任务",
                "desc": null,
                "is_active": true,
                "is_archived": false,
                "is_default": true,
                "position": 0
            },
            "relationships": {
                "todos": {
                    "data": []
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

更新项目信息
PATCH    https://tower.im/api/v1/projects/{id}

参数
Unable to copy while content loads
Status: 200 OK

删除项目
DELETE https://tower.im/api/v1/projects/{id}

Status: 204 OK

获取项目成员
GET https://tower.im/api/v1/projects/{project_id}/members

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": [
        {
            "id": "8ead8fc12a804eb198c2196abbf",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:09:27.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        }
    ],
    "included": [
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    },
    "links": {
        "self": "https://tower.im/api/v1/teams/:id/members?page%5Bnumber%5D=1&page%5Bsize%5D=200",
        "first": "https://tower.im/api/v1/teams/:id/members?page%5Bnumber%5D=1&page%5Bsize%5D=200",
        "prev": null,
        "next": null,
        "last": "https://tower.im/api/v1/teams/:id/members?page%5Bnumber%5D=1&page%5Bsize%5D=200"
    }
}



任务清单
获取项目中所有任务清单
GET https://tower.im/api/v1/projects/{project_id}/todolists

Status: 200 OK

{
    "data": [
        {
            "id": "2d1fbfd51ed7429296bc1a5fcb",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "desc": "",
                "is_active": true,
                "is_archived": false,
                "is_default": false,
                "position": 1
            },
            "relationships": {
                "todos": {
                    "data": [
                        {
                            "id": "fb31376b01894058b2a434813ffd",
                            "type": "todos"
                        }
                    ]
                }
            }
        },
        {
            "id": "862ed55e1564487f85dc1343ca45",
            "type": "todolists",
            "attributes": {
                "name": "清单外任务",
                "desc": null,
                "is_active": true,
                "is_archived": false,
                "is_default": true,
                "position": 0
            },
            "relationships": {
                "todos": {
                    "data": []
                }
            }
        }
    ],
    "included": [
        {
            "id": "fb31376b01894058b2a434813ffda",
            "type": "todos",
            "attributes": {
                "content": "任务",
                "desc": "",
                "is_active": true,
                "is_completed": false,
                "due_at": null,
                "closed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a1",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:09:27.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

创建任务清单
POST https://tower.im/api/v1/projects/{project_id}/todolists

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "da8aef40e9c04feb8e289529aa23b63e",
        "type": "todolists",
        "attributes": {
            "name": "Todolist",
            "desc": "Todolist Desc",
            "is_active": true,
            "is_archived": false,
            "is_default": false,
            "completed_at": null,
            "created_at": "2018-04-16T17:10:38.000+08:00",
            "updated_at": "2018-04-16T17:10:38.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "fd746ae1145c46398973b61876a3f0a6",
                    "type": "projects"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "archiver": {
                "data": null
            },
            "todos": {
                "data": []
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "fd746ae1145c46398973b61876a3f0a6",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:09:27.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

获取任务清单信息
GET https://tower.im/api/v1/todolists/{id}

Status: 200 OK

{
    "data": {
        "id": "da8aef40e9c04feb8e289529aa23b63e",
        "type": "todolists",
        "attributes": {
            "name": "Todolist",
            "desc": "Todolist Desc",
            "is_active": true,
            "is_archived": false,
            "is_default": false,
            "completed_at": null,
            "created_at": "2018-04-16T17:10:38.000+08:00",
            "updated_at": "2018-04-16T17:10:38.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "fd746ae1145c46398973b61876a3f0a6",
                    "type": "projects"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "archiver": {
                "data": null
            },
            "todos": {
                "data": []
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "fd746ae1145c46398973b61876a3f0a6",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:09:27.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

更新任务列表
PATCH https://tower.im/api/v1/todolists/{id}

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "da8aef40e9c04feb8e289529aa23b63e",
        "type": "todolists",
        "attributes": {
            "name": "Todolist",
            "desc": "Todolist Desc",
            "is_active": true,
            "is_archived": false,
            "is_default": false,
            "completed_at": null,
            "created_at": "2018-04-16T17:10:38.000+08:00",
            "updated_at": "2018-04-16T17:10:38.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "fd746ae1145c46398973b61876a3f0a6",
                    "type": "projects"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "archiver": {
                "data": null
            },
            "todos": {
                "data": []
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "fd746ae1145c46398973b61876a3f0a6",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:09:27.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

删除任务清单
DELETE https://tower.im/api/v1/todolists/{id}

Status: 204 OK


任务
获取清单任务
GET https://tower.im/api/v1/todolists/{todolist_id}/todos

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": [
        {
            "id": "46d952895c10440",
            "type": "todos",
            "attributes": {
                "team_wide_id": 4116, //资源ID
                "content": "任务名称",
                "desc": "任务描述",
                "is_active": true,
                "is_completed": false,
                "due_at": null,
                "closed_at": null,
                "priority": "higher",
                "labels": ["缺陷", "v12.32"]
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "043bd9be9c10",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "included": [
        {
            "id": "043bd9be9c104f0a",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/avatar",
                "role": "owner",
                "comment": "123123123123121",
                "phone": "123",
                "created_at": "2017-07-12T10:47:29.000+08:00",
                "updated_at": "2018-04-16T10:16:34.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "82196e7031a24ac",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": [
                        {
                            "id": "ab855eec4b6f49",
                            "type": "subgroups"
                        }
                    ]
                }
            }
        },
        {
            "id": "82196e7031a24",
            "type": "teams",
            "attributes": {
                "name": "name",
                "created_at": "2017-07-12T10:47:29.000+08:00",
                "updated_at": "2018-04-16T10:16:34.000+08:00"
            }
        },
        {
            "id": "ab855eec4b6f49bab8a7589408dcc29d",
            "type": "subgroups",
            "attributes": {
                "name": "groupname"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

priority 字段说明：
highest: 最高
higher: 较高
normal: 普通
lower: 较低

创建任务
POST https://tower.im/api/v1/todolists/{todolist_id}/todos

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "2d5de72adb4e414f8f299753f4f1a87a",
        "type": "todos",
        "attributes": {
            "content": "Todo",
            "desc": "Todo Desc",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:02:41.000+08:00",
            "updated_at": "2018-04-16T16:02:41.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "0a81690ff28d45cb94e43ebf431eedff",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "cf0b8fcef47d470b906859c861194f6f",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "b79acb8a6816467c9a926a3d053ac5f0",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": []
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "0a81690ff28d45cb94e43ebf431eedff",
            "type": "projects",
            "attributes": {
                "name": "艾泽拉斯大事件",
                "is_archived": false
            }
        },
        {
            "id": "cf0b8fcef47d470b906859c861194f6f",
            "type": "todolists",
            "attributes": {
                "name": "部落",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "b79acb8a6816467c9a926a3d053ac5f0",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "admin",
                "comment": "beizhu",
                "phone": "133",
                "created_at": "2017-09-04T15:23:25.000+08:00",
                "updated_at": "2018-04-16T15:57:13.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "82196e7031a24a",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "82196e7031a24ac980",
            "type": "teams",
            "attributes": {
                "name": "Me",
                "created_at": "2017-07-12T10:47:29.000+08:00",
                "updated_at": "2018-04-16T10:16:34.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

获取任务信息
GET https://tower.im/api/v1/todos/{todo_id}

Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "team_wide_id": 4116, //资源ID
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "custom_field_value": {
                "data": {
                    "id": "2",
                    "type": "todos_custom_field_values"
                }
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        },
        {
            "id": "2",
            "type": "todos_custom_field_values",
            "attributes": {
                "custom_fields": {
                    "number_Y4B7RiMh": {
                        "name": "任务估点",
                        "value": "8",
                        "field_type": "number"
                    },
                    "multi_select_QeTbTNAR": {
                        "name": "所属平台",
                        "value": [
                            "微信",
                            "安卓",
                            "企业微信"
                        ],
                        "field_type": "multi_select"
                    },
                    "date_SkFsCU6t": {
                        "name": "截止日期",
                        "value": "2019-07-25",
                        "field_type": "date"
                    },
                    "string_i5timka4": {
                        "name": "备注",
                        "value": "备注信息",
                        "field_type": "string"
                    },
                    "member_GrB9U8fJ": {
                        "name": "维护人",
                        "value": "2a4b425e1f0d663668ce19b94ed3688d",
                        "field_type": "member"
                    },
                    "select_WDvNVBqF": {
                        "name": "性别",
                        "value": "男",
                        "field_type": "select"
                    },
                    "boolean_ZFxG2S6U": {
                        "name": "是否停用",
                        "value": "true",
                        "field_type": "boolean"
                    }
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

更新任务信息
PATCH https://tower.im/api/v1/todos/{todo_id}

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "team_wide_id": 4116, //资源ID
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

删除任务
DELETE /todos/{todo_id}

Status: 204 OK

完成任务
POST https://tower.im/api/v1/todos/{todo_id}/completion

Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "team_wide_id": 4116, //资源ID
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

打开任务
DELETE https://tower.im/api/v1/todos/{todo_id}/completion

使用 HTTP 的 Delete 方法，对已完成任务完成进行删除，表示重新打开任务。

Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "team_wide_id": 4116, //资源ID
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

发布评论
POST https://tower.im/api/v1/todos/{id}/comments

参数
Unable to copy while content loads
评论中 @ 他人，需要将评论中的@Tower转化成<a href=\"/members/{member_id}\" data-mention=\"true\">@Tower</a>

Status: 200 OK

{
    "data": {
        "id": "9dce33eb2cd24",
        "type": "comments",
        "attributes": {
            "content": "text",
            "created_at": "2018-03-28T11:10:30.000+08:00",
            "updated_at": "2018-03-28T11:10:30.000+08:00"
        },
        "relationships": {
            "creator": {
                "data": {
                    "id": "b79acb8a6816467c9a926a3d053ac5f0",
                    "type": "members"
                }
            }
        }
    },
    "included": [
        {
            "id": "b79acb8a6816",
            "type": "members",
            "attributes": {
                "nickname": "nickname",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/gavatar",
                "role": "admin",
                "created_at": "2017-09-04T15:23:25.000+08:00",
                "updated_at": "2018-03-27T15:14:26.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "82196e7031a24",
                        "type": "teams"
                    }
                }
            }
        },
        {
            "id": "82196e7031a24a",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2017-07-12T10:47:29.000+08:00",
                "updated_at": "2018-03-27T09:57:54.000+08:00"
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

指派任务负责人
PATCH https://tower.im/api/v1/todos/{todo_id}/assignment

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}


移除任务负责人
DELETE https://tower.im/api/v1/todos/{todo_id}/assignment

Status: 200 OK

更新任务到期日
PATCH https://tower.im/api/v1/todos/{todo_id}/due

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "team_wide_id": 4116, //资源ID
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}

更新任务描述
PATCH https://tower.im/api/v1/todos/{todo_id}/desc

参数
Unable to copy while content loads
Status: 200 OK

{
    "data": {
        "id": "2388246f04414e1aa286cd1cdb60a5b3",
        "type": "todos",
        "attributes": {
            "content": "任务名称",
            "desc": "<p>任务描述</p>",
            "is_active": true,
            "is_completed": false,
            "due_at": null,
            "closed_at": null,
            "created_at": "2018-04-16T16:07:54.000+08:00",
            "updated_at": "2018-04-16T16:08:15.000+08:00"
        },
        "relationships": {
            "project": {
                "data": {
                    "id": "5448bef3f013403db51b82d5ba3c473e",
                    "type": "projects"
                }
            },
            "todolist": {
                "data": {
                    "id": "462c6ca5442c4d6394b8bed46480e195",
                    "type": "todolists"
                }
            },
            "creator": {
                "data": {
                    "id": "8ead8fc12a804eb198c2196abbf1a18e",
                    "type": "members"
                }
            },
            "assignee": {
                "data": null
            },
            "closer": {
                "data": null
            },
            "todos_check_items": {
                "data": [
                    {
                        "id": "66c2977494fd4dadb3ec8cd3248744bf",
                        "type": "todos_check_items"
                    }
                ]
            },
            "comments": {
                "data": []
            }
        }
    },
    "included": [
        {
            "id": "5448bef3f013403db51b82d5ba3c473e",
            "type": "projects",
            "attributes": {
                "name": "Project Name",
                "is_archived": false
            }
        },
        {
            "id": "462c6ca5442c4d6394b8bed46480e195",
            "type": "todolists",
            "attributes": {
                "name": "清单名称",
                "is_active": true,
                "is_archived": false,
                "is_default": false
            }
        },
        {
            "id": "8ead8fc12a804eb198c2196abbf1a18e",
            "type": "members",
            "attributes": {
                "nickname": "GaoYu",
                "is_active": true,
                "gavatar": "https://avatar.tower.im/",
                "role": "owner",
                "comment": null,
                "phone": null,
                "created_at": "2018-04-16T16:07:35.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            },
            "relationships": {
                "team": {
                    "data": {
                        "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
                        "type": "teams"
                    }
                },
                "groups": {
                    "data": []
                }
            }
        },
        {
            "id": "3fbe491eef5c4fbeaaabc1716b7a1f00",
            "type": "teams",
            "attributes": {
                "name": "API Team",
                "created_at": "2018-04-16T16:07:34.000+08:00",
                "updated_at": "2018-04-16T16:07:35.000+08:00"
            }
        },
        {
            "id": "66c2977494fd4dadb3ec8cd3248744bf",
            "type": "todos_check_items",
            "attributes": {
                "name": "检查项",
                "is_completed": false,
                "due_at": null,
                "completed_at": null
            },
            "relationships": {
                "creator": {
                    "data": {
                        "id": "8ead8fc12a804eb198c2196abbf1a18e",
                        "type": "members"
                    }
                },
                "assignee": {
                    "data": null
                },
                "closer": {
                    "data": null
                }
            }
        }
    ],
    "jsonapi": {
        "version": "1.0"
    }
}


讨论
获取项目讨论列表
GET https://tower.im/api/v1/projects/{project_id}/topics

Status: 200 OK
{
  "data": [
    {
      "id": "0800afd15d7471e4b90a499e02dc4652",
      "type": "topics",
      "attributes": {
        "content": "失声痛哭洁白如玉婀娜多姿千奇百怪啼冰天雪地, 日月如梭千变万化天经地义泪眼汪汪, 蛛丝马迹齐心协力扬眉吐气一触即发秋雨绵绵霎时间百感交集振奋人心对牛弹琴, 两情相悦果实累累胆小如鼠哗哗啦啦能屈能伸, 一见如故望子成龙千奇百怪乌云翻滚红日东升叶公好龙。",
        "is_archived": false,
        "created_at": "2019-07-26T01:48:37.000Z",
        "title": "M 0726 094837.243"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "61f5031ccfcabb3dd423a8a4564e3eff",
            "type": "members"
          }
        },
        "comments": {
          "data": [
            {
              "id": "9b30da26e6447c9ea07330f7dc8307b7",
              "type": "comments"
            }
          ]
        },
        "attachments": {
          "data": [

          ]
        }
      }
    }
  ],
  "included": [
    {
      "id": "61f5031ccfcabb3dd423a8a4564e3eff",
      "type": "members",
      "attributes": {
        "nickname": "碧鲁建意",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/path.jpg",
        "role": "member"
      }
    },
    {
      "id": "9b30da26e6447c9ea07330f7dc8307b7",
      "type": "comments",
      "attributes": {
        "content": "C 0726 094837.357 满山遍野承上启下自高自大十分可恶管中窥豹秋高气爽, 暴雨如注众志成城生气勃勃扫视一目十行大名鼎鼎黑白分明轰轰隆隆, 江水滚滚无牵无挂古色古香子雨打风吹桃红柳绿天老地荒, 车轮滚滚暴雨如注静思默想轰轰隆隆春暖花开牛头马面赞叹不已笑容可掬。",
        "created_at": "2019-07-26T01:48:37.000Z",
        "updated_at": "2019-07-26T01:48:37.000Z"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "663d1d2e60b7f94318d9fcb0b68bf2f1",
            "type": "members"
          }
        },
        "attachments": {
          "data": [

          ]
        }
      }
    },
    {
      "id": "663d1d2e60b7f94318d9fcb0b68bf2f1",
      "type": "members",
      "attributes": {
        "nickname": "理安纯",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/cloud.jpg",
        "role": "member"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  },
  "links": {
    "self": "https://tower.im/api/v1/projects/b0c7b5e87c84c2381ca4611476ec17d5/topics?page%5Bnumber%5D=1&page%5Bsize%5D=25",
    "first": "https://tower.im/api/v1/projects/b0c7b5e87c84c2381ca4611476ec17d5/topics?page%5Bnumber%5D=1&page%5Bsize%5D=25",
    "prev": null,
    "next": null,
    "last": "https://tower.im/api/v1/projects/b0c7b5e87c84c2381ca4611476ec17d5/topics?page%5Bnumber%5D=1&page%5Bsize%5D=25"
  }
}

创建讨论
POST https://tower.im/api/v1/projects/{project_id}/topics

参数
Unable to copy while content loads
Status: 200 OK
{
  "data": {
    "id": "5d0042a851132539a7d0f9508ebce48f",
    "type": "topics",
    "attributes": {
      "content": "Non sint accusantium eaque neque.",
      "is_archived": false,
      "created_at": "2019-07-26T01:54:41.000Z",
      "title": "dolorem"
    },
    "relationships": {
      "creator": {
        "data": {
          "id": "8d825acb9925f1c93019f60971f5e5b8",
          "type": "members"
        }
      },
      "comments": {
        "data": [

        ]
      },
      "attachments": {
        "data": [
          {
            "id": "dcbb9e78229637076d76673618ae9fdc",
            "type": "attachments"
          }
        ]
      }
    }
  },
  "included": [
    {
      "id": "8d825acb9925f1c93019f60971f5e5b8",
      "type": "members",
      "attributes": {
        "nickname": "从昇来",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/waves.jpg",
        "role": "owner"
      }
    },
    {
      "id": "dcbb9e78229637076d76673618ae9fdc",
      "type": "attachments",
      "attributes": {
        "content_type": "image/png",
        "byte_size": 475,
        "width": 0,
        "height": 0,
        "created_at": "2019-07-26T01:54:40.000Z",
        "filename": "IMG_0012.PNG",
        "icon_url": "https://alioss.tower.im/oss/ab12dc67f19f8dbe559af0cae267838d_small?Expires=1564106681&OSSAccessKeyId=your_aliyun_key&Signature=MrY7l%2FSUAp0hgaCsJTT8cyLFqYw%3D&response-content-disposition=inline%3Bfilename%3D%22IMG_0012.PNG%22&response-content-type=image%2Fpng",
        "url": "https://alioss.tower.im/oss/ab12dc67f19f8dbe559af0cae267838d_large?Expires=1564106681&OSSAccessKeyId=your_aliyun_key&Signature=nYNSRRgodYuCp0nnpubOeF3RRFs%3D&response-content-disposition=inline%3Bfilename%3D%22IMG_0012.PNG%22&response-content-type=image%2Fpng"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "8d825acb9925f1c93019f60971f5e5b8",
            "type": "members"
          }
        }
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}

获取讨论
GET https://tower.im/api/v1/topics/{id}

Status: 200 OK

{
  "data": {
    "id": "240567b2bccda0740992028cfe2ee4be",
    "type": "topics",
    "attributes": {
      "content": "千疮百孔首烈日当空交头接耳首屈一指万众一心一泻千里名列前茅一瞬间, 满山遍野铿锵有力绿树成阴绿莹莹十万火急, 远望吉祥如意枣红四海为家。",
      "is_archived": false,
      "created_at": "2019-07-26T01:58:50.000Z",
      "title": "M 0726 095850.291"
    },
    "relationships": {
      "creator": {
        "data": {
          "id": "10d203508104b9104304fb8f5504f12d",
          "type": "members"
        }
      },
      "comments": {
        "data": [

        ]
      },
      "attachments": {
        "data": [

        ]
      }
    }
  },
  "included": [
    {
      "id": "10d203508104b9104304fb8f5504f12d",
      "type": "members",
      "attributes": {
        "nickname": "蔡璇珊",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/jokul.jpg",
        "role": "member"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}

更新讨论
PATCH https://tower.im/api/v1/topics/{id}

参数
Unable to copy while content loads
Status: 200 OK
{
  "data": {
    "id": "160846ca76cc680edc341621ff46fbb5",
    "type": "topics",
    "attributes": {
      "content": "Pariatur quas magnam non excepturi qui necessitatibus.",
      "is_archived": false,
      "created_at": "2019-07-26T02:03:24.000Z",
      "title": "soluta"
    },
    "relationships": {
      "creator": {
        "data": {
          "id": "3c1068e542d78318ad61145babcbfd26",
          "type": "members"
        }
      },
      "comments": {
        "data": [

        ]
      },
      "attachments": {
        "data": [

        ]
      }
    }
  },
  "included": [
    {
      "id": "3c1068e542d78318ad61145babcbfd26",
      "type": "members",
      "attributes": {
        "nickname": "愚昆坚",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/noon.jpg",
        "role": "member"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}

删除讨论
DELETE https://tower.im/api/v1/topics/{id}

Status: 204 OK


文件
获取项目文件列表
GET https://tower.im/api/v1/projects/{project_id}/uploads

Status: 200 OK
{
  "data": [
    {
      "id": "0db8c283a993d43b41c1a50ef236767f",
      "type": "uploads",
      "attributes": {
        "name": "upload name",
        "desc": null,
        "created_at": "2019-07-26T02:10:15.000Z",
        "updated_at": "2019-07-26T02:10:15.000Z"
      },
      "relationships": {
        "attachment": {
          "data": {
            "id": "942c61fefe9c8e82071d378588bfa497",
            "type": "attachments"
          }
        },
        "comments": {
          "data": [

          ]
        }
      }
    }
  ],
  "included": [
    {
      "id": "942c61fefe9c8e82071d378588bfa497",
      "type": "attachments",
      "attributes": {
        "content_type": "image/png",
        "byte_size": 996,
        "width": 0,
        "height": 0,
        "created_at": "2019-07-26T02:10:15.000Z",
        "filename": "十分可恶",
        "icon_url": "https://alioss.tower.im/oss/ccb0bd47bb7e39efe665cedf483e80af_small?Expires=1564107615&OSSAccessKeyId=your_aliyun_key&Signature=yszDUzihq7TkifCk0skmx%2B9kUGM%3D&response-content-disposition=inline%3Bfilename%3D%22%E5%8D%81%E5%88%86%E5%8F%AF%E6%81%B6%22&response-content-type=image%2Fpng",
        "url": "https://alioss.tower.im/oss/ccb0bd47bb7e39efe665cedf483e80af_large?Expires=1564107615&OSSAccessKeyId=your_aliyun_key&Signature=ykPPDdnY%2FLafzbkwMYMbWi0Yd04%3D&response-content-disposition=inline%3Bfilename%3D%22%E5%8D%81%E5%88%86%E5%8F%AF%E6%81%B6%22&response-content-type=image%2Fpng"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "e3f9e235e2f322197eb1962ba80fa160",
            "type": "members"
          }
        }
      }
    },
    {
      "id": "e3f9e235e2f322197eb1962ba80fa160",
      "type": "members",
      "attributes": {
        "nickname": "盘典夫",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/waves.jpg",
        "role": "member"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}

创建文件
POST https://tower.im/api/v1/projects/{project_id}/uploads

参数
Unable to copy while content loads
Status: 200 OK
{
  "data": {
    "id": "72f3648fbedb5d8016568a7309c03ee4",
    "type": "uploads",
    "attributes": {
      "name": "IMG_0012.PNG",
      "desc": "IMG_0012.PNG",
      "created_at": "2019-07-26T02:19:03.000Z",
      "updated_at": "2019-07-26T02:19:03.000Z"
    },
    "relationships": {
      "attachment": {
        "data": {
          "id": "1c27046caba100f6464bcd791c66ef9c",
          "type": "attachments"
        }
      },
      "comments": {
        "data": [

        ]
      }
    }
  },
  "included": [
    {
      "id": "1c27046caba100f6464bcd791c66ef9c",
      "type": "attachments",
      "attributes": {
        "content_type": "image/png",
        "byte_size": 484,
        "width": 0,
        "height": 0,
        "created_at": "2019-07-26T02:19:03.000Z",
        "filename": "IMG_0012.PNG",
        "icon_url": "https://alioss.tower.im/oss/b3b3081844814d528cd776ec83aa3352_small?Expires=1564108143&OSSAccessKeyId=your_aliyun_key&Signature=xz5HAs2LVsWGyIRnwz3YkqJmVlw%3D&response-content-disposition=inline%3Bfilename%3D%22IMG_0012.PNG%22&response-content-type=image%2Fpng",
        "url": "https://alioss.tower.im/oss/b3b3081844814d528cd776ec83aa3352_large?Expires=1564108143&OSSAccessKeyId=your_aliyun_key&Signature=9N%2F8MBOdISg3KNGkPzfZ9YWrnQE%3D&response-content-disposition=inline%3Bfilename%3D%22IMG_0012.PNG%22&response-content-type=image%2Fpng"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "a9baa588ad4db1e893e1d58fd40571f5",
            "type": "members"
          }
        }
      }
    },
    {
      "id": "a9baa588ad4db1e893e1d58fd40571f5",
      "type": "members",
      "attributes": {
        "nickname": "贡江钰",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/cloud.jpg",
        "role": "owner"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}

获取文件
GET https://tower.im/api/v1/uploads/{id}

Status: 200 OK
{
  "data": {
    "id": "c50dd5fa3dee03f77b7612464213a6e0",
    "type": "uploads",
    "attributes": {
      "name": "upload name",
      "desc": null,
      "created_at": "2019-07-26T02:20:55.000Z",
      "updated_at": "2019-07-26T02:20:55.000Z"
    },
    "relationships": {
      "attachment": {
        "data": {
          "id": "9edb50c1ceb80348208691cb6db7fe1b",
          "type": "attachments"
        }
      },
      "comments": {
        "data": [

        ]
      }
    }
  },
  "included": [
    {
      "id": "9edb50c1ceb80348208691cb6db7fe1b",
      "type": "attachments",
      "attributes": {
        "content_type": "image/png",
        "byte_size": 800,
        "width": 0,
        "height": 0,
        "created_at": "2019-07-26T02:20:55.000Z",
        "filename": "鸟语花香",
        "icon_url": "https://alioss.tower.im/oss/054d9db164177fb206c00f613a20dca6_small?Expires=1564108255&OSSAccessKeyId=your_aliyun_key&Signature=dmpdQ9zT1qm1mU35flhYe6Re8kQ%3D&response-content-disposition=inline%3Bfilename%3D%22%E9%B8%9F%E8%AF%AD%E8%8A%B1%E9%A6%99%22&response-content-type=image%2Fpng",
        "url": "https://alioss.tower.im/oss/054d9db164177fb206c00f613a20dca6_large?Expires=1564108255&OSSAccessKeyId=your_aliyun_key&Signature=KIr2RH4lihg72lAClaXxuf%2B8E5g%3D&response-content-disposition=inline%3Bfilename%3D%22%E9%B8%9F%E8%AF%AD%E8%8A%B1%E9%A6%99%22&response-content-type=image%2Fpng"
      },
      "relationships": {
        "creator": {
          "data": {
            "id": "1e567de56ba46e6def9ae89dec6b3485",
            "type": "members"
          }
        }
      }
    },
    {
      "id": "1e567de56ba46e6def9ae89dec6b3485",
      "type": "members",
      "attributes": {
        "nickname": "牟伊妹",
        "is_active": true,
        "gavatar": "https://avatar.tower.im/default_avatars/cloud.jpg",
        "role": "member"
      }
    }
  ],
  "jsonapi": {
    "version": "1.0"
  }
}

删除文件
DELETE https://tower.im/api/v1/uploads/{id}

Status: 204 OK
