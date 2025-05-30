import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from mcp.types import TextContent
from src.tools.snapshot_url import website_snapshot


@pytest.mark.asyncio
async def test_website_snapshot_success():
    """Test successful website snapshot with mocked Playwright"""

    mock_page = AsyncMock()
    mock_page.url = "https://example.com/page"
    mock_page.title = AsyncMock(return_value="Example Page")
    mock_page.set_default_timeout = MagicMock()
    mock_page.on = MagicMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()

    mock_locator = AsyncMock()
    mock_locator.aria_snapshot = AsyncMock(
        return_value="""heading "Example Page"
button "Submit" 
link "Home"
textbox "Email"
button "Login"
"""
    )
    mock_page.locator = MagicMock(return_value=mock_locator)

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_chromium = AsyncMock()
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    mock_playwright = AsyncMock()
    mock_playwright.chromium = mock_chromium

    with patch("src.tools.snapshot_url.async_playwright") as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright

        result = await website_snapshot("https://example.com")

    assert len(result) == 3
    assert all(isinstance(content, TextContent) for content in result)
    assert all(content.type == "text" for content in result)

    assert (
        "✅ Captured snapshot with 4 elements, 0 requests, 0 console messages"
        in result[0].text
    )

    snapshot_text = result[1].text
    assert "🔍 Example Page" in snapshot_text
    assert "📍 https://example.com/page" in snapshot_text
    assert "🎭 Accessibility Snapshot:" in snapshot_text
    assert 'button "Submit"  [ref=1]' in snapshot_text
    assert 'link "Home" [ref=2]' in snapshot_text
    assert 'textbox "Email" [ref=3]' in snapshot_text
    assert 'button "Login" [ref=4]' in snapshot_text

    refs_text = result[2].text
    assert "🎯 Element References:" in refs_text
    assert '[ref=1]: button "Submit"' in refs_text
    assert '[ref=2]: link "Home"' in refs_text
    assert '[ref=3]: textbox "Email"' in refs_text
    assert '[ref=4]: button "Login"' in refs_text


@pytest.mark.asyncio
async def test_website_snapshot_with_network_and_console():
    """Test website snapshot with network requests and console messages"""

    # Create the mock request and response
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url = "https://api.example.com/data"
    mock_request.post_data = AsyncMock(return_value=None)

    mock_response = Mock()
    mock_response.status = 200
    mock_response.request = mock_request
    mock_response.headers = {
        "content-type": "application/json",
        "content-length": "100",
    }
    mock_response.text = AsyncMock(return_value='{"status": "ok"}')

    mock_console_msg = Mock()
    mock_console_msg.type = "log"
    mock_console_msg.text = "Page loaded successfully"

    # Store the handlers
    request_handler = None
    response_handler = None
    console_handler = None

    def on_handler(event, handler):
        nonlocal request_handler, response_handler, console_handler
        if event == "request":
            request_handler = handler
        elif event == "response":
            response_handler = handler
        elif event == "console":
            console_handler = handler

    mock_page = AsyncMock()
    mock_page.url = "https://example.com"
    mock_page.title = AsyncMock(return_value="Test Page")
    mock_page.set_default_timeout = MagicMock()
    mock_page.on = MagicMock(side_effect=on_handler)

    async def mock_goto(*args, **kwargs):
        # Simulate request/response during navigation
        if request_handler:
            await request_handler(mock_request)
        if response_handler:
            await response_handler(mock_response)
        if console_handler:
            console_handler(mock_console_msg)

    mock_page.goto = mock_goto
    mock_page.wait_for_load_state = AsyncMock()
    mock_page.wait_for_selector = AsyncMock()

    mock_locator = AsyncMock()
    mock_locator.aria_snapshot = AsyncMock(return_value='button "Click Me"')
    mock_page.locator = MagicMock(return_value=mock_locator)

    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_chromium = AsyncMock()
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    mock_playwright = AsyncMock()
    mock_playwright.chromium = mock_chromium

    with patch("src.tools.snapshot_url.async_playwright") as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright

        result = await website_snapshot("https://example.com")

    assert len(result) == 3

    summary = result[0].text
    assert (
        "✅ Captured snapshot with 1 elements, 1 requests, 1 console messages"
        in summary
    )

    snapshot_text = result[1].text
    assert "🌐 Network Requests:" in snapshot_text
    assert "🌐 GET https://api.example.com/data" in snapshot_text
    assert "Status: 200" in snapshot_text
    assert 'Response: {"status": "ok"}' in snapshot_text

    assert "🖥️ Console:" in snapshot_text
    assert "🖥️ [LOG] Page loaded successfully" in snapshot_text


@pytest.mark.asyncio
async def test_website_snapshot_invalid_url():
    """Test website snapshot with invalid URL"""

    result = await website_snapshot("not-a-valid-url")

    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "Url must be valid, example: https://example.com" in result[0].text


@pytest.mark.asyncio
async def test_website_snapshot_browser_launch_error():
    """Test website snapshot handles browser launch errors gracefully"""

    # Create a mock browser that has a close method
    mock_browser = AsyncMock()
    mock_browser.close = AsyncMock()

    mock_chromium = AsyncMock()
    # First call to launch raises exception, but browser is still created for finally block
    mock_chromium.launch = AsyncMock(return_value=mock_browser)

    mock_playwright = AsyncMock()
    mock_playwright.chromium = mock_chromium

    # Mock browser.new_context to raise the exception instead
    mock_browser.new_context = AsyncMock(
        side_effect=Exception("Browser context creation failed")
    )

    with patch("src.tools.snapshot_url.async_playwright") as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        mock_async_playwright.return_value.__aexit__.return_value = None

        result = await website_snapshot("https://example.com")

    assert len(result) == 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "❌ Failed: Browser context creation failed" in result[0].text

    # Verify browser was closed
    mock_browser.close.assert_called_once()
