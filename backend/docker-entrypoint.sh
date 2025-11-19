#!/bin/bash
# Docker entrypoint script for VAPID key generation automation
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting backend service initialization...${NC}"

# Check if VAPID keys are already set in environment
if [ -n "$VAPID_PUBLIC_KEY" ] && [ -n "$VAPID_PRIVATE_KEY" ]; then
    echo -e "${GREEN}VAPID keys found in environment variables${NC}"
    
    # Validate keys if validation script is available
    if python -c "from generate_vapid_keys import validate_vapid_keys, get_vapid_keys_from_env; import sys; pub, priv = get_vapid_keys_from_env(); sys.exit(0 if validate_vapid_keys(pub, priv) else 1)" 2>/dev/null; then
        echo -e "${GREEN}VAPID keys are valid${NC}"
    else
        echo -e "${YELLOW}Warning: VAPID keys in environment may be invalid${NC}"
    fi
else
    echo -e "${YELLOW}VAPID keys not found in environment variables${NC}"
    
    # Check if .env file exists and has keys
    if [ -f "/app/.env" ]; then
        echo -e "${GREEN}Checking .env file for VAPID keys...${NC}"
        
        # Try to load keys from .env and validate
        if python -c "from generate_vapid_keys import read_env_file, validate_vapid_keys; from pathlib import Path; env = read_env_file(Path('/app/.env')); pub = env.get('VAPID_PUBLIC_KEY'); priv = env.get('VAPID_PRIVATE_KEY'); import sys; sys.exit(0 if (pub and priv and validate_vapid_keys(pub, priv)) else 1)" 2>/dev/null; then
            echo -e "${GREEN}Valid VAPID keys found in .env file${NC}"
            # Export keys to environment
            export $(grep -E '^VAPID_(PUBLIC|PRIVATE)_KEY=' /app/.env | xargs)
            export $(grep -E '^VAPID_EMAIL=' /app/.env | xargs || echo "VAPID_EMAIL=mailto:example@example.com")
        else
            echo -e "${YELLOW}No valid VAPID keys found in .env file${NC}"
            echo -e "${GREEN}Generating new VAPID keys...${NC}"
            
            # Generate keys and write to .env
            python -c "
from generate_vapid_keys import ensure_vapid_keys
from pathlib import Path
import os

public_key, private_key, was_generated = ensure_vapid_keys(
    env_path=Path('/app/.env'),
    write_to_file=True,
    silent=True
)

if public_key and private_key:
    # Export to environment for this session
    os.environ['VAPID_PUBLIC_KEY'] = public_key
    os.environ['VAPID_PRIVATE_KEY'] = private_key
    os.environ['VAPID_EMAIL'] = os.getenv('VAPID_EMAIL', 'mailto:example@example.com')
    print('VAPID keys generated and written to .env file')
else:
    print('ERROR: Failed to generate VAPID keys')
    exit(1)
"
            
            # Reload environment variables from .env
            export $(grep -E '^VAPID_' /app/.env | xargs)
        fi
    else
        echo -e "${YELLOW}.env file not found${NC}"
        echo -e "${GREEN}Generating new VAPID keys...${NC}"
        
        # Generate keys and create .env file
        python -c "
from generate_vapid_keys import ensure_vapid_keys
from pathlib import Path
import os

public_key, private_key, was_generated = ensure_vapid_keys(
    env_path=Path('/app/.env'),
    write_to_file=True,
    silent=True
)

if public_key and private_key:
    # Export to environment for this session
    os.environ['VAPID_PUBLIC_KEY'] = public_key
    os.environ['VAPID_PRIVATE_KEY'] = private_key
    os.environ['VAPID_EMAIL'] = os.getenv('VAPID_EMAIL', 'mailto:example@example.com')
    print('VAPID keys generated and written to .env file')
else:
    print('ERROR: Failed to generate VAPID keys')
    exit(1)
"
        
        # Reload environment variables from .env if it was created
        if [ -f "/app/.env" ]; then
            export $(grep -E '^VAPID_' /app/.env | xargs)
        fi
    fi
fi

# Verify keys are available
if [ -z "$VAPID_PUBLIC_KEY" ] || [ -z "$VAPID_PRIVATE_KEY" ]; then
    echo -e "${RED}ERROR: VAPID keys are not available. Cannot start service.${NC}"
    exit 1
fi

echo -e "${GREEN}VAPID keys are configured and ready${NC}"
echo -e "${GREEN}Starting FastAPI application...${NC}"

# Execute the main command
exec "$@"
