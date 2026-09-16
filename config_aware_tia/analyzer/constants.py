# ============================================================================== 
# Shared constants used by the Configuration-Aware Test Impact Analyzer.
# ============================================================================== 

# Define source-code extensions that can be inspected by the lexical analyzer.
SOURCE_EXTENSIONS = {  # Start the supported source-code extension set.
    ".py",  # Support Python source files.
    ".java",  # Support Java source files.
    ".js",  # Support JavaScript source files.
    ".jsx",  # Support React JavaScript source files.
    ".ts",  # Support TypeScript source files.
    ".tsx",  # Support React TypeScript source files.
    ".cpp",  # Support C++ source files.
    ".c",  # Support C source files.
    ".h",  # Support C/C++ header files.
    ".hpp",  # Support C++ header files.
    ".cs",  # Support C# source files.
    ".go",  # Support Go source files.
    ".rs",  # Support Rust source files.
    ".kt",  # Support Kotlin source files.
    ".php",  # Support PHP source files.
}  # Finish the source-code extension set.

# Define configuration extensions that can be parsed by the analyzer.
CONFIG_EXTENSIONS = {  # Start the supported configuration extension set.
    ".yml",  # Support YAML files.
    ".yaml",  # Support YAML files.
    ".properties",  # Support Java properties files.
    ".json",  # Support JSON files.
    ".xml",  # Support XML files.
}  # Finish the configuration extension set.

# Define common runtime-setting words that matter in microservice communication.
IMPORTANT_CONFIG_WORDS = {  # Start the important configuration-word set.
    "timeout",  # Track timeout settings.
    "timeouts",  # Track plural timeout settings.
    "retry",  # Track retry settings.
    "retries",  # Track plural retry settings.
    "attempt",  # Track retry-attempt settings.
    "attempts",  # Track retry-attempt settings.
    "backoff",  # Track retry backoff settings.
    "feature",  # Track feature settings.
    "flag",  # Track feature flags.
    "flags",  # Track plural feature flags.
    "connection",  # Track connection settings.
    "pool",  # Track connection-pool settings.
}  # Finish the important configuration-word set.
