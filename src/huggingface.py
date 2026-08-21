from huggingface_hub import login
from huggingface_hub import auth_list
from huggingface_hub import auth_switch
from huggingface_hub import HfApi, get_token
from huggingface_hub import auth_check
import os
import socket
import time
import httpx

# ---- 网络策略：直连优先(3s 探测)，失败/超时则走本机代理 ----
PROXY = "http://127.0.0.1:7897"

def _configure_network():
    try:
        socket.create_connection(("huggingface.co", 443), timeout=3).close()
        print("[网络] 直连 huggingface.co 可用")
    except OSError:
        for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
            os.environ.setdefault(var, PROXY)
        print(f"[网络] 直连失败，走代理 {PROXY}")

def _retry(fn, tries=2):
    """网络调用失败(连接/SSL/超时)时重试，最多 tries 次。"""
    for i in range(1, tries + 1):
        try:
            return fn()
        except (OSError, ConnectionError, TimeoutError, httpx.HTTPError) as e:
            if i == tries:
                raise
            print(f"[网络] 请求失败({e.__class__.__name__})，第 {i} 次重试...")
            time.sleep(1)

_configure_network()

# 登录
# login(token="hf_xxx")                              # 直接传 token
# login(token="hf_xxx", add_to_git_credential=True)    # 同时写入 git 凭据
login()                                             # 浏览器 OAuth / 手动粘贴
# login(skip_if_logged_in=False)                      # 强制重新登录

# 获取当前登录的token
# token = get_token()
# print(f"当前登录的token:={token}")

# 查看本地所有token
auth_list()

# # 切换本地token
# auth_switch("hub_write")       
# auth_list()



api = HfApi()
info = _retry(api.whoami)

def _fmt_bool(v):
    return "是" if v else "否"

print("=" * 48)
print("  Hugging Face 账号信息")
print("=" * 48)
print(f"  用户名      : {info['name']}")
print(f"  全名        : {info.get('fullname', '')}")
print(f"  用户 ID     : {info['id']}")
print(f"  账号类型    : {info['type']}")
print(f"  Pro 会员    : {_fmt_bool(info.get('isPro', False))}")
orgs = info.get('orgs', [])
print(f"  所属组织    : {', '.join(orgs) if orgs else '无'}")
print("-" * 48)
print("  认证信息")
print("-" * 48)
auth = info.get('auth', {})
print(f"  认证类型    : {auth.get('type', '')}")
token = auth.get('accessToken', {})
print(f"  Token 名    : {token.get('displayName', '')}")
print(f"  Token 角色  : {token.get('role', '')}")
print(f"  创建时间    : {token.get('createdAt', '')}")
fg = token.get('fineGrained', {})
print(f"  可读 Gated  : {_fmt_bool(fg.get('canReadGatedRepos', False))}")
print(f"  全局权限    : {', '.join(fg.get('global', [])) or '无'}")
for s in fg.get('scoped', []):
    entity = s.get('entity', {})
    perms = ', '.join(s.get('permissions', []))
    print(f"  范围权限    : {entity.get('name', '')} -> {perms}")
print("=" * 48)




# def resolve_token(token: str | None) -> str | None:
#     """优先级：命令行 token > HUGGINGFACE_TOKEN > HF_TOKEN。"""
#     return token or os.environ.get("HUGGINGFACE_TOKEN") or os.environ.get("HF_TOKEN")

# print(resolve_token(None))

info = _retry(lambda: api.model_info("usst-ziyi/eegnet-bnci2014-001"))

print(f"仓库 ID   : {info.id}")          # e.g. "usst-ziyi/eegnet-bnci2014-001"
print(f"作者      : {info.author}")
print(f"下载量    : {info.downloads}")
print(f"点赞数    : {info.likes}")
print(f"标签      : {info.tags}")         # e.g. ['pytorch', 'eegnet', ...]
print(f"可见性    : {info.private}")       # True 表示私有
last_mod = info.last_modified
if last_mod.tzinfo is not None:              # 是带时区的 UTC 时间，转成本地时间
    last_mod = last_mod.astimezone()
print(f"最后更新  : {last_mod:%Y-%m-%d %H:%M:%S} (北京时间)")
print(f"是否 Gated: {info.gated}")        # 是否需要同意条款

# 文件列表（配合 files_metadata=True 会有大小等信息）
for s in info.siblings:
    print(f"  - {s.rfilename}")


# 卡片信息（需要 expand=["cardData"]）
info = _retry(lambda: api.model_info("usst-ziyi/eegnet-bnci2014-001", expand=["cardData"]))
print(f"卡片数据: {info.card_data}")          # YAML 头部，如 license、base_model 等

# 完整 README 内容需单独下载（ModelInfo 没有 card 属性）
from huggingface_hub import hf_hub_download
readme_path = _retry(lambda: hf_hub_download(
    repo_id="usst-ziyi/eegnet-bnci2014-001",
    filename="README.md",
))
with open(readme_path, "r", encoding="utf-8") as f:
    print("卡片内容:")
    print(f.read())
