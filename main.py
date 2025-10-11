try:
    import nautica
except Exception as e:
    import traceback, colorama
    from nautica.services.logger import LogManager
    
    LogManager("Main").critical(f"Framework failed to initialize: {e}")
    print(colorama.Fore.LIGHTBLACK_EX)
    traceback.print_exc()

print(colorama.Fore.RESET)