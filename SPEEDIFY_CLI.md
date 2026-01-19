# Speedify CLI Reference

This document provides a comprehensive reference for all Speedify CLI commands. The CLI executable is located at `/usr/share/speedify/speedify_cli`.

**Source:** [Speedify CLI Documentation](https://support.speedify.com/article/285-speedify-cli)

---

## Table of Contents

- [Output Formatting](#output-formatting)
- [Exit Codes](#exit-codes)
- [Connection Commands](#connection-commands)
- [Authentication Commands](#authentication-commands)
- [Display Commands](#display-commands)
- [Adapter Management](#adapter-management)
- [Mode and Performance](#mode-and-performance)
- [Network Configuration](#network-configuration)
- [Streaming and Bypass](#streaming-and-bypass)
- [Privacy Commands](#privacy-commands)
- [Pair & Share Commands](#pair--share-commands)
- [Testing Commands](#testing-commands)
- [DSCP and Traffic Rules](#dscp-and-traffic-rules)
- [System Commands](#system-commands)

---

## Output Formatting

Global flags applicable to all commands:

| Flag | Description |
|------|-------------|
| `-s` | Single-line output format |
| `-t` | Adds title to all outputs |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success - JSON output to stdout |
| `1` | API error - JSON error on stderr |
| `2` | Invalid parameter - text error on stderr |
| `3` | Missing parameter - text error on stderr |
| `4` | Unknown parameter - full usage on stderr |

---

## Connection Commands

### connect
Establishes VPN connection to specified server.

```bash
speedify_cli connect [closest | public | private | p2p | <country> [<city> [<number>]] | last | <tag>]
```

**Examples:**
```bash
speedify_cli connect closest      # Connect to nearest server
speedify_cli connect us           # Connect to US server
speedify_cli connect us chicago   # Connect to Chicago, US
speedify_cli connect last         # Reconnect to last server
```

### disconnect
Terminates active VPN connection.

```bash
speedify_cli disconnect
```

### connectmethod
Sets default connection preference without connecting.

```bash
speedify_cli connectmethod <closest | public | private | p2p | <country> [<city> [<number>]] | <tag>>
```

### state
Retrieves current connection status.

```bash
speedify_cli state
```

**Possible states:**
- `LOGGED_OUT` - Not authenticated
- `LOGGING_IN` - Authentication in progress
- `LOGGED_IN` - Authenticated but not connected
- `AUTO_CONNECTING` - Automatic connection in progress
- `CONNECTING` - Manual connection in progress
- `DISCONNECTING` - Disconnection in progress
- `CONNECTED` - Active VPN connection
- `OVERLIMIT` - Data limit exceeded

---

## Authentication Commands

### login
Authenticates user credentials.

```bash
speedify_cli login <username> [password]
speedify_cli login auto
speedify_cli login oauth [access token]
```

### logout
Clears credentials and disconnects.

```bash
speedify_cli logout
```

### activationcode
Generates device activation code for my.speedify.com.

```bash
speedify_cli activationcode
```

### refresh oauth
Updates security token for same user.

```bash
speedify_cli refresh oauth [access token]
```

---

## Display Commands

### show adapters
Lists all network interfaces with settings.

```bash
speedify_cli show adapters
```

### show servers
Retrieves available VPN server list.

```bash
speedify_cli show servers
```

### show settings
Displays current connection configuration.

```bash
speedify_cli show settings
```

### show currentserver
Shows last/current connected server.

```bash
speedify_cli show currentserver
```

### show user
Outputs logged-in user information.

```bash
speedify_cli show user
```

### show privacy
Reveals privacy-related settings.

```bash
speedify_cli show privacy
```

### show connectmethod
Displays stored connection preference.

```bash
speedify_cli show connectmethod
```

### show streaming
Shows streaming mode configuration.

```bash
speedify_cli show streaming
```

### show streamingbypass
Displays VPN bypass rules.

```bash
speedify_cli show streamingbypass
```

### show disconnect
Reveals reason for last disconnection.

```bash
speedify_cli show disconnect
```

### show directory
Shows current directory server.

```bash
speedify_cli show directory
```

### show speedtest
Displays previous speed test results.

```bash
speedify_cli show speedtest
```

---

## Adapter Management

### adapter priority
Sets network adapter usage priority.

```bash
speedify_cli adapter priority <adapter id> <automatic|always|secondary|backup|never>
```

**Priority levels:**
| Priority | Description |
|----------|-------------|
| `automatic` | Speedify manages usage |
| `always` | Constant use |
| `secondary` | Backup to "always" adapters |
| `backup` | Fallback only |
| `never` | Disabled |

### adapter encryption
Controls encryption per adapter.

```bash
speedify_cli adapter encryption <adapter id> <on|off>
```

### adapter ratelimit
Throttles adapter speed.

```bash
speedify_cli adapter ratelimit <adapter id> <speed in bits per second|unlimited>
```

### adapter datalimit daily
Sets daily data cap.

```bash
speedify_cli adapter datalimit daily <adapter id> <data usage in bytes|unlimited>
```

### adapter datalimit monthly
Establishes monthly data limit.

```bash
speedify_cli adapter datalimit monthly <adapter id> <data usage in bytes|unlimited> <reset day|0>
```

### adapter datalimit dailyboost
Temporarily increases daily allowance.

```bash
speedify_cli adapter datalimit dailyboost <adapter id> <additional bytes>
```

### adapter overlimitratelimit
Applies throttle when data cap exceeded.

```bash
speedify_cli adapter overlimitratelimit <adapter id> <speed bits/second|0>
```

### adapter directionalmode
Configures upload/download behavior.

```bash
speedify_cli adapter directionalmode <adapter id> <upload mode> <download mode>
```

**Modes:** `on`, `backup_off`, `strict_off`

### adapter resetusage
Clears adapter statistics.

```bash
speedify_cli adapter resetusage <adapter id>
```

---

## Mode and Performance

### mode
Selects connection optimization strategy.

```bash
speedify_cli mode <redundant|speed|streaming>
```

| Mode | Description |
|------|-------------|
| `redundant` | Maximizes reliability, sends packets on multiple connections |
| `speed` | Maximizes throughput by combining bandwidth |
| `streaming` | Optimized for live streaming with balanced reliability |

### overflow
Sets secondary connection activation threshold.

```bash
speedify_cli overflow <speed in mbps>
```

Speed in Mbps after which secondary connections are not used.

### priorityoverflow
Configures priority connection threshold.

```bash
speedify_cli priorityoverflow <speed in mbps>
```

### packetpool
Selects packet buffer size.

```bash
speedify_cli packetpool <small|default|large>
```

### maxredundant
Sets redundant connection count.

```bash
speedify_cli maxredundant <number of conns>
```

### targetconnections
Specifies upload/download connection targets.

```bash
speedify_cli targetconnections <number upload connections> <number download connections>
```

---

## Network Configuration

### encryption
Enables/disables VPN traffic encryption globally.

```bash
speedify_cli encryption <on|off>
```

### headercompression
Toggles header compression.

```bash
speedify_cli headercompression <on|off>
```

### jumbo
Allows larger MTU packets.

```bash
speedify_cli jumbo <on|off>
```

### packetaggr
Controls packet aggregation.

```bash
speedify_cli packetaggr <on|off>
```

### dns
Sets custom DNS servers.

```bash
speedify_cli dns <ip address> ...
```

### transport
Selects network protocol.

```bash
speedify_cli transport <auto|tcp|tcp-multi|udp|https>
```

### route default
Controls default internet route via VPN.

```bash
speedify_cli route default <on|off>
```

### ports
Requests public ports on dedicated servers (settings apply after reconnect).

```bash
speedify_cli ports [port/proto] ...
```

### subnets
Configures downstream subnets for enterprise routing.

```bash
speedify_cli subnets [subnet/length] ...
```

---

## Streaming and Bypass

### streaming domains
Adds priority domains for streaming.

```bash
speedify_cli streaming domains <add|rem|set> <domain> ...
```

### streaming ipv4
Adds priority IPv4 addresses.

```bash
speedify_cli streaming ipv4 <add|rem|set> <ip address> ...
```

### streaming ipv6
Adds priority IPv6 addresses.

```bash
speedify_cli streaming ipv6 <add|rem|set> <ip address> ...
```

### streaming ports
Adds priority ports.

```bash
speedify_cli streaming ports <add|rem|set> [port[-range]/proto] ...
```

### streamingbypass domains
Bypasses VPN for specified domains.

```bash
speedify_cli streamingbypass domains <add|rem|set> [<domain> ...]
```

### streamingbypass ipv4
Bypasses VPN for IPv4 addresses.

```bash
speedify_cli streamingbypass ipv4 <add|rem|set> <ip address> ...
```

### streamingbypass ipv6
Bypasses VPN for IPv6 addresses.

```bash
speedify_cli streamingbypass ipv6 <add|rem|set> <ip address> ...
```

### streamingbypass ports
Bypasses VPN for ports.

```bash
speedify_cli streamingbypass ports <add|rem|set> <port[-range]/proto> ...
```

### streamingbypass service
Controls service-specific bypass rules.

```bash
speedify_cli streamingbypass service <enable|disable|service name> [<on|off>]
```

---

## Privacy Commands

### privacy dnsleak
DNS leak prevention (Windows only).

```bash
speedify_cli privacy dnsleak <on|off>
```

### privacy ipleak
IP leak prevention (Windows only).

```bash
speedify_cli privacy ipleak <on|off>
```

### privacy killswitch
Firewall rules to block non-VPN traffic (Windows only).

```bash
speedify_cli privacy killswitch <on|off>
```

### privacy apiProtection
Protects API communications.

```bash
speedify_cli privacy apiProtection <on|off>
```

### privacy advancedIspStats
Controls ISP statistics collection.

```bash
speedify_cli privacy advancedIspStats <on|off>
```

### privacy requestToDisableDoH
Requests browser DoH disabling.

```bash
speedify_cli privacy requestToDisableDoH <on|off>
```

---

## Pair & Share Commands

### networksharing set
Configures device sharing role.

```bash
speedify_cli networksharing set <host|client> <on|off>
```

### networksharing availableshares
Lists discoverable peers.

```bash
speedify_cli networksharing availableshares
```

### networksharing discovery
Shows discovery status.

```bash
speedify_cli networksharing discovery
```

### networksharing startdiscovery
Initiates peer discovery.

```bash
speedify_cli networksharing startdiscovery
```

### networksharing connect
Pairs using connect code.

```bash
speedify_cli networksharing connect <peer connect code>
```

### networksharing peer
Manages peer relationships.

```bash
speedify_cli networksharing peer <allow|reject|request|unpair> <peer uuid>
```

### networksharing reconnect
Re-establishes peer connection.

```bash
speedify_cli networksharing reconnect <peer uuid>
```

### networksharing settings
Displays current sharing configuration.

```bash
speedify_cli networksharing settings
```

### networksharing set displayname
Sets device display name.

```bash
speedify_cli networksharing set displayname <new name>
```

### networksharing set pairRequestBehavior
Controls incoming request handling.

```bash
speedify_cli networksharing set pairRequestBehavior <ask|accept|reject>
```

### networksharing set alwaysOnDiscovery
Enables continuous peer discovery.

```bash
speedify_cli networksharing set alwaysOnDiscovery <on|off>
```

### networksharing set autoPairBehavior
Configures automatic pairing.

```bash
speedify_cli networksharing set autoPairBehavior <manual|auto_user|auto_user_team>
```

### networksharing set peer
Manages individual peer settings.

```bash
speedify_cli networksharing set peer <autoreconnect|allowhost|allowclient> <peer uuid> <on|off>
```

---

## Testing Commands

### speedtest
Runs performance evaluation over VPN tunnel using bundled iPerf3 client.

```bash
speedify_cli speedtest [adapter id]
```

### streamtest
Simulates live streaming conditions (sends 60 Mbps UDP traffic).

```bash
speedify_cli streamtest [adapter id]
```

---

## DSCP and Traffic Rules

### dscp queues add
Creates DSCP queue rules.

```bash
speedify_cli dscp queues add [<dscp 0-63> [priority] <on|off|auto> [replication] <on|off|auto> [retransmissions] <0-255>] ...
```

### dscp queues set
Modifies existing DSCP rules.

```bash
speedify_cli dscp queues set [<dscp 0-63> [priority] <on|off|auto> [replication] <on|off|auto> [retransmissions] <0-255>] ...
```

### dscp queues rem
Deletes DSCP queue rules.

```bash
speedify_cli dscp queues rem [dscp value 0-63] ...
```

### fixeddelay domains
Applies latency to domain traffic.

```bash
speedify_cli fixeddelay domains <add|rem|set> <domain> ...
```

### fixeddelay ips
Applies latency to IP traffic.

```bash
speedify_cli fixeddelay ips <add|rem|set> <ip address> ...
```

### fixeddelay ports
Applies latency to port traffic.

```bash
speedify_cli fixeddelay ports <add|rem|set> [port[-range]/proto] ...
```

---

## System Commands

### stats
Subscribes to real-time connection statistics.

```bash
speedify_cli stats [historic | [duration seconds] [networksharing] [current|day|week|month|total|<hours>] ...]
```

**Examples:**
```bash
speedify_cli stats 1              # Get stats once (1 second)
speedify_cli stats 5              # Stream stats for 5 seconds
speedify_cli stats historic day   # Get historical daily stats
```

### startupconnect
Enables automatic connection at startup.

```bash
speedify_cli startupconnect <on|off>
```

### version
Displays installed Speedify version.

```bash
speedify_cli version
```

### daemon exit
Terminates Speedify service (use with caution).

```bash
speedify_cli daemon exit
```

### directory
Configures directory server.

```bash
speedify_cli directory [directory server domain]
```

### gateway
Sets OAuth gateway URL.

```bash
speedify_cli gateway [directory gateway uri]
```

### connectretry
Sets retry timeout for connections.

```bash
speedify_cli connectretry <time in seconds>
```

### transportretry
Sets retry timeout for transport.

```bash
speedify_cli transportretry <time in seconds>
```

### log erase
Clears log files.

```bash
speedify_cli log erase
```

### log daemon
Configures daemon logging.

```bash
speedify_cli log daemon <file size> <files per daemon> <total files> <verbose|info|warn|error>
```

---

## Captive Portal Commands

### captiveportal check
Detects portal blocking.

```bash
speedify_cli captiveportal check
```

Returns array of adapter IDs blocked by captive portals.

### captiveportal login
Manages portal authentication flow.

```bash
speedify_cli captiveportal login <on|off> <adapter id>
```

Directs web traffic through specified adapter for login.

---

## Commands Used by This Dashboard

The dashboard (`app.py`) uses the following CLI commands:

| Command | Endpoint | Purpose |
|---------|----------|---------|
| `stats 1` | `/api/status` | Get real-time connection statistics |
| `show settings` | `/api/status` | Get current bonding mode |
| `show currentserver` | `/api/server` | Get server location and public IP |
| `mode <mode>` | `/api/change-mode` | Switch bonding mode |

---

## Planned CLI Integrations

The dashboard can be extended to leverage many more CLI commands. See the **"CLI-Based Features"** section in `ROADMAP.md` for a comprehensive list of planned integrations, including:

- **Monitoring features:** `state`, `show disconnect`, `show adapters`, `captiveportal check`, `show servers`
- **Control features:** `adapter priority`, `adapter datalimit`, `connect`, `disconnect`
- **Diagnostics:** `speedtest`, `streamtest`, `show speedtest`
- **Event-specific:** POS mode presets, streaming readiness checks, carrier failover status

Each planned feature includes the CLI command mapping, proposed API endpoint, value assessment, and implementation complexity.
