from textual.theme import Theme

frostTheme = Theme(
    name="frost",
    
    primary="#45a6ff",    
    secondary="#6ab8ff",
    accent="#c4e2fe",
        
    foreground="#d9e3f7",
    background="#000117",
        
    success="#67ff9b",
    warning="#ffc768",
    error="#fe6c6c",
        
    surface="#1e213d",
    panel="#14162a",
        
    dark=True,
    
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#45a6ff",
        "input-selection-background": "#45a6ff 35%",        
    },
)

catppuccinTheme = Theme(
    name="catppuccin",
    
    primary="#89b4fa",    
    secondary="#cba6f7",
    accent="#f5c2e7",
        
    foreground="#cdd6f4",
    background="#1e1e2e",
        
    success="#a6e3a1",
    warning="#f9e2af",
    error="#f38ba8",
        
    surface="#313244",
    panel="#11111b",
        
    dark=True,
    
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#cba6f7",
        "input-selection-background": "#cba6f7 35%",        
    },
)