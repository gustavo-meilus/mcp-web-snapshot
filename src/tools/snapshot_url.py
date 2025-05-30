from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from mcp.types import TextContent
from playwright.async_api import async_playwright, Response, Request
from pydantic import BaseModel, Field
from urllib.parse import urlparse


class AuthenticatedSnapshotArgs(BaseModel):
    url: str = Field(
        description="Path to navigate to after authentication (e.g., /leads)"
    )
    include_network: bool = Field(
        default=True, description="Include network monitoring"
    )
    include_console: bool = Field(default=True, description="Include console messages")


@dataclass
class NetworkRequest:
    request: Optional[Request] = None
    response: Optional[Response] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None


CONFIG = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "timeout": 15000,
}


def should_show_content(content_type: str, content_length: int) -> bool:
    return content_length <= 50000 and any(
        content_type.startswith(t)
        for t in ["application/json", "text/", "application/xml"]
    )


def format_requests(requests: List[NetworkRequest]) -> str:
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
                formatted.append(f"   Response: {req.response_body[:200]}...")
    return "\n".join(formatted)


def format_console(messages: List[Any]) -> str:
    if not messages:
        return "No console messages"
    return "\n".join(
        [
            f"🖥️ [{getattr(msg, 'type', 'log').upper()}] {getattr(msg, 'text', str(msg))}"
            for msg in messages
        ]
    )


def add_element_refs(snapshot: str) -> str:
    lines = snapshot.split("\n")
    ref_counter = 1

    for i, line in enumerate(lines):
        if any(
            keyword in line.lower()
            for keyword in ["button", "link", "input", "textbox"]
        ):
            lines[i] = f"{line} [ref={ref_counter}]"
            ref_counter += 1

    return "\n".join(lines)


def parse_refs(snapshot: str) -> List[Dict[str, str]]:
    refs = []
    for line in snapshot.split("\n"):
        if "[ref=" in line:
            ref_start = line.find("[ref=") + 5
            ref_end = line.find("]", ref_start)
            if ref_end > ref_start:
                refs.append(
                    {
                        "ref": line[ref_start:ref_end],
                        "element": line[: line.find("[ref=")].strip(),
                    }
                )
    return refs


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


async def website_snapshot(target_url: str) -> List[TextContent]:
    """
    Take authenticated page snapshots with monitoring
    Example: https://example.com
    """

    if not is_valid_url(target_url):
        return [
            TextContent(
                type="text", text="Url must be valid, example: https://example.com"
            )
        ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        try:
            context = await browser.new_context(
                viewport=CONFIG["viewport"], user_agent=CONFIG["user_agent"]
            )

            page = await context.new_page()
            page.set_default_timeout(CONFIG["timeout"])

            network_requests: List[NetworkRequest] = []
            console_messages: List[Any] = []

            # Setup monitoring
            page.on("console", lambda msg: console_messages.append(msg))

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
                            content_length = int(
                                response.headers.get("content-length", "0")
                            )

                            if should_show_content(content_type, content_length):
                                entry.response_body = await response.text()
                            else:
                                entry.response_body = (
                                    f"[{content_type} - {content_length} bytes]"
                                )
                        except Exception:
                            entry.response_body = "[Error reading response]"
                        break

            page.on("request", handle_request)
            page.on("response", handle_response)

            # Navigate to target and capture snapshot
            await page.goto(target_url, wait_until="domcontentloaded")
            await page.wait_for_load_state("load", timeout=CONFIG["timeout"])

            try:
                await page.wait_for_selector(
                    "[data-testid], button, .MuiButton-root", timeout=10000
                )
            except Exception:
                await page.wait_for_timeout(3000)

            # Capture snapshot
            aria_snapshot = await page.locator("body").aria_snapshot()
            snapshot_with_refs = add_element_refs(aria_snapshot)
            element_refs = parse_refs(snapshot_with_refs)

            # Format output
            output_parts = [
                f"🔍 {await page.title()}",
                f"📍 {page.url}",
                "",
                "🎭 Accessibility Snapshot:",
                snapshot_with_refs,
            ]

            output_parts.extend(
                ["", "🌐 Network Requests:", format_requests(network_requests)]
            )

            output_parts.extend(["", "🖥️ Console:", format_console(console_messages)])

            summary_parts = [f"{len(element_refs)} elements"]

            summary_parts.append(
                f"{len([r for r in network_requests if r.request])} requests"
            )

            summary_parts.append(f"{len(console_messages)} console messages")

            await context.close()

            return [
                TextContent(
                    type="text",
                    text=f"✅ Captured snapshot with {', '.join(summary_parts)}",
                ),
                TextContent(type="text", text="\n".join(output_parts)),
                TextContent(
                    type="text",
                    text="🎯 Element References:\n"
                    + "\n".join(
                        [f"[ref={r['ref']}]: {r['element']}" for r in element_refs]
                    ),
                ),
            ]

        except Exception as error:
            return [TextContent(type="text", text=f"❌ Failed: {str(error)}")]
        finally:
            await browser.close()
