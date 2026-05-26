TCSS = """
/* Main Layout */
Header {
    height: 3;
    dock: top;
    border-top: dashed $primary;
}

.page { height: 1fr; }
.spacer { width: 1fr; }

/* Home Page */
HomePage {
    height: 1fr;
    width: 1fr;
}


HomePage #home-container {
    height: 1fr;
    width: 1fr;
    
    padding: 0 1;
    margin: 1 2;
}

HomePage #log {
    width: 1fr;
    
    border: round $secondary;
}

#log-input {
    height: 1;
    border: none;
    
    width: 1fr;
    margin: 0 1 0 0;
}

.checkbox-sm {
    height: 1;
    border: none;
    
    padding: 0;
    background: $background;
}

#log-footer {
    padding: 0 2 1 1;
}

#log-autoscroll {
    padding: 0 2 0 0;
}

.log-timestamp {
    opacity: 30%;
    width: 9;
}

.log-level {
    width: 6;
    text-overflow: ellipsis;
}

.log-module { 
    max-width: 24;
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

#thread-container {
    width: 30%;
    height: 1fr;
    
    margin: 0 0 0 1;
}

#threads {
    width: 1fr;
    height: 70%;
    margin: 0 1 0 0;
    
    border: round $secondary;
    background: $background;
}

#threadsAsync {
    width: 1fr;
    height: 30%;
    
    border: round $secondary;
    background: $background;
}

/* Auto Complete */
CommandInput {
    height: auto;
    width: 1fr;
}

#cmd-input {
    height: 1;
    border: none;
    width: 1fr;
}

#suggestions {
    layer: above;
    padding: 0;
    dock: bottom;
    margin-bottom: 2;
    margin-left: 1;
    width: 50%;
    
    display: none;
    border: none;
}
"""
