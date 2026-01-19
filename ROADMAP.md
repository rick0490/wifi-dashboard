# Speedify Dashboard Roadmap

This document outlines the current state of the dashboard, known issues, and planned improvements organized by priority.

## System Purpose

This machine is a **portable network bonding solution** designed for:
- **Conventions & Trade Shows** - Vendor booths, artist alleys, merchandise sales
- **In-Person Events** - Concerts, festivals, pop-up markets, sporting events
- **Outdoor Settings** - Parks, fairgrounds, parking lots, temporary venues

**Primary Use Cases:**
- Point of Sale (POS) systems for credit card processing
- Live streaming of events to online audiences
- Event operations (registration, badge printing, check-in)

---

## E2E Test Results (Latest)

| Test | Status |
|------|--------|
| Main page (`GET /`) | PASSED |
| Status API (`GET /api/status`) | PASSED |
| Server API (`GET /api/server`) | PASSED |
| Mode change validation (`POST /api/change-mode`) | PASSED |
| Frontend-Backend integration | PASSED |

**Current Metrics:**
- Overall Status: CONNECTED (good)
- MOS Score: 4.39
- Latency: 26.0 ms
- Jitter: 2.5 ms
- Uptime: 52+ days

---

## Completed Fixes

### Priority Fixes (Completed)
- [x] Fixed MOS averaging logic to filter out invalid scores (MOS=0)
- [x] Moved `request` import to top of file
- [x] Added 10-second timeout to all subprocess calls
- [x] Aligned MOS thresholds between CLAUDE.md, backend (3.5), and frontend (3.5)

---

## Phase 1: Bug Fixes & Code Quality (High Priority)

### Backend (`app.py`)

| Issue | Location | Description | Effort |
|-------|----------|-------------|--------|
| Bare except clauses | Lines 32, 44, 116 | Replace with specific `json.JSONDecodeError` exceptions | Low |
| Print statements | Lines 49, 278, 285, 329 | Replace with Python `logging` module | Low |
| Debug mode in production | Line 336 | Use environment variable for debug flag | Low |
| Hardcoded CLI path | Multiple | Extract to config constant | Low |
| No request validation | `change_mode()` | Add null check for `request.get_json()` | Low |

### Frontend (`templates/index.html`)

| Issue | Location | Description | Effort |
|-------|----------|-------------|--------|
| Alert() for errors | Lines 845, 850 | Replace with toast notification component | Medium |
| No debounce on mode buttons | `changeMode()` | Add debounce to prevent rapid clicks during state transitions | Low |
| Missing error boundary | `updateStatus()` | Wrap DOM updates in try-catch to prevent silent failures | Low |

---

## Phase 2: Performance Optimizations (Medium Priority)

### Backend

| Improvement | Description | Benefit |
|-------------|-------------|---------|
| Response caching | Cache CLI results for 1-2 seconds to reduce subprocess calls | Reduced CPU, faster response |
| Separate polling intervals | Server info rarely changes - poll every 30s instead of 3s | Reduced load |
| Health check endpoint | Add `GET /api/health` for monitoring | Better observability |
| Connection pooling | Consider using a background thread for CLI polling | Reduced latency |

### Frontend

| Improvement | Description | Benefit |
|-------------|-------------|---------|
| Differential updates | Only update DOM elements that changed | Reduced reflows |
| RequestAnimationFrame | Use RAF for smooth animations | Better performance |
| Lazy loading | Defer non-critical JS | Faster initial load |

---

## Phase 3: UI/UX Enhancements (Medium Priority)

### Visual Improvements

| Feature | Description | Complexity |
|---------|-------------|------------|
| Last updated timestamp | Show "Updated X seconds ago" in header | Low |
| Toast notifications | Replace alerts with slide-in toast messages | Medium |
| Loading pulse during refresh | Subtle animation showing data is refreshing | Low |
| Adapter sorting | Show connected adapters first, disconnected last | Low |
| Collapsible disconnected adapters | Collapse or hide disconnected adapters by default | Medium |

### Data Visualization

| Feature | Description | Complexity |
|---------|-------------|------------|
| Real-time throughput bars | Visual bars showing upload/download speed per adapter | Medium |
| Sparkline history | Mini graphs showing latency/MOS trends over time | High |
| Connection quality gauge | Visual gauge/meter for overall connection health | Medium |
| Data usage progress bars | Visual representation of daily/monthly data usage | Low |

### Accessibility

| Feature | Description | Complexity |
|---------|-------------|------------|
| ARIA labels | Add aria-live regions for dynamic content | Low |
| Keyboard navigation | Ensure all interactive elements are keyboard accessible | Medium |
| Screen reader support | Add descriptive labels for status indicators | Low |
| Focus indicators | Visible focus states for all interactive elements | Low |

### Mobile Experience

| Feature | Description | Complexity |
|---------|-------------|------------|
| Improved grid stacking | Better responsive layout for adapter details | Low |
| Touch-friendly buttons | Larger tap targets for mode buttons | Low |
| Pull-to-refresh | Native-feeling refresh gesture | Medium |
| PWA support | Add manifest and service worker for app-like experience | Medium |

---

## Phase 4: New Features (Lower Priority)

### Functionality

| Feature | Description | Complexity |
|---------|-------------|------------|
| Copy IP to clipboard | Click-to-copy for public IP address | Low |
| Server selection | UI to change Speedify server | Medium |
| Adapter priority control | UI to adjust adapter priorities | Medium |
| Historical data | Store and display performance history | High |
| Alerts/notifications | Browser notifications for connection issues | Medium |
| Export data | Download session stats as CSV/JSON | Low |

### Configuration

| Feature | Description | Complexity |
|---------|-------------|------------|
| Dark/light mode toggle | User-selectable theme | Medium |
| Custom refresh interval | Let users set polling frequency | Low |
| Threshold customization | Let users set custom warning thresholds | Medium |
| Dashboard layout options | Customizable widget positions | High |

---

## Event & Convention-Specific Features

These features are specifically designed for the machine's primary use cases: POS systems, live streaming, and event operations in convention/outdoor settings.

### Point of Sale (POS) & Payment Processing

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Transaction-Safe Indicator** | Large, prominent indicator showing if connection is stable enough for payment processing (requires low latency + no packet loss) | Critical | Low |
| **POS Mode Preset** | One-click mode that optimizes for payment processing: prioritizes redundancy over speed, ensures no dropped connections | Critical | Low |
| **Payment Gateway Latency** | Monitor latency to common payment processors (Square, Stripe, PayPal, Clover) with periodic pings | High | Medium |
| **Transaction Window Protection** | Visual countdown/lock during active transactions to prevent mode changes | High | Low |
| **Offline Queue Indicator** | Show when POS systems might be queuing transactions due to connectivity issues | Medium | Medium |
| **Daily Sales Session Stats** | Track uptime and connection quality specifically during "sales hours" | Medium | Medium |
| **PCI Compliance Notes** | Display security status and reminders about secure connection practices | Low | Low |

### Live Streaming Support

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Stream Health Dashboard** | Dedicated view showing metrics critical for streaming: upload bandwidth, stability, dropped frames potential | Critical | Medium |
| **Bitrate Recommendation** | Calculate and display recommended streaming bitrate based on current upload capacity (e.g., "Safe: 4500 kbps, Max: 6000 kbps") | Critical | Low |
| **Upload Bandwidth Focus** | Prominent display of upload speed with historical graph (streamers care most about upload) | High | Low |
| **Stream Mode Preset** | One-click optimization for live streaming: prioritizes upload, enables redundant mode | High | Low |
| **OBS/Streaming Software Integration** | API endpoint that OBS can poll to show connection status in stream overlay | High | Medium |
| **Stream Duration Tracker** | Timer showing how long current streaming session has been stable | Medium | Low |
| **Dropped Frame Predictor** | Warning when conditions might cause dropped frames (high jitter, packet loss spikes) | Medium | Medium |
| **Multi-Platform Status** | Quick-check if bandwidth supports streaming to multiple platforms simultaneously | Medium | Low |
| **Recording Backup Reminder** | Notification to ensure local recording is enabled as backup | Low | Low |
| **Go Live Checklist** | Pre-stream checklist: connection stable, upload sufficient, redundancy active | Medium | Low |

### Event Operations

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Event Mode Selector** | Preset modes: "Setup" (speed priority), "Live Event" (redundancy), "Pack Down" (speed) | High | Low |
| **Badge/Registration Priority** | Mode that prioritizes low-latency for check-in systems | Medium | Low |
| **Connected Devices Counter** | Show number of devices connected to the WiFi access point | High | Medium |
| **Device Bandwidth Allocation** | Visual breakdown of bandwidth usage per connected device | Medium | High |
| **Event Session Logging** | Log all connection events during an event for post-event analysis | High | Medium |
| **Quick Diagnostics Panel** | One-click diagnostic that tests all connections and reports issues in plain language | High | Medium |
| **Attendee Density Warning** | Alert when connection quality degrades (likely due to cell tower congestion) | Medium | Medium |
| **Shift Handoff Report** | Generate summary for shift changes: current status, any issues, data usage | Medium | Low |

### Convention/Trade Show Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Booth Setup Wizard** | Step-by-step setup guide for new venue: test connections, verify POS, check streaming | High | Medium |
| **Venue Signal Map** | Log and display signal strength at different times (helps identify dead zones) | Medium | High |
| **Convention Schedule Integration** | Adjust modes based on convention schedule (e.g., redundant during peak hours) | Medium | High |
| **Neighboring Booth Interference** | Detect and warn about WiFi channel congestion from nearby booths | Medium | Medium |
| **Vendor Dashboard Mode** | Simplified view for non-technical booth staff: just shows "OK to sell" or "Wait" | High | Low |
| **Multi-Day Event Stats** | Track performance across multi-day events with daily summaries | Medium | Medium |
| **Setup Verification Checklist** | Pre-event checklist: all adapters connected, signal strength acceptable, test transaction passed | High | Low |

### Outdoor & Field Deployment

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Carrier Signal Strength** | Display cellular signal strength for each carrier (Verizon, T-Mobile) | Critical | Medium |
| **Signal Quality Trend** | Show if signal is improving or degrading (useful when positioning equipment) | High | Low |
| **Carrier Failover Status** | Clear indication of which carrier is primary and if failover is ready | High | Low |
| **Data Cap Dashboard** | Prominent display of data usage vs. plan limits with projections | Critical | Medium |
| **Data Cap Alerts** | Warnings at 50%, 75%, 90% of data cap with estimated time to limit | Critical | Low |
| **Carrier-Specific Stats** | Separate performance metrics for each cellular connection | High | Low |
| **Weather Impact Warning** | Note when weather conditions might affect cellular signal | Low | High |
| **Power Status** | Display system power status, battery level if on UPS | Medium | Medium |
| **Low Power Mode** | Reduce polling frequency and disable animations to save power | Medium | Low |
| **Portable Hotspot Battery** | Monitor and display battery levels of connected hotspot devices (if supported) | Medium | High |
| **GPS Location Logging** | Log GPS coordinates with connection quality for venue mapping | Low | Medium |

### Quick Actions & Emergency Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Emergency Mode Button** | Single button to switch to maximum redundancy mode | Critical | Low |
| **Quick Restart** | Restart Speedify service without full system reboot | High | Low |
| **Adapter Quick Toggle** | Enable/disable specific adapters with one click | High | Low |
| **Fallback Mode** | Automatically switch to single best connection if bonding fails | High | Medium |
| **Connection Recovery** | Automatic reconnection attempts with visual status | High | Medium |
| **Network Reset** | One-click reset of all network connections | Medium | Low |
| **Speed Priority Override** | Temporarily prioritize speed over redundancy for large downloads | Medium | Low |
| **Status Screenshot** | One-click capture of current dashboard state for troubleshooting/support | Low | Low |

### Pre-Event & Post-Event Tools

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Venue Pre-Check** | Run comprehensive test suite when arriving at new venue | High | Medium |
| **Speed Test History** | Store and compare speed tests across different venues | Medium | Medium |
| **Event Report Generator** | Generate PDF report of event: uptime, data usage, issues encountered | High | Medium |
| **Issue Timeline** | Visual timeline of any connection issues during event | Medium | Medium |
| **Venue Notes** | Save notes about specific venues (best placement, known dead zones) | Medium | Low |
| **Equipment Checklist** | Pre-departure checklist: hotspots charged, cables packed, etc. | Medium | Low |
| **Post-Event Data Sync** | Sync event logs to cloud storage for analysis | Low | Medium |

---

## Feature Suggestions

### Network Monitoring Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Speed Test Integration** | Built-in speed test button using speedtest-cli or fast.com API | High | Medium |
| **Bandwidth Allocation Display** | Show how Speedify is distributing traffic across adapters | High | Medium |
| **Connection Timeline** | Visual timeline showing connect/disconnect events | Medium | Medium |
| **Packet Loss Visualization** | Real-time graph showing packet loss trends | High | Medium |
| **Latency Heatmap** | Color-coded time-of-day latency patterns | Medium | High |
| **Network Quality Score** | Single 0-100 score combining all metrics | High | Low |
| **Adapter Health History** | Track reliability of each adapter over time | Medium | High |
| **Failover Log** | Detailed log of all failover events with timestamps | High | Low |
| **DNS Response Time** | Monitor and display DNS lookup performance | Low | Medium |
| **MTU Detection** | Display detected MTU for each connection | Low | Low |

### Alert & Notification Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Threshold Alerts** | Configurable alerts when metrics exceed thresholds | High | Medium |
| **Email Notifications** | Send email when connection drops or degrades | Medium | Medium |
| **Webhook Support** | POST to external URL on events (for Slack, Discord, etc.) | Medium | Low |
| **Audio Alerts** | Optional sound when connection status changes | Low | Low |
| **Desktop Notifications** | Browser push notifications for critical events | Medium | Medium |
| **Daily Summary Email** | Automated daily report of network performance | Low | Medium |
| **Uptime Alerts** | Notify when uptime milestones are reached | Low | Low |

### Data & Analytics Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Performance Reports** | Generate PDF/HTML reports for date ranges | Medium | High |
| **Data Export (CSV/JSON)** | Export all historical data | Medium | Low |
| **Comparative Analysis** | Compare performance between adapters | Medium | Medium |
| **Peak Usage Times** | Identify when network usage is highest | Low | Medium |
| **Cost Per GB Tracking** | Track data costs per adapter (user-configured rates) | Medium | Medium |
| **Bandwidth Budgeting** | Set monthly data limits with warnings | High | Medium |
| **API for External Tools** | REST API for integration with Grafana, etc. | Medium | Low |

### Multi-Device & Access Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Remote Access** | Secure access from outside local network | High | High |
| **Multi-User Support** | Different users with different permission levels | Low | High |
| **Mobile App** | Native mobile app or improved PWA | Medium | High |
| **Widget/Embedded View** | Minimal view for embedding in other dashboards | Low | Low |
| **Kiosk Mode** | Full-screen display mode for wall-mounted monitors | Low | Low |
| **QR Code Sharing** | QR code to quickly access dashboard from mobile | Low | Low |

### Speedify Control Features

| Feature | Description | Value | Complexity |
|---------|-------------|-------|------------|
| **Server Browser** | Browse and select from all available Speedify servers | High | Medium |
| **Favorite Servers** | Save frequently used servers | Medium | Low |
| **Auto-Server Selection** | UI to configure automatic server selection rules | Medium | Medium |
| **Adapter Enable/Disable** | Toggle adapters on/off from dashboard | High | Low |
| **Bandwidth Limits** | Set per-adapter bandwidth limits | Medium | Medium |
| **Protocol Selection** | Change connection protocol (TCP/UDP/Auto) | Medium | Low |
| **Encryption Settings** | View/change encryption mode | Low | Low |
| **Streaming Mode Presets** | Quick presets for gaming, video calls, etc. | Medium | Medium |
| **Schedule-Based Modes** | Auto-switch modes based on time of day | Medium | High |

---

## UI/UX Upgrade Suggestions

### Dashboard Layout Improvements

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Customizable Grid Layout** | Drag-and-drop widget positioning | High | High |
| **Collapsible Sections** | Allow users to collapse unused sections | Medium | Low |
| **Full-Screen Widgets** | Click to expand any widget to full screen | Medium | Medium |
| **Compact View Mode** | Condensed view showing only key metrics | Medium | Medium |
| **Split View** | Side-by-side comparison of adapters | Low | Medium |
| **Tabbed Interface** | Organize features into tabs (Overview, Adapters, History) | Medium | Medium |
| **Sidebar Navigation** | Move from top header to sidebar for more screen space | Low | Medium |
| **Floating Action Button** | Quick access to common actions (speed test, refresh) | Low | Low |

### Visual Design Upgrades

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Theme System** | Multiple color themes (dark, light, OLED black, high contrast) | Medium | Medium |
| **Custom Accent Colors** | User-selectable accent color | Low | Low |
| **Animated Backgrounds** | Subtle animated network visualization background | Low | Medium |
| **Icon Pack Options** | Different icon styles (outlined, filled, minimal) | Low | Low |
| **Typography Options** | Font size and family preferences | Low | Low |
| **Glassmorphism Option** | Frosted glass effect for cards | Low | Low |
| **Status Color Customization** | Custom colors for good/warn/bad states | Low | Low |
| **Connection Visualization** | Animated lines showing data flow between adapters and server | Medium | High |

### Data Visualization Upgrades

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Real-Time Charts** | Live updating line charts for all metrics | High | Medium |
| **Speedometer Gauges** | Circular gauges for current speeds | Medium | Medium |
| **Network Topology Map** | Visual diagram of network connections | Medium | High |
| **Stacked Area Charts** | Show combined bandwidth from all adapters | Medium | Medium |
| **Donut Charts** | Data usage breakdown by adapter | Low | Low |
| **Trend Arrows** | Up/down arrows showing metric direction | Medium | Low |
| **Mini Sparklines** | Tiny inline graphs next to each metric | High | Medium |
| **Heatmap Calendar** | GitHub-style heatmap of daily performance | Low | Medium |
| **Sankey Diagram** | Flow diagram showing traffic distribution | Low | High |

### Interaction Improvements

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Hover Tooltips** | Detailed info on hover for all metrics | High | Low |
| **Click-to-Drill-Down** | Click metrics to see detailed breakdown | Medium | Medium |
| **Context Menus** | Right-click menus for quick actions | Low | Medium |
| **Keyboard Shortcuts** | Power-user keyboard navigation (R=refresh, 1/2/3=modes) | Medium | Low |
| **Gesture Support** | Swipe gestures on mobile for navigation | Medium | Medium |
| **Search/Filter** | Search within adapters and logs | Low | Low |
| **Undo/Redo** | Undo recent mode changes | Low | Medium |
| **Confirmation Dialogs** | Confirm before critical actions | Medium | Low |

### Status & Feedback Improvements

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Toast Notifications** | Slide-in notifications for all events | High | Medium |
| **Progress Indicators** | Show progress for long operations | Medium | Low |
| **Skeleton Loading** | Animated placeholders while loading | Medium | Low |
| **Error Recovery UI** | Clear error messages with retry buttons | High | Low |
| **Success Animations** | Subtle animations on successful actions | Low | Low |
| **Connection Status Banner** | Prominent banner when disconnected | High | Low |
| **Maintenance Mode** | UI indication when Speedify is updating | Low | Low |
| **Sync Indicator** | Show when data is being refreshed | Medium | Low |

### Mobile-Specific Upgrades

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Bottom Navigation** | Thumb-friendly navigation at bottom of screen | High | Medium |
| **Swipe Between Views** | Swipe left/right to change sections | Medium | Medium |
| **Pull-to-Refresh** | Native pull gesture to refresh data | High | Low |
| **Haptic Feedback** | Vibration feedback on actions | Low | Low |
| **Portrait/Landscape Layouts** | Optimized layouts for both orientations | Medium | Medium |
| **Offline Indicator** | Clear indication when dashboard can't reach server | High | Low |
| **App Install Banner** | Prompt to install PWA on mobile | Medium | Low |
| **Share Button** | Share current status via native share | Low | Low |

### Accessibility Upgrades

| Upgrade | Description | Impact | Complexity |
|---------|-------------|--------|------------|
| **Screen Reader Support** | Full ARIA labels and live regions | High | Medium |
| **High Contrast Mode** | WCAG AAA compliant contrast option | Medium | Low |
| **Reduced Motion** | Respect prefers-reduced-motion | Medium | Low |
| **Focus Management** | Logical focus order and visible indicators | High | Low |
| **Text Scaling** | Support for browser text zoom | Medium | Low |
| **Color Blind Modes** | Alternative color schemes for color blindness | Medium | Medium |
| **Keyboard-Only Navigation** | Full functionality without mouse | High | Medium |
| **Skip Links** | Skip to main content links | Low | Low |

---

## Feature Priority Matrix

### Critical for Events (Implement First)

These features directly support the machine's core purpose and should be prioritized:

| Feature | Use Case | Complexity |
|---------|----------|------------|
| **Connection Health Widget** | All | Low | ✅ IMPLEMENTED |
| Transaction-Safe Indicator | POS | Low |
| POS Mode Preset | POS | Low |
| Bitrate Recommendation | Streaming | Low |
| Stream Mode Preset | Streaming | Low |
| Data Cap Dashboard | Field/Outdoor | Medium |
| Data Cap Alerts | Field/Outdoor | Low |
| Emergency Mode Button | All | Low |
| Carrier Signal Strength | Field/Outdoor | Medium |
| Vendor Dashboard Mode | Conventions | Low |

### High Value + Low Complexity (Do First)
- Transaction-Safe Indicator (large "OK TO SELL" / "WAIT" display)
- POS Mode Preset (one-click payment optimization)
- Stream Mode Preset (one-click streaming optimization)
- Bitrate Recommendation display
- Data Cap Alerts (50%, 75%, 90% warnings)
- Emergency Mode Button
- Carrier Failover Status indicator
- Upload Bandwidth Focus display
- Network Quality Score (single 0-100 metric)
- Go Live Checklist for streaming
- Setup Verification Checklist
- Trend arrows on metrics
- Hover tooltips
- Toast notifications
- Adapter enable/disable toggle
- Pull-to-refresh

### High Value + Medium Complexity (Plan Next)
- Stream Health Dashboard
- Data Cap Dashboard with projections
- Carrier Signal Strength display
- Connected Devices Counter
- Event Session Logging
- Quick Diagnostics Panel
- Booth Setup Wizard
- Venue Pre-Check tool
- Event Report Generator
- Real-time charts
- Speed test integration
- Threshold alerts
- OBS/Streaming Software Integration

### Medium Value + Low Complexity (Quick Wins)
- Vendor Dashboard Mode (simplified view)
- Signal Quality Trend arrows
- Stream Duration Tracker
- Shift Handoff Report
- Venue Notes storage
- Equipment Checklist
- Quick Restart button
- Network Reset button
- Collapsible sections
- Skeleton loading states
- Offline indicator
- QR code for mobile access

### Consider Carefully (High Complexity)
- Venue Signal Map
- Convention Schedule Integration
- Device Bandwidth Allocation per client
- GPS Location Logging
- Weather Impact Warning
- Multi-Day Event Stats with trends
- Customizable grid layout
- Historical data storage
- Remote access
- Mobile native app

---

## Phase 5: Infrastructure (Lower Priority)

| Improvement | Description | Complexity |
|-------------|-------------|------------|
| Proper logging | Structured logging with log levels | Low |
| Environment configuration | Use `.env` file for settings | Low |
| Unit tests | Add pytest tests for backend functions | Medium |
| Integration tests | Automated E2E tests with pytest | Medium |
| Docker support | Containerize the application | Medium |
| Rate limiting | Prevent API abuse | Low |
| Authentication | Optional password protection | Medium |

---

## Technical Debt Summary

### Code Quality Issues

```
app.py:
├── Line 32, 44, 116: Bare except clauses
├── Line 49, 278, 285, 329: Print statements instead of logging
├── Line 336: Debug mode hardcoded
└── Multiple: Hardcoded CLI path

index.html:
├── Line 845, 850: Browser alert() for errors
├── Line 871-874: Both endpoints poll at same interval
└── No TypeScript or type checking
```

### Missing Features
- No automated tests
- No CI/CD pipeline
- No error tracking/monitoring
- No request rate limiting
- No authentication option

---

## Recommended Implementation Order

### Phase A: Code Quality & Foundation
1. Replace bare except clauses with specific exceptions
2. Add logging module
3. Add environment variable for debug mode
4. Add health check endpoint
5. Add response caching

### Phase B: Critical Event Features
1. **Transaction-Safe Indicator** - Large visual indicator for POS safety
2. **Data Cap Alerts** - Warnings at usage thresholds
3. **Emergency Mode Button** - One-click maximum redundancy
4. **Upload Bandwidth Display** - Prominent upload speed for streamers
5. **Bitrate Recommendation** - Calculated safe streaming bitrate
6. **Carrier Failover Status** - Clear primary/backup indicator

### Phase C: Mode Presets & Quick Actions
1. **POS Mode Preset** - Optimized for payment processing
2. **Stream Mode Preset** - Optimized for live streaming
3. **Event Mode Selector** - Setup / Live Event / Pack Down
4. **Adapter Quick Toggle** - Enable/disable adapters
5. **Quick Restart** - Restart Speedify service

### Phase D: UI/UX Improvements
1. Toast notifications (replace alerts)
2. Last updated timestamp
3. Improved mobile responsive design
4. Pull-to-refresh gesture
5. Hover tooltips for all metrics
6. Trend arrows on metrics

### Phase E: Event Operations Tools
1. **Go Live Checklist** - Pre-stream verification
2. **Setup Verification Checklist** - Pre-event checks
3. **Vendor Dashboard Mode** - Simplified "OK/WAIT" view
4. **Connected Devices Counter** - WiFi client count
5. **Quick Diagnostics Panel** - One-click troubleshooting

### Phase F: Streaming Enhancements
1. **Stream Health Dashboard** - Dedicated streaming view
2. **Stream Duration Tracker** - Stability timer
3. **Dropped Frame Predictor** - Early warning system
4. **OBS Integration API** - Endpoint for stream overlays

### Phase G: Reporting & Analytics
1. **Event Session Logging** - Connection event history
2. **Event Report Generator** - PDF/HTML reports
3. **Venue Notes** - Save venue-specific information
4. **Speed Test History** - Compare across venues
5. **Multi-Day Event Stats** - Cross-day analysis

### Phase H: Advanced Features
1. **Carrier Signal Strength** - Cellular signal display
2. **Data Cap Dashboard** - Usage vs. limits with projections
3. **Booth Setup Wizard** - Guided new venue setup
4. **Venue Pre-Check** - Comprehensive arrival test
5. **Power Status** - UPS/battery monitoring

### Phase Z: Infrastructure (Ongoing)
- Unit tests with pytest
- Integration tests
- Docker containerization
- PWA support
- Authentication system

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Initial | Base dashboard with status, server, mode controls |
| 1.0.1 | Current | Fixed MOS averaging, added subprocess timeouts, aligned thresholds |

---

## Contributing

When making changes:
1. Test all API endpoints manually
2. Verify frontend updates in multiple browsers
3. Check mobile responsiveness
4. Update this roadmap with completed items
