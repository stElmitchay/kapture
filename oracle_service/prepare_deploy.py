#!/usr/bin/env python3
"""
Prepare oracle keypair for deployment.
Converts keypair file to environment variable format.
"""

import json
import sys
from pathlib import Path

def prepare_for_deployment():
    """Convert oracle keypair to deployment format."""

    print("\n" + "="*70)
    print("🚀 PREPARE ORACLE FOR DEPLOYMENT")
    print("="*70)

    # Find oracle keypair
    keypair_path = Path.home() / '.loggerheads' / 'oracle-keypair.json'

    if not keypair_path.exists():
        print("\n❌ Oracle keypair not found!")
        print(f"   Expected: {keypair_path}")
        print("\nGenerate one first:")
        print("   python3 -m loggerheads.oracle_secure --generate")
        sys.exit(1)

    # Read keypair
    with open(keypair_path, 'r') as f:
        keypair_data = json.load(f)

    # Convert to JSON string for environment variable
    keypair_json = json.dumps(keypair_data)

    print(f"\n✅ Keypair loaded from: {keypair_path}")
    print("\n" + "="*70)
    print("📋 COPY THIS ENVIRONMENT VARIABLE")
    print("="*70)
    print("\nKey: ORACLE_KEYPAIR_JSON")
    print(f"Value: {keypair_json}")
    print("\n" + "="*70)

    print("\n📝 DEPLOYMENT STEPS:")
    print("\n1. Copy the value above (the entire JSON array)")
    print("\n2. In your deployment platform (Railway/Render/Heroku):")
    print("   - Add environment variable")
    print("   - Key: ORACLE_KEYPAIR_JSON")
    print("   - Value: [paste the JSON array]")
    print("\n3. Deploy!")
    print("\n" + "="*70)

    # Save to file for reference
    deploy_info_path = keypair_path.parent / 'oracle-deploy-env.txt'
    with open(deploy_info_path, 'w') as f:
        f.write(f"ORACLE_KEYPAIR_JSON={keypair_json}\n")

    print(f"\n💾 Also saved to: {deploy_info_path}")
    print("   (Keep this file secure! Do NOT commit to git)")

    print("\n" + "="*70)
    print("✅ READY TO DEPLOY")
    print("="*70)
    print("\nSee oracle_service/DEPLOY.md for detailed instructions.")
    print("\n")


if __name__ == '__main__':
    prepare_for_deployment()
