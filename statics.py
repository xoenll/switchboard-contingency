class SwitchStatus:
    DISABLED = "1"
    SELECTIVE = "2"
    GLOBAL = "3"
    INHERIT = "4"


class Routes:
    ADD = "/add_condition"
    REMOVE = "/remove_condition"
    STATUS = "/status"
    POST = "/check-feature-list"
    GET = "/feature-flags"
