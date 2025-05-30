# Website Snapshot MCP: Building an MCP from scratch and use Playwright for capturing context for LLMs

In today's AI-driven landscape, Large Language Models must understand and interact with web content to deliver meaningful value across an expanding array of use cases. This increasing demand creates significant challenges for developers who must bridge the gap between static LLM knowledge and dynamic web applications. The Model Context Protocol (MCP) has been tailored for quickly provide context to LLMs.

This implementation a context extraction tool that can be used by LLM tools for improve results. Built on the proven foundation of Microsoft's Playwright MCP server, we'll focus on architectural patterns that promote reliability, comprehensive data capture, and seamless LLM integration. By following this battle-tested approach, you'll dive deeply into how to create useful MCPs, ultimately enabling more intelligent and context-aware AI applications.

## Practical Application: LLM-Guided Test Architecture from Web Snapshots

Before diving into implementation details, let's examine how Large Language Models leverage comprehensive website snapshots to autonomously create testing architecture. This real-world example demonstrates how structured web context enables LLMs to make intelligent decisions about Page Object Model design and test creation.

### LLM Interpretation of Snapshot Data

When an LLM receives the snapshot from `https://playwright.dev/`, it immediately recognizes patterns and structures that inform testing strategy:

```
✅ Captured snapshot with 44 elements, 31 requests, 0 console messages
🔍 Fast and reliable end-to-end testing for modern web apps | Playwright
📍 https://playwright.dev/

🎭 Accessibility Snapshot:
- navigation "Main":
  - link "Docs": [ref=3]
  - link "API": [ref=4]
  - button "Node.js" [ref=5]
  - link "GitHub repository": [ref=7]
- banner:
  - heading "Playwright enables reliable end-to-end testing for modern web apps."
  - link "Get started": [ref=11]
  - link "Star microsoft/playwright on GitHub": [ref=12]
- main:
  - heading "Any browser • Any platform • One API"
  - link "TypeScript": [ref=14]
  - link "JavaScript": [ref=15]
  - link "Python": [ref=16]
```

**LLM Analysis Process**: The model recognizes semantic HTML structures (`navigation`, `banner`, `main`) and immediately understands this represents distinct functional areas requiring separate Page Object sections.

### LLM-Driven Architecture Decisions

Using the snapshot data, the LLM autonomously reasons through Page Object Model design:

**LLM Reasoning**: _"I see a `navigation 'Main'` section with multiple interaction points. This should become a NavigationSection class with methods that encapsulate complete user workflows, not just element clicks."_

```typescript
class NavigationSection {
  async navigateToDocumentation(): Promise<void> {
    await this.getDocsLink().click();
    await expect(this.page).toHaveURL(/.*\/docs\/intro/);
  }

  async openGitHubRepository(): Promise<Page> {
    const [newPage] = await Promise.all([
      this.page.context().waitForEvent("page"),
      this.getGitHubLink().click(),
    ]);
    return newPage;
  }
}
```

**LLM Reasoning**: _"The `banner` area contains primary call-to-action elements. I'll create a HeroSection that focuses on conversion-critical interactions."_

```typescript
class HeroSection {
  async startGettingStarted(): Promise<void> {
    await this.getStartedButton().click();
    await expect(this.page).toHaveURL(/.*\/docs\/intro/);
  }
}
```

### LLM Element Reference Strategy

The LLM uses the reference system (`[ref=3]`, `[ref=4]`) to make intelligent selector choices:

**LLM Decision Process**: _"I have reference IDs, but I should prioritize semantic selectors for maintainability. The snapshot shows these are within a navigation context, so I'll use role-based targeting."_

```typescript
// LLM chooses semantic selectors over reference IDs
getDocsLink(): Locator {
  return this.page.locator('nav').getByRole('link', { name: 'Docs' });
}

// Instead of brittle reference-based targeting
// return this.page.locator('[ref="3"]');
```

### LLM Test Scenario Generation

Based on the snapshot's network activity (31 requests) and element structure, the LLM generates comprehensive test scenarios:

**LLM Planning**: _"I see external links to GitHub and multiple programming language documentation. I need tests for cross-tab navigation, multi-language support, and external integrations."_

```typescript
test("should navigate external repository and community links", async () => {
  // LLM identifies this as cross-tab navigation requirement
  const repoPage = await homePage.navigation.openGitHubRepository();
  await expect(repoPage).toHaveURL(/.*github\.com\/microsoft\/playwright/);
  await repoPage.close();
});

test("should explore all supported programming languages", async () => {
  // LLM recognizes pattern from snapshot language links
  const languages = ["TypeScript", "JavaScript", "Python", ".NET", "Java"];
  for (const language of languages) {
    await homePage.features.navigateToLanguageDoc(language);
    await homePage.page.goBack();
  }
});
```

### LLM Self-Correction Process

When tests initially failed, the LLM used error feedback to refine its approach:

**LLM Error Analysis**: _"I'm getting strict mode violations for company logos. The snapshot shows these are in the main content area. I need to scope my selectors more precisely."_

```typescript
// Original LLM approach (caused failures)
await expect(this.page.getByRole("link", { name: company })).toBeVisible();

// LLM self-correction
const companySection = this.page.locator("main").getByRole("list").last();
await expect(
  companySection.getByRole("link", { name: company, exact: true })
).toBeVisible();
```

### LLM-Generated Success Metrics

The LLM's snapshot-driven approach achieved:

- **10 autonomous test scenarios** derived from structural analysis
- **100% test pass rate** after LLM self-correction
- **Zero manual selector engineering** - all generated from snapshot context
- **Cross-browser validation** automatically configured

### LLM Decision Validation

**LLM Reflection**: _"The snapshot provided complete context about page structure, element relationships, and user workflows. This eliminated guesswork and enabled me to create maintainable tests that mirror actual user behavior rather than arbitrary technical implementations."_

This example demonstrates how structured web snapshots transform LLMs from code generators into intelligent test architects, capable of understanding web applications holistically and making informed decisions about testing strategy, element targeting, and scenario coverage without human intervention.

## Setting Up Your Project Foundation

A well-structured MCP server begins with thoughtful configuration. This section explores the essential elements that form the bedrock of a scalable web snapshot architecture, focusing on settings that enhance reliability, performance, and maintainability.

### Optimizing Your MCP Configuration

The server architecture defines your system's behavior. Key configuration options include:

1. **Protocol Implementation**: Leverage FastMCP for automatic compliance.

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server with clear identification
mcp = FastMCP("Website Snapshot")
```

2. **Tool Registration**: Centralize tool management for maintainability.

```python
from registry import register_all_tools

# Single point of tool registration
register_all_tools(mcp)
```

Here's the server implementation:

```python
# server.py
from mcp.server.fastmcp import FastMCP
from registry import register_all_tools

# Create an MCP server
mcp = FastMCP("Website Snapshot")

# Register all tools
register_all_tools(mcp)

if __name__ == "__main__":
    mcp.run()
```

This configuration ensures clean separation of concerns, protocol compliance, and extensibility, establishing the foundation upon which the rest of your web snapshot architecture will build.

## Structuring Your Project Folders

This section introduces a modular design pattern that scales naturally with your requirements, keeping related functionality together while maintaining clear boundaries between different aspects of web data extraction.

### Organizing for Clarity and Scale

A well-organized project structure maintains clarity as your feature set grows. Consider this tool-based organization:

```
├── src/
│   ├── server.py           # Main MCP server entry point
│   ├── registry.py         # Tool registration logic
│   └── tools/
│       ├── __init__.py
│       └── snapshot_url.py # Web snapshot implementation
├── pyproject.toml          # Project configuration
└── README.md              # Documentation
```

This structure implements four key principles:

1. **Tool Isolation**: Each tool lives in its own module for independent development
2. **Central Registry**: All tools register through a single point for consistency
3. **Clear Entry Points**: Server initialization is separate from tool logic
4. **Dependency Management**: Project configuration defines all requirements

This organization enables efficient tool development and testing while supporting the modular architecture needed for complex mcp applications. This structure not only makes it easier to add new tools but also naturally enforces architectural boundaries that promote code quality. With tools clearly separated, changes to one tool have minimal impact on others, reducing the risk of unintended side effects when making updates.

## Creating the Website Snapshot Tool

The snapshot tool is the cornerstone of this application, but implementing it effectively requires sophisticated handling of modern web technologies. This section introduces a comprehensive approach to website snapshots that captures not just visible content but the complete context LLMs need using Playwright.

### Separating Concerns with Data Structures

Decouple data representation from capture logic for cleaner, more maintainable code:

```python
# snapshot_url.py
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class NetworkRequest:
    request: Optional[Request] = None
    response: Optional[Response] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None
```

This data structure captures the complete request/response cycle. This separation provides three key benefits:

1. **Focused Responsibility**: Data structures define shape, capture logic defines behavior
2. **Targeted Maintenance**: Update structures in isolation when requirements change
3. **Enhanced Reusability**: Share data structures across different snapshot scenarios

### Environment Configuration

Separate configuration from code for cleaner management.

```python
CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "timeout": 15000,
}
```

### Resource Management

Implement safeguards for production stability.

```python
def should_show_content(content_type: str, content_length: int) -> bool:
    return content_length <= 50000 and any(
        content_type.startswith(t)
        for t in ["application/json", "text/", "application/xml"]
    )
```

### Building the Snapshot Foundation

Start with a clear function signature that defines the contract for web snapshots and defines the setup for a tool in this architecture:

```python
from mcp.types import TextContent
from playwright.async_api import async_playwright, Response, Request

async def website_snapshot(target_url: str) -> List[TextContent]:
    """
    Take authenticated page snapshots with monitoring
    Example: https://example.com
    """

    if not is_valid_url(target_url):
        return [
            TextContent(type="text", text='Url must be valid, example: https://example.com')
        ]
```

Then implement comprehensive monitoring capabilities:

```python
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)

    try:
        context = await browser.new_context(
            viewport=CONFIG["viewport"],
            user_agent=CONFIG["user_agent"]
        )

        page = await context.new_page()
        page.set_default_timeout(CONFIG["timeout"])

        # Initialize monitoring systems
        network_requests: List[NetworkRequest] = []
        console_messages: List[Any] = []

        # Setup comprehensive monitoring
        page.on("console", lambda msg: console_messages.append(msg))
        page.on("request", handle_request)
        page.on("response", handle_response)

        # Navigate and capture
        await page.goto(target_url, wait_until="domcontentloaded")
        await page.wait_for_load_state("load", timeout=CONFIG["timeout"])

        # Capture accessibility snapshot
        aria_snapshot = await page.locator("body").aria_snapshot()
        snapshot_with_refs = add_element_refs(aria_snapshot)

        return format_snapshot_output(
            page, snapshot_with_refs, network_requests, console_messages
        )

    finally:
        await browser.close()
```

### Request and Response Handling

Implement detailed network monitoring to capture API interactions:

```python
async def handle_request(request: Request):
    request_body = None
    if request.method.upper() in ["POST", "PUT", "PATCH"]:
        try:
            request_body = await request.post_data()
        except Exception:
            pass
    network_requests.append(
        NetworkRequest(request=request, request_body=request_body)
    )

async def handle_response(response: Response):
    for entry in network_requests:
        if entry.request == response.request and not entry.response:
            entry.response = response
            try:
                content_type = response.headers.get("content-type", "")
                content_length = int(response.headers.get("content-length", "0"))

                if should_show_content(content_type, content_length):
                    entry.response_body = await response.text()
                else:
                    entry.response_body = f"[{content_type} - {content_length} bytes]"
            except Exception:
                entry.response_body = "[Error reading response]"
            break
```

### Element Reference System

Create a system for precise element identification:

```python
def add_element_refs(snapshot: str) -> str:
    """Add reference IDs to interactive elements for precise targeting"""
    lines = snapshot.split("\n")
    ref_counter = 1

    for i, line in enumerate(lines):
        if any(keyword in line.lower()
               for keyword in ["button", "link", "input", "textbox"]):
            lines[i] = f"{line} [ref={ref_counter}]"
            ref_counter += 1

    return "\n".join(lines)
```

This reference system enables:

- **Precise Identification**: Each interactive element has a unique reference
- **Clear Communication**: LLMs can see exact elements to interact with
- **Reduced Ambiguity**: No confusion when multiple similar elements exist

### Output Formatting

Structure the captured data for optimal LLM consumption:

```python
def format_snapshot_output(page, snapshot, requests, console_msgs):
    """Format all captured data into structured output"""

    # Parse element references
    element_refs = parse_refs(snapshot)

    # Build structured output
    output_parts = [
        f"🔍 {await page.title()}",
        f"📍 {page.url}",
        "",
        "🎭 Accessibility Snapshot:",
        snapshot,
    ]

    # Add network activity if present
    if requests:
        output_parts.extend([
            "",
            "🌐 Network Requests:",
            format_requests(requests)
        ])

    # Add console output if present
    if console_msgs:
        output_parts.extend([
            "",
            "🖥️ Console:",
            format_console(console_msgs)
        ])

    # Create summary
    summary_parts = [
        f"{len(element_refs)} interactive elements",
        f"{len(requests)} network requests",
        f"{len(console_msgs)} console messages"
    ]

    return [
        TextContent(
            type="text",
            text=f"✅ Captured snapshot with {', '.join(summary_parts)}"
        ),
        TextContent(type="text", text="\n".join(output_parts)),
        TextContent(
            type="text",
            text="🎯 Element References:\n" +
            "\n".join([f"[ref={r['ref']}]: {r['element']}" for r in element_refs])
        ),
    ]
```

This structured approach delivers four major benefits:

1. **Complete Context**: All page data available for LLM analysis
2. **Clear Organization**: Information logically grouped for processing
3. **Actionable References**: Direct mapping between elements and actions
4. **Performance Insights**: Network and console data reveal page behavior

The snapshot engine truly shines when dealing with complex web applications. By capturing not just the visible content but the entire context of page interactions, you create a more accurate representation that mirrors the application's actual behavior. This approach not only makes LLM interactions more reliable but also provides debugging information that helps understand why certain behaviors occur. The resulting snapshots become more intuitive, easier to process, and significantly more valuable for AI-driven analysis.

## Highlighting the Core Functionalities

Modern web applications require sophisticated approaches to capture their full behavior. This section explores advanced techniques that ensure comprehensive data extraction while maintaining performance.

### Network Activity Formatting

Transform raw network data into LLM-friendly formats:

```python
def format_requests(requests: List[NetworkRequest]) -> str:
    """Format network requests for LLM understanding"""
    if not requests:
        return "No requests captured"

    formatted = []
    for req in requests:
        if req.request:
            formatted.append(f"🌐 {req.request.method} {req.request.url}")
            formatted.append(
                f"   Status: {req.response.status if req.response else 'Pending'}"
            )
            if req.response_body:
                # Show meaningful preview
                preview = req.response_body[:200]
                if len(req.response_body) > 200:
                    preview += "..."
                formatted.append(f"   Response: {preview}")

    return "\n".join(formatted)
```

### Console Message Processing

Capture and categorize client-side logs:

```python
def format_console(messages: List[Any]) -> str:
    """Format console messages with severity indicators"""
    if not messages:
        return "No console messages"

    formatted = []
    for msg in messages:
        msg_type = getattr(msg, 'type', 'log').upper()
        msg_text = getattr(msg, 'text', str(msg))

        # Add visual indicators
        emoji = {
            'ERROR': '❌',
            'WARNING': '⚠️',
            'INFO': 'ℹ️',
            'LOG': '📝'
        }.get(msg_type, '🖥️')

        formatted.append(f"{emoji} [{msg_type}] {msg_text}")

    return "\n".join(formatted)
```

### Dynamic Content Strategies

Handle JavaScript-heavy applications intelligently:

```python
# Smart waiting for dynamic content
try:
    await page.wait_for_selector(
        "[data-testid], button, .MuiButton-root",
        timeout=10000
    )
except Exception:
    # Fallback to time-based wait
    await page.wait_for_timeout(3000)
```

This multi-layered approach ensures content capture across different application architectures.

## Configuration and Deployment

The true power of the web snapshot tool emerges through proper configuration and deployment strategies. This section covers essential patterns for different environments.

### Development Configuration

Set up an efficient development workflow:

```bash
# Clone and install
git clone https://github.com/gustavo-meilus/mcp-web-snapshot.git
cd mcp-web-snapshot
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Test with MCP inspector
uv run mcp dev src/server.py
```

### Client Integration

Configure for MCP client:

**For Cursor IDE using uv:**

```json
{
  "mcpServers": {
    "mcp-web-snapshot": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/home/gustavo/github/mcp-web-snapshot",
        "python",
        "src/server.py"
      ]
    }
  }
}
```

### Production Considerations

Deploy with reliability in mind:

1. **Resource Limits**: Prevent runaway browser instances
2. **Timeout Configuration**: Balance completeness with responsiveness
3. **Error Recovery**: Graceful handling of network failures
4. **Monitoring**: Track snapshot success rates and performance

## Conclusion

The comprehensive approach outlined in this implementation addresses the common pitfalls when creating mcp servers and provides a solid foundation that evolves alongside both web technologies and LLM capabilities.

By implementing this architecture, you create a web context system with multiple layers of value:

1. **Technical Excellence**: The modular design, comprehensive monitoring, and structured output produce clean, maintainable code that follows MCP best practices.

2. **Operational Efficiency**: Automated data extraction, intelligent waiting strategies, and error handling dramatically reduce the complexity of providing web context to LLMs.

3. **Scalability**: As your AI tools grow, the clear structure and consistent patterns make adding new extraction capabilities straightforward and reliable.

4. **Context Quality**: The resulting snapshots provide rich, structured data that enables LLMs to understand and reason about web content effectively.

As the Model Context Protocol use cases continues to evolve, this architectural foundation will integrate new capabilities seamlessly, ensuring your web context strategy remains current without sacrificing scalability and maintainability. By adopting these patterns, you're not just be able to create good MCPs but also foster a sustainable advantage that will benefit your AI projects throughout their entire lifecycle.
