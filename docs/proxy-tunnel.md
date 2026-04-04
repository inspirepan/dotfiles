# 代理 + Tunnel / VPN 共存

TUN 模式代理（Mihomo/Clash）与 Cloudflare Tunnel、Tailscale 的共存配置。

---

## Cloudflare Tunnel 与 TUN 模式

### 问题

TUN 模式（fake-ip）会破坏 `cloudflared` 的连接。

`cloudflared` 会通过 SRV DNS 查询（`_v2-origintunneld._tcp.argotunnel.com`）
直接获取 Cloudflare 边缘 IP（`198.41.x.x`）。这些 IP 会绕过 fake-ip 的
A/AAAA 映射，所以基于域名的 `DIRECT` 规则无法命中。TUN 会拦截这条连接并把它
通过代理转发，最终导致 TLS 握手时出现 EOF。

### 修复：Clash Verge

需要做三件事：

1. **规则增强**（在当前 profile 的 rules 文件里追加前置规则；订阅刷新后依然保留）：

```yaml
- PROCESS-NAME,cloudflared,DIRECT
- DOMAIN-SUFFIX,argotunnel.com,DIRECT
```

2. **合并配置**（通过 `fake-ip-filter` 让 tunnel 相关 DNS 返回真实 IP）：

```yaml
dns:
  fake-ip-filter:
    - ".argotunnel.com"
```

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

- 在 Clash Verge 中，规则增强文件（prepend rules）会在订阅刷新后保留。主配置 `clash-verge.yaml` 会重新生成，但增强配置会自动合并进去。
- 在 Mihomo Party 中，`mihomo.yaml` 是全局基础配置，不会被订阅更新覆盖。`work/config.yaml` 是自动生成的，不要把需要持久保留的改动写进去。
- 对于 SRV 查询或直接连 IP 的场景，基于域名的 `DIRECT` 规则不会生效。必须使用 `route-exclude-address`、`IP-CIDR` 或 `PROCESS-NAME` 规则。
- `198.41.128.0/17` 覆盖了 Cloudflare Tunnel 的边缘节点范围：`198.41.128.0` 到 `198.41.255.255`。

---

## Tailscale 与 TUN 模式（Clash Verge）

### 为 Tailscale 子网绕过 TUN

在 Clash Verge 的 merge config（不会被订阅覆盖的 profile yaml）中加入：

```yaml
tun:
  route-exclude-address:
    - 100.64.0.0/10
    - fd7a:115c:a1e0::/48
```

### 用规则让 Tailscale 流量走 DIRECT

在 Clash Verge 的 prepend rules 中加入：

```yaml
- DOMAIN-SUFFIX,tailscale.com,DIRECT
- DOMAIN-SUFFIX,tailscale.io,DIRECT
- IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
- IP-CIDR6,fd7a:115c:a1e0::/48,DIRECT,no-resolve
```

### 关闭 Tailscale MagicDNS

```bash
tailscale set --accept-dns=false
```

这样可以避免 Tailscale 把系统 DNS 劫持到 `100.100.100.100`，否则会和 Clash
TUN 的 DNS 劫持（`any:53` -> fake-ip）冲突。

权衡：不能再使用 Tailscale 主机名（例如 `ssh machine-name`），必须改用
Tailscale IP（例如 `ssh 100.65.x.x`）。该设置在重启后依然保留。
