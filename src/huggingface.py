from huggingface_hub import login
from huggingface_hub import auth_list
from huggingface_hub import auth_switch
from huggingface_hub import HfApi, get_token

# 登录
# login(token="hf_xxx")                              # 直接传 token
# login(token="hf_xxx", add_to_git_credential=True)    # 同时写入 git 凭据
login()                                             # 浏览器 OAuth / 手动粘贴
# login(skip_if_logged_in=False)                      # 强制重新登录

# 获取当前登录的token
token = get_token()
# print(f"当前登录的token:={token}")

# 查看本地所有token
auth_list()

# # 切换本地token
# auth_switch("hub_write")       
# auth_list()



api = HfApi()
info = api.whoami()
for key, value in info.items():
    print(f"{key}: {value}")


# 检查读写权限
tok = info["auth"]["accessToken"]
perms = tok.get("fineGrained", {}).get("scoped", [])
can_write = any("repo.write" in p["permissions"] for p in perms)
print(f"user={info['name']} token={tok['displayName']} role={tok['role']} can_write={can_write}")

can_read = any("repo.access.read" in p["permissions"] for p in perms)
print(f"user={info['name']} token={tok['displayName']} role={tok['role']} can_read={can_read}")