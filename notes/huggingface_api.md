让我从源码提取 HfApi 类的所有方法。


用户想了解 HfApi 一共提供了哪些 API，列出名称和作用。这是一个文档性/查询性问题。HfApi 类有很多方法，我可以从源码中提取所有方法名。

让我从 hf_api.py 里提取 HfApi 类的所有方法。这个类方法很多（几百个），我可以列出主要的、分类的 API。

我需要先看看 HfApi 类的所有方法。方法定义格式 `def method_name`。让我 grep 出来。

用户当前的文件版本变了（又回退了，第 9 行是 `login()`，没有 Path 了）。但这不是重点，用户只是问 HfApi 的方法列表。

我应该提取 HfApi 的所有方法名。让我 grep hf_api.py 里 HfApi 类定义之后的所有 `def `。

HfApi 类从 2238 行开始，到文件结束。方法非常多。让我 grep 出来。

HfApi 有非常多的方法（200+ 个公开方法）。用户问"一共提供了哪些 api，列出名称和作用"。列出 200 个太多了，我应该按类别归纳整理，列主要的常用 API，并说明类别。这样更有用。

让我按功能分类整理这些方法。注意过滤掉内部方法（下划线开头）和 `__init__` 等。

公开方法分类：

1. **身份/认证**
   - `whoami()` - 当前登录用户信息
   - `auth_check()` - 检查权限

2. **模型/数据集/Space 列表与搜索**
   - `list_models()` - 列出模型
   - `list_datasets()` - 列出数据集
   - `list_spaces()` - 列出 Spaces
   - `search_spaces()` - 搜索 Spaces
   - `list_user_repos()` - 列出用户仓库
   - `list_liked_repos()` - 列出点赞仓库
   - `like()/unlike()` - 点赞/取消
   - `list_repo_likers()` - 仓库点赞者

3. **仓库信息**
   - `model_info()` / `dataset_info()` / `space_info()` / `kernel_info()` - 仓库元信息
   - `repo_info()` - 通用仓库信息
   - `repo_exists()` / `revision_exists()` / `file_exists()` - 存在性检查
   - `list_repo_files()` / `list_repo_tree()` - 文件列表
   - `list_repo_commits()` / `list_repo_refs()` - 提交/引用
   - `resolve_revision()` - 解析版本
   - `get_paths_info()` - 路径信息
   - `get_model_tags()` / `get_dataset_tags()` - 标签

4. **仓库管理**
   - `create_repo()` - 创建仓库
   - `delete_repo()` - 删除仓库
   - `update_repo_settings()` - 更新设置
   - `move_repo()` - 移动/重命名
   - `duplicate_repo()` / `duplicate_space()` - 复制
   - `get_full_repo_name()` - 完整名称
   - `super_squash_history()` - 压缩历史

5. **文件上传/下载**
   - `create_commit()` - 多文件提交
   - `upload_file()` - 上传单文件
   - `upload_folder()` - 上传文件夹
   - `upload_large_folder()` - 大文件夹
   - `delete_file()` / `delete_files()` / `delete_folder()` - 删除
   - `download_bucket_files()`... 这个是 bucket
   - `hf_hub_download()` / `snapshot_download()` - 下载
   - `preupload_lfs_files()` - LFS
   - `list_lfs_files()` / `permanently_delete_lfs_files()` - LFS 管理
   - `verify_repo_checksums()` - 校验

6. **分支/标签**
   - `create_branch()` / `delete_branch()`
   - `create_tag()` / `delete_tag()`

7. **讨论/PR**
   - `get_repo_discussions()` - 讨论列表
   - `get_discussion_details()`
   - `create_discussion()` / `create_pull_request()`
   - `comment_discussion()`
   - `rename_discussion()` / `change_discussion_status()`
   - `merge_pull_request()`
   - `edit_discussion_comment()` / `hide_discussion_comment()`

8. **Space 管理**
   - `add_space_secret()` / `delete_space_secret()` / `get_space_secrets()` - 密钥
   - `get_space_variables()` / `add_space_variable()` / `delete_space_variable()`
   - `get_space_runtime()` / `list_spaces_hardware()` / `request_space_hardware()`
   - `set_space_sleep_time()` / `pause_space()`
   - `enable_space_dev_mode()` / `disable_space_dev_mode()` / `restart_space()`
   - `fetch_space_logs()` / `wait_for_space()`
   - `request_space_storage()` / `set_space_volumes()` 等

9. **Inference Endpoints**
   - `list_inference_endpoints()` / `create_inference_endpoint()` / `get_inference_endpoint()`
   - `update_inference_endpoint()` / `delete_inference_endpoint()`
   - `pause_inference_endpoint()` / `resume_inference_endpoint()` / `scale_to_zero_inference_endpoint()`
   - `list_inference_endpoints_hardware()`

10. **Collections（收藏集）**
    - `list_collections()` / `get_collection()` / `create_collection()`
    - `update_collection_metadata()` / `delete_collection()`
    - `add_collection_item()` / `update_collection_item()` / `delete_collection_item()`

11. **Gated 访问请求（门禁仓库）**
    - `list_pending_access_requests()` / `list_accepted_access_requests()` / `list_rejected_access_requests()`
    - `cancel_access_request()` / `accept_access_request()` / `reject_access_request()`
    - `grant_access()`

12. **Webhooks**
    - `get_webhook()` / `list_webhooks()` / `create_webhook()` / `update_webhook()`
    - `enable_webhook()` / `disable_webhook()` / `delete_webhook()`

13. **用户/组织**
    - `get_user_overview()` / `get_organization_overview()`
    - `list_organization_members()` / `list_organization_followers()`
    - `list_user_followers()` / `list_user_following()`

14. **Papers（论文）**
    - `list_papers()` / `paper_info()` / `read_paper()` / `list_daily_papers()`

15. **Jobs（Hugging Face 计算任务）**
    - `run_job()` / `list_jobs()` / `inspect_job()` / `cancel_job()`
    - `wait_for_job()` / `fetch_job_logs()` / `fetch_job_metrics()`
    - `run_uv_job()` / `create_scheduled_job()` 等

16. **Buckets（对象存储）**
    - `create_bucket()` / `bucket_info()` / `list_buckets()` / `delete_bucket()` / `move_bucket()`
    - `list_bucket_tree()` / `sync_bucket()` / `download_bucket_files()`

17. **其他/工具**
    - `run_as_future()` - 后台运行
    - `get_hf_file_metadata()` / `get_safetensors_metadata()`
    - `list_space_templates()` / `list_inference_catalog()`

这个列表太长。用户问"一共提供了哪些api,请列出名称和作用"。我应该给一个分类整理的精简版本，聚焦常用 API，但要覆盖主要类别。完全列出 200 个没必要，反而信息过载。我会按类别列出主要 API 及其作用，并说明"总共约 200+ 个方法"。

让我整理一个结构化的回答。用户是中文，用中文回答。

我会用 Markdown 表格或分组列表。为了可读性，用分组 + 方法名 + 作用。聚焦常用/核心的，其余归类概括。
HfApi 是 huggingface_hub 的核心客户端，**公开方法共 200+ 个**（不含 `_` 开头的内部方法），覆盖 Hub 几乎所有功能。全部列出来会很长，我按**功能分类**整理如下（每个方法一句话说明作用）：

## 身份与权限
| 方法 | 作用 |
|---|---|
| `whoami()` | 查询当前登录用户信息（你脚本就在用） |
| `auth_check()` | 校验 token 对某个仓库的权限（read/write） |

## 搜索与列举
| 方法 | 作用 |
|---|---|
| `list_models()` / `list_datasets()` / `list_spaces()` | 按条件列出模型/数据集/Space |
| `search_spaces()` | 搜索 Spaces |
| `list_user_repos()` | 列出某用户的仓库 |
| `list_liked_repos()` / `like()` / `unlike()` | 点赞/取消点赞 |
| `get_model_tags()` / `get_dataset_tags()` | 获取所有可用的 tag 列表 |

## 仓库信息查询
| 方法 | 作用 |
|---|---|
| `model_info()` / `dataset_info()` / `space_info()` | 获取模型/数据集/Space 元信息 |
| `repo_info()` | 通用仓库信息 |
| `repo_exists()` / `revision_exists()` / `file_exists()` | 检查仓库/版本/文件是否存在 |
| `list_repo_files()` / `list_repo_tree()` | 列出仓库文件 / 目录树 |
| `list_repo_commits()` / `list_repo_refs()` | 提交历史 / 分支标签列表 |
| `resolve_revision()` | 解析分支/tag/commit 到具体版本 |
| `get_paths_info()` | 获取指定路径的 LFS/大小等信息 |
| `get_full_repo_name()` | 把短名字补全成 `owner/repo` |

## 仓库管理
| 方法 | 作用 |
|---|---|
| `create_repo()` / `delete_repo()` | 创建/删除仓库 |
| `update_repo_settings()` | 更新仓库设置（private 等） |
| `move_repo()` | 移动/重命名仓库 |
| `duplicate_repo()` / `duplicate_space()` | 复制仓库/Space |
| `super_squash_history()` | 把仓库历史压平成单次提交 |

## 文件上传 / 下载 / 删除
| 方法 | 作用 |
|---|---|
| `create_commit()` | 一次提交多个文件操作（add/update/delete） |
| `upload_file()` / `upload_folder()` | 上传单文件/整个文件夹 |
| `upload_large_folder()` | 大文件夹分片上传 |
| `delete_file()` / `delete_files()` / `delete_folder()` | 删除文件/文件夹 |
| `hf_hub_download()` / `snapshot_download()` | 下载单文件 / 整个仓库快照 |
| `get_hf_file_metadata()` | 获取远端文件元信息 |
| `preupload_lfs_files()` / `list_lfs_files()` / `permanently_delete_lfs_files()` | LFS 大文件管理 |
| `verify_repo_checksums()` | 校验仓库 LFS 文件完整性 |
| `get_safetensors_metadata()` | 获取 safetensors 文件元数据 |

## 分支与标签
| 方法 | 作用 |
|---|---|
| `create_branch()` / `delete_branch()` | 创建/删除分支 |
| `create_tag()` / `delete_tag()` | 创建/删除 tag |

## 讨论与 Pull Request
| 方法 | 作用 |
|---|---|
| `get_repo_discussions()` / `get_discussion_details()` | 讨论列表/详情 |
| `create_discussion()` / `create_pull_request()` | 发起讨论 / PR |
| `comment_discussion()` | 发表评论 |
| `edit_discussion_comment()` / `hide_discussion_comment()` | 编辑/隐藏评论 |
| `merge_pull_request()` | 合并 PR |
| `change_discussion_status()` | 打开/关闭讨论 |

## Space 管理
| 方法 | 作用 |
|---|---|
| `add_space_secret()` / `get_space_secrets()` / `delete_space_secret()` | Space 密钥管理 |
| `add_space_variable()` / `get_space_variables()` / `delete_space_variable()` | Space 环境变量 |
| `get_space_runtime()` / `list_spaces_hardware()` / `request_space_hardware()` | 运行状态 / 硬件申请 |
| `pause_space()` / `restart_space()` / `wait_for_space()` | 暂停 / 重启 / 等待就绪 |
| `fetch_space_logs()` | 拉取运行日志 |
| `set_space_sleep_time()` / `request_space_storage()` / `set_space_volumes()` | 休眠 / 存储 / 挂载卷 |

## Inference Endpoints（推理端点）
| 方法 | 作用 |
|---|---|
| `list_inference_endpoints()` / `create_inference_endpoint()` / `get_inference_endpoint()` | 列出/创建/查询推理端点 |
| `update_inference_endpoint()` / `delete_inference_endpoint()` | 更新/删除端点 |
| `pause_inference_endpoint()` / `resume_inference_endpoint()` / `scale_to_zero_inference_endpoint()` | 暂停/恢复/缩零 |
| `list_inference_endpoints_hardware()` | 硬件选项 |

## Collections（收藏集）
| 方法 | 作用 |
|---|---|
| `list_collections()` / `get_collection()` / `create_collection()` | 列出/获取/创建收藏集 |
| `add_collection_item()` / `update_collection_item()` / `delete_collection_item()` | 收藏集条目增删改 |
| `delete_collection()` | 删除收藏集 |

## 门禁仓库（Gated Repos）权限申请
| 方法 | 作用 |
|---|---|
| `list_pending_access_requests()` / `list_accepted_access_requests()` / `list_rejected_access_requests()` | 待处理/已通过/已拒绝的申请 |
| `accept_access_request()` / `reject_access_request()` / `cancel_access_request()` | 通过/拒绝/取消申请 |
| `grant_access()` | 直接授权访问 |

## Webhooks
| 方法 | 作用 |
|---|---|
| `list_webhooks()` / `get_webhook()` / `create_webhook()` / `update_webhook()` | Webhook 增删改查 |
| `enable_webhook()` / `disable_webhook()` / `delete_webhook()` | 启用/禁用/删除 |

## 用户与组织
| 方法 | 作用 |
|---|---|
| `get_user_overview()` / `get_organization_overview()` | 用户/组织信息 |
| `list_user_followers()` / `list_user_following()` | 用户粉丝/关注列表 |
| `list_organization_members()` / `list_organization_followers()` | 组织成员/关注者 |

## Papers（论文库）
| 方法 | 作用 |
|---|---|
| `list_papers()` / `list_daily_papers()` | 论文列表 / 每日论文 |
| `paper_info()` / `read_paper()` | 论文信息 / 全文 |

## Jobs（Hub 上的计算任务）与 Buckets（对象存储）
- **Jobs**：`run_job()` / `run_uv_job()` / `list_jobs()` / `inspect_job()` / `cancel_job()` / `wait_for_job()` / `fetch_job_logs()` / `create_scheduled_job()` 等，用于提交/管理云端训练任务和定时任务。
- **Buckets**：`create_bucket()` / `list_buckets()` / `delete_bucket()` / `sync_bucket()` / `download_bucket_files()` / `copy_files()` 等，用于 Hugging Face 对象存储。

## 工具方法
| 方法 | 作用 |
|---|---|
| `run_as_future()` | 让某个 API 调用在后台线程异步执行 |
| `list_space_templates()` / `list_inference_catalog()` | 列出 Space 模板 / 推理目录 |

---

**和你项目最相关的是**：`whoami`（在用）、`create_repo`（推模型时自动建仓）、`upload_file`/`upload_folder`、`repo_info`、`model_info`、`list_repo_files`。你 [eegnet_hub_example.py](file:///Users/usst_ziyi/Programs/ChatGPT/braindecode-hugingface/src/eegnet_hub_example.py#L109-L113) 里的 `model.push_to_hub()` 底层就是在调 `create_commit` / `upload_file` / `create_repo` 这一族。

如果需要某个具体方法的完整参数说明，告诉我方法名，我可以展开讲。