"""Browse FRR prefixes and inspect trace_route output in a Textual UI."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.widgets import Footer, Header, OptionList, Static
from textual.widgets.option_list import Option, OptionDoesNotExist

from correlate import format_trace_report, trace_route
from frr import get_routes
from kernel import get_kernel_routes
from redis import get_apply_db_routes


def _fetch_traces():
    frr = get_routes()
    if not frr:
        return None
    kernel = get_kernel_routes() or {}
    appl_db = get_apply_db_routes() or {}
    prefixes = sorted(frr.keys())
    details = {p: trace_route(p, frr, kernel, appl_db) for p in prefixes}
    return prefixes, details


class RouteBrowserApp(App[None]):
    TITLE = "sonic-trace"
    CSS = """
    #main-row {
        height: 1fr;
    }
    #prefix-pane {
        width: 38;
        min-width: 28;
        height: 100%;
        border: tall $primary;
    }
    #prefix-list {
        height: 100%;
        border: none;
    }
    #detail-pane {
        width: 1fr;
        height: 100%;
        border: tall $primary;
        padding: 0 1;
    }
    #detail-content {
        width: 100%;
    }
    #status-strip {
        dock: top;
        height: 1;
        background: $surface;
        color: $text;
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "reload", "Reload"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._prefixes: list[str] = []
        self._details: dict[str, dict] = {}
        self._load_error: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(" Prefixes | ↑↓ scroll · Tab switch pane · r reload · q quit", id="status-strip")
        with Horizontal(id="main-row"):
            with Vertical(id="prefix-pane"):
                yield OptionList(id="prefix-list")
            with ScrollableContainer(id="detail-pane"):
                yield Static("", id="detail-content", expand=True)
        yield Footer()

    async def on_mount(self) -> None:
        await self.action_reload()

    async def action_reload(self) -> None:
        plist = self.query_one("#prefix-list", OptionList)
        detail = self.query_one("#detail-content", Static)
        prev_id: str | None = None
        opt = plist.highlighted_option
        if opt is not None and opt.id is not None:
            prev_id = opt.id

        plist.clear_options()
        self._load_error = None

        out = _fetch_traces()
        if out is None:
            self._prefixes = []
            self._details = {}
            self._load_error = "Could not load FRR routes (get_routes failed or returned nothing)."
            detail.update(self._load_error)
            self.sub_title = "error"
            plist.focus()
            return

        self._prefixes, self._details = out
        self.sub_title = f"{len(self._prefixes)} prefixes"

        for p in self._prefixes:
            plist.add_option(Option(p, id=p))

        if self._prefixes:
            try:
                if prev_id is not None:
                    plist.highlighted = plist.get_option_index(prev_id)
                else:
                    plist.highlighted = 0
            except OptionDoesNotExist:
                plist.highlighted = 0
            hi = plist.highlighted if plist.highlighted is not None else 0
            self._show_detail(self._prefixes[hi])
        else:
            detail.update("No prefixes in FRR.")

        plist.focus()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if self._load_error or not event.option.id:
            return
        self._show_detail(event.option.id)

    def _show_detail(self, prefix: str) -> None:
        detail = self.query_one("#detail-content", Static)
        result = self._details.get(prefix)
        if result is None:
            detail.update("No trace data for this prefix.")
            return
        detail.update(format_trace_report(prefix, result))


def run() -> None:
    RouteBrowserApp().run()


if __name__ == "__main__":
    run()
