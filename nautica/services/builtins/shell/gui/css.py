TCSS = """
/* Main Layout */
Header {
    height: 3;
    dock: top;
    padding: 0 1;
    border: round $primary;
}

.page { height: 1fr; }
.spacer { width: 1fr; }

/* Home Page */
HomePage {
    height: 1fr;
    width: 1fr;
}

HomePage #log {
    height: 1fr;
    width: 1fr;
    
    border: hkey $primary;
    background: $panel;
    padding: 0 1;
    margin: 1;
}

#log-input {
    height: 1;
    border: none;
    
    width: 1fr;
    margin: 0 1 0 0;
}

#log-autoscroll {
    height: 1;
    border: none;
    
    padding: 0;
    background: $background;
}

.log-timestamp {
    opacity: 30%;
    width: 9;
}

.log-level {
    width: 10;
    text-overflow: ellipsis;
}

.log-module { 
    width: 20;
    min-width: 30;
    text-overflow: ellipsis;
    margin: 0 2 0 0;
}

.log-level-info { color: $primary; }
.log-level-ok { color: $success; }
.log-level-warn { color: $warning; }
.log-level-error { color: $error; }
.log-level-critical { color: $error; }
.log-level-debug { color: $secondary; }
.log-level-trace { color: $surface; }

.log-message { 
    width: 1fr;
}

"""
