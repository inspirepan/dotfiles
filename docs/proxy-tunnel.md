# 代理 + Tunnel / VPN 共存

TUN 模式代理（FlClash / Mihomo）与 Cloudflare Tunnel、Tailscale 的共存配置。

FlClash 配置目录：`~/Library/Application Support/com.follow.clash/`

---

## FlClash 覆写机制

FlClash 通过 **覆写（Overwrite）** 页面管理用户自定义规则，支持两种模式：

- **Standard 模式**：在 UI 中添加/编辑/排序规则，规则存储在本地 SQLite 数据库中，前置到订阅规则之前。订阅刷新后自动重新合并，不会丢失。
- **Script 模式**：编写 JavaScript 脚本对整个配置进行任意修改，适合修改 DNS、TUN 等非规则字段。

操作路径：**配置 (Profiles) -> 选中 profile -> 覆写 (Overwrite)**

一键配置常用覆写规则（SSH / Cloudflare Tunnel / Tailscale 直连）：

```bash
~/code/dotfiles/scripts/setup-flclash.sh
```

---

## Cloudflare Tunnel 与 TUN 模式

### 问题

TUN 模式（fake-ip）会破坏 `cloudflared` 的连接。

`cloudflared` 会通过 SRV DNS 查询（`_v2-origintunneld._tcp.argotunnel.com`）
直接获取 Cloudflare 边缘 IP（`198.41.x.x`）。这些 IP 会绕过 fake-ip 的
A/AAAA 映射，所以基于域名的 `DIRECT` 规则无法命中。TUN 会拦截这条连接并把它
通过代理转发，最终导致 TLS 握手时出现 EOF。

### 修复：FlClash

需要做两件事：

1. **添加覆写规则**（覆写 → Standard → 添加规则，前置到订阅规则之前）：

```
PROCESS-NAME,cloudflared,DIRECT
DOMAIN-SUFFIX,argotunnel.com,DIRECT
```

2. **修改 DNS fake-ip-filter**（覆写 → Script，让 tunnel 相关 DNS 返回真实 IP）：

```javascript
function main(config) {
  if (!config.dns) config.dns = {};
  if (!config.dns['fake-ip-filter']) config.dns['fake-ip-filter'] = [];
  config.dns['fake-ip-filter'].push('.argotunnel.com');
  return config;
}
```

或者在 FlClash 的 **设置 → 覆写 → DNS** 中手动添加 fake-ip-filter 条目。

3. **只保留一个 `cloudflared` 服务**：如果同时安装了 Homebrew 版本和官方安装器版本，停掉 Homebrew 的那个：

```bash
brew services stop cloudflared
launchctl disable user/$(id -u)/homebrew.mxcl.cloudflared
```

最终只应有 `com.cloudflare.cloudflared` 在运行。

### 修复：Mihomo Party

在 `~/Library/Application Support/mihomo-party/mihomo.yaml` 中，把 Cloudflare
边缘 IP 加到 `route-exclude-address`：

```yaml
tun:
  route-exclude-address:
    - 198.41.128.0/17   # Cloudflare Tunnel 边缘 IP
```

然后重载配置并重启 `cloudflared`：

```bash
launchctl stop com.cloudflare.cloudflared
launchctl start com.cloudflare.cloudflared
```

### 说明

- 在 FlClash 中，覆写规则存储在本地数据库，订阅刷新后自动前置合并，不会被覆盖。`config.yaml` 是运行时自动生成的合并结果，不要直接编辑。
- 在 Mihomo Party 中，`mihomo.yaml` 是全局基础配置，不会被订阅更新覆盖。`work/config.yaml` 是自动生成的，不要把需要持久保留的改动写进去。
- 对于 SRV 查询或直接连 IP 的场景，基于域名的 `DIRECT` 规则不会生效。必须使用 `route-exclude-address`、`IP-CIDR` 或 `PROCESS-NAME` 规则。
- `198.41.128.0/17` 覆盖了 Cloudflare Tunnel 的边缘节点范围：`198.41.128.0` 到 `198.41.255.255`。

---

## SSH 与 TUN 模式

### 问题

TUN 模式会接管所有流量，包括 SSH 连接。SSH 是长连接且非 HTTP 协议，
经过 TUN 处理后连接会被截断，表现为 `Connection closed by x.x.x.x port 22`。

### 修复：FlClash

在覆写（Standard 模式）中添加规则：

```
PROCESS-NAME,ssh,DIRECT
```

所有 `ssh` 进程的流量会绕过 TUN 直连，不影响其他代理规则。

### 说明

- `dotfiles/ssh/.ssh/config` 中已配置 GitHub SSH 走 `ssh.github.com:443`，stow 后生效，作为额外的保障。
- 如果只需要解决 GitHub 的问题，也可以只加 `DOMAIN-SUFFIX,github.com,DIRECT`，但 `PROCESS-NAME,ssh` 更通用，覆盖所有 SSH 连接。

---

## Tailscale 与 TUN 模式（FlClash）

### 为 Tailscale 子网绕过 TUN

在覆写（Script 模式）中添加 route-exclude-address：

```javascript
function main(config) {
  if (!config.tun) config.tun = {};
  if (!config.tun['route-exclude-address']) config.tun['route-exclude-address'] = [];
  config.tun['route-exclude-address'].push('100.64.0.0/10');
  config.tun['route-exclude-address'].push('fd7a:115c:a1e0::/48');
  return config;
}
```

### 用规则让 Tailscale 流量走 DIRECT

在覆写（Standard 模式）中添加规则：

```
DOMAIN-SUFFIX,tailscale.com,DIRECT
DOMAIN-SUFFIX,tailscale.io,DIRECT
IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
IP-CIDR6,fd7a:115c:a1e0::/48,DIRECT,no-resolve
```

### 关闭 Tailscale MagicDNS

```bash
tailscale set --accept-dns=false
```

这样可以避免 Tailscale 把系统 DNS 劫持到 `100.100.100.100`，否则会和
TUN 的 DNS 劫持（`any:53` -> fake-ip）冲突。

权衡：不能再使用 Tailscale 主机名（例如 `ssh machine-name`），必须改用
Tailscale IP（例如 `ssh 100.65.x.x`）。该设置在重启后依然保留。
