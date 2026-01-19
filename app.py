from flask import Flask, jsonify, render_template, request
import subprocess
import json
import datetime

app = Flask(__name__)

def run_speedify_cli(cmd_args):
    try:
        result = subprocess.run(['/usr/share/speedify/speedify_cli'] + cmd_args,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              timeout=10)
        # Parse the complex JSON structure returned by Speedify CLI
        raw_output = result.stdout.strip()
        
        # The output contains multiple JSON arrays, we need to parse each section
        sections = {}
        lines = raw_output.split('\n')
        current_json = ""
        
        for line in lines:
            if line.strip():
                current_json += line
            else:
                if current_json.strip():
                    try:
                        parsed = json.loads(current_json)
                        if isinstance(parsed, list) and len(parsed) >= 2:
                            section_name = parsed[0]
                            section_data = parsed[1]
                            sections[section_name] = section_data
                    except:
                        pass
                    current_json = ""
        
        # Handle the last section if no trailing newline
        if current_json.strip():
            try:
                parsed = json.loads(current_json)
                if isinstance(parsed, list) and len(parsed) >= 2:
                    section_name = parsed[0]
                    section_data = parsed[1]
                    sections[section_name] = section_data
            except:
                pass
                
        return sections
    except Exception as e:
        print(f"Error running Speedify CLI: {e}")
        return {}

def calculate_status_level(latency, jitter, mos, loss_send, loss_receive):
    """Calculate status level: good, warn, bad"""
    issues = 0
    
    # Check latency (good: <50ms, warn: 50-100ms, bad: >100ms)
    if latency > 100:
        issues += 2
    elif latency > 50:
        issues += 1
    
    # Check jitter (good: <10ms, warn: 10-30ms, bad: >30ms)
    if jitter > 30:
        issues += 2
    elif jitter > 10:
        issues += 1
    
    # Check MOS score (good: >=4.0, warn: 3.5-4.0, bad: <3.5)
    if mos < 3.5:
        issues += 2
    elif mos < 4.0:
        issues += 1
    
    # Check packet loss (good: 0%, warn: <1%, bad: >=1%)
    total_loss = max(loss_send, loss_receive)
    if total_loss >= 1.0:
        issues += 2
    elif total_loss > 0:
        issues += 1
    
    if issues >= 4:
        return "bad"
    elif issues >= 2:
        return "warn"
    else:
        return "good"

def format_bytes(bytes_val):
    """Format bytes to human readable format"""
    if bytes_val >= 1024**3:
        return f"{bytes_val / 1024**3:.2f} GB"
    elif bytes_val >= 1024**2:
        return f"{bytes_val / 1024**2:.2f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:.2f} KB"
    else:
        return f"{bytes_val} B"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status")
def get_status():
    # Get comprehensive stats
    stats_data = run_speedify_cli(["stats", "1"])
    
    # Get current settings for accurate bonding mode
    settings_result = subprocess.run(['/usr/share/speedify/speedify_cli', 'show', 'settings'],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   timeout=10)
    current_settings = {}
    if settings_result.returncode == 0:
        try:
            current_settings = json.loads(settings_result.stdout.strip())
        except:
            pass
    
    # Extract different sections
    state = stats_data.get("state", {})
    connection_stats = stats_data.get("connection_stats", {})
    session_stats = stats_data.get("session_stats", {})
    streaming_stats = stats_data.get("streaming_stats", {})
    adapters_data = stats_data.get("adapters", [])
    
    # Overall connection state
    overall_state = state.get("state", "UNKNOWN")
    
    # Process connections for detailed stats
    connections = connection_stats.get("connections", [])
    active_connections = [conn for conn in connections if conn.get("connected", False)]
    
    # Calculate aggregated stats
    total_latency = 0
    total_jitter = 0
    total_mos = 0
    total_loss_send = 0
    total_loss_receive = 0
    active_count = 0
    valid_mos_count = 0  # Track connections with valid MOS scores separately

    detailed_connections = []

    for conn in active_connections:
        if conn.get("latencyMs", 0) > 0:  # Only count connections with valid latency
            latency = conn.get("latencyMs", 0)
            jitter = conn.get("jitterMs", 0) if conn.get("jitterMs", 0) >= 0 else 0
            mos = conn.get("mos", 0)
            loss_send = conn.get("lossSend", 0)
            loss_receive = conn.get("lossReceive", 0)

            total_latency += latency
            total_jitter += jitter
            # Only include valid MOS scores (> 0) in the average
            if mos > 0:
                total_mos += mos
                valid_mos_count += 1
            total_loss_send += loss_send
            total_loss_receive += loss_receive
            active_count += 1
            
            # Calculate status for this connection
            status = calculate_status_level(latency, jitter, mos, loss_send, loss_receive)
            
            detailed_connections.append({
                "adapterID": conn.get("adapterID", "Unknown"),
                "protocol": conn.get("protocol", "Unknown"),
                "latency": latency,
                "jitter": jitter,
                "mos": mos,
                "loss_send": loss_send,
                "loss_receive": loss_receive,
                "status": status,
                "receiveBps": conn.get("receiveBps", 0),
                "sendBps": conn.get("sendBps", 0),
                "totalBps": conn.get("totalBps", 0)
            })
    
    # Calculate averages
    avg_latency = total_latency / active_count if active_count > 0 else 0
    avg_jitter = total_jitter / active_count if active_count > 0 else 0
    avg_mos = total_mos / valid_mos_count if valid_mos_count > 0 else 0  # Use valid_mos_count
    avg_loss_send = total_loss_send / active_count if active_count > 0 else 0
    avg_loss_receive = total_loss_receive / active_count if active_count > 0 else 0
    
    # Overall status calculation
    overall_status = calculate_status_level(avg_latency, avg_jitter, avg_mos, avg_loss_send, avg_loss_receive)
    
    # Session statistics
    session_total = session_stats.get("total", {})
    uptime_minutes = session_total.get("totalConnectedMinutes", 0)
    uptime_str = str(datetime.timedelta(minutes=uptime_minutes))
    
    # Streaming stats - get bonding mode from settings for accuracy
    bonding_mode = current_settings.get("bondingMode", streaming_stats.get("bondingMode", "unknown"))
    bad_indicators = {
        "badCpu": streaming_stats.get("badCpu", False),
        "badLatency": streaming_stats.get("badLatency", False),
        "badLoss": streaming_stats.get("badLoss", False),
        "badMemory": streaming_stats.get("badMemory", False)
    }
    
    # Process adapters with enhanced info
    processed_adapters = []
    for adapter in adapters_data:
        adapter_status = "good"
        if adapter.get("state") != "connected":
            adapter_status = "bad"
        
        # Find matching connection data
        matching_conn = next((conn for conn in detailed_connections 
                             if conn["adapterID"] == adapter.get("adapterID")), None)
        
        processed_adapters.append({
            "adapterID": adapter.get("adapterID", "Unknown"),
            "name": adapter.get("name", "Unknown"),
            "type": adapter.get("type", "Unknown"),
            "isp": adapter.get("isp", "Unknown ISP"),
            "state": adapter.get("state", "unknown"),
            "workingPriority": adapter.get("workingPriority", "unknown"),
            "status": adapter_status,
            "dataUsage": {
                "daily": format_bytes(adapter.get("dataUsage", {}).get("usageDaily", 0)),
                "monthly": format_bytes(adapter.get("dataUsage", {}).get("usageMonthly", 0))
            },
            "connectionStats": matching_conn
        })
    
    return jsonify({
        "overall": {
            "state": overall_state,
            "status": overall_status,
            "bondingMode": bonding_mode,
            "badIndicators": bad_indicators
        },
        "performance": {
            "latency": round(avg_latency, 1),
            "jitter": round(avg_jitter, 1),
            "mos": round(avg_mos, 2),
            "lossSend": round(avg_loss_send * 100, 2),  # Convert to percentage
            "lossReceive": round(avg_loss_receive * 100, 2),
            "activeConnections": active_count
        },
        "session": {
            "uptime": uptime_str,
            "bytesReceived": format_bytes(session_total.get("bytesReceived", 0)),
            "bytesSent": format_bytes(session_total.get("bytesSent", 0)),
            "failovers": session_total.get("numFailovers", 0),
            "maxDownloadSpeed": round(session_total.get("maxDownloadSpeed", 0), 2),
            "maxUploadSpeed": round(session_total.get("maxUploadSpeed", 0), 2)
        },
        "adapters": processed_adapters,
        "connections": detailed_connections
    })

# Add route to get current server info
@app.route("/api/server")
def get_server():
    try:
        # Get current server info - this returns direct JSON, not sectioned like stats
        result = subprocess.run(['/usr/share/speedify/speedify_cli', 'show', 'currentserver'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              timeout=10)
        
        if result.returncode == 0:
            current_server = json.loads(result.stdout.strip())
            
            # Extract location and IP from the known structure
            location = current_server.get("friendlyName", "Unknown")
            public_ips = current_server.get("publicIP", [])
            public_ip = public_ips[0] if public_ips and len(public_ips) > 0 else "Unknown"
            
            return jsonify({
                "location": location,
                "publicIP": public_ip
            })
        else:
            print(f"Speedify CLI error: {result.stderr}")
            return jsonify({
                "location": "CLI Error",
                "publicIP": "CLI Error"
            })
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return jsonify({
            "location": "Parse Error",
            "publicIP": "Parse Error"
        })
    except Exception as e:
        print(f"Error getting server info: {e}")
        return jsonify({
            "location": "Error",
            "publicIP": "Error"
        })

# Add route to change bonding mode
@app.route("/api/change-mode", methods=["POST"])
def change_mode():
    try:
        data = request.get_json()
        mode = data.get('mode', '').lower()
        
        # Validate mode
        if mode not in ['speed', 'streaming', 'redundant']:
            return jsonify({
                "success": False,
                "error": "Invalid mode. Must be 'speed', 'streaming', or 'redundant'"
            }), 400
        
        # Execute the mode change command
        result = subprocess.run(['/usr/share/speedify/speedify_cli', 'mode', mode],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                              timeout=10)
        
        if result.returncode == 0:
            return jsonify({
                "success": True,
                "message": f"Mode changed to {mode}",
                "mode": mode
            })
        else:
            return jsonify({
                "success": False,
                "error": f"CLI error: {result.stderr}"
            }), 500
            
    except Exception as e:
        print(f"Error changing mode: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
