import logging

from .config import settings

# CAUTION: This file is AI generated (:

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("dynaconf")


def explore_settings() -> None:
    """Exploring what attributes actually exist in settings."""
    logger.info("=== EXPLORING SETTINGS OBJECT ===")

    # Get all attributes of the settings object
    all_attrs = dir(settings)

    # Filter only "our" settings (not internal ones)
    user_settings = [
        attr
        for attr in all_attrs
        if not attr.startswith("_")
        and attr
        not in [
            "get",
            "exists",
            "keys",
            "values",
            "items",
            "reload",
            "validators",
            "current_env",
        ]
    ]

    logger.info(f"Available settings: {user_settings}")

    # Check each setting
    for setting in user_settings:
        try:
            value = getattr(settings, setting)
            logger.info(f"  {setting}: {value}")
        except Exception as e:
            logger.info(f"  {setting}: <access error: {e}>")


def read_settings_safely() -> None:
    """Safe reading of settings."""
    logger.info("\n=== SAFE SETTINGS READING ===")

    # Method 1: Using get() with default value
    debug = settings.get("DEBUG", False)
    logger.info(f"DEBUG (via get): {debug}")

    # Method 2: Check existence before access
    if settings.exists("VERSION"):
        logger.info(f"VERSION: {settings.VERSION}")
    else:
        logger.info("VERSION not found")

    # Method 3: Using hasattr
    if hasattr(settings, "database"):
        logger.info(f"database: {settings.database}")

    # Method 4: Direct access to known settings
    known_settings = [
        "DEBUG",
        "ENVIRONMENTS_FOR_DYNACONF",
        "SETTINGS_FILE_FOR_DYNACONF",
        "LOADERS_FOR_DYNACONF",
    ]
    for ks in known_settings:
        value = settings.get(ks, "not found")
        logger.info(f"{ks}: {value}")


def update_settings_safely() -> None:
    """Safe settings update."""
    logger.info("\n=== UPDATING SETTINGS ===")

    # Creating new settings (they will be automatically saved to DB)
    try:
        settings.MY_CUSTOM_SETTING = "test_value_123"
        logger.info("✓ MY_CUSTOM_SETTING set to 'test_value_123'")
    except Exception as e:
        logger.error(f"✗ Error setting MY_CUSTOM_SETTING: {e}")

    try:
        settings.ANOTHER_SETTING = 42
        logger.info("✓ ANOTHER_SETTING set to 42")
    except Exception as e:
        logger.error(f"✗ Error setting ANOTHER_SETTING: {e}")

    try:
        settings.NESTED_CONFIG = {"key1": "value1", "key2": [1, 2, 3]}
        logger.info(f"✓ NESTED_CONFIG set to {settings.NESTED_CONFIG}")
    except Exception as e:
        logger.error(f"✗ Error setting NESTED_CONFIG: {e}")


def demonstrate_dynaconf_features() -> None:
    """Demonstrating Dynaconf capabilities."""
    logger.info("\n=== DYNACONF CAPABILITIES ===")

    # Current environment
    env = settings.get("CURRENT_ENV", "default")
    logger.info(f"Current environment: {env}")

    # All loaded files
    settings_files = settings.get("SETTINGS_FILES", [])
    logger.info(f"Settings files: {settings_files}")

    # Loaders
    loaders = settings.get("LOADERS_FOR_DYNACONF", [])
    logger.info(f"Loaders: {loaders}")

    # All settings keys
    all_keys = list(settings.keys())
    logger.info(f"Total keys in settings: {len(all_keys)}")
    logger.info(f"First 10 keys: {all_keys[:10]}")


def simulate_application_usage() -> None:
    """Simulating application usage."""
    logger.info("\n=== SIMULATING APPLICATION OPERATION ===")

    # Reading configuration at startup
    logger.info("Loading application configuration...")

    app_config = {
        "debug": settings.get("DEBUG", False),
        "env": settings.get("ENV_FOR_DYNACONF", "development"),
        "version": settings.get("VERSION", "1.0.0"),
    }
    logger.info(f"Application configuration: {app_config}")

    # Changing configuration during runtime
    logger.info("Updating configuration during runtime...")

    settings.APP_UPTIME = 3600
    settings.APP_STATUS = "running"
    settings.APP_USERS_COUNT = 150

    logger.info(f"APP_UPTIME: {settings.get('APP_UPTIME')}")
    logger.info(f"APP_STATUS: {settings.get('APP_STATUS')}")
    logger.info(f"APP_USERS_COUNT: {settings.get('APP_USERS_COUNT')}")

    # Reading updated configuration
    updated_config = {
        key: settings.get(key)
        for key in ["APP_UPTIME", "APP_STATUS", "APP_USERS_COUNT"]
        if settings.exists(key)
    }
    logger.info(f"Updated configuration: {updated_config}")


def check_database_persistence() -> None:
    """Checking database persistence."""
    logger.info("\n=== CHECKING DATABASE PERSISTENCE ===")

    # Settings we created
    custom_settings = [
        "MY_CUSTOM_SETTING",
        "ANOTHER_SETTING",
        "NESTED_CONFIG",
        "APP_UPTIME",
        "APP_STATUS",
        "APP_USERS_COUNT",
    ]

    for setting in custom_settings:
        if settings.exists(setting):
            value = settings.get(setting)
            logger.info(f"✓ {setting} = {value} (saved to DB)")
        else:
            logger.info(f"✗ {setting} not found in settings")


def main() -> None:
    """Main function."""
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING CONFIG EXAMPLE")
    logger.info("\n" + "=" * 60)

    # Step 1: Explore what actually exists in settings
    explore_settings()

    # Step 2: Safely read settings
    read_settings_safely()

    # Step 3: Demonstrate Dynaconf capabilities
    demonstrate_dynaconf_features()

    # Step 4: Update settings
    update_settings_safely()

    # Step 5: Simulate application usage
    simulate_application_usage()

    # Step 6: Check database persistence
    check_database_persistence()

    logger.info("\n" + "=" * 60)
    logger.info("EXAMPLE COMPLETED")
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    main()
